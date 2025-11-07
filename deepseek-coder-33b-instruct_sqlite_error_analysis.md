## 1. Summary  

| Metric | Value |
|--------|-------|
| **experiment_id** | `2025-11-06_18-21-47_sharp_mccarthy` (derived from `csv_path`) |
| **total** | 100 |
| **executed** | 85 |
| **correct** | 38 |
| **accuracy** | 0.4471 |

**exp_config**  

- `csv_path`: `results/2025-11-06_18-21-47_sharp_mccarthy/all_results.csv`  
- `sample_size`: 20  
- `filter_by_model`: `deepseek-coder-33b-instruct`  
- `filter_by_dialect`: `sqlite`  

---

## 2. Failure Patterns  

### 2.1 Wrong Join or Table  *(Model error)*  

**Question IDs:** 3349, 3336, 3266, 3342, 3343, 3278  

| Example (≤120 chars) | Key Difference |
|----------------------|----------------|
| 3349 | Gold joins `foreign_data`; predicted counts all cards. |
| 3336 | Gold filters `disp.type='OWNER'`; predicted uses `account.frequency`. |
| 3266 | Gold joins `molecule`; predicted joins only `atom`‑`bond`. |
| 3342 | Gold filters `cards.id`; predicted adds unnecessary `sets` join. |
| 3343 | Gold references `set_translations.language`; predicted omits the join. |
| 3278 | Gold filters `set_translations.id=5`; predicted filters `sets.id=5`. |

**Shared mistake:** The model repeatedly omits required tables or adds unrelated joins, causing the logical relationship between entities to be broken. This leads to either missing rows, extra rows, or runtime errors (e.g., “no such column”).  

---

### 2.2 Predicate or Filter Error  *(Model error)*  

**Question IDs:** 3319, 3288, 3339, 3270  

| Example (≤120 chars) | Key Difference |
|----------------------|----------------|
| 3319 | `'Directly funded'` vs `'Directly Funded'`. |
| 3288 | Uses `NOT IN` sub‑query; gold uses `CASE WHEN element <> 'f'`. |
| 3339 | Compares full `dob` to `'1971'`; gold extracts year with `STRFTIME`. |
| 3270 | Adds spurious `Patient.Admission='+'` filter. |

**Shared mistake:** The generated WHERE‑clauses either mis‑spell literals, apply the wrong logical test, or introduce extra conditions that were not present in the reference query, altering the intended row set.  

---

### 2.3 Output Shape Mismatch  *(Model error)*  

**Question IDs:** 3305, 3276, 3296  

| Example (≤120 chars) | Key Difference |
|----------------------|----------------|
| 3305 | Gold returns raw `NumTstTakr`; predicted returns `SUM(NumTstTakr)`. |
| 3276 | Gold selects two IDs; predicted adds an extra `id` column. |
| 3296 | Gold uses `SELECT DISTINCT`; predicted may return duplicates. |

**Shared mistake:** The model changes the cardinality or column list of the result—by aggregating, adding columns, or omitting `DISTINCT`—so the output shape no longer matches the specification.  

---

### 2.4 Other Issues  

**Aggregation or Order Logic** – *Model error*  

- **Question ID:** 3356  
- **Key Difference:** Gold orders by raw `points`; predicted aggregates with `SUM(points)` and adds a `total_points` column.  

This single‑occurrence pattern does not meet the “≥ 2” threshold, so it is grouped under “Other Issues”.  

---

## 3. Pattern Totals  

| Pattern                     | Count | Question IDs |
|-----------------------------|-------|--------------|
| wrong_join_or_table         | 6 | 3349, 3336, 3266, 3342, 3343, 3278 |
| predicate_or_filter_error   | 4 | 3319, 3288, 3339, 3270 |
| output_shape_mismatch       | 3 | 3305, 3276, 3296 |
| aggregation_or_order_logic  | 1 | 3356 |
| syntax_error                | 0 | – |
| semantic_error              | 0 | – |
| missing_column_error        | 0 | – |
| type_mismatch_error         | 0 | – |
| runtime_error               | 0 | – |
| data_type_error             | 0 | – |
| other_error                 | 0 | – |

*Sorted by descending count.*  

---

## 4. TL;DR  

- The model’s biggest weakness is **incorrect joins** (6 cases) – it either drops needed tables or adds unrelated ones, breaking relational logic.  
- **Predicate/filter mistakes** (4 cases) often involve misspelled literals or wrong column usage, leading to filtered row sets that diverge from the gold standard.  
- **Output shape mismatches** (3 cases) show the model frequently changes the number or type of columns returned, e.g., by aggregating or adding extra fields.  
- Only one isolated **aggregation/order** error was observed; no evaluation‑framework errors were detected.  

Overall, the majority of failures stem from **model‑generated SQL logic errors**, not from flaws in the evaluation framework.