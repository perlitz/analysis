# Staff Evaluation Report  

## 1. Summary  

| Metric | Value |
|--------|-------|
| **experiment_id** | `2025-11-06_18-21-47_sharp_mccarthy` (derived from `csv_path`) |
| **total** | 100 |
| **executed** | 44 |
| **correct** | 16 |
| **accuracy** | 0.3636 |

**Experiment configuration (`exp_config`)**  

- `csv_path`: `results/2025-11-06_18-21-47_sharp_mccarthy/all_results.csv`  
- `sample_size`: 20  
- `filter_by_model`: `llama-3-1-8b-instruct`  
- `filter_by_dialect`: `duckdb`  

> *All fields are taken directly from the supplied metadata; no field was missing.*

---

## 2. Failure Patterns  

### 2.1 Wrong Join or Table  *(6 occurrences)*  

**Question IDs:** 2055, 2016, 1972, 2002, 2045, 2049  

**Representative key‑differences** (≤ 120 chars)  

- 2055: uses `T1.language` instead of joining `foreign_data` for `language`.  
- 2016: selects only from `frpm`; never joins `schools` to filter admin name.  
- 1972: joins unrelated `connected` table and omits `bond_type = '-'`.  
- 2002: joins on non‑existent `atom.atom_id2` and adds extra self‑join.  
- 2045: no join between `drivers` and `results`; uses two independent SELECTs.  
- 2049: omits join between `sets` and `set_translations`; aggregates wrong column.  

**Shared mistake** – The model repeatedly omitted required joins or referenced columns that belong to a different table, leading to binder or logical errors. In many cases the query also used `QUALIFY` where a `WHERE` clause was appropriate, compounding the problem.  

**Error type:** **Model error**  

---

### 2.2 Unsupported Dialect Feature  *(5 occurrences)*  

**Question IDs:** 2025, 2042, 2011, 2005, 1976  

**Representative key‑differences**  

- 2025: inserts `QUALIFY` before `WHERE`; `QUALIFY` is not DuckDB syntax.  
- 2042: uses `QUALIFY LIST_VALUE(...)`, both unsupported in DuckDB.  
- 2011: `QUALIFY ANY (...)` – non‑DuckDB construct, also missing joins.  
- 2005: `QUALIFY T2.major_name = 'Business'` without a window function.  
- 1976: applies `SUBSTR` to a TIMESTAMP column (unsupported) and joins unrelated table.  

**Shared mistake** – The model generated SQL that relies on Snowflake‑style clauses (`QUALIFY`, `LIST_VALUE`, `ANY`) or functions not available in DuckDB, causing parser or binder failures.  

**Error type:** **Model error**  

---

### 2.3 Aggregation or Order Logic  *(2 occurrences)*  

**Question IDs:** 1994, 2003  

**Representative key‑differences**  

- 1994: uses `SUM(CASE …)` instead of `COUNT(DISTINCT …)` for the numerator.  
- 2003: replaces the required `FavoriteCount` column with `COUNT(T2.favorite_count)`.  

**Shared mistake** – The model altered the aggregation semantics, either by counting the wrong rows or by aggregating a column that should have been returned raw, leading to mismatched result shapes and incorrect numbers.  

**Error type:** **Model error**  

---

### 2.4 Output Shape Mismatch  *(3 occurrences)*  

**Question IDs:** 1982, 1990, 2048  

**Representative key‑differences**  

- 1982: returns only `T1.id` (single column) instead of two‑column result.  
- 1990: selects ambiguous `name` (both tables have it) rather than `t2.name`.  
- 2048: projects `T2.language` from `sets`, a column that does not exist there.  

**Shared mistake** – The model either omitted required columns, selected ambiguous/unqualified columns, or referenced non‑existent columns, producing a result set that does not match the gold schema.  

**Error type:** **Model error**  

---

### 2.5 Other Issues *(1 occurrence)*  

**Pattern:** Predicate or Filter Error  

- **Question ID:** 1984 – filters on `sets.id = 5` instead of `set_translations.id = 5` and drops the `GROUP BY`.  

This singleton is grouped under “Other Issues” because it does not reach the 2‑occurrence threshold.  

**Error type:** **Model error**  

---

## 3. Pattern Totals  

| Pattern                         | Count | Question IDs |
|--------------------------------|-------|--------------|
| wrong_join_or_table            | 6     | 2055, 2016, 1972, 2002, 2045, 2049 |
| unsupported_dialect_feature    | 5     | 2025, 2042, 2011, 2005, 1976 |
| output_shape_mismatch          | 3     | 1982, 1990, 2048 |
| aggregation_or_order_logic     | 2     | 1994, 2003 |
| predicate_or_filter_error      | 1     | 1984 |
| **Other catalog patterns (not observed)** | 0 | – |
| – syntax_error                 | 0     | – |
| – semantic_error               | 0     | – |
| – missing_table                | 0     | – |
| – missing_column               | 0     | – |
| – type_mismatch                | 0     | – |

*Only the five patterns that appear in the judgments are listed with non‑zero counts; the remaining six catalog patterns are shown with a count of zero.*

---

## 4. TL;DR  

- The model struggled most with **wrong joins / missing tables** (6 cases) and **unsupported DuckDB features** (5 cases).  
- Errors often involved using `QUALIFY` where DuckDB expects `WHERE`, and referencing columns that belong to tables not joined in the query.  
- Aggregation logic and output‑shape mismatches also contributed to failures, but no **evaluation‑framework** errors were detected.  
- Overall accuracy was low (≈ 36 %), indicating that the model needs stronger awareness of the target SQL dialect (DuckDB) and of join requirements.  