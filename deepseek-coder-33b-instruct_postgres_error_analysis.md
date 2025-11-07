# 📊 Evaluation Report  

## 1. Summary  

| Metric | Value |
|--------|-------|
| **experiment_id** | `2025-11-06_18-21-47_sharp_mccarthy` |
| **total** | 100 |
| **executed** | 82 |
| **correct** | 32 |
| **accuracy** | 0.3902 |

**Experiment configuration (`exp_config`)**  

- **csv_path**: `results/2025-11-06_18-21-47_sharp_mccarthy/all_results.csv`  
- **sample_size**: 20  
- **filter_by_model**: `deepseek-coder-33b-instruct`  
- **filter_by_dialect**: `postgres`  

The model answered 82 out of 100 test cases; only 32 were correct, yielding an accuracy of **≈ 39 %**.

---

## 2. Failure Patterns  

### 2.1 Wrong Join or Table  *(5 occurrences)*  

| Question IDs | Representative **key_difference** (≤120 chars) |
|--------------|---------------------------------------------------|
| 479, 466, 396, 472, 473 | “Gold joins `cards` ↔ `foreign_data`; predicted uses `language` from `cards` (no join).” |
| | “Gold joins `disp` and filters `disp.type='OWNER'`; predicted filters `account.frequency='OWNER'` (no join).” |
| | “Gold: `INNER JOIN molecule` before `bond`; predicted joins only `atom` ↔ `bond`.” |
| | “Gold: no `sets` join, filter by `cards.id`; predicted joins `sets` and `set_translations`.” |
| | “Gold joins `sets` ↔ `set_translations`; predicted queries only `sets` and uses `MAX(COUNT(language))`.” |

**Shared mistake** – The model frequently omitted required joins or joined the wrong tables, causing column‑not‑found errors or logically different result sets. All instances are **Model error**.

---

### 2.2 Predicate or Filter Error  *(2 occurrences)*  

| Question IDs | Representative **key_difference** |
|--------------|-------------------------------------|
| 449, 408 | “Gold extracts year via `strftime('%Y', OpenDate)` and filters `FundingType='Directly funded'`; predicted uses full date range and mismatched string case.” |
| | “Gold filters on `set_translations.id = 5` and groups; predicted filters on `sets.id = 5` and omits GROUP BY.” |

**Shared mistake** – The model applied the wrong predicate (wrong column, wrong value, or wrong date handling) and often missed required grouping. All instances are **Model error**.

---

### 2.3 Aggregation or Order Logic  *(2 occurrences)*  

| Question IDs | Representative **key_difference** |
|--------------|-------------------------------------|
| 435, 486 | “Gold selects raw `NumTstTakr`; predicted uses `SUM(num_tst_takr)` (adds aggregation).” |
| | “Gold orders by single `points` value; predicted aggregates with `SUM(points)` and returns extra `total_points` column.” |

**Shared mistake** – The model introduced unintended aggregations or changed ordering semantics, altering the intended output. All instances are **Model error**.

---

### 2.4 Output Shape Mismatch  *(4 occurrences)*  

| Question IDs | Representative **key_difference** |
|--------------|-------------------------------------|
| 406, 426, 400, 472* | “Gold returns only two IDs; predicted also returns `id` column (extra column).” |
| | “Gold uses `SELECT DISTINCT T3.element`; predicted drops `DISTINCT` (duplicates possible).” |
| | “Gold returns `ID` and `Admission`; predicted adds `sex`, `birthday` and extra admission filter.” |
| | *(also counted under wrong‑join pattern)* “Gold filters by `cards.id`; predicted adds `sets` join and extra columns.” |

**Shared mistake** – The model either projected additional columns, omitted `DISTINCT`, or added unnecessary filters, resulting in a different result‑set shape. All instances are **Model error**.

---

### 2.5 Other Issues  *(2 singleton patterns merged)*  

| Question IDs | Issue |
|--------------|-------|
| 440 | Uses column names with spaces that do not exist in the schema (invalid identifiers). |
| 418 | Wraps the SQL in markdown code fences (```sql … ```), which the PostgreSQL parser rejects. |

Both are **Model errors** (syntax‑level problems rather than logical ones).

---

## 3. Pattern Totals  

| Pattern | Count | Question IDs |
|---------|-------|--------------|
| wrong_join_or_table | **5** | 479, 466, 396, 472, 473 |
| predicate_or_filter_error | **2** | 449, 408 |
| aggregation_or_order_logic | **2** | 435, 486 |
| output_shape_mismatch | **4** | 406, 426, 400, 472* |
| unsupported_dialect_feature | **1** | 418 |
| other | **1** | 440 |
| syntax_error | **0** | – |
| missing_clause | **0** | – |
| incorrect_alias | **0** | – |
| type_mismatch | **0** | – |
| ordering_error | **0** | – |

*Note: Question 472 appears in both “wrong_join_or_table” and “output_shape_mismatch” because it exhibits both errors.*

The table lists **all 11 catalog patterns**, showing zero for those not observed.

---

## 4. TL;DR  

- The model’s biggest weakness is **missing or incorrect joins** (5 cases), leading to column‑not‑found or logically wrong results.  
- **Predicate/filter mismatches** and **unintended aggregations** each appear twice, showing a pattern of mis‑interpreting the required condition or aggregation level.  
- **Output‑shape mismatches** (extra columns, missing DISTINCT) affect 4 queries, indicating the model does not reliably respect the exact projection required.  
- No **Evaluation framework errors** were detected; all failures stem from the model’s SQL generation.  

**Bottom line:** The model struggles with relational reasoning (joins) and precise predicate formulation, which together account for the majority of its errors and explain the sub‑40 % accuracy.