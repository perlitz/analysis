# Staff Evaluation Report  

## 1. Summary  

| Item | Value |
|------|-------|
| **experiment_id** | `2025-11-06_18-21-47_sharp_mccarthy` (derived from `csv_path`) |
| **total** | 95 |
| **executed** | 85 |
| **correct** | 29 |
| **accuracy** | 0.3411764705882353 |

**Experiment configuration (`exp_config`)**  

- `csv_path`: `results/2025-11-06_18-21-47_sharp_mccarthy/all_results.csv`  
- `sample_size`: 20  
- `filter_by_model`: `gpt-oss-120b`  
- `filter_by_dialect`: `duckdb`  

---

## 2. Failure Patterns  

### 2.1. **output_shape_mismatch**  *(6 occurrences – Model error)*  

**Question IDs:** 768, 722, 736, 706, 751, 743  

| Example (≤120 chars) | Key Difference |
|----------------------|----------------|
| 768 | Gold selects `users.creation_date`; predicted selects `comments.creation_date`. |
| 722 | Gold returns only `Consumption`; predicted returns `customer_id, consumption`. |
| 736 | Gold: `SELECT DISTINCT member_id`; predicted adds `first_name, last_name, email`. |
| 706 | Gold: `cardKingdomFoilId, cardKingdomId`; predicted only `id`. |
| 751 | Gold: `category, type`; predicted only `category`. |
| 743 | Gold: three columns (`age`, `forename`, `surname`); predicted concatenates name → two columns. |

**Shared mistake:** The model consistently projects the wrong set of columns – either omitting required fields, adding extra ones, or selecting from the wrong table. This changes the output schema, causing a mismatch with the gold result set.

---

### 2.2. **wrong_join_or_table**  *(3 occurrences – Model error)*  

**Question IDs:** 769, 696, 735  

| Example (≤120 chars) | Key Difference |
|----------------------|----------------|
| 769 | Gold joins `cards` → `set_translations` directly; predicted adds a `sets` join and uses `set_code`. |
| 696 | Gold includes an `INNER JOIN molecule`; predicted drops that join entirely. |
| 735 | Gold joins `district` and `client` with ordering/limit; predicted omits `district`, adds unrelated `disp` join. |

**Shared mistake:** The generated SQL either adds unnecessary joins, drops required ones, or joins on the wrong columns, altering the relational path and therefore the result set.

---

### 2.3. **predicate_or_filter_error**  *(3 occurrences – Model error)*  

**Question IDs:** 741, 708, 724  

| Example (≤120 chars) | Key Difference |
|----------------------|----------------|
| 741 | Predicted ends with `HAVING COUNT(*) > ` (incomplete) and misses meeting‑type filter. |
| 708 | Gold filters on `set_translations.id = 5`; predicted filters on `sets.id = 5`. |
| 724 | Gold uses inclusive `BETWEEN 80 AND 500` and `> 1990`; predicted uses exclusive `> 80 AND < 500` and `>= 1990`. |

**Shared mistake:** The model mis‑specifies predicates – either leaving them syntactically incomplete, applying them to the wrong column/table, or using the wrong comparison operators, leading to incorrect row selection.

---

### 2.4. **Other Issues**  *(3 occurrences – Model error)*  

| Question ID | Pattern | Brief note |
|-------------|---------|------------|
| 718 | other | No SQL generated (`NaN`). |
| 780 | group_by_or_having_mismatch | Missing required `GROUP BY`; ordering differs. |
| 700 | unsupported_dialect_feature | Uses `year()` which DuckDB does not support. |

These singleton cases were grouped here because they each appear only once.

---

## 3. Pattern Totals  

| Pattern | Count | Question IDs |
|---------|-------|--------------|
| output_shape_mismatch | 6 | 768, 722, 736, 706, 751, 743 |
| wrong_join_or_table | 3 | 769, 696, 735 |
| predicate_or_filter_error | 3 | 741, 708, 724 |
| group_by_or_having_mismatch | 1 | 780 |
| unsupported_dialect_feature | 1 | 700 |
| other | 1 | 718 |
| syntax_error | 0 | – |
| semantic_error | 0 | – |
| missing_table | 0 | – |
| missing_column | 0 | – |
| type_mismatch | 0 | – |

*Sorted by descending count.*

---

## 4. TL;DR  

- The model’s biggest weakness is **output‑shape mismatches** (6/13 errors), where it selects the wrong columns or adds extras.  
- **Join errors** and **predicate/filter mistakes** each account for three failures, showing a pattern of incorrect relational logic and predicate formulation.  
- Only three singleton issues remain (no‑SQL, missing GROUP BY, unsupported function), none of which indicate a problem with the evaluation framework.  
- **No evaluation‑framework errors** were detected; all mismatches stem from the model’s generation.  

---  