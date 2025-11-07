## 1. Summary  

| Item | Value |
|------|-------|
| **experiment_id** | `2025-11-06_18-21-47_sharp_mccarthy` |
| **total** | 100 |
| **executed** | 71 |
| **correct** | 23 |
| **accuracy** | 0.3239 |
| **csv_path** | `results/2025-11-06_18-21-47_sharp_mccarthy/all_results.csv` |
| **sample_size** | 20 |
| **filter_by_model** | `deepseek-coder-33b-instruct` |
| **filter_by_dialect** | `bigquery` |

*All fields are taken directly from the supplied experiment metadata; any missing field would be reported as “not provided”.*  

---

## 2. Failure Patterns  

### 2.1 Wrong Join or Table  *(Model error)*  

**Question IDs:** 1068, 1055, 985, 1015, 1058, 1075, 1061, 997  

**Representative key differences**  
- `1068`: gold uses `foreign_data.language`; predicted selects `language` from `cards`.  
- `1055`: gold joins `disp` and filters `disp.type='OWNER'`; predicted filters `account.frequency='OWNER'`.  
- `985`: gold joins `atom → molecule → bond`; predicted joins only `atom → bond`.  
- `1015`: gold joins via `connected` table and uses `DISTINCT`; predicted joins `atom` directly to `bond`.  

**Shared mistake** – The model repeatedly omits required joins or joins the wrong tables/columns, producing queries that reference columns unavailable in the current FROM‑clause. This leads to “Unrecognized name” or logically incorrect result sets.

---

### 2.2 Predicate or Filter Error  *(Model error)*  

**Question IDs:** 1038, 995  

**Representative key differences**  
- `1038`: gold filter `FundingType = 'Directly funded'`; predicted uses `'Directly Funded'`.  
- `995`: gold (and predicted) use camelCase column names that do **not** exist; correct schema uses snake_case (`card_kingdom_id`).  

**Shared mistake** – The model either mismatches literal values (case‑sensitivity) or references column names that differ from the schema, causing filter predicates to fail or return empty results.

---

### 2.3 Output Shape Mismatch  *(Model error)*  

**Question IDs:** 1024, 989  

**Representative key differences**  
- `1024`: gold `SELECT NumTstTakr` (row‑wise); predicted `SELECT SUM(num_tst_takr)` (single scalar).  
- `989`: gold `SELECT DISTINCT ID, Admission`; predicted returns extra columns (`sex`, `birthday`, `rbc`).  

**Shared mistake** – The model changes the cardinality or column list of the result, violating the expected output shape required by the task.

---

### 2.4 Other Issues  

| Question ID | Pattern | Explanation |
|-------------|---------|-------------|
| 1007 | Unsupported Dialect Feature | Query wrapped in markdown fences and backticks, which BigQuery cannot parse. |
| 1062 | Schema Backend Mismatch *(Evaluation framework error)* | Uses column `releaseDate` instead of the schema‑defined `release_date`, causing an execution error unrelated to model reasoning. |

These singleton cases do not fit the three dominant patterns and are therefore grouped under “Other Issues”.

---

## 3. Pattern Totals  

| Pattern | Count | Question IDs |
|---------|-------|--------------|
| **wrong_join_or_table** | 8 | 1068, 1055, 985, 1015, 1058, 1075, 1061, 997 |
| **predicate_or_filter_error** | 2 | 1038, 995 |
| **output_shape_mismatch** | 2 | 1024, 989 |
| **unsupported_dialect_feature** | 1 | 1007 |
| **schema_backend_mismatch** | 1 | 1062 |
| missing_column_error | 0 | – |
| syntax_error | 0 | – |
| type_mismatch | 0 | – |
| ambiguous_reference | 0 | – |
| missing_table | 0 | – |
| other | 0 | – |

*The table lists all 11 catalog patterns, showing zero for those not observed in the current sample.*

---

## 4. TL;DR  

- The model’s biggest weakness is **missing or incorrect joins** (8 out of 14 errors), leading to column‑not‑found and logical‑result problems.  
- **Predicate/filter mismatches** (case‑sensitivity and wrong column names) appear in 2 cases, showing a need for stricter schema awareness.  
- **Output shape violations** also occur twice, indicating the model sometimes aggregates or adds columns when the task expects raw rows.  
- Only **one evaluation‑framework error** was detected (`schema_backend_mismatch`), so the majority of failures stem from the model itself.  
- Improving schema‑driven validation and join‑logic reasoning should raise the current accuracy of ~32 % toward a more usable level.