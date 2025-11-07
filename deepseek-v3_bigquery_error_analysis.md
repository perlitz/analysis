# Staff Evaluation Report  

## 1. Summary  

| Item | Value |
|------|-------|
| **experiment_id** | `2025-11-06_18-21-47_sharp_mccarthy` (derived from `csv_path`) |
| **total** | 100 |
| **executed** | 86 |
| **correct** | 30 |
| **accuracy** | 0.3488 (≈ 34.9 %) |
| **exp_config.csv_path** | `results/2025-11-06_18-21-47_sharp_mccarthy/all_results.csv` |
| **exp_config.sample_size** | 20 |
| **exp_config.filter_by_model** | `deepseek-v3` |
| **exp_config.filter_by_dialect** | `bigquery` |

*All fields are taken directly from the supplied metadata; none are missing.*

---

## 2. Failure Patterns  

### 2.1. **unsupported_dialect_feature**  *(2 occurrences)*  

- **Question IDs:** 1955, 1894  
- **Representative key differences**  
  1. `Gold uses CAST(... * 100 / COUNT(...))` – predicted uses `DIVIDE(...)` (BigQuery has no `DIVIDE`).  
  2. `Gold: standard arithmetic` – predicted: `DIVIDE(COUNTIF(...), COUNTIF(...))`.  
- **Shared mistake:** The model inserts the `DIVIDE` function, which is not part of the BigQuery function set, causing a runtime “function‑not‑found” error.  
- **Error type:** **Model error**  

### 2.2. **output_shape_mismatch**  *(3 occurrences)*  

- **Question IDs:** 1942, 1945, 1876  
- **Representative key differences**  
  1. `Gold: SELECT account_id` – predicted adds `district_id, frequency, date`.  
  2. `Gold: driverId, code, STRFTIME('%Y', dob)` – predicted returns `driver_id, code, EXTRACT(YEAR FROM dob)`.  
  3. `Gold: SELECT DISTINCT ID, Admission` – predicted returns extra columns (`sex, rbc, STRUCT`).  
- **Shared mistake:** The generated SQL returns a different column set (extra columns, different naming conventions, or different data‑type wrappers) than the reference, breaking downstream expectations.  
- **Error type:** **Model error**  

### 2.3. **aggregation_or_order_logic**  *(2 occurrences)*  

- **Question IDs:** 1911, 1962  
- **Representative key differences**  
  1. `Gold: SELECT NumTstTakr …` – predicted wraps it in `SUM(num_tst_takr)`.  
  2. `Gold: ORDER BY points DESC LIMIT 1` – predicted adds `SUM(points) … GROUP BY name`.  
- **Shared mistake:** The model introduces unnecessary aggregation (`SUM`) or changes the ordering logic, turning a row‑wise selection into a grouped summary that does not match the intended result.  
- **Error type:** **Model error**  

### 2.4. **wrong_join_or_table**  *(5 occurrences)*  

- **Question IDs:** 1872, 1902, 1948, 1949, 1884  
- **Representative key differences**  
  1. `Gold: atom → molecule → bond` – predicted: `bond → connected → atom` (missing molecule).  
  2. `Gold: join on c.atom_id = a.atom_id` – predicted adds `OR c.atom_id2 = a.atom_id`.  
  3. `Gold: join set_translations directly to cards` – predicted joins via `sets` using `set_code`.  
- **Shared mistake:** The model either omits a required table, adds an extra join condition, or follows an incorrect join path, leading to wrong relational semantics or missing columns.  
- **Error type:** **Model error**  

### 2.5. **Other Issues**  *(2 singleton patterns merged)*  

| Pattern | Question ID | Key Difference (≤120 chars) |
|---------|-------------|------------------------------|
| **date_or_time_logic_error** | 1925 | Gold uses `strftime('%Y', OpenDate)`; predicted parses full date with `PARSE_DATE` and compares whole dates. |
| **predicate_or_filter_error** | 1884 | Gold filters on `st.id = 5` and groups; predicted filters on `s.id = 5` and omits `GROUP BY`. |

Both singletons are **Model errors**; they do not meet the “≥ 2 occurrences” threshold for a dedicated subsection, so they are grouped here.

---

## 3. Pattern Totals  

| Pattern                     | Count | Question IDs |
|-----------------------------|-------|--------------|
| wrong_join_or_table         | 5     | 1872, 1902, 1948, 1949, 1884 |
| output_shape_mismatch       | 3     | 1942, 1945, 1876 |
| unsupported_dialect_feature| 2     | 1955, 1894 |
| aggregation_or_order_logic  | 2     | 1911, 1962 |
| date_or_time_logic_error    | 1     | 1925 |
| predicate_or_filter_error   | 1     | 1884 |
| syntax_error                | 0     | – |
| missing_column              | 0     | – |
| type_mismatch               | 0     | – |
| performance_issue           | 0     | – |
| other                       | 0     | – |

*The table lists all 11 catalog patterns, showing zero for those not observed.*

---

## 4. TL;DR  

- The model’s **accuracy** on this BigQuery‑filtered run is only **≈ 35 %**, with 30 correct out of 86 executed queries.  
- The most frequent failure mode is **wrong join logic** (5 cases), followed by **output‑shape mismatches** (3 cases).  
- **Unsupported dialect features** (use of `DIVIDE`) and **incorrect aggregation** each appear twice, indicating systematic gaps in dialect awareness and aggregation handling.  
- **No evaluation‑framework errors** were detected; all mis‑behaviours stem from the model itself.  

---  

*End of report.*