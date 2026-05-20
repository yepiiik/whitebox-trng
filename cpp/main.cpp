#include <iostream>
#include <fstream>
#include <string>
#include <chrono>
#include <cstdint>
#include <vector>
#include <cstring>
#include <openssl/evp.h>
#include <openssl/err.h>

// --- TRNG SECTION ---

// Interface for Random Number Generators
class IRandomGenerator {
public:
    virtual ~IRandomGenerator() = default;
    virtual uint8_t next_bit() = 0;
    
    virtual std::vector<uint8_t> generate_bytes(size_t num_bytes) {
        std::vector<uint8_t> buffer(num_bytes);
        for (size_t i = 0; i < num_bytes; ++i) {
            uint8_t current_byte = 0;
            for (int bit = 0; bit < 8; ++bit) {
                current_byte = (current_byte << 1) | (next_bit() & 1);
            }
            buffer[i] = current_byte;
        }
        return buffer;
    }
};

// MurmurHash3 based Random Number Generator
class RandoGenerator : public IRandomGenerator {
public:
    RandoGenerator(uint32_t seed = 0) : seed_(seed) {}

    uint8_t next_bit() override {
        uint64_t alpha = get_cpu_clock();
        size_t l = sizeof(alpha);
        uint64_t beta = get_cpu_clock();
        
        uint32_t delta = murmur3_32(
            reinterpret_cast<const uint8_t*>(&alpha), 
            l,
            static_cast<uint32_t>(beta) ^ seed_
        );
        
        return static_cast<uint8_t>(delta & 1);
    }

private:
    uint32_t seed_;

    static uint64_t get_cpu_clock() {
        return std::chrono::high_resolution_clock::now().time_since_epoch().count();
    }

    static uint32_t murmur3_32(const uint8_t* key, size_t len, uint32_t seed) {
        uint32_t h = seed;
        if (len > 3) {
            const uint32_t* key_x4 = (const uint32_t*)key;
            size_t i = len >> 2;
            do {
                uint32_t k = *key_x4++;
                k *= 0xcc9e2d51; k = (k << 15) | (k >> 17); k *= 0x1b873593;
                h ^= k; h = (h << 13) | (h >> 19); h = (h * 5) + 0xe6546b64;
            } while (--i);
            key = (const uint8_t*)key_x4;
        }
        if (len & 3) {
            size_t i = len & 3;
            uint32_t k = 0;
            key = &key[i - 1];
            do {
                k <<= 8; k |= *key--;
            } while (--i);
            k *= 0xcc9e2d51; k = (k << 15) | (k >> 17); k *= 0x1b873593;
            h ^= k;
        }
        h ^= len; h ^= h >> 16; h *= 0x85ebca6b; h ^= h >> 13; h *= 0xc2b2ae35; h ^= h >> 16;
        return h;
    }
};

// --- CRYPTO SECTION ---

// Helper to handle OpenSSL errors safely
void handleErrors() {
    ERR_print_errors_fp(stderr);
    abort();
}

// AES-GCM Encryption
std::vector<uint8_t> aes_gcm_encrypt(const std::vector<uint8_t>& plaintext, 
                                     const std::vector<uint8_t>& key, 
                                     const std::vector<uint8_t>& nonce) {
    EVP_CIPHER_CTX* ctx = EVP_CIPHER_CTX_new();
    if (!ctx) handleErrors();

    if (1 != EVP_EncryptInit_ex(ctx, EVP_aes_256_gcm(), nullptr, nullptr, nullptr)) handleErrors();
    if (1 != EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_IVLEN, (int)nonce.size(), nullptr)) handleErrors();
    if (1 != EVP_EncryptInit_ex(ctx, nullptr, nullptr, key.data(), nonce.data())) handleErrors();

    std::vector<uint8_t> ciphertext(plaintext.size());
    int len = 0;

    if (1 != EVP_EncryptUpdate(ctx, ciphertext.data(), &len, plaintext.data(), (int)plaintext.size())) handleErrors();

    if (1 != EVP_EncryptFinal_ex(ctx, ciphertext.data() + len, &len)) handleErrors();

    std::vector<uint8_t> tag(16);
    if (1 != EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_GET_TAG, 16, tag.data())) handleErrors();

    EVP_CIPHER_CTX_free(ctx);

    std::vector<uint8_t> package;
    package.reserve(nonce.size() + ciphertext.size() + tag.size());
    package.insert(package.end(), nonce.begin(), nonce.end());
    package.insert(package.end(), ciphertext.begin(), ciphertext.end());
    package.insert(package.end(), tag.begin(), tag.end());

    return package;
}

// AES-GCM Decryption
std::vector<uint8_t> aes_gcm_decrypt(const std::vector<uint8_t>& package, 
                                     const std::vector<uint8_t>& key) {
    const size_t NONCE_SIZE = 12;
    const size_t TAG_SIZE = 16;

    if (package.size() < NONCE_SIZE + TAG_SIZE) {
        throw std::runtime_error("Payload too short.");
    }

    std::vector<uint8_t> nonce(package.begin(), package.begin() + NONCE_SIZE);
    std::vector<uint8_t> tag(package.end() - TAG_SIZE, package.end());
    std::vector<uint8_t> ciphertext(package.begin() + NONCE_SIZE, package.end() - TAG_SIZE);

    EVP_CIPHER_CTX* ctx = EVP_CIPHER_CTX_new();
    if (!ctx) handleErrors();

    if (1 != EVP_DecryptInit_ex(ctx, EVP_aes_256_gcm(), nullptr, nullptr, nullptr)) handleErrors();
    if (1 != EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_IVLEN, (int)nonce.size(), nullptr)) handleErrors();
    if (1 != EVP_DecryptInit_ex(ctx, nullptr, nullptr, key.data(), nonce.data())) handleErrors();

    std::vector<uint8_t> plaintext(ciphertext.size());
    int len = 0;
    int plaintext_len = 0;

    if (1 != EVP_DecryptUpdate(ctx, plaintext.data(), &len, ciphertext.data(), (int)ciphertext.size())) handleErrors();
    plaintext_len = len;

    if (1 != EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_TAG, (int)TAG_SIZE, tag.data())) handleErrors();

    int ret = EVP_DecryptFinal_ex(ctx, plaintext.data() + len, &len);

    EVP_CIPHER_CTX_free(ctx);

    if (ret > 0) {
        plaintext_len += len;
        plaintext.resize(plaintext_len);
        return plaintext;
    } else {
        throw std::runtime_error("Decryption failed! Authentication tag is invalid.");
    }
}

// --- UTILITY SECTION ---

void generate_nist_data(const std::string& filename, int total_bits, IRandomGenerator& generator) {
    std::ofstream outfile(filename, std::ios::binary);
    if (!outfile.is_open()) {
        std::cerr << "Failed to open file!" << std::endl;
        return;
    }

    std::cout << "Generating " << total_bits << " bits to " << filename << " (binary)..." << std::endl;

    uint8_t current_byte = 0;
    int bit_count = 0;

    for (int i = 0; i < total_bits; ++i) {
        uint8_t bit = generator.next_bit();
        current_byte = (current_byte << 1) | (bit & 1);
        bit_count++;

        if (bit_count == 8) {
            outfile.put(static_cast<char>(current_byte));
            current_byte = 0;
            bit_count = 0;
        }

        if ((i + 1) % 1000000 == 0) {
            std::cout << "Generated " << (i + 1) << " bits..." << std::endl;
        }
    }

    if (bit_count > 0) {
        current_byte <<= (8 - bit_count);
        outfile.put(static_cast<char>(current_byte));
    }
    
    outfile.close();
    std::cout << "Generation complete!" << std::endl;
}

// --- BENCHMARK SECTION ---

void benchmark_trng_throughput(IRandomGenerator& generator, int duration_ms) {
    std::cout << "\nStarting TRNG benchmark: generating bits for " << duration_ms << "ms..." << std::endl;

    long long bit_count = 0;
    auto start = std::chrono::high_resolution_clock::now();
    auto end_time = start + std::chrono::milliseconds(duration_ms);

    while (true) {
        for (int i = 0; i < 10000; ++i) {
            generator.next_bit();
            bit_count++;
        }
        if (std::chrono::high_resolution_clock::now() >= end_time) break;
    }

    auto actual_end = std::chrono::high_resolution_clock::now();
    auto actual_duration = std::chrono::duration_cast<std::chrono::microseconds>(actual_end - start).count();

    double seconds = actual_duration / 1000000.0;
    std::cout << "TRNG Benchmark complete!" << std::endl;
    std::cout << "Total bits generated: " << bit_count << std::endl;
    std::cout << "Throughput: " << (bit_count / seconds) / 1000.0 << " kbit/s" << std::endl;
    std::cout << "Throughput: " << (bit_count / 8.0 / seconds) / 1024.0 << " KiB/s" << std::endl;
}

void benchmark_encryption(IRandomGenerator& generator, int duration_ms) {
    std::cout << "\nStarting encryption benchmark: encrypting messages for " << duration_ms << "ms..." << std::endl;

    std::vector<uint8_t> secret_key = generator.generate_bytes(32);
    std::vector<uint8_t> trng_nonce = generator.generate_bytes(12);
    std::string message = "Performance test message for AES-GCM benchmark.";
    std::vector<uint8_t> plaintext(message.begin(), message.end());

    long long count = 0;
    auto start = std::chrono::high_resolution_clock::now();
    auto end_time = start + std::chrono::milliseconds(duration_ms);

    while (std::chrono::high_resolution_clock::now() < end_time) {
        std::vector<uint8_t> packet = aes_gcm_encrypt(plaintext, secret_key, trng_nonce);
        count++;
    }

    auto actual_end = std::chrono::high_resolution_clock::now();
    auto actual_duration = std::chrono::duration_cast<std::chrono::microseconds>(actual_end - start).count();

    double seconds = actual_duration / 1000000.0;
    std::cout << "Encryption Benchmark complete!" << std::endl;
    std::cout << "Total messages encrypted: " << count << std::endl;
    std::cout << "Throughput: " << (count / seconds) << " messages/second" << std::endl;
}

int main() {
    RandoGenerator generator;

    // 1. Generate TRNG-backed Key (32 bytes) and Nonce (12 bytes)
    std::cout << "Generating high-entropy key and nonce from TRNG..." << std::endl;
    std::vector<uint8_t> secret_key = generator.generate_bytes(32);
    std::vector<uint8_t> trng_nonce = generator.generate_bytes(12);

    // 2. Prepare message
    std::string secret_message = "Hello! This is a message encrypted via TRNG inputs.";
    std::vector<uint8_t> plaintext(secret_message.begin(), secret_message.end());

    std::cout << "Original Text: " << secret_message << std::endl;

    // 3. Encrypt
    try {
        std::vector<uint8_t> packet = aes_gcm_encrypt(plaintext, secret_key, trng_nonce);
        std::cout << "Encrypted packet size: " << packet.size() << " bytes." << std::endl;

        // 4. Decrypt
        std::vector<uint8_t> decrypted_bytes = aes_gcm_decrypt(packet, secret_key);
        std::string decrypted_message(decrypted_bytes.begin(), decrypted_bytes.end());
        std::cout << "Decrypted Text: " << decrypted_message << std::endl;

        // 5. Benchmarks
        benchmark_trng_throughput(generator, 1000); // 1 second TRNG test
        benchmark_encryption(generator, 200);      // 200ms Encryption test

    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}
