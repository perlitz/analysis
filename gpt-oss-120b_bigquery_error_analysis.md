# Evaluation Report  

## 1. Summary  

| Item | Value |
|------|-------|
| **experiment_id** | `2025-11-06_18-21-47_sharp_mccarthy` (derived from `csv_path`) |
| **total** | 94 |
| **executed** | 82 |
| **correct** | 27 |
| **accuracy** | 0.32926829268292684 |

**exp_config**  

- `csv_path`: `results/2025-11-06_18-21-47_sharp_mccarthy/all_results.csv`  
- `sample_size`: 20  
- `filter_by_model`: `gpt-oss-120b`  
- `filter_by_dialect`: `bigquery`  

*All fields were supplied; none are missing.*

---

## 2. Failure Patterns  

### 2.1. **output_shape_mismatch**  *(Model error)*  

**Question IDs:** 3212, 3227, 3182, 3262, 3176  

**Representative key differences**  

- 3212: *Gold selects `DISTINCT T3.member_id`; predicted returns many member attributes.*  
- 3227: *Gold includes `type`; predicted returns only `category`.*  
- 3182: *Gold returns `cardKingdomFoilId, cardKingdomId`; predicted returns only `id`.*  
- 3262: *Gold returns `player_name`; predicted adds `height` column.*  
- 3176: *Gold returns `ID, Admission`; predicted adds `sex, birthday, age, rbc`.*

**Shared mistake** – The model consistently projects a different set of columns than required, either by omitting needed columns or by adding extra ones. This changes the result schema, causing a direct mismatch with the gold output shape.

---

### 2.2. **wrong_join_or_table**  *(Model error)*  

**Question IDs:** 3194, 3172, 3255, 3207, 3200  

**Representative key differences**  

- 3194: *Gold joins `yearmonth`; predicted extracts year/month from `transactions_1k.date`.*  
- 3172: *Gold joins `molecule`; predicted uses a sub‑query on `bond` only.*  
- 3255: *Gold uses `INNER JOIN`; predicted uses `LEFT JOIN` with `COUNT(DISTINCT…)`.*  
- 3207: *Gold joins `yearmonth` and sums `consumption`; predicted joins `transactions_1k` and sums `amount`.*  
- 3200: *Gold joins tables to filter on `YEAR > 1990`; predicted uses a different inequality and joins.*

**Shared mistake** – The generated SQL either joins the wrong table, omits a required join, or substitutes a different join type. Consequently the logical relationship between tables diverges from the gold query, leading to incorrect row sets or aggregations.

---

### 2.3. **predicate_or_filter_error**  *(Model error)*  

**Question IDs:** 3244, 3198, 3239, 3216, 3184, 3200, 3221  

**Representative key differences**  

- 3244: *Gold uses `LIKE '%http://%'`; predicted adds `LOWER()` and `DISTINCT`.*  
- 3198: *Gold selects `Consumption`; predicted adds `customer_id` and a division‑by‑zero predicate.*  
- 3239: *Gold filters `disp.type = 'OWNER'`; predicted ends with dangling `AND` and misses the filter.*  
- 3216: *Gold compares integer `29`; predicted compares string `'29'`.*  
- 3184: *Gold filters `T2.id = 5`; predicted filters `s.id = 5` (wrong table).*  
- 3200: *Gold uses `YEAR > 1990` and `IGA BETWEEN 80 AND 500`; predicted uses `>=` and separate `>`/`<` checks.*  
- 3221: *Gold has no ordering; predicted adds `ORDER BY r.year`.*

**Shared mistake** – The model alters the logical conditions of the `WHERE` clause (wrong column, wrong operator, extra functions, missing predicates) or adds unintended clauses such as `ORDER BY`. These changes affect which rows are selected or how they are presented.

---

### 2.4. **Other Issues**  

| Question ID | Pattern | Explanation |
|-------------|---------|-------------|
| 3211 | other | No SQL was generated (`NaN`), so the harness received a missing query. |
| 3234 | schema_backend_mismatch | Fully‑qualified table names (`sqlite_import_f3d0a0fe.*`) caused a backend‑schema resolution error, even though the tables exist. |
| 3221 | aggregation_or_order_logic | Added an `ORDER BY` that was not present in the gold query (already covered under predicate errors but catalogued separately). |

These singleton cases are grouped here because they do not reach the 2‑occurrence threshold for a dedicated subsection.

---

## 3. Pattern Totals  

| Pattern                     | Count | Question IDs |
|-----------------------------|-------|--------------|
| output_shape_mismatch       | 5 | 3212, 3227, 3182, 3262, 3176 |
| wrong_join_or_table         | 5 | 3194, 3172, 3255, 3207, 3200 |
| predicate_or_filter_error   | 7 | 3244, 3198, 3239, 3216, 3184, 3200, 3221 |
| other                       | 1 | 3211 |
| schema_backend_mismatch     | 1 | 3234 |
| aggregation_or_order_logic  | 1 | 3221 |
| **Unobserved catalog patterns** | 0 | – |

*The table lists all catalog patterns referenced in the judgments; any pattern not observed is reported with a count of 0.*

---

## 4. TL;DR  

- The model’s biggest weaknesses are **output‑shape mismatches**, **incorrect joins**, and **faulty predicates** (each appearing in ≥5 cases).  
- A single **evaluation‑framework error** was detected (`schema_backend_mismatch`), indicating a backend‑schema naming issue rather than a modeling flaw.  
- One instance produced **no SQL at all**, highlighting a failure mode that bypasses normal pattern detection.  
- Overall accuracy is low (≈33 %); systematic fixes to column projection, join logic, and predicate formulation are needed to improve performance.