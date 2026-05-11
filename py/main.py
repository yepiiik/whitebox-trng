import time
import mmh3
import xxhash

# Helper functions to strictly match the pseudocode's procedural calls
def GETCPUCLOCK():
    # Using time_ns() to ensure high-entropy, continuously changing clock values
    return time.time_ns()

def CONVERTTOSTRING(alpha):
    return str(alpha)

def LENGTH(K):
    return len(K)

def STRINGHASHFUNCTION(K, l, beta, hash_type="xxhash"):
    """
    Simulates the C-level hash function call. 
    It takes the string K, its length l, and the seed beta.
    """
    # Enforce processing only up to length 'l' (as expected by C implementations)
    key_bytes = K[:l].encode('utf-8')
    
    # Hash functions natively expect a 32-bit unsigned integer for the seed.
    # While the pseudocode passes beta directly, we must mask it here 
    # to avoid overflow errors in the Python wrappers.
    seed = beta & 0xFFFFFFFF
    
    if hash_type == "murmur":
        return mmh3.hash(key_bytes, seed)
    elif hash_type == "xxhash":
        x = xxhash.xxh32(key_bytes, seed=seed)
        return x.intdigest()
    else:
        raise ValueError("Unsupported hash function")

# 1: procedure RANDO(m)
def RANDO(m, hash_type="xxhash"):
    # Pre-allocate the array. (Python arrays are 0-indexed, 
    # so we will adjust the index placement on line 9).
    B = [0] * m 
    
    # 2: i <- 1
    i = 1
    
    # 3: while i <= m do
    while i <= m:
        # 4: alpha <- GETCPUCLOCK()
        alpha = GETCPUCLOCK()
        
        # 5: K <- CONVERTTOSTRING(alpha)
        K = CONVERTTOSTRING(alpha)
        
        # 6: beta <- GETCPUCLOCK()
        beta = GETCPUCLOCK()
        
        # 7: l <- LENGTH(K)
        l = LENGTH(K)
        
        # 8: delta <- STRINGHASHFUNCTION(K, l, beta)
        delta = STRINGHASHFUNCTION(K, l, beta, hash_type)
        
        # 9: B[i] <- (delta \wedge 1)
        # Using bitwise AND (&) to extract the LSB. 
        # Note: We use [i - 1] because Python is 0-indexed, but the pseudocode is 1-indexed.
        B[i - 1] = (delta & 1)
        
        # 10: i <- i + 1
        i = i + 1
        
    # 11: end while
    return B
# 12: end procedure

# --- Example Execution ---
if __name__ == "__main__":
    m_bits = 64
    
    # Execute the algorithm
    generated_array = RANDO(m_bits, hash_type="xxhash")
    
    print(f"Generated {m_bits}-bit Array:\n{generated_array}")