## 1. Summary  

| Item | Value |
|------|-------|
| **experiment_id** | not provided |
| **total** | 100 |
| **executed** | 93 |
| **correct** | 40 |
| **accuracy** | 0.43010752688172044 |

**exp_config**  

- `csv_path`: `results/2025-11-06_18-21-47_sharp_mccarthy/all_results.csv`  
- `sample_size`: 20  
- `filter_by_model`: `llama-4-maverick`  
- `filter_by_dialect`: `duckdb`  

The run processed 93 of the 100 sampled questions; 40 of those predictions matched the gold standard, yielding an accuracy of ~43 %.

---

## 2. Failure Patterns  

### 2.1 aggregation_or_order_logic  *(2 occurrences)*  

- **Question IDs:** 924, 907  
- **Representative key differences**  
  1. `Gold: SELECT T1.NumTstTakr …` → `Predicted: SELECT SUM(T1.num_tst_takr) …`  
  2. `Gold: COUNT(DISTINCT …) * 100 / COUNT(DISTINCT …)` → `Predicted: 100 - AVG(CASE …)`  

**Shared mistake** – The model introduced an aggregation function (SUM or AVG) where the gold query either returned raw column values or used a different aggregation strategy (COUNT + DISTINCT). This changes the numeric semantics of the result set, producing values that are not comparable to the expected output.  

**Error type:** **Model error**  

---

### 2.2 wrong_join_or_table  *(3 occurrences)*  

- **Question IDs:** 915, 889, 961  
- **Representative key differences**  
  1. Gold joins on `connected.atom_id`; Predicted adds a UNION that also joins on `connected.atom_id2`.  
  2. Gold uses `INNER JOIN Patient ↔ Laboratory`; Predicted replaces the join with an `IN` sub‑query.  
  3. Gold filters `set_translations` via a sub‑query on `cards.id`; Predicted joins on `set_code`.  

**Shared mistake** – The model either altered the join condition, introduced an extra join/UNION, or swapped a required explicit join for a sub‑query. In each case the row‑level relationship between tables is mis‑specified, leading to extra, missing, or mis‑aligned rows.  

**Error type:** **Model error**  

---

### 2.3 predicate_or_filter_error  *(2 occurrences)*  

- **Question IDs:** 958, 897  
- **Representative key differences**  
  1. Gold: `fastestLapTime IS NOT NULL`; Predicted: `fastest_lap_time = (SELECT MIN(...))`.  
  2. Gold: `WHERE T2.id = 5`; Predicted: `WHERE T1.id = 5`.  

**Shared mistake** – The predicate is applied to the wrong column or with an overly restrictive condition (e.g., equality to a global minimum). This changes the filter logic, often discarding valid rows that the gold query would keep.  

**Error type:** **Model error**  

---

### 2.4 Other Issues *(singleton patterns merged)*  

| Pattern | Question ID | Representative key difference |
|---------|-------------|--------------------------------|
| `date_or_time_logic_error` | 938 | Gold extracts year via `strftime('%Y', OpenDate)`; Predicted compares full dates. |
| `output_shape_mismatch` | 975 | Gold selects `name`; Predicted also selects `points`. |
| `group_by_or_having_mismatch` | 962 | Gold groups by `releaseDate`; Predicted selects `language` with `AVG` but no `GROUP BY`. |

**Shared mistake** – Each singleton reflects a distinct logical slip: (1) mismatched date granularity, (2) projecting an extra column, or (3) missing/incorrect `GROUP BY` causing a binder error. All are **Model errors**.

---

## 3. Pattern Totals  

| Pattern | Count | Question IDs |
|---------|-------|--------------|
| aggregation_or_order_logic | 2 | 924, 907 |
| wrong_join_or_table | 3 | 915, 889, 961 |
| predicate_or_filter_error | 2 | 958, 897 |
| date_or_time_logic_error | 1 | 938 |
| output_shape_mismatch | 1 | 975 |
| group_by_or_having_mismatch | 1 | 962 |
| syntax_error | 0 | – |
| missing_column | 0 | – |
| type_mismatch | 0 | – |
| incorrect_alias | 0 | – |
| duplicate_rows | 0 | – |

*The table lists all 11 catalog patterns, showing zero counts for those not observed in the current batch.*

---

## 4. TL;DR  

- The model most frequently mishandles **joins** (3 cases) and **aggregation logic** (2 cases).  
- Errors are consistently **model‑generated**; no evaluation‑framework faults were identified.  
- Singleton issues (date handling, output shape, missing GROUP BY) highlight additional edge‑case weaknesses.  
- Overall accuracy (≈43 %) suggests substantial room for improvement in logical reasoning about predicates, joins, and aggregation semantics.  