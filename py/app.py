import time
import xxhash
import matplotlib.pyplot as plt
import numpy as np
# from nist import run_full_nist_suite

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
            print(f"Beta (CPU Clock): {beta}")
            print(f"Delta (Hash Output): {delta}")

    # Combine the list of binary strings and parse as base-2 integer
    binary_string = "".join(random_bits)
    return int(binary_string, 2)

def display_alpha_beta_delta_diagram(batch_size: int = 100000) -> None:
    """
    Generate a batch of random numbers and display a diagram showing
    the distribution of alpha (CPU clock 1), beta (CPU clock 2), and 
    delta (hash output) values.
    
    Args:
        batch_size: Number of random bits to generate (default 1000)
    """
    alphas = []
    betas = []
    deltas = []
    time_diffs = []
    
    print(f"Generating {batch_size} random numbers and collecting timing data...")
    
    # Generate random numbers and collect timing data
    for i in range(batch_size):
        alpha = time.perf_counter_ns()
        alphas.append(alpha)
        
        k = str(alpha).encode('utf-8')
        beta = time.perf_counter_ns()
        betas.append(beta)
        
        seed = beta & 0xFFFFFFFF
        delta = xxhash.xxh64(k, seed=seed).intdigest()
        deltas.append(delta)
        
        # Calculate time difference between alpha and beta in nanoseconds
        time_diff = beta - alpha
        time_diffs.append(time_diff)
    
    # Create a figure with 4 subplots
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(f'Alpha, Beta, Delta Analysis for {batch_size} Generated Numbers', 
                 fontsize=16, fontweight='bold')
    
    # Subplot 1: Time difference between Beta and Alpha
    mean_diff = np.mean(time_diffs)
    std_diff = np.std(time_diffs)
    
    # Calculate percentile range to show most data while filtering outliers
    p1 = np.percentile(time_diffs, 1)
    p99 = np.percentile(time_diffs, 99)
    
    # Create histogram with filtered range
    axes[0, 0].hist(time_diffs, bins=50, color='skyblue', edgecolor='black', alpha=0.7, range=(p1, p99))
    axes[0, 0].set_xlabel('Time Difference (nanoseconds)', fontsize=11)
    axes[0, 0].set_ylabel('Frequency', fontsize=11)
    axes[0, 0].set_title(f'Beta - Alpha Time Differences (1st-99th percentile)', fontweight='bold')
    axes[0, 0].grid(axis='y', alpha=0.3)
    
    # Add statistics text
    axes[0, 0].text(0.98, 0.97, f'Mean: {mean_diff:.1f} ns\nStd Dev: {std_diff:.1f} ns\n1st %ile: {p1:.0f} ns\n99th %ile: {p99:.0f} ns',
                    transform=axes[0, 0].transAxes, fontsize=9,
                    verticalalignment='top', horizontalalignment='right',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    # Subplot 2: Delta (Hash Output) Distribution
    axes[0, 1].hist(deltas, bins=50, color='lightcoral', edgecolor='black', alpha=0.7)
    axes[0, 1].set_xlabel('Delta Value (Hash Output)', fontsize=11)
    axes[0, 1].set_ylabel('Frequency', fontsize=11)
    axes[0, 1].set_title('Delta (Hash Output) Distribution', fontweight='bold')
    axes[0, 1].grid(axis='y', alpha=0.3)
    
    # Add statistics text
    mean_delta = np.mean(deltas)
    std_delta = np.std(deltas)
    axes[0, 1].text(0.98, 0.97, f'Mean: {mean_delta:.2e}\nStd Dev: {std_delta:.2e}',
                    transform=axes[0, 1].transAxes, fontsize=10,
                    verticalalignment='top', horizontalalignment='right',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    # Subplot 3: Time Difference vs Iteration (sequence plot)
    axes[1, 0].plot(range(batch_size), time_diffs, linewidth=0.5, color='green', alpha=0.6)
    axes[1, 0].set_xlabel('Iteration', fontsize=11)
    axes[1, 0].set_ylabel('Time Difference (nanoseconds)', fontsize=11)
    axes[1, 0].set_title('Time Difference Sequence', fontweight='bold')
    axes[1, 0].grid(alpha=0.3)
    
    # Subplot 4: Summary Statistics Table
    axes[1, 1].axis('off')
    summary_data = [
        ['Metric', 'Value'],
        ['Total Numbers Generated', f'{batch_size}'],
        ['Avg Time Diff (Alpha→Beta)', f'{mean_diff:.2f} ns'],
        ['Std Dev Time Diff', f'{std_diff:.2f} ns'],
        ['Min Time Diff', f'{min(time_diffs):.0f} ns'],
        ['Max Time Diff', f'{max(time_diffs):.0f} ns'],
        ['Avg Delta Value', f'{mean_delta:.2e}'],
        ['Std Dev Delta', f'{std_delta:.2e}'],
        ['Min Delta', f'{min(deltas):.2e}'],
        ['Max Delta', f'{max(deltas):.2e}'],
    ]
    
    table = axes[1, 1].table(cellText=summary_data, cellLoc='left', loc='center',
                              colWidths=[0.5, 0.5])
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.8)
    
    # Style header row
    for i in range(2):
        table[(0, i)].set_facecolor('#40466e')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Alternate row colors
    for i in range(1, len(summary_data)):
        for j in range(2):
            if i % 2 == 0:
                table[(i, j)].set_facecolor('#f0f0f0')
            else:
                table[(i, j)].set_facecolor('#ffffff')
    
    plt.tight_layout()
    plt.show()
    
    print(f"\nDiagram displayed successfully!")
    print(f"Summary Statistics:")
    print(f"  Average time between Alpha and Beta: {mean_diff:.2f} ns")
    print(f"  Average Delta value: {mean_delta:.2e}")


def display_alpha_beta_diagram(batch_size: int = 1000) -> None:
    """
    Generate a batch of random numbers and display a diagram showing
    the alpha (CPU clock 1) and beta (CPU clock 2) distributions only.
    
    Args:
        batch_size: Number of random bits to generate (default 1000)
    """
    alphas = []
    betas = []
    
    print(f"Generating {batch_size} random numbers and collecting alpha/beta timing data...")
    
    # Generate random numbers and collect timing data
    for i in range(batch_size):
        alpha = time.perf_counter_ns()
        alphas.append(alpha)
        
        k = str(alpha).encode('utf-8')
        beta = time.perf_counter_ns()
        betas.append(beta)
    
    # Create a figure with 2 subplots
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(f'Alpha and Beta Distribution for {batch_size} Generated Numbers', 
                 fontsize=16, fontweight='bold')
    
    # Subplot 1: Alpha distribution
    mean_alpha = np.mean(alphas)
    std_alpha = np.std(alphas)
    
    axes[0].hist(alphas, bins=50, color='skyblue', edgecolor='black', alpha=0.7)
    axes[0].set_xlabel('Alpha Value (nanoseconds)', fontsize=11)
    axes[0].set_ylabel('Frequency', fontsize=11)
    axes[0].set_title('Alpha (CPU Clock 1) Distribution', fontweight='bold')
    axes[0].grid(axis='y', alpha=0.3)
    
    # Add statistics text
    axes[0].text(0.98, 0.97, f'Mean: {mean_alpha:.2e} ns\nStd Dev: {std_alpha:.2e} ns\nMin: {min(alphas):.2e} ns\nMax: {max(alphas):.2e} ns',
                transform=axes[0].transAxes, fontsize=9,
                verticalalignment='top', horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    # Subplot 2: Beta distribution
    mean_beta = np.mean(betas)
    std_beta = np.std(betas)
    
    axes[1].hist(betas, bins=50, color='lightcoral', edgecolor='black', alpha=0.7)
    axes[1].set_xlabel('Beta Value (nanoseconds)', fontsize=11)
    axes[1].set_ylabel('Frequency', fontsize=11)
    axes[1].set_title('Beta (CPU Clock 2) Distribution', fontweight='bold')
    axes[1].grid(axis='y', alpha=0.3)
    
    # Add statistics text
    axes[1].text(0.98, 0.97, f'Mean: {mean_beta:.2e} ns\nStd Dev: {std_beta:.2e} ns\nMin: {min(betas):.2e} ns\nMax: {max(betas):.2e} ns',
                transform=axes[1].transAxes, fontsize=9,
                verticalalignment='top', horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.show()
    
    print(f"\nDiagram displayed successfully!")
    print(f"Alpha Statistics:")
    print(f"  Mean: {mean_alpha:.2e} ns")
    print(f"  Std Dev: {std_alpha:.2e} ns")
    print(f"\nBeta Statistics:")
    print(f"  Mean: {mean_beta:.2e} ns")
    print(f"  Std Dev: {std_beta:.2e} ns")


# Generate a 64-bit True Random Number
if __name__ == "__main__":
    # Option 1: Generate single 64-bit random number
    m = 64
    true_random_number = rando_trng(m)
    print(f"Generated {m}-bit random number: {true_random_number}")
    print(f"Binary representation: {bin(true_random_number)}")
    
    print("\n" + "="*60)
    print("Generating diagram for alpha and beta of 1000 random numbers...")
    print("="*60 + "\n")
    
    # Display diagram for batch of 1000 numbers (alpha and beta only)
    display_alpha_beta_diagram(1000)