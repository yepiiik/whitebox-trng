import numpy as np
from nistrng import pack_sequence, unpack_sequence, check_eligibility_all_battery, run_all_battery, SP800_22R1A_BATTERY

def run_full_nist_suite(bits):
    # Convert the list of bits into a numpy array of 8-bit integers
    binary_sequence = np.array(bits, dtype=int)

    # Check which NIST tests are eligible for the given bit length
    eligible_battery: dict = check_eligibility_all_battery(binary_sequence, SP800_22R1A_BATTERY)

    print(f"Eligible tests for {len(bits)} bits: {len(eligible_battery)}")

    # Run all eligible tests
    results = run_all_battery(binary_sequence, eligible_battery, False)

    print("\n--- Full NIST Test Results ---")
    for result, elapsed_time in results:
        test_passed = result.passed
        print(f"Test: {result.name}")
        print(f" - Passed: {test_passed}")
        print(f" - P-Value: {result.p_value:.6f}\n")