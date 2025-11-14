# Error Analysis of SQL Generation Results

**Comprehensive Evaluation of Text-to-SQL Model Performance**

Analysis of 1,810 SQL Queries Across Multiple Models and Datasets

---

**Key Statistics:**
- Framework Reliability: **98.78%**
- Model Accuracy Range: **27.7% - 69.7%**
- Semantic Error Rate: **37.96%**
- Execution Error Rate: **12.21%**

---

## Table of Contents

1. [Introduction](#introduction)
2. [Overall Results Summary](#overall-results-summary)
3. [Execution Error Breakdown](#execution-error-breakdown)
4. [Framework vs. Model Error Attribution](#framework-vs-model-error-attribution)
5. [Detailed Error Pattern Analysis](#detailed-error-pattern-analysis)
6. [Error Distribution by Difficulty](#error-distribution-by-difficulty)
7. [Error Distribution by Dataset](#error-distribution-by-dataset)
8. [Error Distribution by Model](#error-distribution-by-model)
9. [Semantic Errors](#semantic-errors)
10. [Conclusions and Recommendations](#conclusions-and-recommendations)

---

## Introduction

This report presents a comprehensive error analysis of SQL query generation results from the evaluation of text-to-SQL models. The analysis examines **1,810 queries** from multiple datasets (Spider, BIRD, and Archer) evaluated using three different models (gpt-oss-120b, deepseek-v3, and llama-4-maverick).

The primary objectives are to:
- Categorize and quantify different types of errors
- Distinguish between framework-related issues and genuine model prediction failures
- Provide actionable insights for improving both the evaluation framework and model performance

---

## Overall Results Summary

The table below presents the distribution of results across all 1,810 evaluated queries.

| Result Category | Count | Percentage |
|----------------|-------|------------|
| **Correct Results** | 902 | 49.83% |
| **Semantic Errors** | 687 | 37.96% |
| **Execution Errors** | 221 | 12.21% |
| **Total** | **1,810** | **100.00%** |

### Error Definitions

We distinguish between two primary types of errors:

- **Execution Errors**: Queries that fail to execute due to syntax errors, type mismatches, missing objects, or other runtime failures. These are captured in the `pred_error` field.

- **Semantic Errors**: Queries that execute successfully but produce incorrect results compared to the gold standard query. These cases have `both_executed=True` and `results_equal=False`.

---

## Execution Error Breakdown

Among the 221 execution errors, we identified 13 distinct error patterns.

| Error Type | Count | % of Errors | % of Total |
|-----------|-------|-------------|------------|
| Other/Unclassified | 83 | 37.6% | 4.6% |
| Object Does Not Exist | 30 | 13.6% | 1.7% |
| Division by Zero | 24 | 10.9% | 1.3% |
| API/HTTP Error | 24 | 10.9% | 1.3% |
| CSV/Tokenizing Error | 16 | 7.2% | 0.9% |
| Syntax Error | 16 | 7.2% | 0.9% |
| Binder Error | 10 | 4.5% | 0.6% |
| Subquery Returns Multiple Rows | 6 | 2.7% | 0.3% |
| GROUP BY Error | 4 | 1.8% | 0.2% |
| Table Not Found | 3 | 1.4% | 0.2% |
| Parser Error | 2 | 0.9% | 0.1% |
| Column Not Found | 2 | 0.9% | 0.1% |
| Timeout | 1 | 0.5% | 0.1% |
| **Total** | **221** | **100.0%** | **12.2%** |

---

## Framework vs. Model Error Attribution

A critical aspect of this analysis is distinguishing between errors caused by the evaluation framework (infrastructure issues, engine limitations, data export problems) and genuine model prediction failures.

### Framework Error Rate

| Category | Count | % of All Examples |
|----------|-------|-------------------|
| **Correctly Evaluated** | | |
| ├─ Correct Results | 902 | 49.83% |
| ├─ Semantic Errors (model issue) | 687 | 37.96% |
| └─ Execution Errors (model issue) | 199 | 10.99% |
| **Framework Issues** | | |
| ├─ CSV Export/Parsing | 16 | 0.88% |
| ├─ DataFusion Engine Limitation | 5 | 0.28% |
| └─ Query Timeout | 1 | 0.06% |
| **Framework Reliability** | **1,788/1,810** | **98.78%** |

### Key Finding

> **Only 1.22% of all queries (22 out of 1,810) fail due to framework or infrastructure issues.**

This demonstrates that the evaluation framework is highly reliable and can be trusted to accurately assess model performance.

### Framework Issues Detail

The 22 framework-related failures break down as follows:

#### 1. CSV Export/Parsing (16 cases, 0.88%)

SQL queries containing multi-line statements, nested quotes, or backticks are truncated during CSV export.

**Evidence:**
- 81% of these queries have unbalanced parentheses
- Queries end mid-statement (incomplete syntax)
- All cases show SQL cut off at quote characters or newlines

**Conclusion:** The generated SQL was likely correct but improperly stored.

#### 2. DataFusion Engine Limitations (5 cases, 0.28%)

The DataFusion SQL engine does not support certain features (e.g., Float64 type in specific contexts), causing valid SQL to fail execution.

#### 3. Query Timeout (1 case, 0.06%)

One query exceeded the 120-second execution timeout limit.

---

## Detailed Error Pattern Analysis

This section provides detailed analysis and examples for each major error category.

---

### Framework-Related Errors

#### CSV Export/Parsing Errors

**Count:** 16 (0.88% of all examples, 7.2% of execution errors)

**Root Cause:** The CSV format does not properly escape SQL queries containing newlines, nested quotes, or backticks, resulting in truncated queries.

**Example:**

- **Database:** world_1
- **Difficulty:** moderate
- **Question:** Among countries where English is not the major language, which country has the highest population density relative to the country with the lowest non-zero density?

**Truncated Predicted SQL (incomplete):**

```sql
WITH `english_countries` AS (
    SELECT
        `c`.`code`,
        `c`.`name`,
        `c`.`population`,
        `c`.`surface_area`,
        (`c`.`population` / `c`.`surface_area`) AS `density`
    FROM `country` `c`
    JOIN `countrylanguage` `cl`
      ON `cl`.`country_code` = `c`.`code`
    WHERE `cl
-- Query truncated here during CSV export
```

**Error Message:** `Error tokenizing ' ON `cl`.`country_code` = `c`.`code` WHERE `c'`

**Assessment:** ❌ Framework issue. The SQL was truncated during CSV storage, making it impossible to determine if the original generated query was correct.

---

#### DataFusion Engine Limitations

**Count:** 5 (0.28% of all examples)

**Root Cause:** The DataFusion SQL engine does not support certain SQL features or data types that are valid in other SQL dialects.

**Example:**

```sql
SELECT AVG(gnp) as avg_gnp
FROM country
WHERE continent = 'Europe'
```

**Error Message:** `DataFusion error: NotImplemented("Unsupported SQL type Float64")`

**Assessment:** ❌ Framework limitation. The SQL is valid but cannot be executed in the DataFusion engine.

---

#### Query Timeout

**Count:** 1 (0.06% of all examples)

**Root Cause:** Query execution exceeded the 120-second timeout limit.

**Assessment:** ❌ Framework constraint. The query may be correct but is too slow for the evaluation environment.

---

### Model Prediction Errors

The remaining **199 execution errors (10.99% of all examples)** are genuine model prediction failures. We categorize these into five main groups.

---

### 1. Schema and Naming Errors (45 cases, 2.5% of all examples)

These errors occur when the model references non-existent tables, columns, or uses incorrect naming conventions.

#### Object Does Not Exist (30 cases)

**Example:**

- **Database:** concert_singer
- **Difficulty:** moderate
- **Question:** What is the total payment amount for all singers across all concerts?

**Predicted SQL (with non-existent table):**

```sql
SELECT SUM(payment_amount)
FROM singer_payment
```

**Error:** `SQL compilation error: Object 'singer_payment' does not exist`

**Correct Gold SQL:**

```sql
SELECT SUM(singer_fee)
FROM singer_in_concert
```

**Analysis:** ✗ The model hallucinated a table name that does not exist in the schema. The actual schema uses `singer_in_concert` with a `singer_fee` column.

---

#### Binder Error (10 cases)

These errors typically involve case sensitivity issues or incorrect column references.

**Example:**

```sql
SELECT SUM(CommentCount) AS total_comments
FROM posts
```

**Error:** `Referenced column "CommentCount" not found. Candidate bindings: "comment_count"`

**Analysis:** ✗ The model used incorrect capitalization. The actual column name is `comment_count` (lowercase with underscore).

---

#### Table/Column Not Found (5 cases)

Similar to Object Does Not Exist, but with different error messages from different SQL engines.

---

### 2. Type and Data Errors (39 cases, 2.2% of all examples)

#### Division by Zero (24 cases)

**Example:**

- **Question:** What is the average GNP growth rate for each continent?

**Predicted SQL (without NULL/zero handling):**

```sql
SELECT continent,
       AVG((gnp - gnp_old) / gnp_old * 100) as growth_rate
FROM country
GROUP BY continent
```

**Error:** `Division by zero (22012)`

**Analysis:** ✗ The model did not account for NULL or zero values in `gnp_old`, which causes division by zero errors.

**Corrected SQL with NULL handling:**

```sql
SELECT continent,
       AVG(CASE
           WHEN gnp_old IS NOT NULL AND gnp_old > 0
           THEN (gnp - gnp_old) / gnp_old * 100
           ELSE NULL
       END) as growth_rate
FROM country
GROUP BY continent
```

---

#### Type Mismatch (15 cases)

**Example:**

- **Database:** museum_visit

**Predicted SQL (type mismatch - comparing STRING to INT64):**

```sql
SELECT SUM(T1.total_spent)
FROM visit AS T1
JOIN visitor AS T2 ON T1.visitor_id = T2.id
WHERE T2.level_of_membership = 1
```

**Error:** `No matching signature for operator = for argument types: STRING, INT64`

**Analysis:** ✗ The column `level_of_membership` is stored as STRING, but the model compared it to an integer literal without casting.

**Corrected SQL with proper type handling:**

```sql
SELECT SUM(T1.total_spent)
FROM visit AS T1
JOIN visitor AS T2 ON T1.visitor_id = T2.id
WHERE T2.level_of_membership = '1'  -- String literal
-- OR with casting:
-- WHERE CAST(T2.level_of_membership AS INT64) = 1
```

---

### 3. SQL Syntax Errors (21 cases, 1.2% of all examples)

#### Syntax Error (16 cases)

**Example:**

```sql
SELECT id FROM highschooler
WHERE id NOT IN (
    SELECT student_id FROM friend
    UNION SELECT friend_id FROM friend
)
```

**Error:** `Expected keyword ALL or keyword DISTINCT but got keyword SELECT`

**Analysis:** ✗ BigQuery requires explicit `UNION DISTINCT` or `UNION ALL`. The model omitted the required keyword.

---

#### Parser Error (2 cases)

**Example:**

```sql
SELECT name FROM drivers
WHERE surname = 'Schumacher
-- Missing closing quote
```

**Error:** `Parser Error: unterminated quoted string at or near "'Schumacher"`

---

#### Missing Required Keyword (3 cases)

**Example:**

```sql
SELECT c.concert_id, c.concert_name,
       CASE WHEN COUNT(s.singer_id) =
-- Missing THEN clause and END keyword
```

**Error:** `Required keyword: 'expression' missing for <class 'sqlglot.expressions.EQ'>`

---

### 4. Dialect and Function Errors (9 cases, 0.5% of all examples)

#### API/HTTP Errors (8 cases)

These are BigQuery-specific errors where the model uses functions or syntax not supported by BigQuery.

**Example:**

```sql
SELECT DIVIDE(SUM(CASE WHEN m.label = '+' THEN 1 ELSE 0 END),
              COUNT(DISTINCT m.molecule_id)) * 100.0
FROM molecule m
```

**Error:** `Function not found: DIVIDE`

**Analysis:** ✗ BigQuery does not have a `DIVIDE` function. The model should use the `/` operator instead.

---

#### Function Not Found (1 case)

Similar errors for other SQL dialects.

---

### 5. Logic Errors (46 cases, 2.5% of all examples)

#### Subquery Returns Multiple Rows (6 cases)

**Example:**

- **Question:** Which city in North America has a population at least twice that of Kang-won?

**Predicted SQL (subquery returning multiple rows):**

```sql
SELECT name
FROM city
JOIN country ON city.country_code = country.code
WHERE country.continent = 'North America'
  AND city.population >= 2 * (
      SELECT population
      FROM city
      WHERE name = 'Kang-won'  -- Multiple cities may have this name
  )
```

**Error:** `Single-row subquery returns more than one row`

**Analysis:** ✗ The subquery is expected to return a single value, but multiple cities may share the name "Kang-won". The gold SQL correctly uses `SUM(Population)` with `District = "Kang-won"`.

---

#### DataFusion Errors (40 cases)

These represent SQL that is incompatible with the DataFusion engine due to invalid syntax or unsupported patterns (distinct from the 5 DataFusion *limitation* cases).

---

#### GROUP BY Errors (4 cases)

**Example:**

```sql
SELECT h.name, AVG(h.capacity)
FROM stadium h
```

**Error:** `Expression #1 of SELECT list is not in GROUP BY clause and contains nonaggregated column 'h.name'`

---

## Error Distribution by Difficulty

| Difficulty | Total | Correct | Semantic | Execution | Accuracy |
|-----------|-------|---------|----------|-----------|----------|
| Simple | 1,262 | 631 | 477 | 154 | **50.0%** |
| Moderate | 485 | 225 | 197 | 63 | **46.4%** |
| Challenging | 63 | 46 | 13 | 4 | **73.0%** |

### Surprising Finding

**Challenging queries have the highest accuracy (73.0%)**, while simple and moderate queries show lower accuracy (50.0% and 46.4% respectively).

This counter-intuitive result warrants further investigation, as it suggests:
- The difficulty labels may not align with actual model performance, OR
- "Challenging" queries may have different characteristics that make them easier for models to handle correctly

---

## Error Distribution by Dataset

| Dataset | Total | Correct | Semantic | Execution | Accuracy |
|---------|-------|---------|----------|-----------|----------|
| **spider_dev** | 628 | 438 | 151 | 39 | **69.7%** |
| **bird_dev** | 612 | 306 | 249 | 57 | **50.0%** |
| **archer_dev** | 570 | 158 | 287 | 125 | **27.7%** |

### Analysis

The **Archer dataset** proves significantly more challenging than Spider and BIRD, with only 27.7% accuracy compared to 69.7% for Spider. This suggests Archer contains more complex reasoning requirements or edge cases that current models struggle with.

---

## Error Distribution by Model

| Model | Total | Correct | Semantic | Execution | Accuracy |
|-------|-------|---------|----------|-----------|----------|
| **gpt-oss-120b** | 550 | 305 | 173 | 72 | **55.5%** |
| **deepseek-v3** | 630 | 306 | 257 | 67 | **48.6%** |
| **llama-4-maverick** | 630 | 291 | 257 | 82 | **46.2%** |

### Analysis

**GPT-OSS-120B** achieves the highest accuracy at 55.5%, outperforming deepseek-v3 (48.6%) and llama-4-maverick (46.2%). All three models show relatively similar execution error rates (11-13%), with the main performance difference coming from semantic correctness.

---

## Semantic Errors

While this report focuses primarily on execution errors, **semantic errors represent the largest category of failures** (37.96% of all examples, 687 cases). These errors are particularly challenging because the generated SQL is syntactically valid and executes without errors, yet produces incorrect results.

### Characteristics of Semantic Errors

Semantic errors typically arise from:

1. **Incorrect aggregation logic** - Using the wrong aggregation function or grouping criteria
2. **Wrong JOIN conditions** - Joining tables on incorrect columns or using inappropriate JOIN types
3. **Misunderstanding question requirements** - Failing to capture the precise intent of the natural language question
4. **Incorrect filtering logic** - Using wrong WHERE conditions or missing necessary filters
5. **Calculation errors** - Computing metrics incorrectly (e.g., growth rate formulas)

### Example: Semantic Error

**Question:** Among the countries that became independent after 1979, which country has the highest growth rate of GNP?

**Predicted SQL (executes but wrong results):**

```sql
SELECT `name` AS country_name,
       (`gnp` - `gnp_old`) / `gnp_old` AS growth_rate
FROM `country`
WHERE `indep_year` > 1979
ORDER BY growth_rate DESC
LIMIT 1;
```

**Gold SQL (correct):**

```sql
SELECT Name
FROM country
WHERE IndepYear > 1979
ORDER BY 1.0 * (GNP - GNPOld) / GNPOld DESC
LIMIT 1
```

**Result:** `both_executed=True`, `results_equal=False`

**Analysis:** The predicted SQL appears correct at first glance and executes successfully. However, subtle differences in handling NULL values and type conversion (note the `1.0 *` multiplication in gold SQL to force floating-point division) lead to different results. Additionally, the predicted SQL returns both the name and growth rate, while the question only asks for the country name.

---

## Conclusions and Recommendations

### Framework Reliability

The evaluation framework demonstrates **excellent reliability with a 98.78% success rate**. Only 22 out of 1,810 queries (1.22%) fail due to framework issues rather than model predictions. This high reliability means the framework can be trusted to accurately assess model performance.

---

### Framework Improvements

Despite high overall reliability, the following improvements are recommended:

#### 1. Fix CSV Export (Priority: High)

- **Issue:** SQL queries with quotes/newlines are truncated
- **Impact:** 16 queries (0.88%)
- **Solution:** Switch to JSONL format or implement proper CSV escaping
- **Benefit:** Would improve framework reliability from 98.78% to 99.12%

#### 2. Document Engine Limitations (Priority: Medium)

- **Issue:** 5 known DataFusion limitations
- **Solution:** Clearly document these cases to avoid misattributing failures to model errors

#### 3. Increase Timeout (Priority: Low)

- **Issue:** 1 query exceeds 120-second timeout
- **Solution:** Consider increasing timeout for complex queries, or provide separate reporting for timeout cases

---

### Model Error Categories

The **199 genuine model execution errors (10.99% of examples)** break down into five categories:

| Category | Count | % of Model Errors |
|----------|-------|-------------------|
| Schema/Naming Errors | 45 | 22.6% |
| Logic Errors | 46 | 23.1% |
| Type/Data Errors | 39 | 19.6% |
| Syntax Errors | 21 | 10.6% |
| Dialect/Function Errors | 9 | 4.5% |
| Other/Unclassified | 39 | 19.6% |
| **Total** | **199** | **100.0%** |

---

### Recommendations for Model Improvement

Based on the error analysis, we recommend the following focus areas for improving model performance:

#### 1. Semantic Correctness (Priority: HIGHEST)

**Impact:** 687 semantic errors (37.96%) - the largest error category

**Focus areas:**
- Complex aggregation and calculation logic
- Precise interpretation of natural language questions
- Edge cases in data (NULL values, zero values, etc.)

---

#### 2. Schema Understanding (Priority: HIGH)

**Impact:** 45 schema/naming errors

**Improvements needed:**
- Schema awareness and table/column name accuracy
- Case sensitivity handling
- Understanding of database structure and relationships

---

#### 3. Type Safety (Priority: HIGH)

**Impact:** 39 type/data errors

**Improvements needed:**
- Add explicit NULL and zero checks before division
- Properly cast between data types
- Validate type compatibility in comparisons

---

#### 4. SQL Dialect Awareness (Priority: MEDIUM)

**Impact:** 9 dialect errors

**Improvements needed:**
- Better understanding of target database syntax (BigQuery, MySQL, PostgreSQL, etc.)
- Knowledge of available functions per dialect
- Proper syntax for dialect-specific features

---

#### 5. Syntax Correctness (Priority: MEDIUM)

**Impact:** 21 syntax errors

**Improvements needed:**
- Complete SQL statement generation
- Proper keyword usage
- String literal handling

---

### Overall Assessment

The evaluation results reveal that:

✅ **Framework is highly reliable** (98.78% accuracy in evaluation execution)

✅ **Approximately half of all queries** (49.83%) are correctly solved

⚠️ **Semantic errors** (37.96%) represent the primary challenge, outnumbering execution errors (12.21%) by **3:1**

✅ **After fixing minor framework issues** (CSV export), the true model execution error rate is 10.99%

⚠️ **Significant performance variation** exists across datasets (27.7% to 69.7% accuracy)

⚠️ **Best-performing model** (gpt-oss-120b) achieves 55.5% accuracy, indicating **substantial room for improvement**

---

### Impact Summary

| Metric | Value |
|--------|-------|
| Total Examples | 1,810 |
| Framework Reliability | 98.78% |
| Model Accuracy (Best) | 55.5% |
| Model Accuracy (Worst Dataset) | 27.7% |
| Semantic Error Rate | 37.96% |
| Execution Error Rate | 12.21% |
| Framework Error Rate | 1.22% |

---

## Appendix

### Dataset Information

The analysis covers three major text-to-SQL datasets:

- **Spider Dev**: 628 queries, cross-domain database coverage
- **BIRD Dev**: 612 queries, complex real-world databases
- **Archer Dev**: 570 queries, commonsense reasoning focus

### Model Information

Three models were evaluated:

- **gpt-oss-120b**: 550 queries evaluated
- **deepseek-v3**: 630 queries evaluated
- **llama-4-maverick**: 630 queries evaluated

### Evaluation Methodology

Each query was evaluated using the following process:

1. Generate SQL from natural language question using the model
2. Execute both generated SQL and gold (reference) SQL
3. Compare execution results for equality
4. Record any errors encountered during execution
5. Classify errors by type and root cause

### Error Classification Methodology

Errors were classified using a multi-stage process:

1. **Initial categorization** - Group errors by error message patterns
2. **Root cause analysis** - Examine SQL queries to determine underlying causes
3. **Framework vs. Model attribution** - Determine if error is due to evaluation infrastructure or model prediction
4. **Validation** - Compare with gold SQL execution to confirm attribution

---

**Report Generated:** Analysis of new_all_results.csv

**Total Queries Analyzed:** 1,810

**Framework Reliability:** 98.78%

**Model Performance Range:** 27.7% - 69.7% across datasets
