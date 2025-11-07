# 📊 Staff Evaluation Report  

## 1. Summary  

| Item | Value |
|------|-------|
| **experiment_id** | not provided |
| **total** | 100 |
| **executed** | 63 |
| **correct** | 19 |
| **accuracy** | 0.3016 (≈ 30 %) |
| **exp_config.csv_path** | `results/2025-11-06_18-21-47_sharp_mccarthy/all_results.csv` |
| **exp_config.sample_size** | 20 |
| **exp_config.filter_by_model** | `llama-3-1-8b-instruct` |
| **exp_config.filter_by_dialect** | `bigquery` |

The experiment ran 63 out of the 100 sampled questions. Only 19 predictions matched the gold‑standard SQL, yielding an accuracy of roughly **30 %**. All mismatches were flagged as **model errors** by the judges.

---

## 2. Failure Patterns  

### 1️⃣ unsupported_dialect_feature  *(Model error)*  

- **Question IDs:** 1568, 1507, 1489  
- **Representative key differences**  
  - `DIVIDE(COUNT(...), COUNT(...))` – DIVIDE is not a BigQuery function.  
  - `TIMESTAMP_SUB(CURRENT_TIMESTAMP, INTERVAL 50 YEAR)` – YEAR interval not supported.  
- **Shared mistake:** The model generated SQL that relies on functions or interval specifications that do **not exist** in the BigQuery dialect, causing runtime “function‑not‑found” or syntax errors.  

### 2️⃣ predicate_or_filter_error  *(Model error)*  

- **Question IDs:** 1538, 1497  
- **Representative key differences**  
  - `funding_type = 'Directly Funded'` vs. required `'Directly funded'` (case mismatch).  
  - `WHERE T1.id = 5` instead of `WHERE T2.id = 5` (filtering the wrong table).  
- **Shared mistake:** The predicate logic is either case‑sensitive or applied to the wrong column/table, which changes the filtered row set and yields incorrect results.  

### 3️⃣ wrong_join_or_table  *(Model error)*  

- **Question IDs:** 1555, 1529, 1485, 1515, 1575  
- **Representative key differences**  
  - Joins `disp` → `district` on a non‑existent `d.district_id`.  
  - Uses only `frpm` table, omitting the required `schools` join.  
  - Adds extra joins to `connected` and duplicates `bond` tables.  
- **Shared mistake:** The model selects the wrong tables or joins on columns that do not exist, breaking the relational path defined in the gold query and often dropping essential filters.  

### 4️⃣ aggregation_or_order_logic  *(Model error)*  

- **Question IDs:** 1524, 1562, 1516  
- **Representative key differences**  
  - `SELECT COUNT(num_tst_takr)` instead of returning raw `NumTstTakr`.  
  - `MAX(COUNT(language))` – an illegal aggregation‑of‑aggregation in BigQuery.  
  - `COUNT(T2.favorite_count)` replaces the required `FavoriteCount` column.  
- **Shared mistake:** The model mis‑applies aggregation functions (wrong metric, extra nesting, or missing `DISTINCT`), leading to incorrect row counts or ordering.  

### 5️⃣ output_shape_mismatch  *(Model error)*  

- **Question IDs:** 1558, 1561  
- **Representative key differences**  
  - `SELECT driver_id` vs. gold `SELECT driverId`.  
  - `SELECT T2.language` from `sets` (column does not exist) instead of `set_translations`.  
- **Shared mistake:** Column names or source tables are mismatched, so the result schema does not line up with the expected output even if the data values happen to be similar.  

### Other Issues  

- **Pattern:** `limit_or_pagination_error` (singleton)  
  - **Question ID:** 1495  
  - **Key difference:** Missing `LIMIT 3` clause and inclusion of an unnecessary self‑join.  
  - **Explanation:** The model fails to enforce the required result‑set size, returning more rows than specified.  

---

## 3. Pattern Totals  

| Pattern                     | Count | Question IDs |
|-----------------------------|-------|--------------|
| unsupported_dialect_feature | 3 | 1568, 1507, 1489 |
| predicate_or_filter_error   | 2 | 1538, 1497 |
| wrong_join_or_table          | 5 | 1555, 1529, 1485, 1515, 1575 |
| aggregation_or_order_logic   | 3 | 1524, 1562, 1516 |
| limit_or_pagination_error    | 1 | 1495 |
| output_shape_mismatch        | 2 | 1558, 1561 |
| syntax_error                 | 0 | – |
| missing_column               | 0 | – |
| type_mismatch                | 0 | – |
| duplicate_rows               | 0 | – |
| unknown_pattern              | 0 | – |

*The table lists all 11 catalog patterns; those not observed are shown with a count of 0.*

---

## 4. TL;DR  

- The model’s **accuracy is only ~30 %**, with **all failures classified as model errors**—no evaluation‑framework bugs were detected.  
- The most common flaw is **wrong joins/tables** (5 occurrences), indicating the model struggles with relational path reasoning.  
- **Dialect‑specific syntax** (unsupported functions or intervals) appears in 3 cases, showing a need for tighter BigQuery grounding.  
- Predicate mismatches, aggregation misuse, and output‑shape mismatches each affect multiple queries, suggesting systematic issues in case‑sensitivity, aggregation logic, and column naming.  
- Only a single pagination error was observed; overall, the model frequently omits required joins or uses non‑existent columns/functions, which drives the low accuracy.  