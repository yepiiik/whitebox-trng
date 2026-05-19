#include <iostream>
#include <fstream>
#include <string>
#include <chrono>
#include <cstdint>
#include <vector>

// Interface for Random Number Generators
class IRandomGenerator {
public:
    virtual ~IRandomGenerator() = default;
    virtual uint8_t next_bit() = 0;
};

// MurmurHash3 based Random Number Generator
class MurmurHashGenerator : public IRandomGenerator {
public:
    MurmurHashGenerator(uint32_t seed = 0) : seed_(seed) {}

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

    // Returns the current high-resolution clock count as a 64-bit value.
    // This is used to introduce timing-based variability into the generator.
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

    // Handle remaining bits if total_bits is not a multiple of 8
    if (bit_count > 0) {
        current_byte <<= (8 - bit_count); // Pad with zeros to the right
        outfile.put(static_cast<char>(current_byte));
    }
    
    outfile.close();
    std::cout << "Generation complete!" << std::endl;
}

int main() {
    MurmurHashGenerator generator;
    // Generate 100 million bits for NIST testing (100 bitstreams of 1,000,000 bits each)
    generate_nist_data("batch1m.bin", 100000000, generator);
    return 0;
}