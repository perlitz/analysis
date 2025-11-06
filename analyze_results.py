#!/usr/bin/env python3
"""
Comprehensive Analysis of Text-to-SQL Experimental Results
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

# Set style for better-looking plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

def load_data(filepath):
    """Load the experimental results CSV"""
    print("Loading data...")
    df = pd.read_csv(filepath)
    print(f"Loaded {len(df)} rows with {len(df.columns)} columns")
    return df

def basic_statistics(df):
    """Calculate and display basic statistics"""
    print("\n" + "="*80)
    print("BASIC STATISTICS")
    print("="*80)

    print(f"\nTotal Experiments: {len(df)}")
    print(f"Unique Questions: {df['question_id'].nunique()}")
    print(f"Unique Models: {df['model_name'].nunique()}")
    print(f"Unique Experiments: {df['experiment_id'].nunique()}")

    print("\n--- Execution Statistics ---")
    both_executed = df['both_executed'].sum()
    print(f"Both queries executed: {both_executed} ({both_executed/len(df)*100:.2f}%)")

    if 'results_equal' in df.columns:
        results_equal = df['results_equal'].sum()
        print(f"Results equal (correct): {results_equal} ({results_equal/len(df)*100:.2f}%)")

        # Execution match rate (among those that executed)
        executed_df = df[df['both_executed'] == True]
        if len(executed_df) > 0:
            exec_match = executed_df['results_equal'].sum()
            print(f"Execution Match Rate: {exec_match}/{len(executed_df)} ({exec_match/len(executed_df)*100:.2f}%)")

    print("\n--- Error Statistics ---")
    gold_errors = df['gold_error'].notna().sum()
    pred_errors = df['pred_error'].notna().sum()
    print(f"Gold SQL errors: {gold_errors} ({gold_errors/len(df)*100:.2f}%)")
    print(f"Predicted SQL errors: {pred_errors} ({pred_errors/len(df)*100:.2f}%)")

    return {
        'total': len(df),
        'both_executed': both_executed,
        'results_equal': results_equal if 'results_equal' in df.columns else 0,
        'gold_errors': gold_errors,
        'pred_errors': pred_errors
    }

def analyze_by_model(df):
    """Analyze performance by model"""
    print("\n" + "="*80)
    print("PERFORMANCE BY MODEL")
    print("="*80)

    model_stats = []

    for model in df['model_name'].unique():
        model_df = df[df['model_name'] == model]

        total = len(model_df)
        both_exec = model_df['both_executed'].sum()
        results_eq = model_df['results_equal'].sum() if 'results_equal' in model_df.columns else 0
        pred_errors = model_df['pred_error'].notna().sum()

        # Execution accuracy (among those that executed)
        executed_df = model_df[model_df['both_executed'] == True]
        exec_accuracy = (executed_df['results_equal'].sum() / len(executed_df) * 100) if len(executed_df) > 0 else 0

        model_stats.append({
            'Model': model,
            'Total': total,
            'Both Executed': both_exec,
            'Both Exec %': f"{both_exec/total*100:.2f}%",
            'Results Equal': results_eq,
            'Accuracy %': f"{results_eq/total*100:.2f}%",
            'Exec Accuracy %': f"{exec_accuracy:.2f}%",
            'Pred Errors': pred_errors,
            'Error Rate %': f"{pred_errors/total*100:.2f}%"
        })

    model_df_summary = pd.DataFrame(model_stats)
    model_df_summary = model_df_summary.sort_values('Accuracy %', ascending=False)
    print("\n", model_df_summary.to_string(index=False))

    return model_df_summary

def analyze_by_experiment(df):
    """Analyze performance by experiment_id"""
    print("\n" + "="*80)
    print("PERFORMANCE BY EXPERIMENT")
    print("="*80)

    exp_stats = []

    for exp_id in df['experiment_id'].unique():
        exp_df = df[df['experiment_id'] == exp_id]

        total = len(exp_df)
        both_exec = exp_df['both_executed'].sum()
        results_eq = exp_df['results_equal'].sum() if 'results_equal' in exp_df.columns else 0

        model_name = exp_df['model_name'].iloc[0] if len(exp_df) > 0 else 'Unknown'
        engine = exp_df['model_engine'].iloc[0] if 'model_engine' in exp_df.columns else 'Unknown'
        n_examples = exp_df['n_examples'].iloc[0] if 'n_examples' in exp_df.columns else 'Unknown'
        instr_level = exp_df['instructions_level'].iloc[0] if 'instructions_level' in exp_df.columns else 'Unknown'

        exp_stats.append({
            'Experiment ID': exp_id,
            'Model': model_name,
            'Engine': engine,
            'N Examples': n_examples,
            'Instr Level': instr_level,
            'Total': total,
            'Accuracy': f"{results_eq/total*100:.2f}%",
            'Exec Rate': f"{both_exec/total*100:.2f}%"
        })

    exp_df_summary = pd.DataFrame(exp_stats)
    exp_df_summary = exp_df_summary.sort_values('Accuracy', ascending=False)
    print("\n", exp_df_summary.to_string(index=False))

    return exp_df_summary

def analyze_errors(df):
    """Analyze error patterns"""
    print("\n" + "="*80)
    print("ERROR ANALYSIS")
    print("="*80)

    # Predicted errors
    pred_error_df = df[df['pred_error'].notna()]
    if len(pred_error_df) > 0:
        print(f"\n--- Top 10 Most Common Predicted SQL Errors ---")
        error_counts = pred_error_df['pred_error'].value_counts().head(10)
        for error, count in error_counts.items():
            print(f"{count:4d} | {error[:80]}")

    # Gold errors
    gold_error_df = df[df['gold_error'].notna()]
    if len(gold_error_df) > 0:
        print(f"\n--- Gold SQL Errors ---")
        error_counts = gold_error_df['gold_error'].value_counts()
        print(f"Total unique gold errors: {len(error_counts)}")
        print(error_counts.head(5))

def analyze_by_parameters(df):
    """Analyze impact of different parameters"""
    print("\n" + "="*80)
    print("PARAMETER IMPACT ANALYSIS")
    print("="*80)

    # By number of examples
    if 'n_examples' in df.columns:
        print("\n--- By Number of Examples ---")
        for n_ex in sorted(df['n_examples'].unique()):
            sub_df = df[df['n_examples'] == n_ex]
            accuracy = sub_df['results_equal'].sum() / len(sub_df) * 100
            print(f"N={n_ex:3d}: {len(sub_df):5d} queries, {accuracy:5.2f}% accuracy")

    # By instruction level
    if 'instructions_level' in df.columns:
        print("\n--- By Instruction Level ---")
        for level in sorted(df['instructions_level'].unique()):
            sub_df = df[df['instructions_level'] == level]
            accuracy = sub_df['results_equal'].sum() / len(sub_df) * 100
            print(f"Level {level}: {len(sub_df):5d} queries, {accuracy:5.2f}% accuracy")

    # By model engine
    if 'model_engine' in df.columns:
        print("\n--- By Model Engine ---")
        for engine in df['model_engine'].unique():
            sub_df = df[df['model_engine'] == engine]
            accuracy = sub_df['results_equal'].sum() / len(sub_df) * 100
            print(f"{engine:10s}: {len(sub_df):5d} queries, {accuracy:5.2f}% accuracy")

def create_visualizations(df, model_summary):
    """Create visualization plots"""
    print("\n" + "="*80)
    print("GENERATING VISUALIZATIONS")
    print("="*80)

    # Figure 1: Overall Accuracy by Model
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # Plot 1: Accuracy by Model
    model_acc = []
    for model in df['model_name'].unique():
        model_df = df[df['model_name'] == model]
        acc = model_df['results_equal'].sum() / len(model_df) * 100
        model_acc.append({'Model': model, 'Accuracy': acc})

    acc_df = pd.DataFrame(model_acc).sort_values('Accuracy', ascending=True)
    axes[0, 0].barh(acc_df['Model'], acc_df['Accuracy'], color='skyblue')
    axes[0, 0].set_xlabel('Accuracy (%)')
    axes[0, 0].set_title('Overall Accuracy by Model')
    axes[0, 0].set_xlim(0, 100)

    # Plot 2: Execution Rate vs Accuracy
    exec_rates = []
    accuracies = []
    model_names = []
    for model in df['model_name'].unique():
        model_df = df[df['model_name'] == model]
        exec_rate = model_df['both_executed'].sum() / len(model_df) * 100
        acc = model_df['results_equal'].sum() / len(model_df) * 100
        exec_rates.append(exec_rate)
        accuracies.append(acc)
        model_names.append(model)

    axes[0, 1].scatter(exec_rates, accuracies, s=100, alpha=0.6)
    for i, model in enumerate(model_names):
        axes[0, 1].annotate(model, (exec_rates[i], accuracies[i]), fontsize=8)
    axes[0, 1].set_xlabel('Execution Rate (%)')
    axes[0, 1].set_ylabel('Accuracy (%)')
    axes[0, 1].set_title('Execution Rate vs Accuracy')
    axes[0, 1].set_xlim(0, 105)
    axes[0, 1].set_ylim(0, 105)

    # Plot 3: Error Rates by Model
    error_rates = []
    for model in df['model_name'].unique():
        model_df = df[df['model_name'] == model]
        error_rate = model_df['pred_error'].notna().sum() / len(model_df) * 100
        error_rates.append({'Model': model, 'Error Rate': error_rate})

    error_df = pd.DataFrame(error_rates).sort_values('Error Rate', ascending=True)
    axes[1, 0].barh(error_df['Model'], error_df['Error Rate'], color='salmon')
    axes[1, 0].set_xlabel('Error Rate (%)')
    axes[1, 0].set_title('Prediction Error Rate by Model')

    # Plot 4: Parameter Impact
    if 'n_examples' in df.columns and df['n_examples'].nunique() > 1:
        param_data = []
        for n_ex in sorted(df['n_examples'].unique()):
            sub_df = df[df['n_examples'] == n_ex]
            accuracy = sub_df['results_equal'].sum() / len(sub_df) * 100
            param_data.append({'N Examples': n_ex, 'Accuracy': accuracy})

        param_df = pd.DataFrame(param_data)
        axes[1, 1].plot(param_df['N Examples'], param_df['Accuracy'], marker='o', linewidth=2)
        axes[1, 1].set_xlabel('Number of Examples')
        axes[1, 1].set_ylabel('Accuracy (%)')
        axes[1, 1].set_title('Impact of Number of Examples on Accuracy')
        axes[1, 1].grid(True, alpha=0.3)
    else:
        axes[1, 1].text(0.5, 0.5, 'Insufficient data for\nparameter analysis',
                       ha='center', va='center', transform=axes[1, 1].transAxes)
        axes[1, 1].set_title('Parameter Impact Analysis')

    plt.tight_layout()
    plt.savefig('analysis_overview.png', dpi=300, bbox_inches='tight')
    print("Saved: analysis_overview.png")

    # Figure 2: Detailed Model Comparison
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # Stacked bar chart for execution outcomes
    models = df['model_name'].unique()
    correct = []
    incorrect = []
    errors = []

    for model in models:
        model_df = df[df['model_name'] == model]
        total = len(model_df)
        correct.append(model_df['results_equal'].sum() / total * 100)
        incorrect.append((model_df['both_executed'].sum() - model_df['results_equal'].sum()) / total * 100)
        errors.append(model_df['pred_error'].notna().sum() / total * 100)

    x = np.arange(len(models))
    axes[0].bar(x, correct, label='Correct', color='green', alpha=0.7)
    axes[0].bar(x, incorrect, bottom=correct, label='Incorrect (Executed)', color='orange', alpha=0.7)
    axes[0].bar(x, errors, bottom=np.array(correct)+np.array(incorrect), label='Errors', color='red', alpha=0.7)
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(models, rotation=45, ha='right')
    axes[0].set_ylabel('Percentage (%)')
    axes[0].set_title('Outcome Distribution by Model')
    axes[0].legend()
    axes[0].set_ylim(0, 100)

    # Execution accuracy (accuracy among executed queries)
    exec_acc = []
    for model in models:
        model_df = df[df['model_name'] == model]
        executed_df = model_df[model_df['both_executed'] == True]
        if len(executed_df) > 0:
            acc = executed_df['results_equal'].sum() / len(executed_df) * 100
        else:
            acc = 0
        exec_acc.append(acc)

    axes[1].bar(x, exec_acc, color='steelblue', alpha=0.7)
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(models, rotation=45, ha='right')
    axes[1].set_ylabel('Execution Accuracy (%)')
    axes[1].set_title('Accuracy Among Successfully Executed Queries')
    axes[1].set_ylim(0, 100)

    plt.tight_layout()
    plt.savefig('model_comparison.png', dpi=300, bbox_inches='tight')
    print("Saved: model_comparison.png")

def generate_report(df, basic_stats, model_summary, exp_summary):
    """Generate a markdown report"""
    print("\n" + "="*80)
    print("GENERATING REPORT")
    print("="*80)

    report = []
    report.append("# Text-to-SQL Experimental Results Analysis")
    report.append(f"\n**Analysis Date:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"\n**Dataset:** all_results.csv")
    report.append(f"\n---\n")

    report.append("## Executive Summary\n")
    report.append(f"- **Total Experiments:** {basic_stats['total']:,}")
    report.append(f"- **Unique Models Tested:** {df['model_name'].nunique()}")
    report.append(f"- **Unique Questions:** {df['question_id'].nunique()}")
    report.append(f"- **Overall Accuracy:** {basic_stats['results_equal']/basic_stats['total']*100:.2f}%")
    report.append(f"- **Execution Rate:** {basic_stats['both_executed']/basic_stats['total']*100:.2f}%")
    report.append(f"- **Prediction Error Rate:** {basic_stats['pred_errors']/basic_stats['total']*100:.2f}%\n")

    report.append("## Key Findings\n")

    # Best performing model
    best_model = None
    best_accuracy = 0
    for model in df['model_name'].unique():
        model_df = df[df['model_name'] == model]
        acc = model_df['results_equal'].sum() / len(model_df) * 100
        if acc > best_accuracy:
            best_accuracy = acc
            best_model = model

    report.append(f"### Best Performing Model")
    report.append(f"- **Model:** {best_model}")
    report.append(f"- **Accuracy:** {best_accuracy:.2f}%\n")

    # Model with highest execution rate
    best_exec_model = None
    best_exec_rate = 0
    for model in df['model_name'].unique():
        model_df = df[df['model_name'] == model]
        exec_rate = model_df['both_executed'].sum() / len(model_df) * 100
        if exec_rate > best_exec_rate:
            best_exec_rate = exec_rate
            best_exec_model = model

    report.append(f"### Most Reliable Model (Highest Execution Rate)")
    report.append(f"- **Model:** {best_exec_model}")
    report.append(f"- **Execution Rate:** {best_exec_rate:.2f}%\n")

    report.append("## Detailed Model Performance\n")
    report.append("| Model | Total | Accuracy | Exec Rate | Error Rate |")
    report.append("|-------|-------|----------|-----------|------------|")

    for model in df['model_name'].unique():
        model_df = df[df['model_name'] == model]
        total = len(model_df)
        acc = model_df['results_equal'].sum() / total * 100
        exec_rate = model_df['both_executed'].sum() / total * 100
        error_rate = model_df['pred_error'].notna().sum() / total * 100
        report.append(f"| {model} | {total} | {acc:.2f}% | {exec_rate:.2f}% | {error_rate:.2f}% |")

    report.append("\n## Error Analysis\n")
    pred_errors = df[df['pred_error'].notna()]
    if len(pred_errors) > 0:
        report.append(f"**Total Prediction Errors:** {len(pred_errors)}\n")
        report.append("### Top 5 Most Common Errors:\n")
        for i, (error, count) in enumerate(pred_errors['pred_error'].value_counts().head(5).items(), 1):
            report.append(f"{i}. `{error}` ({count} occurrences)")

    report.append("\n## Visualizations\n")
    report.append("![Analysis Overview](analysis_overview.png)")
    report.append("\n![Model Comparison](model_comparison.png)")

    report.append("\n## Recommendations\n")
    report.append(f"1. **Primary Model Choice:** Use {best_model} for highest accuracy ({best_accuracy:.2f}%)")
    report.append(f"2. **Reliability:** {best_exec_model} has the highest execution success rate ({best_exec_rate:.2f}%)")

    if 'n_examples' in df.columns and df['n_examples'].nunique() > 1:
        # Analyze if more examples help
        examples_impact = []
        for n_ex in sorted(df['n_examples'].unique()):
            sub_df = df[df['n_examples'] == n_ex]
            acc = sub_df['results_equal'].sum() / len(sub_df) * 100
            examples_impact.append((n_ex, acc))

        if len(examples_impact) > 1 and examples_impact[-1][1] > examples_impact[0][1]:
            report.append(f"3. **Few-shot Learning:** Increasing examples from {examples_impact[0][0]} to {examples_impact[-1][0]} improves accuracy by {examples_impact[-1][1] - examples_impact[0][1]:.2f}%")

    report.append("\n---")
    report.append("\n*Generated by analyze_results.py*")

    report_text = "\n".join(report)

    with open('ANALYSIS_REPORT.md', 'w') as f:
        f.write(report_text)

    print("Saved: ANALYSIS_REPORT.md")
    return report_text

def main():
    """Main analysis pipeline"""
    print("\n" + "="*80)
    print("TEXT-TO-SQL EXPERIMENTAL RESULTS ANALYSIS")
    print("="*80)

    # Load data
    df = load_data('all_results.csv')

    # Basic statistics
    basic_stats = basic_statistics(df)

    # Model analysis
    model_summary = analyze_by_model(df)

    # Experiment analysis
    exp_summary = analyze_by_experiment(df)

    # Error analysis
    analyze_errors(df)

    # Parameter impact
    analyze_by_parameters(df)

    # Generate visualizations
    create_visualizations(df, model_summary)

    # Generate report
    generate_report(df, basic_stats, model_summary, exp_summary)

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE!")
    print("="*80)
    print("\nGenerated files:")
    print("  - ANALYSIS_REPORT.md (comprehensive report)")
    print("  - analysis_overview.png (overview visualizations)")
    print("  - model_comparison.png (model comparison charts)")

if __name__ == "__main__":
    main()
