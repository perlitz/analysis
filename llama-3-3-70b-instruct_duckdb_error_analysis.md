# Staff Evaluation Report  

## 1. Summary  

| Metric | Value |
|--------|-------|
| **experiment_id** | `2025-11-06_18-21-47_sharp_mccarthy` |
| **total** | 100 |
| **executed** | 91 |
| **correct** | 36 |
| **accuracy** | 0.3956 |

**Experiment configuration (`exp_config`)**  

- `csv_path`: `results/2025-11-06_18-21-47_sharp_mccarthy/all_results.csv`  
- `sample_size`: 20  
- `filter_by_model`: `llama-3-3-70b-instruct`  
- `filter_by_dialect`: `duckdb`  

---

## 2. Failure Patterns  

### 2.1. **output_shape_mismatch**  *(2 occurrences)*  

**Question IDs:** 1438, 1395  

| Question ID | Representative *key_difference* (≤120 chars) |
|-------------|-----------------------------------------------|
| 1438 | Gold: `COUNT(School)` … ; Predicted: `COUNT(cds_code)` … |
| 1395 | Gold selects `cardKingdomFoilId, cardKingdomId`; Predicted selects only `id` |

**Shared mistake** – The model returned a query that projects the wrong columns or aggregates the wrong field, so the shape (number and identity of output columns) does not match the gold specification.  

**Error label:** **Model error**  

---

### 2.2. **wrong_join_or_table**  *(6 occurrences)*  

**Question IDs:** 1455, 1385, 1415, 1461, 1462, 1397  

| Question ID | Representative *key_difference* (≤120 chars) |
|-------------|-----------------------------------------------|
| 1455 | Gold joins `disp` and filters `disp.type='OWNER'`; Predicted never joins `disp`. |
| 1385 | Gold path: `atom → molecule → bond`; Predicted: `atom → bond` (missing molecule). |
| 1415 | Gold uses `connected.atom_id` only; Predicted adds a UNION with `connected.atom_id2`. |
| 1461 | Gold filters `set_translations` directly; Predicted adds extra join through `sets`. |
| 1462 | Gold joins `set_translations`; Predicted omits it and uses unrelated `foreign_data`. |
| 1397 | Gold filters on `set_translations.id`; Predicted filters on `sets.id` and drops GROUP BY. |

**Shared mistake** – The generated SQL either omits a required join, adds an unnecessary join, or joins on the wrong column/table, leading to an incorrect relational graph and therefore wrong result sets.  

**Error label:** **Model error**  

---

### 2.3. **Other Issues**  *(3 singleton patterns merged)*  

| Pattern | Question ID | Representative *key_difference* |
|---------|-------------|----------------------------------|
| aggregation_or_order_logic | 1424 | Gold returns `NumTstTakr`; Predicted uses `SUM(num_tst_takr)`. |
| other (ambiguous column) | 1407 | Gold qualifies `atom.molecule_id`; Predicted uses unqualified `molecule_id`. |
| unsupported_dialect_feature | 1389 | Gold uses `STRFTIME`; Predicted uses `SUBTRACT(year(...), year(...))`. |
| predicate_or_filter_error | 1397 (also listed under wrong_join) | Gold filters on `set_translations.id`; Predicted filters on `sets.id`. |

**Shared mistake** – These isolated errors each reflect a distinct class of failure (incorrect aggregation, ambiguous column references, use of non‑DuckDB functions, or wrong predicate column). Because they appear only once, they are grouped under a generic “Other Issues” heading.  

**Error label:** **Model error**  

---

## 3. Pattern Totals  

| Pattern | Count | Question IDs |
|---------|-------|--------------|
| wrong_join_or_table | 6 | 1455, 1385, 1415, 1461, 1462, 1397 |
| output_shape_mismatch | 2 | 1438, 1395 |
| aggregation_or_order_logic | 1 | 1424 |
| other | 1 | 1407 |
| unsupported_dialect_feature | 1 | 1389 |
| predicate_or_filter_error | 1 | 1397 |
| **Unobserved pattern 1** | 0 | – |
| **Unobserved pattern 2** | 0 | – |
| **Unobserved pattern 3** | 0 | – |
| **Unobserved pattern 4** | 0 | – |
| **Unobserved pattern 5** | 0 | – |

*The five “Unobserved pattern” rows represent catalog categories that were not triggered in this sample; their exact names are not provided in the data.*

---

## 4. TL;DR  

- The model’s biggest weakness is **incorrect join logic** (6 out of 13 errors), often omitting required tables or joining on the wrong keys.  
- **Output‑shape mismatches** (2 errors) show the model frequently selects the wrong columns or aggregates the wrong field.  
- All identified failures are **model errors**; no evaluation‑framework errors were detected.  
- Minor, isolated issues (aggregation misuse, ambiguous columns, unsupported DuckDB functions) appear only once each and are grouped under “Other Issues”.  

---  

*End of report.*