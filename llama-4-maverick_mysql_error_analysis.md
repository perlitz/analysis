# Staff Evaluation Report  

## 1. Summary  

| Item | Value |
|------|-------|
| **experiment_id** | `2025-11-06_18-21-47_sharp_mccarthy` |
| **total** | 100 |
| **executed** | 96 |
| **correct** | 40 |
| **accuracy** | 0.4167 |

**exp_config**  

- `csv_path`: `results/2025-11-06_18-21-47_sharp_mccarthy/all_results.csv`  
- `sample_size`: 20  
- `filter_by_model`: `llama-4-maverick`  
- `filter_by_dialect`: `mysql`  

> *All fields are taken directly from the supplied metadata; any missing field would be reported as “not provided”.*  

---

## 2. Failure Patterns  

### 2.1 Aggregation or Order Logic  

- **Question IDs**: 2255, 2211, 2249  
- **Representative key differences**  
  1. `CAST(SUM(...) AS REAL) * 100 / COUNT(...)` vs. `(COUNT(CASE…) / COUNT(CASE…)) * 100`  
  2. `SELECT T1.NumTstTakr …` (no aggregation) vs. `SELECT SUM(T1.num_tst_takr) …` (adds SUM)  
  3. `AVG(total_set_size)` vs. `(SUM(id)/COUNT(id))/4` with missing GROUP BY / ORDER BY  

- **Shared mistake**: The model consistently mis‑applies aggregation functions or omits required casts, leading to incorrect numeric results or missing grouping/ordering clauses. In each case the gold query uses a precise aggregate expression (often with a cast to a real type) while the prediction substitutes a simpler or wrong aggregate, or drops the GROUP BY/ORDER BY entirely.  

- **Error type**: **Model error**  

---

### 2.2 Predicate or Filter Error  

- **Question IDs**: 2194, 2245, 2184  
- **Representative key differences**  
  1. `COUNT(DISTINCT CASE WHEN element <> 'f' …)` vs. `100 - (COUNT(DISTINCT … WHERE element='f') / total) * 100`  
  2. `fastestLapTime IS NOT NULL` vs. `fastest_lap_time = (SELECT MIN(fastest_lap_time) …)`  
  3. `WHERE set_translations.id = 5` (INNER) vs. `WHERE sets.id = 5` (LEFT)  

- **Shared mistake**: The model rewrites the filter condition in a way that changes the logical intent. Instead of preserving the original predicate (e.g., “non‑NULL”, “element not equal to ‘f’”, “specific translation id”), the model introduces a different comparison (minimum value, opposite element, wrong table column) or swaps join types, which yields a mismatched result set.  

- **Error type**: **Model error**  

---

### 2.3 Wrong Join or Table  

- **Question IDs**: 2172, 2262, 2248  
- **Representative key differences**  
  1. `atom → molecule → bond` (gold) vs. `atom → connected → bond` (predicted)  
  2. `constructorStandings JOIN constructors` vs. `constructors JOIN constructor_results`  
  3. `set_translations.id IN (SELECT id FROM cards …)` vs. `set_translations → sets → cards` on `set_code`  

- **Shared mistake**: The model selects an incorrect relationship path, either by joining to a table that is not part of the required foreign‑key chain or by using the wrong join column. This produces either missing rows, duplicate rows, or completely unrelated data.  

- **Error type**: **Model error**  

---

### 2.4 Other Issues  

| Question ID | Pattern (merged) | Key Difference (≤120 chars) |
|-------------|------------------|------------------------------|
| 2202 | Output‑shape mismatch | `SELECT DISTINCT a1.element, a2.element` → duplicate column name |
| 2176 | Unsupported dialect feature | Uses MySQL `TIMESTAMPDIFF` / `CURDATE()` instead of SQLite `STRFTIME` |

*Both of these singletons are grouped under “Other Issues” because they do not share a frequent pattern with the larger groups above.*  

---

## 3. Pattern Totals  

| Pattern                     | Count | Question IDs |
|-----------------------------|-------|--------------|
| aggregation_or_order_logic  | 3 | 2255, 2211, 2249 |
| predicate_or_filter_error   | 3 | 2194, 2245, 2184 |
| wrong_join_or_table         | 3 | 2172, 2262, 2248 |
| output_shape_mismatch       | 1 | 2202 |
| unsupported_dialect_feature | 1 | 2176 |
| syntax_error                | 0 | – |
| missing_column              | 0 | – |
| type_mismatch               | 0 | – |
| performance_issue           | 0 | – |
| security_risk               | 0 | – |
| other                       | 0 | – |

*The table lists all eleven catalog patterns, showing zero for those not observed in the current batch.*  

---

## 4. TL;DR  

- The model’s biggest weaknesses are **aggregation/order logic**, **predicate/filter formulation**, and **incorrect join paths** – each appears in three separate questions.  
- Errors are uniformly **model errors**; no evaluation‑framework (ground‑truth) mistakes were detected.  
- Single‑instance issues (duplicate column names, MySQL‑specific functions) are isolated under “Other Issues”.  
- Overall accuracy is low (≈ 42 %), indicating that the model needs targeted remediation on aggregate casting, filter semantics, and proper foreign‑key navigation for the MySQL dialect.  