import time
import xxhash
from nist import run_full_nist_suite

def rando_trng(m: int) -> int:
    """
    Rando: A General-purpose True Random Number Generator.
    Generates an `m`-bit true random number.
    """
    random_bits = []
    
    # 2: i <- 1
    # 3: while i <= m do
    for _ in range(m):
        # 4: α <- GETCPUCLOCK()
        # Extract highest-precision CPU clock value available in Python
        alpha = time.perf_counter_ns()
        
        # 5: K <- CONVERTTOSTRING(α)
        # Convert the first CPU clock value to a byte string
        k = str(alpha).encode('utf-8')
        
        # 6: β <- GETCPUCLOCK()
        # Extract a second clock value immediately after. 
        # The subtle delay between `alpha` and `beta` provides entropy.
        beta = time.perf_counter_ns()
        
        # 7: l <- LENGTH(K) (Implicitly handled by the hash function in Python)
        # 8: δ <- STRINGHASHFUNCTION(K, l, β)
        # We use xxHash64 as recommended by the paper, using `beta` as the seed.
        # We mask beta to 32 bits to fit the standard seed requirement of the hash library.
        seed = beta & 0xFFFFFFFF
        delta = xxhash.xxh64(k, seed=seed).intdigest()
        # 9: B[i] <- (δ ∧ 1)
        # Bitwise ANDing the hash output with 1 extracts the Least Significant Bit (LSB)
        bit = delta & 1
        
        # Append the generated true random bit to our array
        random_bits.append(str(bit))
        
        # 10: i <- i + 1 (Implicit in Python's for-loop)
        
        if _ == m - 1:  # Print the last alpha for debugging
            print(f"Alpha (CPU Clock): {alpha}")
            print(f"Length of K: {len(k)} bytes")
            print(f"Delta (Hash Output): {delta}")

    # Combine the list of binary strings and parse as base-2 integer
    binary_string = "".join(random_bits)
    return int(binary_string, 2)

# Generate a 64-bit True Random Number
if __name__ == "__main__":
    m = 64
    true_random_number = rando_trng(m)
    print(f"Generated {m}-bit random number: {true_random_number}")
    print(f"Binary representation: {bin(true_random_number)}")