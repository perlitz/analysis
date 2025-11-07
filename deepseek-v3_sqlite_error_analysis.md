# Staff Evaluation Report  

## 1. Summary  

| Item | Value |
|------|-------|
| **experiment_id** | `2025-11-06_18-21-47_sharp_mccarthy` |
| **total** | 100 |
| **executed** | 93 |
| **correct** | 44 |
| **accuracy** | 0.4731 |
| **csv_path** | `results/2025-11-06_18-21-47_sharp_mccarthy/all_results.csv` |
| **sample_size** | 20 |
| **filter_by_model** | `deepseek-v3` |
| **filter_by_dialect** | `sqlite` |

*All fields are taken directly from the supplied experiment metadata. No missing values were encountered.*

---

## 2. Failure Patterns  

### 2.1 Wrong Join or Table  

- **Pattern catalog name:** `wrong_join_or_table`  
- **Question IDs:** 0, 83, 76  
- **Representative key‑differences**  
  1. *Gold uses `atom → molecule → bond`; predicted skips `molecule`.*  
  2. *Gold counts after an `INNER JOIN`; predicted uses a `LEFT JOIN` and counts all rows.*  
  3. *Gold joins `cards` directly to `set_translations` via `id`; predicted adds an extra `sets` join.*  

**Shared mistake:** The model selects an incorrect join path or table, either omitting a required table or inserting an unnecessary one. This changes the row set that subsequent predicates operate on, leading to systematic mis‑calculations.  

**Error type:** **Model error**  

---

### 2.2 Predicate or Filter Error  

- **Pattern catalog name:** `predicate_or_filter_error`  
- **Question IDs:** 53, 12  
- **Representative key‑differences**  
  1. *Gold filters `FundingType = 'Directly funded'`; predicted uses `'Directly Funded'` (case mismatch).*  
  2. *Gold filters on `set_translations.id`; predicted filters on `sets.id`.*  

**Shared mistake:** The generated SQL applies a predicate to the wrong column/value (case‑sensitivity, wrong table), so the WHERE clause does not match the intended rows.  

**Error type:** **Model error**  

---

### 2.3 Output Shape Mismatch  

- **Pattern catalog name:** `output_shape_mismatch`  
- **Question IDs:** 22, 4, 77  
- **Representative key‑differences**  
  1. *Gold returns a single scalar percentage; predicted groups by `molecule_id`.*  
  2. *Gold selects only `ID, Admission`; predicted adds `SEX, Birthday, RBC`.*  
  3. *Gold returns one annual average; predicted adds a per‑year column and pulls language from the wrong table.*  

**Shared mistake:** The model produces a result set with a different schema (extra columns, extra GROUP BY, or wrong aggregation level) than the gold answer, violating the expected output shape.  

**Error type:** **Model error**  

---

### 2.4 Other Issues  

- **Pattern catalog name:** `aggregation_or_order_logic` (singleton)  
- **Question IDs:** 39  
- **Key difference:** *Gold lists `NumTstTakr` row‑wise; predicted wraps it in `SUM(NumTstTakr)`, collapsing all rows into a single total.*  

**Explanation:** The model introduced an aggregation that was not present in the reference query, altering the semantics of the result.  

**Error type:** **Model error**  

---

## 3. Pattern Totals  

| Pattern                     | Count | Question IDs                |
|-----------------------------|-------|-----------------------------|
| wrong_join_or_table         | 3     | 0, 83, 76                   |
| output_shape_mismatch       | 3     | 22, 4, 77                   |
| predicate_or_filter_error   | 2     | 53, 12                      |
| aggregation_or_order_logic  | 1     | 39                          |
| missing_column              | 0     | —                           |
| incorrect_alias             | 0     | —                           |
| syntax_error                | 0     | —                           |
| type_mismatch               | 0     | —                           |
| ordering_error              | 0     | —                           |
| limit_error                 | 0     | —                           |
| duplicate_rows              | 0     | —                           |

*The table is sorted by descending count. All eleven catalog patterns are listed; those not observed receive a count of zero.*

---

## 4. TL;DR  

- The model’s dominant failure modes are **incorrect join paths**, **mis‑specified predicates**, and **output‑shape mismatches** (each affecting multiple queries).  
- No evidence of **Evaluation framework errors** was found; all issues are classified as **Model errors**.  
- Singleton issues (unexpected aggregation) are isolated under “Other Issues” and do not form a recurring pattern.  
- Overall accuracy (≈ 47 %) reflects that more than half of the executed queries contain one of the identified systematic mistakes.  

---  