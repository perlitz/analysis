#!/usr/bin/env python3
"""
Statistical Analysis of the SQL Dialect Gap Hypothesis

Hypothesis: There is a significant gap in model performance across different SQL dialects,
suggesting that models are not equally proficient in all SQL variants.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import f_oneway, chi2_contingency, kruskal
import warnings
warnings.filterwarnings('ignore')

# Set style for better-looking plots
sns.set_style("whitegrid")
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (14, 8)

# Model parameter counts (in billions)
MODEL_PARAMS = {
    'deepseek-v3': 671,
    'llama-4-maverick': 128,
    'gpt-oss-120b': 120,
    'llama-3-3-70b-instruct': 70,
    'deepseek-coder-33b-instruct': 33,
    'llama-3-1-8b-instruct': 8
}

def extract_dialect(experiment_id):
    """Extract SQL dialect from experiment_id"""
    # Format: modelname_dialect_number
    parts = experiment_id.rsplit('_', 2)
    if len(parts) >= 2:
        return parts[-2]
    return 'unknown'

def load_and_prepare_data(filepath):
    """Load data and add derived columns"""
    print("Loading and preparing data...")
    df = pd.read_csv(filepath)

    # Extract dialect from experiment_id
    df['dialect'] = df['experiment_id'].apply(extract_dialect)

    # Add model parameters
    df['model_params_b'] = df['model_name'].map(MODEL_PARAMS)

    # Create binary success column (1 if results equal, 0 otherwise)
    # NaN means query didn't execute or comparison failed, treat as 0
    df['success'] = df['results_equal'].fillna(False).astype(int)

    # Create execution success column
    df['executed'] = df['both_executed'].fillna(False).astype(int)

    print(f"Loaded {len(df)} rows")
    print(f"Dialects found: {sorted(df['dialect'].unique())}")
    print(f"Models found: {sorted(df['model_name'].unique())}")

    return df

def descriptive_statistics_by_dialect(df):
    """Calculate descriptive statistics by dialect"""
    print("\n" + "="*80)
    print("DESCRIPTIVE STATISTICS BY SQL DIALECT")
    print("="*80)

    dialect_stats = []

    for dialect in sorted(df['dialect'].unique()):
        dialect_df = df[df['dialect'] == dialect]

        total = len(dialect_df)
        success_count = dialect_df['success'].sum()
        exec_count = dialect_df['executed'].sum()

        accuracy = success_count / total * 100
        exec_rate = exec_count / total * 100

        # Calculate among executed
        executed_df = dialect_df[dialect_df['executed'] == 1]
        exec_accuracy = (executed_df['success'].sum() / len(executed_df) * 100) if len(executed_df) > 0 else 0

        # Number of models and experiments
        n_models = dialect_df['model_name'].nunique()
        n_experiments = len(dialect_df)

        dialect_stats.append({
            'Dialect': dialect,
            'N': total,
            'Accuracy (%)': f"{accuracy:.2f}",
            'Exec Rate (%)': f"{exec_rate:.2f}",
            'Exec Accuracy (%)': f"{exec_accuracy:.2f}",
            'Success Count': success_count,
            'Models': n_models,
            'accuracy_num': accuracy,
            'exec_accuracy_num': exec_accuracy
        })

    stats_df = pd.DataFrame(dialect_stats).sort_values('accuracy_num', ascending=False)
    print("\n", stats_df[['Dialect', 'N', 'Accuracy (%)', 'Exec Rate (%)', 'Exec Accuracy (%)', 'Models']].to_string(index=False))

    return stats_df

def calculate_dialect_variance(df):
    """Calculate variance metrics to quantify the dialect gap"""
    print("\n" + "="*80)
    print("DIALECT GAP VARIANCE METRICS")
    print("="*80)

    # For each model, calculate variance in performance across dialects
    model_variance = []

    for model in df['model_name'].unique():
        model_df = df[df['model_name'] == model]

        dialect_accuracies = []
        for dialect in model_df['dialect'].unique():
            dialect_model_df = model_df[model_df['dialect'] == dialect]
            accuracy = dialect_model_df['success'].mean() * 100
            dialect_accuracies.append(accuracy)

        if len(dialect_accuracies) > 1:
            variance = np.var(dialect_accuracies, ddof=1)
            std_dev = np.std(dialect_accuracies, ddof=1)
            range_val = max(dialect_accuracies) - min(dialect_accuracies)
            cv = (std_dev / np.mean(dialect_accuracies) * 100) if np.mean(dialect_accuracies) > 0 else 0

            model_variance.append({
                'Model': model,
                'Params (B)': MODEL_PARAMS.get(model, 'Unknown'),
                'Variance': variance,
                'Std Dev': std_dev,
                'Range (%)': range_val,
                'CV (%)': cv,
                'Mean Accuracy': np.mean(dialect_accuracies)
            })

    variance_df = pd.DataFrame(model_variance).sort_values('Variance', ascending=False)
    print("\nVariance in Accuracy Across Dialects (Per Model):")
    print(variance_df.to_string(index=False))

    # Overall variance
    overall_accuracies = []
    for dialect in df['dialect'].unique():
        dialect_df = df[df['dialect'] == dialect]
        accuracy = dialect_df['success'].mean() * 100
        overall_accuracies.append(accuracy)

    print(f"\n{'='*80}")
    print("Overall Dialect Performance Variance:")
    print(f"  Mean Accuracy: {np.mean(overall_accuracies):.2f}%")
    print(f"  Std Dev: {np.std(overall_accuracies, ddof=1):.2f}%")
    print(f"  Range: {max(overall_accuracies) - min(overall_accuracies):.2f}%")
    print(f"  CV: {np.std(overall_accuracies, ddof=1) / np.mean(overall_accuracies) * 100:.2f}%")

    return variance_df

def test_dialect_effect_anova(df):
    """Test if dialect has significant effect on accuracy using ANOVA"""
    print("\n" + "="*80)
    print("STATISTICAL SIGNIFICANCE TESTING: ANOVA")
    print("="*80)

    print("\nNull Hypothesis (H0): There is NO difference in model performance across SQL dialects")
    print("Alternative Hypothesis (H1): There IS a significant difference in performance across dialects")

    # Prepare data for ANOVA - group success rates by dialect
    dialect_groups = []
    dialect_names = []

    for dialect in df['dialect'].unique():
        dialect_df = df[df['dialect'] == dialect]
        # Use binary success values for each attempt
        dialect_groups.append(dialect_df['success'].values)
        dialect_names.append(dialect)

    # Perform one-way ANOVA
    f_stat, p_value = f_oneway(*dialect_groups)

    print(f"\n--- One-Way ANOVA Results ---")
    print(f"F-statistic: {f_stat:.4f}")
    print(f"p-value: {p_value:.6f}")

    alpha = 0.05
    if p_value < alpha:
        print(f"\n✓ REJECT H0 (p < {alpha})")
        print("  There IS a statistically significant difference in performance across SQL dialects.")
        print("  The 'dialect gap' hypothesis is SUPPORTED.")
    else:
        print(f"\n✗ FAIL TO REJECT H0 (p >= {alpha})")
        print("  There is NO statistically significant difference in performance across SQL dialects.")
        print("  The 'dialect gap' hypothesis is NOT SUPPORTED.")

    # Calculate effect size (eta-squared)
    # Total sum of squares
    grand_mean = df['success'].mean()
    ss_total = np.sum((df['success'] - grand_mean) ** 2)

    # Between-group sum of squares
    ss_between = 0
    for dialect in df['dialect'].unique():
        dialect_df = df[df['dialect'] == dialect]
        group_mean = dialect_df['success'].mean()
        n = len(dialect_df)
        ss_between += n * (group_mean - grand_mean) ** 2

    eta_squared = ss_between / ss_total

    print(f"\nEffect Size (η²): {eta_squared:.4f}")
    if eta_squared < 0.01:
        effect_interpretation = "negligible"
    elif eta_squared < 0.06:
        effect_interpretation = "small"
    elif eta_squared < 0.14:
        effect_interpretation = "medium"
    else:
        effect_interpretation = "large"
    print(f"Effect Size Interpretation: {effect_interpretation}")

    return f_stat, p_value, eta_squared

def test_dialect_effect_kruskal(df):
    """Non-parametric test (Kruskal-Wallis) as alternative to ANOVA"""
    print("\n" + "="*80)
    print("STATISTICAL SIGNIFICANCE TESTING: KRUSKAL-WALLIS (Non-parametric)")
    print("="*80)

    dialect_groups = []
    for dialect in df['dialect'].unique():
        dialect_df = df[df['dialect'] == dialect]
        dialect_groups.append(dialect_df['success'].values)

    h_stat, p_value = kruskal(*dialect_groups)

    print(f"\n--- Kruskal-Wallis H-Test Results ---")
    print(f"H-statistic: {h_stat:.4f}")
    print(f"p-value: {p_value:.6f}")

    alpha = 0.05
    if p_value < alpha:
        print(f"\n✓ REJECT H0 (p < {alpha})")
        print("  Non-parametric test confirms: dialect significantly affects performance.")
    else:
        print(f"\n✗ FAIL TO REJECT H0 (p >= {alpha})")

    return h_stat, p_value

def pairwise_dialect_comparisons(df):
    """Perform pairwise comparisons between dialects"""
    print("\n" + "="*80)
    print("POST-HOC ANALYSIS: PAIRWISE DIALECT COMPARISONS")
    print("="*80)

    dialects = sorted(df['dialect'].unique())
    n_comparisons = len(dialects) * (len(dialects) - 1) // 2

    # Bonferroni correction
    alpha = 0.05
    bonferroni_alpha = alpha / n_comparisons

    print(f"\nPerforming {n_comparisons} pairwise t-tests with Bonferroni correction")
    print(f"Adjusted significance level: α = {bonferroni_alpha:.6f}")

    comparisons = []

    for i, dialect1 in enumerate(dialects):
        for dialect2 in dialects[i+1:]:
            group1 = df[df['dialect'] == dialect1]['success'].values
            group2 = df[df['dialect'] == dialect2]['success'].values

            # Two-sample t-test
            t_stat, p_value = stats.ttest_ind(group1, group2)

            # Calculate means
            mean1 = np.mean(group1) * 100
            mean2 = np.mean(group2) * 100
            diff = mean1 - mean2

            # Cohen's d (effect size)
            pooled_std = np.sqrt((np.var(group1, ddof=1) + np.var(group2, ddof=1)) / 2)
            cohens_d = (np.mean(group1) - np.mean(group2)) / pooled_std if pooled_std > 0 else 0

            significant = "YES" if p_value < bonferroni_alpha else "No"

            comparisons.append({
                'Dialect 1': dialect1,
                'Dialect 2': dialect2,
                'Mean 1 (%)': f"{mean1:.2f}",
                'Mean 2 (%)': f"{mean2:.2f}",
                'Diff (%)': f"{diff:.2f}",
                'p-value': f"{p_value:.6f}",
                'Significant': significant,
                'Cohen\'s d': f"{cohens_d:.3f}",
                'p_val_num': p_value,
                'diff_num': abs(diff)
            })

    comp_df = pd.DataFrame(comparisons).sort_values('p_val_num')

    print("\nTop 10 Most Significant Pairwise Comparisons:")
    print(comp_df[['Dialect 1', 'Dialect 2', 'Mean 1 (%)', 'Mean 2 (%)', 'Diff (%)', 'p-value', 'Significant']].head(10).to_string(index=False))

    # Count significant differences
    n_significant = comp_df[comp_df['Significant'] == 'YES'].shape[0]
    print(f"\n{n_significant} out of {n_comparisons} comparisons are statistically significant after Bonferroni correction")

    return comp_df

def control_for_model_size(df):
    """Analyze dialect gap controlling for model size"""
    print("\n" + "="*80)
    print("CONTROLLING FOR MODEL SIZE")
    print("="*80)

    print("\nAnalyzing whether dialect gap persists across different model sizes...")

    # Group models by size category
    df['size_category'] = df['model_params_b'].apply(lambda x:
        'Small (< 50B)' if x < 50 else
        'Medium (50-150B)' if x < 150 else
        'Large (>= 150B)'
    )

    for size_cat in sorted(df['size_category'].unique()):
        print(f"\n--- {size_cat} Models ---")
        size_df = df[df['size_category'] == size_cat]

        models = size_df['model_name'].unique()
        print(f"Models: {', '.join(models)}")

        # Calculate variance across dialects for this size category
        dialect_accuracies = []
        for dialect in size_df['dialect'].unique():
            dialect_size_df = size_df[size_df['dialect'] == dialect]
            accuracy = dialect_size_df['success'].mean() * 100
            dialect_accuracies.append(accuracy)

        if len(dialect_accuracies) > 1:
            print(f"  Range across dialects: {max(dialect_accuracies) - min(dialect_accuracies):.2f}%")
            print(f"  Std Dev: {np.std(dialect_accuracies, ddof=1):.2f}%")

def analyze_model_size_correlation(df):
    """Test if larger models have smaller dialect gaps"""
    print("\n" + "="*80)
    print("MODEL SIZE vs DIALECT GAP CORRELATION")
    print("="*80)

    model_gap_data = []

    for model in df['model_name'].unique():
        model_df = df[df['model_name'] == model]
        params = MODEL_PARAMS.get(model, None)

        if params is None:
            continue

        # Calculate range of accuracy across dialects
        dialect_accuracies = []
        for dialect in model_df['dialect'].unique():
            dialect_model_df = model_df[model_df['dialect'] == dialect]
            accuracy = dialect_model_df['success'].mean() * 100
            dialect_accuracies.append(accuracy)

        if len(dialect_accuracies) > 1:
            gap = max(dialect_accuracies) - min(dialect_accuracies)
            std_dev = np.std(dialect_accuracies, ddof=1)

            model_gap_data.append({
                'model': model,
                'params': params,
                'gap': gap,
                'std_dev': std_dev
            })

    gap_df = pd.DataFrame(model_gap_data)

    # Correlation test
    if len(gap_df) > 2:
        corr_gap, p_gap = stats.pearsonr(gap_df['params'], gap_df['gap'])
        corr_std, p_std = stats.pearsonr(gap_df['params'], gap_df['std_dev'])

        print("\nCorrelation: Model Size (params) vs Dialect Gap (range)")
        print(f"  Pearson r: {corr_gap:.4f}")
        print(f"  p-value: {p_gap:.4f}")
        print(f"  Interpretation: {'Larger models have ' + ('smaller' if corr_gap < 0 else 'larger') + ' dialect gaps' if p_gap < 0.05 else 'No significant correlation'}")

        print("\nCorrelation: Model Size (params) vs Dialect Variability (std dev)")
        print(f"  Pearson r: {corr_std:.4f}")
        print(f"  p-value: {p_std:.4f}")

        return gap_df, corr_gap, p_gap

    return gap_df, None, None

def create_visualizations(df, dialect_stats, comp_df, gap_df):
    """Create comprehensive visualizations"""
    print("\n" + "="*80)
    print("GENERATING VISUALIZATIONS")
    print("="*80)

    # Figure 1: Main Dialect Gap Visualization
    fig = plt.figure(figsize=(18, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

    # Plot 1: Accuracy by Dialect (Overall)
    ax1 = fig.add_subplot(gs[0, :2])
    dialect_order = dialect_stats.sort_values('accuracy_num', ascending=True)
    colors = plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(dialect_order)))
    bars = ax1.barh(dialect_order['Dialect'], dialect_order['accuracy_num'], color=colors)
    ax1.set_xlabel('Accuracy (%)', fontsize=12)
    ax1.set_title('Overall Accuracy by SQL Dialect', fontsize=14, fontweight='bold')
    ax1.set_xlim(0, max(dialect_order['accuracy_num']) * 1.1)

    # Add value labels
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax1.text(width + 0.5, bar.get_y() + bar.get_height()/2,
                f'{width:.1f}%', ha='left', va='center', fontsize=10)

    # Plot 2: Distribution Box Plot
    ax2 = fig.add_subplot(gs[0, 2])
    dialect_accuracy_data = []
    dialect_labels = []
    for dialect in sorted(df['dialect'].unique()):
        dialect_df = df[df['dialect'] == dialect]
        # Calculate accuracy per question
        question_accuracies = []
        for qid in dialect_df['question_id'].unique():
            q_df = dialect_df[dialect_df['question_id'] == qid]
            acc = q_df['success'].mean() * 100
            question_accuracies.append(acc)
        dialect_accuracy_data.append(question_accuracies)
        dialect_labels.append(dialect)

    bp = ax2.boxplot(dialect_accuracy_data, labels=dialect_labels, vert=True, patch_artist=True)
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
    ax2.set_ylabel('Accuracy (%)', fontsize=10)
    ax2.set_title('Accuracy Distribution', fontsize=12, fontweight='bold')
    ax2.tick_params(axis='x', rotation=45, labelsize=8)
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')

    # Plot 3: Heatmap - Model x Dialect Performance
    ax3 = fig.add_subplot(gs[1, :])

    # Create matrix
    models = sorted(df['model_name'].unique(), key=lambda x: MODEL_PARAMS.get(x, 0), reverse=True)
    dialects = sorted(df['dialect'].unique())

    matrix = np.zeros((len(models), len(dialects)))
    for i, model in enumerate(models):
        for j, dialect in enumerate(dialects):
            subset = df[(df['model_name'] == model) & (df['dialect'] == dialect)]
            if len(subset) > 0:
                matrix[i, j] = subset['success'].mean() * 100
            else:
                matrix[i, j] = np.nan

    im = ax3.imshow(matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=60)
    ax3.set_xticks(np.arange(len(dialects)))
    ax3.set_yticks(np.arange(len(models)))
    ax3.set_xticklabels(dialects, rotation=45, ha='right')

    # Add model sizes to labels
    model_labels = [f"{m} ({MODEL_PARAMS.get(m, '?')}B)" for m in models]
    ax3.set_yticklabels(model_labels)

    ax3.set_title('Accuracy Heatmap: Model × Dialect (%)', fontsize=14, fontweight='bold')

    # Add text annotations
    for i in range(len(models)):
        for j in range(len(dialects)):
            if not np.isnan(matrix[i, j]):
                text = ax3.text(j, i, f'{matrix[i, j]:.0f}',
                               ha="center", va="center", color="black", fontsize=8)

    cbar = plt.colorbar(im, ax=ax3)
    cbar.set_label('Accuracy (%)', rotation=270, labelpad=20)

    # Plot 4: Dialect Gap by Model (Range)
    ax4 = fig.add_subplot(gs[2, 0])

    model_gaps = []
    model_names = []
    model_sizes = []

    for model in models:
        model_df = df[df['model_name'] == model]
        dialect_accs = []
        for dialect in model_df['dialect'].unique():
            subset = model_df[model_df['dialect'] == dialect]
            dialect_accs.append(subset['success'].mean() * 100)

        if len(dialect_accs) > 1:
            gap = max(dialect_accs) - min(dialect_accs)
            model_gaps.append(gap)
            model_names.append(model)
            model_sizes.append(MODEL_PARAMS.get(model, 0))

    # Color by size
    colors_size = plt.cm.viridis(np.array(model_sizes) / max(model_sizes))
    bars = ax4.barh(model_names, model_gaps, color=colors_size)
    ax4.set_xlabel('Dialect Gap (Range in %)', fontsize=10)
    ax4.set_title('Dialect Gap by Model', fontsize=12, fontweight='bold')

    # Plot 5: Model Size vs Dialect Gap
    ax5 = fig.add_subplot(gs[2, 1])

    if gap_df is not None and len(gap_df) > 0:
        scatter = ax5.scatter(gap_df['params'], gap_df['gap'],
                            s=100, alpha=0.6, c=gap_df['params'], cmap='viridis')

        # Add trend line
        z = np.polyfit(gap_df['params'], gap_df['gap'], 1)
        p = np.poly1d(z)
        x_trend = np.linspace(gap_df['params'].min(), gap_df['params'].max(), 100)
        ax5.plot(x_trend, p(x_trend), "r--", alpha=0.8, linewidth=2)

        # Annotate points
        for idx, row in gap_df.iterrows():
            ax5.annotate(row['model'].split('-')[0][:8],
                        (row['params'], row['gap']),
                        fontsize=8, ha='right', va='bottom')

        ax5.set_xlabel('Model Size (Billion Parameters)', fontsize=10)
        ax5.set_ylabel('Dialect Gap (Range in %)', fontsize=10)
        ax5.set_title('Model Size vs Dialect Gap', fontsize=12, fontweight='bold')
        ax5.grid(True, alpha=0.3)

    # Plot 6: Execution Accuracy by Dialect
    ax6 = fig.add_subplot(gs[2, 2])

    exec_accs = []
    dialect_names_exec = []
    for dialect in sorted(df['dialect'].unique()):
        dialect_df = df[df['dialect'] == dialect]
        executed_df = dialect_df[dialect_df['executed'] == 1]
        if len(executed_df) > 0:
            exec_acc = executed_df['success'].mean() * 100
            exec_accs.append(exec_acc)
            dialect_names_exec.append(dialect)

    ax6.bar(range(len(dialect_names_exec)), exec_accs, color='steelblue', alpha=0.7)
    ax6.set_xticks(range(len(dialect_names_exec)))
    ax6.set_xticklabels(dialect_names_exec, rotation=45, ha='right', fontsize=8)
    ax6.set_ylabel('Exec Accuracy (%)', fontsize=10)
    ax6.set_title('Among Executed Queries', fontsize=12, fontweight='bold')
    ax6.set_ylim(0, 100)

    plt.savefig('dialect_gap_analysis.png', dpi=300, bbox_inches='tight')
    print("Saved: dialect_gap_analysis.png")

    # Figure 2: Statistical Significance Visualization
    fig2, axes = plt.subplots(2, 2, figsize=(16, 12))

    # Plot 1: Pairwise comparison matrix
    ax = axes[0, 0]

    # Create significance matrix
    dialects_sorted = sorted(df['dialect'].unique())
    n_dialects = len(dialects_sorted)
    sig_matrix = np.zeros((n_dialects, n_dialects))

    for idx, row in comp_df.iterrows():
        d1_idx = dialects_sorted.index(row['Dialect 1'])
        d2_idx = dialects_sorted.index(row['Dialect 2'])

        # Use p-value (darker = more significant)
        p_val = row['p_val_num']
        sig_value = -np.log10(p_val + 1e-10)  # Log scale

        sig_matrix[d1_idx, d2_idx] = sig_value
        sig_matrix[d2_idx, d1_idx] = sig_value

    im = ax.imshow(sig_matrix, cmap='Reds', aspect='auto')
    ax.set_xticks(np.arange(n_dialects))
    ax.set_yticks(np.arange(n_dialects))
    ax.set_xticklabels(dialects_sorted, rotation=45, ha='right')
    ax.set_yticklabels(dialects_sorted)
    ax.set_title('Pairwise Significance Matrix\n(Darker = More Significant)', fontweight='bold')

    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('-log10(p-value)', rotation=270, labelpad=20)

    # Plot 2: Dialect ranking with confidence intervals
    ax = axes[0, 1]

    dialect_means = []
    dialect_sems = []
    dialect_names_ci = []

    for dialect in sorted(df['dialect'].unique()):
        dialect_df = df[df['dialect'] == dialect]
        success_rate = dialect_df['success'].values
        mean = np.mean(success_rate) * 100
        sem = stats.sem(success_rate) * 100

        dialect_means.append(mean)
        dialect_sems.append(sem * 1.96)  # 95% CI
        dialect_names_ci.append(dialect)

    # Sort by mean
    sorted_indices = np.argsort(dialect_means)
    dialect_means = [dialect_means[i] for i in sorted_indices]
    dialect_sems = [dialect_sems[i] for i in sorted_indices]
    dialect_names_ci = [dialect_names_ci[i] for i in sorted_indices]

    y_pos = np.arange(len(dialect_names_ci))
    ax.barh(y_pos, dialect_means, xerr=dialect_sems,
            color='skyblue', alpha=0.7, capsize=5)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(dialect_names_ci)
    ax.set_xlabel('Accuracy (%) with 95% CI', fontsize=10)
    ax.set_title('Dialect Performance with Confidence Intervals', fontweight='bold')
    ax.grid(axis='x', alpha=0.3)

    # Plot 3: Model-specific dialect gaps
    ax = axes[1, 0]

    # For each model, show range across dialects
    model_ranges = []
    model_means = []
    model_labels_range = []

    for model in sorted(df['model_name'].unique(), key=lambda x: MODEL_PARAMS.get(x, 0), reverse=True):
        model_df = df[df['model_name'] == model]
        dialect_accs = []

        for dialect in model_df['dialect'].unique():
            subset = model_df[model_df['dialect'] == dialect]
            dialect_accs.append(subset['success'].mean() * 100)

        if len(dialect_accs) > 1:
            model_means.append(np.mean(dialect_accs))
            model_ranges.append((min(dialect_accs), max(dialect_accs)))
            model_labels_range.append(f"{model}\n({MODEL_PARAMS.get(model, '?')}B)")

    y_pos = np.arange(len(model_labels_range))

    for i, (low, high) in enumerate(model_ranges):
        ax.plot([low, high], [i, i], 'o-', linewidth=3, markersize=8, alpha=0.7)
        ax.plot([model_means[i]], [i], 's', markersize=10, color='red', alpha=0.7)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(model_labels_range, fontsize=9)
    ax.set_xlabel('Accuracy Range Across Dialects (%)', fontsize=10)
    ax.set_title('Model Performance Range Across Dialects\n(Red square = mean, line = range)',
                 fontweight='bold')
    ax.grid(axis='x', alpha=0.3)

    # Plot 4: Variance decomposition
    ax = axes[1, 1]

    # Calculate variance components
    # Total variance
    total_var = df['success'].var()

    # Variance due to dialect
    dialect_means_all = df.groupby('dialect')['success'].mean()
    grand_mean = df['success'].mean()
    dialect_var = np.sum(df.groupby('dialect').size() * (dialect_means_all - grand_mean)**2) / len(df)

    # Variance due to model
    model_means_all = df.groupby('model_name')['success'].mean()
    model_var = np.sum(df.groupby('model_name').size() * (model_means_all - grand_mean)**2) / len(df)

    # Residual variance
    residual_var = total_var - dialect_var - model_var

    components = ['Dialect\nEffect', 'Model\nEffect', 'Residual\n(Question, etc.)']
    variances = [dialect_var, model_var, residual_var]
    percentages = [v / total_var * 100 for v in variances]

    colors_var = ['#ff6b6b', '#4ecdc4', '#95e1d3']
    bars = ax.bar(components, percentages, color=colors_var, alpha=0.7)
    ax.set_ylabel('Percentage of Total Variance (%)', fontsize=10)
    ax.set_title('Variance Decomposition', fontweight='bold')
    ax.set_ylim(0, max(percentages) * 1.2)

    # Add value labels
    for bar, pct in zip(bars, percentages):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{pct:.1f}%',
                ha='center', va='bottom', fontweight='bold', fontsize=12)

    plt.tight_layout()
    plt.savefig('dialect_gap_statistical_analysis.png', dpi=300, bbox_inches='tight')
    print("Saved: dialect_gap_statistical_analysis.png")

def generate_dialect_gap_report(df, dialect_stats, f_stat, p_value, eta_squared,
                                comp_df, gap_df, corr_gap, p_gap):
    """Generate comprehensive dialect gap report"""
    print("\n" + "="*80)
    print("GENERATING DIALECT GAP REPORT")
    print("="*80)

    report = []
    report.append("# SQL Dialect Gap Analysis")
    report.append(f"\n**Analysis Date:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("\n---\n")

    report.append("## Research Question")
    report.append("\n**Hypothesis:** There is a significant gap in the ability of LLMs to generate SQL")
    report.append("across different SQL dialects, suggesting that models are not equally proficient")
    report.append("in all SQL variants.\n")

    report.append("## Executive Summary\n")

    # Conclusion
    alpha = 0.05
    if p_value < alpha:
        report.append(f"### ✅ HYPOTHESIS SUPPORTED")
        report.append(f"\nThe experimental results **strongly support** the dialect gap hypothesis.")
        report.append(f"Statistical analysis reveals **significant differences** in model performance")
        report.append(f"across SQL dialects (p = {p_value:.6f}, p < {alpha}).\n")
    else:
        report.append(f"### ❌ HYPOTHESIS NOT SUPPORTED")
        report.append(f"\nThe experimental results **do not support** the dialect gap hypothesis.")
        report.append(f"Statistical analysis shows **no significant differences** in model performance")
        report.append(f"across SQL dialects (p = {p_value:.6f}, p >= {alpha}).\n")

    # Key metrics
    report.append("### Key Metrics\n")

    # Dialect performance range
    min_acc = dialect_stats['accuracy_num'].min()
    max_acc = dialect_stats['accuracy_num'].max()
    range_acc = max_acc - min_acc

    report.append(f"- **Dialect Performance Range:** {range_acc:.2f}% ({min_acc:.2f}% to {max_acc:.2f}%)")
    report.append(f"- **ANOVA F-statistic:** {f_stat:.4f}")
    report.append(f"- **ANOVA p-value:** {p_value:.6f}")

    if eta_squared < 0.01:
        effect_interpretation = "negligible"
    elif eta_squared < 0.06:
        effect_interpretation = "small"
    elif eta_squared < 0.14:
        effect_interpretation = "medium"
    else:
        effect_interpretation = "large"

    report.append(f"- **Effect Size (η²):** {eta_squared:.4f} ({effect_interpretation})")

    # Variance decomposition
    total_var = df['success'].var()
    dialect_means_all = df.groupby('dialect')['success'].mean()
    grand_mean = df['success'].mean()
    dialect_var = np.sum(df.groupby('dialect').size() * (dialect_means_all - grand_mean)**2) / len(df)
    dialect_pct = dialect_var / total_var * 100

    report.append(f"\n- **Variance Explained by Dialect:** {dialect_pct:.2f}%")

    # Number of significant pairwise comparisons
    n_significant = comp_df[comp_df['Significant'] == 'YES'].shape[0]
    n_total = len(comp_df)

    report.append(f"- **Significant Pairwise Differences:** {n_significant}/{n_total} comparisons")
    report.append(f"- **Models Analyzed:** {df['model_name'].nunique()}")
    report.append(f"- **SQL Dialects Tested:** {df['dialect'].nunique()}")
    report.append(f"- **Total Experiments:** {len(df):,}\n")

    report.append("## Dialect Performance Ranking\n")
    report.append("| Rank | Dialect | Accuracy | Exec Rate | Exec Accuracy | N |")
    report.append("|------|---------|----------|-----------|---------------|---|")

    for idx, row in dialect_stats.sort_values('accuracy_num', ascending=False).iterrows():
        rank = idx + 1
        report.append(f"| {rank} | {row['Dialect']} | {row['Accuracy (%)']} | "
                     f"{row['Exec Rate (%)']} | {row['Exec Accuracy (%)']} | {row['N']} |")

    report.append("\n### Interpretation\n")

    best_dialect = dialect_stats.iloc[0]['Dialect']
    worst_dialect = dialect_stats.iloc[-1]['Dialect']

    report.append(f"- **Best Performing Dialect:** {best_dialect} ({dialect_stats.iloc[0]['Accuracy (%)']}% accuracy)")
    report.append(f"- **Worst Performing Dialect:** {worst_dialect} ({dialect_stats.iloc[-1]['Accuracy (%)']}% accuracy)")
    report.append(f"- **Performance Gap:** {range_acc:.2f} percentage points\n")

    report.append("## Statistical Significance Tests\n")
    report.append("### One-Way ANOVA\n")
    report.append(f"- **Null Hypothesis (H₀):** No difference in performance across dialects")
    report.append(f"- **Alternative Hypothesis (H₁):** Significant difference exists")
    report.append(f"- **F-statistic:** {f_stat:.4f}")
    report.append(f"- **p-value:** {p_value:.6f}")
    report.append(f"- **Significance Level:** α = {alpha}")
    report.append(f"- **Decision:** {'REJECT H₀' if p_value < alpha else 'FAIL TO REJECT H₀'}")
    report.append(f"- **Effect Size (η²):** {eta_squared:.4f}\n")

    report.append("### Post-Hoc Pairwise Comparisons (Bonferroni Corrected)\n")
    report.append(f"\n{n_significant} out of {n_total} pairwise comparisons are statistically significant.\n")

    report.append("\n**Top 5 Most Significant Dialect Differences:**\n")
    report.append("| Dialect 1 | Dialect 2 | Diff (%) | p-value | Cohen's d |")
    report.append("|-----------|-----------|----------|---------|-----------|")

    for idx, row in comp_df.head(5).iterrows():
        cohens_d = row["Cohen's d"]
        report.append(f"| {row['Dialect 1']} | {row['Dialect 2']} | {row['Diff (%)']} | "
                     f"{row['p-value']} | {cohens_d} |")

    report.append("\n## Dialect Gap by Model\n")

    report.append("Individual model performance ranges across dialects:\n")
    report.append("| Model | Size (B) | Range (%) | Std Dev | Mean Accuracy |")
    report.append("|-------|----------|-----------|---------|---------------|")

    for model in sorted(df['model_name'].unique(), key=lambda x: MODEL_PARAMS.get(x, 0), reverse=True):
        model_df = df[df['model_name'] == model]
        dialect_accs = []

        for dialect in model_df['dialect'].unique():
            subset = model_df[model_df['dialect'] == dialect]
            dialect_accs.append(subset['success'].mean() * 100)

        if len(dialect_accs) > 1:
            range_val = max(dialect_accs) - min(dialect_accs)
            std_val = np.std(dialect_accs, ddof=1)
            mean_val = np.mean(dialect_accs)
            params = MODEL_PARAMS.get(model, '?')

            report.append(f"| {model} | {params} | {range_val:.2f} | {std_val:.2f} | {mean_val:.2f} |")

    report.append("\n### Model Size vs Dialect Gap\n")

    if corr_gap is not None and p_gap is not None:
        report.append(f"- **Correlation (Pearson r):** {corr_gap:.4f}")
        report.append(f"- **p-value:** {p_gap:.4f}")

        if p_gap < 0.05:
            direction = "smaller" if corr_gap < 0 else "larger"
            report.append(f"- **Interpretation:** Larger models tend to have **{direction}** dialect gaps (significant)")
        else:
            report.append(f"- **Interpretation:** No significant correlation between model size and dialect gap")

    report.append("\n## Visualizations\n")
    report.append("### Main Analysis")
    report.append("![Dialect Gap Analysis](dialect_gap_analysis.png)\n")
    report.append("### Statistical Analysis")
    report.append("![Statistical Analysis](dialect_gap_statistical_analysis.png)\n")

    report.append("## Conclusions\n")

    if p_value < alpha:
        report.append("1. **The dialect gap is real and statistically significant.** Models demonstrate")
        report.append("   measurably different performance across SQL dialects.")
        report.append(f"\n2. **The effect size is {('negligible' if eta_squared < 0.01 else 'small' if eta_squared < 0.06 else 'medium' if eta_squared < 0.14 else 'large')}.** ")
        report.append(f"   SQL dialect explains {dialect_pct:.1f}% of the variance in model performance.")
        report.append(f"\n3. **{best_dialect} shows the best performance** while **{worst_dialect} performs worst,**")
        report.append(f"   with a {range_acc:.1f} percentage point gap.")
        report.append(f"\n4. **{n_significant} pairwise dialect comparisons are statistically significant,**")
        report.append("   indicating that the gap is not just between a few outlier dialects.")
    else:
        report.append("1. **The data does not support a significant dialect gap.** While there are")
        report.append("   numerical differences in performance, they are not statistically significant.")
        report.append(f"\n2. **The observed differences may be due to chance or other factors** such as")
        report.append("   question difficulty, database schemas, or experimental noise.")

    report.append("\n## Recommendations\n")

    if p_value < alpha:
        report.append(f"1. **Prioritize training data for weaker dialects** ({worst_dialect}, etc.)")
        report.append(f"2. **Leverage {best_dialect} as a baseline** for developing dialect-specific training")
        report.append("3. **Consider dialect-specific fine-tuning** to reduce performance gaps")
        report.append("4. **Investigate which SQL features drive the gap** (joins, window functions, etc.)")
        report.append("5. **For production use, consider dialect-specific models or ensembles**")
    else:
        report.append("1. **Current models show relatively uniform performance across dialects**")
        report.append("2. **Focus optimization efforts on overall accuracy** rather than dialect-specific tuning")
        report.append("3. **Monitor for dialect-specific issues** but no immediate action required")

    report.append("\n---")
    report.append("\n*Generated by dialect_gap_analysis.py*")

    report_text = "\n".join(report)

    with open('DIALECT_GAP_REPORT.md', 'w') as f:
        f.write(report_text)

    print("Saved: DIALECT_GAP_REPORT.md")

    return report_text

def main():
    """Main analysis pipeline"""
    print("\n" + "="*80)
    print("SQL DIALECT GAP HYPOTHESIS TESTING")
    print("="*80)

    # Load data
    df = load_and_prepare_data('all_results.csv')

    # Descriptive statistics
    dialect_stats = descriptive_statistics_by_dialect(df)

    # Calculate variance metrics
    variance_df = calculate_dialect_variance(df)

    # Statistical significance testing
    f_stat, p_value, eta_squared = test_dialect_effect_anova(df)
    h_stat, p_kw = test_dialect_effect_kruskal(df)

    # Pairwise comparisons
    comp_df = pairwise_dialect_comparisons(df)

    # Control for model size
    control_for_model_size(df)

    # Model size correlation
    gap_df, corr_gap, p_gap = analyze_model_size_correlation(df)

    # Create visualizations
    create_visualizations(df, dialect_stats, comp_df, gap_df)

    # Generate report
    generate_dialect_gap_report(df, dialect_stats, f_stat, p_value, eta_squared,
                               comp_df, gap_df, corr_gap, p_gap)

    print("\n" + "="*80)
    print("DIALECT GAP ANALYSIS COMPLETE!")
    print("="*80)
    print("\nGenerated files:")
    print("  - DIALECT_GAP_REPORT.md (comprehensive report with hypothesis test)")
    print("  - dialect_gap_analysis.png (main visualizations)")
    print("  - dialect_gap_statistical_analysis.png (statistical test visualizations)")

if __name__ == "__main__":
    main()
