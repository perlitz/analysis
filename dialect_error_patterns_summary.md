# SQL Dialect Error Patterns - Cross-Model Analysis

## Executive Summary

This document analyzes error patterns across 6 SQL dialects (BigQuery, MySQL, Postgres, SQLite, Snowflake, DuckDB) based on analysis reports from multiple LLM models. All errors are **model-generated** with no evaluation framework issues detected.

---

## 1. BigQuery Error Patterns

**Typical Accuracy:** ~35%

### Primary Issues (Ranked by Frequency)

1. **Wrong Join or Table Logic** (5+ occurrences)
   - Missing required intermediate tables (e.g., `atom → molecule → bond` becomes `atom → bond`)
   - Incorrect join conditions (adding `OR` clauses inappropriately)
   - Wrong join paths through foreign keys
   - Example: Joining `cards` directly to `set_translations` instead of going through `sets`

2. **Output Shape Mismatch** (3-4 occurrences)
   - Returning extra columns beyond gold specification
   - Missing `DISTINCT` keywords
   - Wrong column names or data type wrappers (e.g., `STRUCT`)
   - Example: Gold returns `(account_id)` but predicted adds `district_id, frequency, date`

3. **Unsupported Dialect Features** (2 occurrences)
   - **Critical:** Use of non-existent `DIVIDE()` function instead of standard division operator
   - Models hallucinate functions that don't exist in BigQuery
   - Example: `DIVIDE(COUNTIF(...), COUNTIF(...))` instead of `CAST(...) / COUNT(...)`

4. **Aggregation or Order Logic** (2-3 occurrences)
   - Introducing unnecessary `SUM()` or `AVG()` wrappers
   - Nested aggregations (e.g., `AVG(COUNT(...))`) which are illegal in BigQuery
   - Wrong aggregation level (row-wise vs. grouped)
   - Missing type casts in division operations

5. **Date/Time Logic & Predicate Errors** (1-2 occurrences each)
   - Using `PARSE_DATE` when `strftime` semantics needed
   - Filtering on wrong columns or wrong literal values

---

## 2. MySQL Error Patterns

**Typical Accuracy:** ~44-45%

### Primary Issues (Ranked by Frequency)

1. **Output Shape Mismatch** (5 occurrences)
   - Most frequent error in MySQL
   - Projecting wrong columns (using `*` instead of specific columns)
   - Combining columns (e.g., `CONCAT(forename, ' ', surname)` when separate columns needed)
   - Adding extra columns or missing required ones
   - Example: Gold wants `(forename, surname)` but predicted returns `CONCAT(...) AS full_name`

2. **Wrong Join or Table Logic** (3-4 occurrences)
   - Omitting required joins (e.g., skipping `molecule` table)
   - Adding unnecessary joins that change cardinality
   - Using wrong table names in predicates
   - Example: Gold needs `schools ↔ frpm` join but predicted queries only `frpm`

3. **Aggregation or Order Logic** (3 occurrences)
   - Mis-applying `COUNT(CASE...)` vs. proper division
   - Adding aggregation where row-wise results needed
   - Mixing aggregation levels
   - Missing required type casts for numeric operations
   - Example: Gold uses `CAST(SUM(...) AS REAL) * 100 / COUNT(id)` but predicted uses `COUNT(CASE...) / COUNT(CASE...)`

4. **Predicate or Filter Errors** (2 occurrences)
   - Filtering on wrong table/column
   - Incorrect date predicates
   - Example: Filtering `sets.id = 5` instead of `set_translations.id = 5`

5. **Other Issues** (Isolated)
   - Ambiguous column references (e.g., both `sets` and `set_translations` have `id`)
   - Unnecessary `DISTINCT` changing duplicate handling
   - GROUP BY omissions

---

## 3. Postgres Error Patterns

**Typical Accuracy:** ~35-40%

### Primary Issues (Ranked by Frequency)

1. **Wrong Join or Table Logic** (3-5 occurrences)
   - Most common issue across all Postgres tests
   - Omitting required joins entirely
   - Joining on incorrect foreign keys
   - Adding unnecessary intermediate tables
   - Example: Gold needs `atom → molecule → bond` but predicted uses `atom → connected → bond`

2. **Predicate or Filter Errors** (3 occurrences)
   - Case sensitivity issues in string literals
   - Example: `'Directly funded'` vs. `'Directly Funded'`
   - Applying filter to wrong table/column
   - Reversing inclusion/exclusion logic (e.g., using `NOT EXISTS` when should be `COUNT(DISTINCT CASE WHEN ...)`)

3. **Unsupported Dialect Features** (3-4 occurrences)
   - Models emit PostgreSQL-specific syntax when targeting other dialects
   - Using `FILTER (WHERE ...)` clause inappropriately
   - Type casting with `::DATE` syntax
   - Using `EXTRACT(YEAR FROM AGE(...))`
   - Example: Generating Postgres syntax when target is SQLite

4. **Output Shape Mismatch** (2 occurrences)
   - Returning multiple columns when single column needed
   - Adding extra columns from joins
   - Example: Gold wants `DISTINCT element` but predicted returns `element, element` (two columns)

5. **Aggregation or Order Logic** (1-2 occurrences)
   - Adding unnecessary `SUM()` aggregation
   - Nesting aggregates incorrectly

---

## 4. SQLite Error Patterns

**Typical Accuracy:** ~47%

### Primary Issues (Ranked by Frequency)

1. **Wrong Join or Table Logic** (3 occurrences)
   - Skipping required intermediate tables
   - Using `LEFT JOIN` instead of `INNER JOIN` (changes row counts)
   - Adding unnecessary joins through wrong paths
   - Example: Gold uses `INNER JOIN` for counting but predicted uses `LEFT JOIN`

2. **Output Shape Mismatch** (3 occurrences)
   - Returning aggregated results when row-wise needed
   - Example: Gold wants single percentage but predicted groups by `molecule_id`
   - Adding extra columns (e.g., `SEX, Birthday, RBC` when only `ID, Admission` needed)
   - Wrong aggregation level in projection

3. **Predicate or Filter Errors** (2 occurrences)
   - Case sensitivity in string literals
   - Example: `'Directly funded'` vs. `'Directly Funded'`
   - Filtering on wrong table's column
   - Example: `set_translations.id` vs. `sets.id`

4. **Aggregation or Order Logic** (1 occurrence)
   - Adding `SUM()` wrapper that collapses row-wise data
   - Example: Gold returns `NumTstTakr` per row but predicted returns `SUM(NumTstTakr)` total

---

## 5. Snowflake Error Patterns

**Typical Accuracy:** ~37%

### Primary Issues (Ranked by Frequency)

1. **Wrong Join or Table Logic** (4 occurrences)
   - Most frequent error pattern
   - Referencing non-existent columns (e.g., `SCHOOLS.ENROLL12`)
   - Adding unnecessary intermediate joins
   - Joining on mismatched columns
   - Example: Using `SETS.CODE = SET_TRANSLATIONS.SET_CODE` incorrectly

2. **Predicate or Filter Errors** (3 occurrences)
   - Wrong case/value for column comparisons (Snowflake is case-sensitive by default)
   - Using wrong column in WHERE clause
   - Concatenating multi-part keys into single string incorrectly
   - Example: Combining first_name and last_name into `'Kacey Gibson'` literal

3. **Unsupported Dialect Features** (2 occurrences)
   - **Critical:** Using non-existent `DIVIDE()` function
   - Same hallucination as BigQuery
   - Example: `DIVIDE(...)` instead of standard division operator

4. **Output Shape Mismatch** (2 occurrences)
   - Returning duplicate columns (e.g., `ELEMENT, ELEMENT`)
   - Adding extra columns and dropping `DISTINCT`
   - Example: Adding `RBC` column not in gold specification

5. **Case-Sensitive Identifier Issues** (1 occurrence)
   - Quoted identifiers like `"MEMBER"."POSITION"` become case-sensitive in Snowflake
   - Causes "invalid identifier" errors
   - Dialect-specific gotcha

---

## 6. DuckDB Error Patterns

**Typical Accuracy:** ~38%

### Primary Issues (Ranked by Frequency)

1. **Wrong Join or Table Logic** (5 occurrences)
   - Highest frequency issue for DuckDB
   - Incorrect column qualification
   - Missing required joins through intermediate tables
   - Adding unnecessary joins
   - Reading from wrong table entirely
   - Example: Gold needs `atom → molecule → bond` but predicted uses `atom → connected → bond`

2. **Predicate or Filter Errors** (2 occurrences)
   - Using non-existent column names
   - Filtering on wrong table
   - Example: Using `FundingType` column that doesn't exist, or `sets.id` instead of `set_translations.id`

3. **Output Shape Mismatch** (2 occurrences)
   - Aggregating results into single row when multiple rows needed
   - Example: Using `LIST(DISTINCT element)` returning single row instead of multiple rows
   - Dropping `DISTINCT` causing duplicate rows

4. **Aggregation or Order Logic** (1 occurrence)
   - Adding unnecessary `SUM()` aggregation
   - Example: Gold wants `NumTstTakr` per row but predicted sums it

5. **Unsupported Dialect Features** (1 occurrence)
   - Using wrong dialect's functions (e.g., MySQL `YEAR()` instead of DuckDB `STRFTIME`)

---

## Cross-Dialect Common Patterns

### Universal Issues (Present in ALL Dialects)

1. **Wrong Join or Table Logic** - Appears in every dialect (3-5 occurrences each)
   - Most persistent cross-dialect failure mode
   - Models struggle with multi-hop foreign key relationships
   - Frequently skip intermediate tables
   - Add unnecessary joins that change cardinality

2. **Output Shape Mismatch** - Appears in every dialect (2-5 occurrences each)
   - Second most common universal issue
   - Models struggle to match exact column specifications
   - Often add extra columns from joins
   - Fail to preserve `DISTINCT` semantics

3. **Predicate or Filter Errors** - Appears in 5/6 dialects (2-3 occurrences each)
   - Case sensitivity issues with string literals
   - Applying filters to wrong table/column
   - Common in MySQL, Postgres, SQLite, Snowflake, DuckDB

### Dialect-Specific Issues

1. **Function Hallucinations**
   - **BigQuery & Snowflake:** Non-existent `DIVIDE()` function (2 occurrences each)
   - Models invent functions that don't exist in these dialects

2. **Cross-Dialect Contamination**
   - **Postgres errors:** Models emit PostgreSQL-specific syntax (`FILTER`, `::`, `EXTRACT`) when targeting other dialects (3-4 occurrences)
   - **DuckDB errors:** Models use MySQL `YEAR()` instead of DuckDB `STRFTIME`

3. **Case Sensitivity**
   - **Snowflake:** Quoted identifiers become case-sensitive
   - **All dialects:** String literal case mismatches (e.g., `'Directly funded'` vs `'Directly Funded'`)

4. **Aggregation Confusion**
   - **BigQuery:** Illegal nested aggregations like `AVG(COUNT(...))`
   - **All dialects:** Adding unnecessary `SUM()` wrappers that change row-wise to aggregate results

---

## Recommendations by Dialect

### BigQuery
- **Priority 1:** Stop generating `DIVIDE()` function calls
- **Priority 2:** Improve multi-table join path selection
- **Priority 3:** Preserve exact output column specifications
- **Priority 4:** Validate aggregation nesting (illegal in BigQuery)

### MySQL
- **Priority 1:** Match exact output schema (biggest weakness at 5 occurrences)
- **Priority 2:** Avoid unnecessary column concatenation
- **Priority 3:** Improve join path selection
- **Priority 4:** Add proper type casts in percentage calculations

### Postgres
- **Priority 1:** Fix join logic (most frequent at 3-5 occurrences)
- **Priority 2:** Handle case-sensitive string literals correctly
- **Priority 3:** Avoid cross-dialect syntax contamination
- **Priority 4:** Validate predicate column references

### SQLite
- **Priority 1:** Improve join logic (tied with output shape)
- **Priority 2:** Match exact output specifications
- **Priority 3:** Handle case sensitivity in literals
- **Priority 4:** Preserve row-wise vs. aggregated semantics

### Snowflake
- **Priority 1:** Fix join logic (4 occurrences)
- **Priority 2:** Stop generating `DIVIDE()` function
- **Priority 3:** Handle case sensitivity properly (both identifiers and values)
- **Priority 4:** Validate column existence before reference

### DuckDB
- **Priority 1:** Fix join logic (5 occurrences - highest)
- **Priority 2:** Improve predicate column references
- **Priority 3:** Preserve output shape and distinctness
- **Priority 4:** Use DuckDB-native functions (not MySQL equivalents)

---

## Key Insights

1. **Join logic is the #1 problem** across all dialects (3-5 occurrences per dialect)
   - Models consistently struggle with multi-hop relationships
   - Intermediate tables are frequently omitted

2. **Output shape preservation is the #2 problem** (2-5 occurrences per dialect)
   - Models add extra columns from joins
   - `DISTINCT` semantics often lost

3. **Function hallucinations are dialect-specific but severe**
   - BigQuery and Snowflake both affected by invented `DIVIDE()` function
   - Represents fundamental gap in dialect knowledge

4. **Cross-dialect contamination is real**
   - PostgreSQL syntax bleeds into other dialect queries
   - Suggests training data mixing or insufficient dialect separation

5. **No evaluation framework errors detected**
   - All failures are genuine model errors
   - Evaluation methodology is sound

---

*Analysis based on reports from: deepseek-v3, deepseek-coder-33b-instruct, llama-3-1-8b-instruct, llama-3-3-70b-instruct, llama-4-maverick, gpt-oss-120b*
