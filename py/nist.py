import numpy as np
from nistrng import check_eligibility_all_battery, run_all_battery, SP800_22R1A_BATTERY

# 1. Read your file
with open("batch1m.txt", "r") as f:
    binary_string = f.read().strip()

# Convert the string to a numpy array of integers
binary_array = np.array([int(bit) for bit in binary_string], dtype=int)

# 2. Run the NIST tests
print("Starting NIST tests (this might take a minute)...")
eligible_battery: dict = check_eligibility_all_battery(binary_array, SP800_22R1A_BATTERY)
results = run_all_battery(binary_array, eligible_battery, False)

# 3. Print the results
print(f"{'Test Name':<32} | {'Status':<6} | {'Score (P-Value)'}")
print("-" * 65)

for result, elapsed_time in results:
    status = "PASS" if result.passed else "FAIL"
    
    # Some tests return a single float, others return a list of floats
    if isinstance(result.score, (list, np.ndarray)):
        # Format a list of scores to 4 decimal places
        score_str = ", ".join([f"{float(s):.4f}" for s in result.score])
    else:
        # Format a single score to 6 decimal places
        score_str = f"{float(result.score):.6f}"
        
    print(f"{result.name:<32} | {status:<6} | {score_str}")