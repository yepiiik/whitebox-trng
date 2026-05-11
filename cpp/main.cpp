#include <iostream>
#include <fstream>
#include <string>
#include <chrono>
#include <cstdint>

// Non-cryptographic String Hash Function (MurmurHash3 32-bit)
// The paper uses MurmurHash or xxHash for bit mixing. 
uint32_t murmur3_32(const uint8_t* key, size_t len, uint32_t seed) {
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

uint64_t get_cpu_clock() {
    return std::chrono::high_resolution_clock::now().time_since_epoch().count();
}

void generate_nist_data(const std::string& filename, int total_bits) {
    std::ofstream outfile(filename);
    if (!outfile.is_open()) {
        std::cerr << "Failed to open file!" << std::endl;
        return;
    }

    std::cout << "Generating " << total_bits << " bits to " << filename << "..." << std::endl;

    for (int i = 0; i < total_bits; ++i) {
        uint64_t alpha = get_cpu_clock();
        std::string k = std::to_string(alpha);
        uint64_t beta = get_cpu_clock();
        size_t l = k.length();
        
        uint32_t delta = murmur3_32(
            reinterpret_cast<const uint8_t*>(k.data()), l, static_cast<uint32_t>(beta)
        );
        
        outfile << (delta & 1);

        if ((i + 1) % 1000000 == 0) {
            std::cout << "Generated " << (i + 1) << " bits..." << std::endl;
        }
    }
    
    outfile.close();
    std::cout << "Generation complete!" << std::endl;
}

int main() {
    // Generate 10 million bits for NIST testing
    generate_nist_data("batch1m.txt", 2000000);
    return 0;
}