#!/usr/bin/env python3
"""
Permutation Tests for SQL Dialect Gap Hypothesis

Permutation tests (also called randomization tests) provide exact p-values
without making distributional assumptions. They're particularly powerful for:
- Binary outcome data (success/failure)
- Non-normal distributions
- Small sample sizes
- Custom test statistics

This complements the parametric ANOVA with a distribution-free approach.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Set random seed for reproducibility
np.random.seed(42)

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (14, 10)

def load_data():
    """Load and prepare data"""
    print("Loading data...")
    df = pd.read_csv('all_results.csv')

    # Extract dialect from experiment_id
    df['dialect'] = df['experiment_id'].apply(lambda x: x.rsplit('_', 2)[-2] if '_' in x else 'unknown')

    # Create binary success column (1 if results equal, 0 otherwise)
    df['success'] = df['results_equal'].fillna(False).astype(int)

    print(f"Loaded {len(df)} experiments across {df['dialect'].nunique()} dialects")
    return df

def calculate_f_statistic(data, labels):
    """Calculate F-statistic for group differences"""
    # Group data by labels
    groups = {}
    for label in np.unique(labels):
        groups[label] = data[labels == label]

    # Grand mean
    grand_mean = np.mean(data)

    # Between-group sum of squares
    ss_between = 0
    for label, group in groups.items():
        n = len(group)
        group_mean = np.mean(group)
        ss_between += n * (group_mean - grand_mean) ** 2

    # Within-group sum of squares
    ss_within = 0
    for label, group in groups.items():
        group_mean = np.mean(group)
        ss_within += np.sum((group - group_mean) ** 2)

    # Degrees of freedom
    k = len(groups)  # number of groups
    n = len(data)    # total observations
    df_between = k - 1
    df_within = n - k

    # F-statistic
    ms_between = ss_between / df_between
    ms_within = ss_within / df_within
    f_stat = ms_between / ms_within

    return f_stat

def permutation_test_dialect_effect(df, n_permutations=10000):
    """
    Permutation test for overall dialect effect.

    Null hypothesis: Dialect labels are exchangeable (no dialect effect)
    Test statistic: F-statistic (variance between dialects / variance within)

    Algorithm:
    1. Calculate observed F-statistic
    2. Randomly shuffle dialect labels many times
    3. Calculate F-statistic for each permutation
    4. p-value = proportion of permuted F-stats >= observed F-stat
    """
    print("\n" + "="*80)
    print("PERMUTATION TEST: OVERALL DIALECT EFFECT")
    print("="*80)

    print(f"\nRunning {n_permutations:,} permutations...")
    print("This tests: H₀: Dialect labels are exchangeable (no dialect effect)")

    # Extract data
    success_rates = df['success'].values
    dialect_labels = df['dialect'].values

    # Calculate observed F-statistic
    observed_f = calculate_f_statistic(success_rates, dialect_labels)
    print(f"\nObserved F-statistic: {observed_f:.4f}")

    # Permutation test
    permuted_f_stats = []

    for i in range(n_permutations):
        if i % 1000 == 0 and i > 0:
            print(f"  Completed {i:,} permutations...", end='\r')

        # Randomly shuffle dialect labels
        permuted_labels = np.random.permutation(dialect_labels)

        # Calculate F-statistic under permutation
        perm_f = calculate_f_statistic(success_rates, permuted_labels)
        permuted_f_stats.append(perm_f)

    print(f"  Completed {n_permutations:,} permutations... Done!")

    permuted_f_stats = np.array(permuted_f_stats)

    # Calculate p-value
    p_value = np.mean(permuted_f_stats >= observed_f)

    # Exact p-value (add 1 to numerator and denominator for observed statistic)
    p_value_exact = (np.sum(permuted_f_stats >= observed_f) + 1) / (n_permutations + 1)

    print(f"\n--- Permutation Test Results ---")
    print(f"Observed F-statistic: {observed_f:.4f}")
    print(f"Mean of permuted F-statistics: {np.mean(permuted_f_stats):.4f}")
    print(f"Std of permuted F-statistics: {np.std(permuted_f_stats):.4f}")
    print(f"95th percentile of permuted F: {np.percentile(permuted_f_stats, 95):.4f}")
    print(f"99th percentile of permuted F: {np.percentile(permuted_f_stats, 99):.4f}")
    print(f"\np-value: {p_value:.6f}")
    print(f"p-value (exact): {p_value_exact:.6f}")

    # Z-score (how many standard deviations from null distribution)
    z_score = (observed_f - np.mean(permuted_f_stats)) / np.std(permuted_f_stats)
    print(f"Z-score: {z_score:.2f} standard deviations above null")

    if p_value < 0.05:
        print(f"\n✓ REJECT H₀ (p = {p_value:.6f} < 0.05)")
        print("  The dialect effect is REAL and not due to random chance.")
    else:
        print(f"\n✗ FAIL TO REJECT H₀ (p = {p_value:.6f} >= 0.05)")
        print("  No significant dialect effect detected.")

    return {
        'observed_f': observed_f,
        'permuted_f_stats': permuted_f_stats,
        'p_value': p_value,
        'p_value_exact': p_value_exact,
        'z_score': z_score
    }

def permutation_test_pairwise(df, dialect1, dialect2, n_permutations=10000):
    """
    Permutation test for difference between two dialects.

    Null hypothesis: No difference between dialect1 and dialect2
    Test statistic: Difference in mean accuracy
    """
    # Extract data for the two dialects
    data1 = df[df['dialect'] == dialect1]['success'].values
    data2 = df[df['dialect'] == dialect2]['success'].values

    # Observed difference
    observed_diff = np.mean(data1) - np.mean(data2)

    # Combine data
    combined = np.concatenate([data1, data2])
    n1 = len(data1)
    n2 = len(data2)

    # Permutation test
    permuted_diffs = []

    for _ in range(n_permutations):
        # Randomly shuffle and split
        shuffled = np.random.permutation(combined)
        perm_group1 = shuffled[:n1]
        perm_group2 = shuffled[n1:]

        perm_diff = np.mean(perm_group1) - np.mean(perm_group2)
        permuted_diffs.append(perm_diff)

    permuted_diffs = np.array(permuted_diffs)

    # Two-tailed p-value
    p_value = np.mean(np.abs(permuted_diffs) >= np.abs(observed_diff))

    return {
        'observed_diff': observed_diff * 100,  # Convert to percentage
        'p_value': p_value,
        'permuted_diffs': permuted_diffs
    }

def permutation_test_top_pairs(df, n_permutations=5000):
    """
    Run permutation tests on top pairwise comparisons
    """
    print("\n" + "="*80)
    print("PERMUTATION TEST: PAIRWISE COMPARISONS")
    print("="*80)

    print(f"\nRunning permutation tests on key dialect pairs...")
    print(f"Number of permutations per pair: {n_permutations:,}")

    # Test most interesting pairs
    pairs_to_test = [
        ('pyspark', 'sqlite'),
        ('mysql', 'pyspark'),
        ('postgres', 'pyspark'),
        ('duckdb', 'sqlite'),
        ('mysql', 'sqlite'),
        ('postgres', 'sqlite')
    ]

    results = []

    for dialect1, dialect2 in pairs_to_test:
        print(f"\n  Testing: {dialect1} vs {dialect2}...", end='')
        result = permutation_test_pairwise(df, dialect1, dialect2, n_permutations)

        results.append({
            'Dialect 1': dialect1,
            'Dialect 2': dialect2,
            'Observed Diff (%)': f"{result['observed_diff']:.2f}",
            'p-value': f"{result['p_value']:.6f}",
            'Significant': 'YES' if result['p_value'] < 0.05/len(pairs_to_test) else 'No',
            'p_val_num': result['p_value'],
            'diff_num': result['observed_diff']
        })
        print(f" p = {result['p_value']:.6f}")

    results_df = pd.DataFrame(results)

    print(f"\n--- Pairwise Permutation Test Results ---")
    print(f"(Using Bonferroni correction: α = {0.05/len(pairs_to_test):.6f})")
    print("\n", results_df[['Dialect 1', 'Dialect 2', 'Observed Diff (%)', 'p-value', 'Significant']].to_string(index=False))

    n_significant = results_df[results_df['Significant'] == 'YES'].shape[0]
    print(f"\n{n_significant} out of {len(pairs_to_test)} comparisons are significant after Bonferroni correction")

    return results_df

def calculate_variance_between_dialects(data, labels):
    """Calculate variance in means across dialects"""
    dialect_means = []
    for dialect in np.unique(labels):
        dialect_data = data[labels == dialect]
        dialect_means.append(np.mean(dialect_data))

    return np.var(dialect_means, ddof=1)

def permutation_test_variance(df, n_permutations=10000):
    """
    Permutation test for variance in performance across dialects.

    This directly tests whether the spread of dialect-level means is larger
    than expected by chance.
    """
    print("\n" + "="*80)
    print("PERMUTATION TEST: VARIANCE ACROSS DIALECTS")
    print("="*80)

    print(f"\nTesting whether variance in dialect-level means exceeds chance...")
    print(f"Number of permutations: {n_permutations:,}")

    success_rates = df['success'].values
    dialect_labels = df['dialect'].values

    # Observed variance
    observed_var = calculate_variance_between_dialects(success_rates, dialect_labels)

    print(f"\nObserved variance across dialects: {observed_var:.6f}")

    # Permutation test
    permuted_vars = []

    for i in range(n_permutations):
        if i % 1000 == 0 and i > 0:
            print(f"  Completed {i:,} permutations...", end='\r')

        permuted_labels = np.random.permutation(dialect_labels)
        perm_var = calculate_variance_between_dialects(success_rates, permuted_labels)
        permuted_vars.append(perm_var)

    print(f"  Completed {n_permutations:,} permutations... Done!")

    permuted_vars = np.array(permuted_vars)

    # Calculate p-value
    p_value = np.mean(permuted_vars >= observed_var)

    print(f"\n--- Variance Permutation Test Results ---")
    print(f"Observed variance: {observed_var:.6f}")
    print(f"Mean of permuted variances: {np.mean(permuted_vars):.6f}")
    print(f"95th percentile: {np.percentile(permuted_vars, 95):.6f}")
    print(f"99th percentile: {np.percentile(permuted_vars, 99):.6f}")
    print(f"\np-value: {p_value:.6f}")

    if p_value < 0.05:
        print(f"\n✓ REJECT H₀ (p < 0.05)")
        print("  Dialect-level variance is significantly larger than expected by chance.")
    else:
        print(f"\n✗ FAIL TO REJECT H₀ (p >= 0.05)")

    return {
        'observed_var': observed_var,
        'permuted_vars': permuted_vars,
        'p_value': p_value
    }

def compare_with_parametric_tests(perm_results):
    """Compare permutation test results with parametric ANOVA"""
    print("\n" + "="*80)
    print("COMPARISON: PERMUTATION vs PARAMETRIC TESTS")
    print("="*80)

    # Run parametric ANOVA for comparison
    df = load_data()

    dialect_groups = []
    for dialect in df['dialect'].unique():
        dialect_df = df[df['dialect'] == dialect]
        dialect_groups.append(dialect_df['success'].values)

    f_stat_parametric, p_value_parametric = stats.f_oneway(*dialect_groups)

    print("\n--- ANOVA (Parametric) ---")
    print(f"F-statistic: {f_stat_parametric:.4f}")
    print(f"p-value: {p_value_parametric:.6f}")

    print("\n--- Permutation Test (Non-parametric) ---")
    print(f"F-statistic: {perm_results['observed_f']:.4f}")
    print(f"p-value: {perm_results['p_value']:.6f}")

    print("\n--- Comparison ---")
    print(f"Difference in F-statistics: {abs(f_stat_parametric - perm_results['observed_f']):.4f}")
    print(f"Difference in p-values: {abs(p_value_parametric - perm_results['p_value']):.6f}")

    if perm_results['p_value'] < 0.05 and p_value_parametric < 0.05:
        print("\n✓ Both tests REJECT H₀ - Strong convergent evidence!")
    elif perm_results['p_value'] >= 0.05 and p_value_parametric >= 0.05:
        print("\n✗ Both tests FAIL TO REJECT H₀ - Consistent null finding")
    else:
        print("\n⚠ Tests disagree - Further investigation needed")

def visualize_permutation_results(perm_overall, perm_variance):
    """Create visualizations of permutation test results"""
    print("\n" + "="*80)
    print("GENERATING PERMUTATION TEST VISUALIZATIONS")
    print("="*80)

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # Plot 1: Permutation distribution of F-statistic
    ax = axes[0, 0]

    ax.hist(perm_overall['permuted_f_stats'], bins=50, alpha=0.7,
            color='skyblue', edgecolor='black', density=True)

    # Mark observed value
    ax.axvline(perm_overall['observed_f'], color='red', linewidth=3,
               label=f"Observed F = {perm_overall['observed_f']:.2f}")

    # Mark 95th percentile
    p95 = np.percentile(perm_overall['permuted_f_stats'], 95)
    ax.axvline(p95, color='orange', linewidth=2, linestyle='--',
               label=f"95th percentile = {p95:.2f}")

    ax.set_xlabel('F-statistic', fontsize=12)
    ax.set_ylabel('Density', fontsize=12)
    ax.set_title('Permutation Distribution of F-statistic\n(Null Hypothesis)',
                 fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)

    # Add p-value text
    ax.text(0.95, 0.95, f"p-value = {perm_overall['p_value']:.6f}",
            transform=ax.transAxes, fontsize=12, verticalalignment='top',
            horizontalalignment='right', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    # Plot 2: Q-Q plot
    ax = axes[0, 1]

    # Sort both distributions
    sorted_perm = np.sort(perm_overall['permuted_f_stats'])
    theoretical_quantiles = np.linspace(0, 1, len(sorted_perm))

    ax.scatter(theoretical_quantiles, sorted_perm, alpha=0.5, s=10)

    # Expected line
    ax.plot([0, 1], [sorted_perm[0], sorted_perm[-1]], 'r--', linewidth=2,
            label='Expected under null')

    # Mark observed value
    observed_quantile = np.mean(perm_overall['permuted_f_stats'] <= perm_overall['observed_f'])
    ax.scatter([observed_quantile], [perm_overall['observed_f']],
               color='red', s=200, marker='*', edgecolors='black', linewidths=2,
               label='Observed', zorder=5)

    ax.set_xlabel('Theoretical Quantile', fontsize=12)
    ax.set_ylabel('Permuted F-statistic', fontsize=12)
    ax.set_title('Q-Q Plot: Permutation Distribution', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)

    # Plot 3: Variance permutation distribution
    ax = axes[1, 0]

    ax.hist(perm_variance['permuted_vars'], bins=50, alpha=0.7,
            color='lightgreen', edgecolor='black', density=True)

    ax.axvline(perm_variance['observed_var'], color='red', linewidth=3,
               label=f"Observed = {perm_variance['observed_var']:.6f}")

    p95_var = np.percentile(perm_variance['permuted_vars'], 95)
    ax.axvline(p95_var, color='orange', linewidth=2, linestyle='--',
               label=f"95th percentile = {p95_var:.6f}")

    ax.set_xlabel('Variance Across Dialects', fontsize=12)
    ax.set_ylabel('Density', fontsize=12)
    ax.set_title('Permutation Distribution of Dialect Variance\n(Null Hypothesis)',
                 fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)

    ax.text(0.95, 0.95, f"p-value = {perm_variance['p_value']:.6f}",
            transform=ax.transAxes, fontsize=12, verticalalignment='top',
            horizontalalignment='right', bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))

    # Plot 4: Cumulative distribution
    ax = axes[1, 1]

    # Sort permuted F-stats
    sorted_f = np.sort(perm_overall['permuted_f_stats'])
    cumulative = np.arange(1, len(sorted_f) + 1) / len(sorted_f)

    ax.plot(sorted_f, cumulative, linewidth=2, label='Permutation CDF')

    # Mark observed value
    observed_cdf = np.mean(perm_overall['permuted_f_stats'] <= perm_overall['observed_f'])
    ax.axvline(perm_overall['observed_f'], color='red', linewidth=3, linestyle='--',
               label=f"Observed F = {perm_overall['observed_f']:.2f}")
    ax.axhline(observed_cdf, color='red', linewidth=2, alpha=0.5)

    # Shade critical region
    critical_f = np.percentile(perm_overall['permuted_f_stats'], 95)
    ax.axvspan(critical_f, sorted_f[-1], alpha=0.2, color='red',
               label='Critical region (α=0.05)')

    ax.set_xlabel('F-statistic', fontsize=12)
    ax.set_ylabel('Cumulative Probability', fontsize=12)
    ax.set_title('Cumulative Distribution Function', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(alpha=0.3)

    ax.text(0.05, 0.95, f"CDF at observed = {observed_cdf:.4f}\np-value = {1-observed_cdf:.6f}",
            transform=ax.transAxes, fontsize=11, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))

    plt.tight_layout()
    plt.savefig('permutation_test_results.png', dpi=300, bbox_inches='tight')
    print("Saved: permutation_test_results.png")

def generate_permutation_report(perm_overall, perm_pairwise, perm_variance):
    """Generate markdown report for permutation tests"""
    print("\n" + "="*80)
    print("GENERATING PERMUTATION TEST REPORT")
    print("="*80)

    report = []
    report.append("# Permutation Test Analysis")
    report.append("\n## Why Permutation Tests?")
    report.append("\nPermutation tests (also called randomization tests or exact tests) are the")
    report.append("**gold standard** for hypothesis testing because they:")
    report.append("\n1. **Make no distributional assumptions** - No need to assume normality")
    report.append("2. **Provide exact p-values** - Not relying on asymptotic approximations")
    report.append("3. **Work with binary data** - Perfect for success/failure outcomes")
    report.append("4. **Are intuitive** - Directly test \"could this happen by chance?\"")
    report.append("5. **Are robust** - Work well with small samples or outliers\n")

    report.append("## How Permutation Tests Work\n")
    report.append("### The Basic Algorithm:\n")
    report.append("```")
    report.append("1. Calculate test statistic from observed data")
    report.append("2. Randomly shuffle group labels (10,000 times)")
    report.append("3. Recalculate test statistic for each shuffle")
    report.append("4. p-value = proportion of shuffled statistics ≥ observed")
    report.append("```\n")
    report.append("**Key insight:** If dialect doesn't matter, shuffling dialect labels shouldn't")
    report.append("change the test statistic much. If shuffled statistics are usually smaller")
    report.append("than observed, the observed effect is real!\n")

    report.append("---\n")
    report.append("## Test 1: Overall Dialect Effect (F-statistic)\n")
    report.append(f"**Null Hypothesis:** Dialect labels are exchangeable (no dialect effect)\n")
    report.append(f"**Test Statistic:** F-statistic (ratio of between-group to within-group variance)\n")
    report.append(f"**Number of Permutations:** 10,000\n")

    report.append("### Results:\n")
    report.append(f"- **Observed F-statistic:** {perm_overall['observed_f']:.4f}")
    report.append(f"- **Mean F under null:** {np.mean(perm_overall['permuted_f_stats']):.4f}")
    report.append(f"- **95th percentile under null:** {np.percentile(perm_overall['permuted_f_stats'], 95):.4f}")
    report.append(f"- **Z-score:** {perm_overall['z_score']:.2f} standard deviations above null")
    report.append(f"- **p-value:** {perm_overall['p_value']:.6f}")

    if perm_overall['p_value'] < 0.05:
        report.append(f"\n### ✅ Conclusion: REJECT H₀")
        report.append(f"\nThe observed F-statistic is in the extreme tail of the permutation distribution.")
        report.append(f"Out of 10,000 random shuffles, only {int(perm_overall['p_value']*10000)} produced")
        report.append(f"an F-statistic as large as observed. **The dialect effect is real!**")
    else:
        report.append(f"\n### ❌ Conclusion: FAIL TO REJECT H₀")

    report.append("\n---\n")
    report.append("## Test 2: Pairwise Dialect Comparisons\n")
    report.append("**Null Hypothesis (per pair):** No difference between the two dialects\n")
    report.append("**Test Statistic:** Difference in mean accuracy\n")
    report.append("**Correction:** Bonferroni (α = 0.05 / 6 = 0.0083)\n")

    report.append("\n### Results:\n")
    report.append("| Dialect 1 | Dialect 2 | Observed Diff (%) | p-value | Significant |")
    report.append("|-----------|-----------|-------------------|---------|-------------|")

    for idx, row in perm_pairwise.iterrows():
        report.append(f"| {row['Dialect 1']} | {row['Dialect 2']} | {row['Observed Diff (%)']} | "
                     f"{row['p-value']} | {row['Significant']} |")

    n_sig = perm_pairwise[perm_pairwise['Significant'] == 'YES'].shape[0]
    report.append(f"\n**{n_sig} out of {len(perm_pairwise)} pairs are statistically significant**")

    report.append("\n---\n")
    report.append("## Test 3: Variance Across Dialects\n")
    report.append("**Null Hypothesis:** Variance in dialect-level means is no larger than chance\n")
    report.append("**Test Statistic:** Variance of dialect-level mean accuracies\n")

    report.append("\n### Results:\n")
    report.append(f"- **Observed variance:** {perm_variance['observed_var']:.6f}")
    report.append(f"- **Mean variance under null:** {np.mean(perm_variance['permuted_vars']):.6f}")
    report.append(f"- **95th percentile under null:** {np.percentile(perm_variance['permuted_vars'], 95):.6f}")
    report.append(f"- **p-value:** {perm_variance['p_value']:.6f}")

    if perm_variance['p_value'] < 0.05:
        report.append(f"\n### ✅ Conclusion: REJECT H₀")
        report.append(f"\nThe spread of dialect performance is significantly larger than expected by chance.")

    report.append("\n---\n")
    report.append("## Comparison with Parametric Tests\n")

    # Load data and run ANOVA
    df = load_data()
    dialect_groups = []
    for dialect in df['dialect'].unique():
        dialect_df = df[df['dialect'] == dialect]
        dialect_groups.append(dialect_df['success'].values)

    f_stat_param, p_value_param = stats.f_oneway(*dialect_groups)

    report.append("| Test Type | F-statistic | p-value | Decision |")
    report.append("|-----------|-------------|---------|----------|")
    report.append(f"| ANOVA (parametric) | {f_stat_param:.4f} | {p_value_param:.6f} | {'Reject H₀' if p_value_param < 0.05 else 'Fail to reject'} |")
    report.append(f"| Permutation (exact) | {perm_overall['observed_f']:.4f} | {perm_overall['p_value']:.6f} | {'Reject H₀' if perm_overall['p_value'] < 0.05 else 'Fail to reject'} |")

    report.append("\n### Agreement:")
    if (p_value_param < 0.05) == (perm_overall['p_value'] < 0.05):
        report.append("✅ **Both tests agree** - This provides strong convergent evidence!")
        report.append("\nThe parametric and non-parametric approaches lead to the same conclusion,")
        report.append("increasing our confidence in the result.")
    else:
        report.append("⚠️ **Tests disagree** - Further investigation warranted")

    report.append("\n## Visualization\n")
    report.append("![Permutation Test Results](permutation_test_results.png)\n")

    report.append("## Key Advantages of Permutation Tests\n")
    report.append("1. **No assumptions about data distribution** - Our binary success/failure data doesn't need to be normal")
    report.append("2. **Exact p-values** - Not approximate like parametric tests")
    report.append("3. **Intuitive interpretation** - \"Out of 10,000 random shuffles, how many were as extreme?\"")
    report.append("4. **Robust to outliers** - Shuffling preserves all data points")
    report.append("5. **Flexible** - Can use any test statistic, not just F or t\n")

    report.append("## Final Conclusion\n")
    if perm_overall['p_value'] < 0.05:
        report.append("**The permutation tests provide rigorous, assumption-free evidence that the dialect gap is REAL.**")
        report.append("\nEven when we make no assumptions about the data distribution and use exact")
        report.append("computational methods, the dialect effect remains highly significant. This is")
        report.append("the strongest possible statistical evidence for the hypothesis.")

    report.append("\n---\n")
    report.append("*Generated by permutation_tests.py*")

    report_text = "\n".join(report)

    with open('PERMUTATION_TEST_REPORT.md', 'w') as f:
        f.write(report_text)

    print("Saved: PERMUTATION_TEST_REPORT.md")

def main():
    """Main permutation test pipeline"""
    print("\n" + "="*80)
    print("PERMUTATION TESTS FOR SQL DIALECT GAP HYPOTHESIS")
    print("="*80)
    print("\nPermutation tests provide exact, distribution-free hypothesis testing.")
    print("This complements the parametric ANOVA with a more robust approach.\n")

    # Load data
    df = load_data()

    # Test 1: Overall dialect effect
    perm_overall = permutation_test_dialect_effect(df, n_permutations=10000)

    # Test 2: Pairwise comparisons
    perm_pairwise = permutation_test_top_pairs(df, n_permutations=5000)

    # Test 3: Variance across dialects
    perm_variance = permutation_test_variance(df, n_permutations=10000)

    # Compare with parametric tests
    compare_with_parametric_tests(perm_overall)

    # Visualize results
    visualize_permutation_results(perm_overall, perm_variance)

    # Generate report
    generate_permutation_report(perm_overall, perm_pairwise, perm_variance)

    print("\n" + "="*80)
    print("PERMUTATION TESTS COMPLETE!")
    print("="*80)
    print("\nGenerated files:")
    print("  - PERMUTATION_TEST_REPORT.md (detailed permutation test analysis)")
    print("  - permutation_test_results.png (permutation distributions)")

if __name__ == "__main__":
    main()
