# SQL Error Analysis - LaTeX Report

This directory contains a comprehensive LaTeX report analyzing SQL generation errors from the `new_all_results.csv` file.

## Files

1. **error_analysis_report.tex** - Complete standalone LaTeX document with title page and appendix
2. **error_analysis_chapter.tex** - Main chapter content (can be included in larger documents)
3. **error_examples.json** - JSON file with detailed error examples

## Compilation Instructions

To compile the LaTeX document to PDF:

```bash
# Run pdflatex twice to resolve cross-references
pdflatex error_analysis_report.tex
pdflatex error_analysis_report.tex
```

Or use your preferred LaTeX editor (TeXShop, TeXstudio, Overleaf, etc.)

## Required LaTeX Packages

The document uses the following packages (usually included in standard LaTeX distributions):

- inputenc (UTF-8 encoding)
- fontenc (T1 font encoding)
- geometry (page layout)
- booktabs (professional tables)
- graphicx (graphics support)
- xcolor (colors)
- listings (code listings)
- hyperref (hyperlinks and PDF metadata)
- amsmath (mathematical symbols)
- enumitem (enhanced lists)

## Document Structure

### Main Report (error_analysis_report.tex)

1. **Title Page** - Overview of key statistics
2. **Table of Contents**
3. **Main Chapter** (from error_analysis_chapter.tex)
4. **Appendix** - Additional information about datasets, models, and methodology

### Main Chapter Content

1. **Introduction** - Overview of the analysis
2. **Overall Results Summary** - High-level statistics
3. **Execution Error Breakdown** - Detailed error type distribution
4. **Framework vs. Model Error Attribution** - Reliability assessment
5. **Detailed Error Pattern Analysis**
   - Framework-related errors (CSV, DataFusion, timeout)
   - Model prediction errors (schema, type, syntax, dialect, logic)
6. **Error Distribution by Difficulty, Dataset, and Model**
7. **Semantic Errors** - Analysis of wrong-result errors
8. **Conclusions and Recommendations**

## Key Findings Highlighted

- **Framework Reliability**: 98.78% (only 1.22% of queries fail due to framework issues)
- **Model Accuracy**: Ranges from 27.7% (Archer) to 69.7% (Spider)
- **Semantic Errors**: 37.96% of all queries (largest error category)
- **Execution Errors**: 12.21% of all queries
  - 90% are genuine model issues
  - 10% are framework issues

## Using the Chapter in Your Document

To include just the chapter content in your own LaTeX document:

```latex
\documentclass{book}  % or report, thesis, etc.

% Include necessary packages (see error_analysis_report.tex for list)

\begin{document}
\input{error_analysis_chapter.tex}
\end{document}
```

## Customization

You can customize:

- Page layout in the `\geometry{}` settings
- Colors and fonts in the `\lstdefinestyle{sqlstyle}` settings
- Table formatting using booktabs options
- Hyperlink colors in `\hypersetup{}`

## Tables and Figures

The document includes 8 tables:

1. Overall distribution of results
2. Execution errors by type
3. Framework reliability assessment
4. Error distribution by difficulty
5. Error distribution by dataset
6. Error distribution by model
7. Model error categories summary

## SQL Code Examples

The document includes numerous SQL code listings with:

- Syntax highlighting
- Line numbers
- Captions and labels
- Error messages and analysis

All examples are actual cases from the evaluation dataset.

## Contact

For questions about the analysis or LaTeX compilation issues, please refer to the original error analysis.
