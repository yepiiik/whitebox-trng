import time
import mmh3
import xxhash

# Importing the full suite from your local nist.py file
from nist import run_full_nist_suite

def get_cpu_clock():
    """Retrieves the current CPU clock value in nanoseconds."""
    return time.perf_counter_ns()

def rando(m, hash_type="xxhash"):
    """Generates a true random number of m bits using the Rando algorithm."""
    B = []
    for _ in range(m):
        alpha = get_cpu_clock()
        K = str(alpha)
        
        beta = get_cpu_clock()
        seed = beta & 0xFFFFFFFF
        
        if hash_type == "murmur":
            delta = mmh3.hash(K, seed)
        elif hash_type == "xxhash":
            x = xxhash.xxh32(K, seed=seed)
            delta = x.intdigest()
        else:
            raise ValueError("Unsupported hash_type.")
            
        B.append(delta & 1)
        
    return B

# --- Example Usage ---
if __name__ == "__main__":
    # Generate a large sample size for statistical testing 
    # (10,000,000 bits aligns with the paper's testing parameters for NIST SP 800-22)
    test_bit_length = 10000000 
    
    print(f"Generating {test_bit_length} bits using xxHash...")
    random_bits_xx = rando(test_bit_length, hash_type="xxhash")

    print("-" * 30)
    print("Running Full NIST SP 800-22 Test Suite...")
    print("-" * 30)
    
    # Run the full NIST suite on the generated bits
    run_full_nist_suite(random_bits_xx)