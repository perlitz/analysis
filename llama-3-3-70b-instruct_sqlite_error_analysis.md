## 1. Summary  

| Item | Value |
|------|-------|
| **experiment_id** | `2025-11-06_18-21-47_sharp_mccarthy` (derived from `csv_path`) |
| **total** | 100 |
| **executed** | 94 |
| **correct** | 41 |
| **accuracy** | 0.43617021276595747 |

**Experiment configuration**  

- `csv_path`: `results/2025-11-06_18-21-47_sharp_mccarthy/all_results.csv`  
- `sample_size`: 20  
- `filter_by_model`: `llama-3-3-70b-instruct`  
- `filter_by_dialect`: `sqlite`  

---

## 2. Failure Patterns  

### 2.1. **aggregation_or_order_logic**  *(2 occurrences)*  

- **Question IDs**: 1168, 1124  
- **Representative key differences**  
  1. `COUNT(T2.power)` vs `COUNT(T1.id)` – denominator mismatch (Q1168)  
  2. `SELECT SUM(T1.NumTstTakr)` vs `SELECT T1.NumTstTakr` – unnecessary aggregation (Q1124)  

**Shared mistake** – The model introduced or altered aggregation functions (COUNT, SUM) in a way that changes the logical scope of the calculation. Instead of mirroring the gold‑standard aggregation (or lack thereof), it either counted a different column or added an extra SUM, producing numerically different results.  

**Error label** – **Model error**  

---

### 2.2. **output_shape_mismatch**  *(4 occurrences)*  

- **Question IDs**: 1138, 1107, 1115, 1089  
- **Representative key differences**  
  1. `COUNT(CDSCode)` vs `COUNT(School)` – different projection column (Q1138)  
  2. Added `GROUP BY T1.molecule_id` turning a scalar into many rows (Q1107)  
  3. Missing `DISTINCT` on `element` (Q1115)  
  4. Missing `DISTINCT` on `ID, Admission` (Q1089)  

**Shared mistake** – The predicted SQL returns a result set whose shape (number of columns/rows) does not match the gold query. Typical deviations are counting a different column, omitting `DISTINCT`, or inserting a `GROUP BY` that fragments a single‑value result into multiple rows.  

**Error label** – **Model error**  

---

### 2.3. **wrong_join_or_table**  *(5 occurrences)*  

- **Question IDs**: 1129, 1085, 1161, 1162, 1097  
- **Representative key differences**  
  1. No join to `schools`; references non‑existent `AdmFName1` (Q1129)  
  2. Skips `molecule` join, limiting scope to `atom → bond` only (Q1085)  
  3. Joins `sets` then `set_translations` via `setCode` instead of linking `set_translations` directly to `cards` (Q1161)  
  4. Uses `foreign_data` instead of `set_translations`; omits required joins (Q1162)  
  5. Filters on `sets.id` rather than `set_translations.id` and drops `GROUP BY` (Q1097)  

**Shared mistake** – The model either omitted a required table join, joined the wrong tables, or used incorrect join keys. This changes the logical domain of the query, often leading to column‑not‑found errors or completely different result sets.  

**Error label** – **Model error**  

---

### 2.4. **Other Issues**  *(2 singleton patterns merged)*  

| Pattern | Question ID | Key Difference (≤120 chars) |
|---------|-------------|------------------------------|
| `predicate_or_filter_error` | 1097 | Filters on `T1.id` instead of `T2.id`; missing GROUP BY |
| `date_or_time_logic_error` | 1116 | Uses `'2014/04/23 20:29:39.0'` (slashes) vs `'2014-04-23 20:29:39.0'` (hyphens) |

Both are **Model errors**; they do not belong to a larger cluster in this sample, so they are reported together under “Other Issues”.

---

## 3. Pattern Totals  

| Pattern | Count | Question IDs |
|---------|-------|--------------|
| `wrong_join_or_table` | 5 | 1129, 1085, 1161, 1162, 1097 |
| `output_shape_mismatch` | 4 | 1138, 1107, 1115, 1089 |
| `aggregation_or_order_logic` | 2 | 1168, 1124 |
| `predicate_or_filter_error` | 1 | 1097 |
| `date_or_time_logic_error` | 1 | 1116 |
| *Other pattern 1* | 0 | – |
| *Other pattern 2* | 0 | – |
| *Other pattern 3* | 0 | – |
| *Other pattern 4* | 0 | – |
| *Other pattern 5* | 0 | – |
| *Other pattern 6* | 0 | – |

*The six “Other pattern” rows represent catalog categories that were not observed in the current sample; counts are therefore zero.*

---

## 4. TL;DR  

- The model’s biggest weaknesses are **wrong joins** (5 cases) and **output‑shape mismatches** (4 cases).  
- Aggregation logic errors appear in 2 queries, typically by counting the wrong column or adding an unnecessary `SUM`.  
- No **Evaluation framework error** was detected; all failures are attributable to the model’s SQL generation.  
- Singleton issues (filtering on the wrong column and date‑format mismatch) are isolated and do not form a recurring pattern.  