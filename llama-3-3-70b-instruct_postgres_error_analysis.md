# Staff Evaluation Report  

## 1. Summary  

| Metric | Value |
|--------|-------|
| **experiment_id** | `2025-11-06_18-21-47_sharp_mccarthy` |
| **total** | 100 |
| **executed** | 90 |
| **correct** | 38 |
| **accuracy** | 0.4222 |

**Experiment configuration (`exp_config`)**  

- `csv_path`: `results/2025-11-06_18-21-47_sharp_mccarthy/all_results.csv`  
- `sample_size`: 20  
- `filter_by_model`: `llama-3-3-70b-instruct`  
- `filter_by_dialect`: `postgres`  

*All fields were supplied in the metadata; none are missing.*

---

## 2. Failure Patterns  

### 2.1. **Predicate or Filter Error**  *(2 occurrences)*  

- **Question IDs**: 2125, 2084  
- **Representative key differences**  
  1. `Gold: FundingType = 'Directly funded' … COUNT(School)` vs. `Predicted: funding_type = 'Directly Funded' … COUNT(*)`  
  2. `Gold: WHERE T2.id = 5` vs. `Predicted: WHERE t1.id = 5` (wrong table)  

**Shared mistake** – The model applied an incorrect predicate: either a case‑sensitive string literal mismatch or a filter on the wrong table/column. Both lead to a result set that does not satisfy the gold specification.  

**Error type**: **Model error**  

---

### 2.2. **Aggregation or Order Logic**  *(2 occurrences)*  

- **Question IDs**: 2111, 2149  
- **Representative key differences**  
  1. `Gold: SELECT T1.NumTstTakr …` vs. `Predicted: SELECT SUM(T1.num_tst_takr) …` (unwanted SUM)  
  2. `Gold: nested GROUP BY, ORDER BY, LIMIT …` vs. `Predicted: MAX(COUNT(...))` (illegal nested aggregate)  

**Shared mistake** – The model introduced or mis‑nested aggregation functions (e.g., adding `SUM`, using `MAX(COUNT(...))`) and omitted required ordering/grouping clauses, producing either a scalar where a row‑wise value is needed or a syntactically invalid statement.  

**Error type**: **Model error**  

---

### 2.3. **Output Shape Mismatch**  *(3 occurrences)*  

- **Question IDs**: 2094, 2082, 2102  
- **Representative key differences**  
  1. `Gold: single scalar COUNT(DISTINCT …)` vs. `Predicted: GROUP BY molecule_id …` (multiple rows)  
  2. `Gold: SELECT cardKingdomFoilId, cardKingdomId …` vs. `Predicted: SELECT id …` (missing column)  
  3. `Gold: SELECT DISTINCT T3.element …` vs. `Predicted: SELECT T1.element …` (DISTINCT omitted)  

**Shared mistake** – The model altered the projection or grouping structure, either dropping required columns, omitting `DISTINCT`, or adding a `GROUP BY` that changes the cardinality of the result.  

**Error type**: **Model error**  

---

### 2.4. **Wrong Join or Table**  *(2 occurrences)*  

- **Question IDs**: 2072, 2148  
- **Representative key differences**  
  1. `Gold: atom → molecule → bond` vs. `Predicted: atom → bond` (missing molecule join)  
  2. `Gold: filter set_translations by id` vs. `Predicted: join sets on set_code` (unnecessary join, wrong condition)  

**Shared mistake** – The model either omitted a required intermediate join or introduced an extra join with an incorrect join condition, leading to an incorrect relational path and therefore wrong rows.  

**Error type**: **Model error**  

---

### 2.5. **Other Issues**  *(1 occurrence – merged singleton)*  

- **Question ID**: 2076  
- **Key difference** – `Gold` uses SQLite‑compatible `STRFTIME` logic; `Predicted` uses PostgreSQL‑only `EXTRACT`/`AGE` and drops the required `ID` column.  

**Explanation** – The model generated SQL that relies on functions unavailable in the target dialect and omitted a mandatory column, a combination of dialect mismatch and projection error.  

**Error type**: **Model error**  

---

## 3. Pattern Totals  

| Pattern                     | Count | Question IDs |
|-----------------------------|-------|--------------|
| output_shape_mismatch       | 3     | 2094, 2082, 2102 |
| predicate_or_filter_error   | 2     | 2125, 2084 |
| aggregation_or_order_logic  | 2     | 2111, 2149 |
| wrong_join_or_table         | 2     | 2072, 2148 |
| unsupported_dialect_feature | 1     | 2076 |
| syntax_error                | 0     | N/A |
| missing_column              | 0     | N/A |
| incorrect_alias             | 0     | N/A |
| type_mismatch               | 0     | N/A |
| performance_issue           | 0     | N/A |
| other                       | 0     | N/A |

*The table lists all eleven catalog patterns; six of them had zero occurrences in this sample.*

---

## 4. TL;DR  

- The model achieved **42.2 % accuracy** (38/90 correct) on the filtered PostgreSQL subset.  
- The most common failure mode was **output‑shape mismatches** (3 cases), where columns or grouping were altered.  
- All identified problems stem from **model errors**; no evaluation‑framework errors were detected.  
- Errors fall into four clear categories: predicate/filter mistakes, wrong aggregation/order logic, incorrect joins, and output‑shape issues, plus a single dialect‑compatibility slip.  

---  

*End of report.*