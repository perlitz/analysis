# Staff Evaluation Report  

## 1. Summary  

| Metric | Value |
|--------|-------|
| **experiment_id** | `2025-11-06_18-21-47_sharp_mccarthy` |
| **total** | 100 |
| **executed** | 81 |
| **correct** | 37 |
| **accuracy** | 0.4567901234567901 |

**exp_config**  

- `csv_path`: `results/2025-11-06_18-21-47_sharp_mccarthy/all_results.csv`  
- `sample_size`: 20  
- `filter_by_model`: `deepseek-coder-33b-instruct`  
- `filter_by_dialect`: `mysql`  

---

## 2. Failure Patterns  

### 2.1 Wrong Join or Table  *(6 occurrences)*  

**Question IDs:** 1855, 1842, 1772, 1862, 1848, 1849  

**Representative key‑differences**  

1. *1855*: Gold joins `foreign_data` and uses `T2.language`; predicted uses `WHERE language='French'` on `cards`.  
2. *1842*: Gold joins `disp` and filters `disp.type='OWNER'`; predicted filters `account.frequency='OWNER'` with no join.  
3. *1772*: Gold includes `INNER JOIN molecule` before `bond`; predicted joins `atom` directly to `bond`.  
4. *1862*: Gold selects `constructors.name` via a join; predicted selects `constructor_id` with no join.  
5. *1848*: Gold filters `set_translations` by `cards.id`; predicted joins `sets` and links via `set_code`.  
6. *1849*: Gold joins `set_translations` for `language`; predicted reads `language` from `sets` alone.  

**Shared mistake** – The model repeatedly omits required joins or references the wrong table/column when a relationship is needed. This leads to unknown‑column errors or logically incorrect result sets because the query never reaches the table that actually stores the requested attribute.  

**Error type:** **Model error**  

---

### 2.2 Output Shape Mismatch *(3 occurrences)*  

**Question IDs:** 1782, 1802, 1776  

**Representative key‑differences**  

1. *1782*: Gold selects `cardKingdomFoilId, cardKingdomId`; predicted adds extra `id` column and uses camel‑case names not in schema.  
2. *1802*: Gold uses `SELECT DISTINCT T3.element`; predicted drops `DISTINCT`, risking duplicate rows.  
3. *1776*: Gold returns only `ID, Admission`; predicted returns `id, sex, birthday, admission` plus an unnecessary filter.  

**Shared mistake** – The model changes the projection (extra columns, missing `DISTINCT`) or adds unnecessary filters, altering the shape of the result set relative to the gold standard.  

**Error type:** **Model error**  

---

### 2.3 Other Issues *(3 singleton patterns merged)*  

| Pattern | Question ID | Brief key‑difference |
|---------|-------------|----------------------|
| **Aggregation or Order Logic** (1811) | 1811 | Gold returns raw `NumTstTakr` rows; predicted adds `SUM(num_tst_takr)` aggregating to a single value. |
| **Unsupported Dialect Feature** (1794) | 1794 | Predicted SQL wrapped in markdown fences (```sql … ```), causing a parsing failure. |
| **Predicate or Filter Error** (1784) | 1784 | Gold filters on `set_translations.id = 5`; predicted filters on `sets.id = 5`. |

All three are **Model errors**; no evaluation‑framework mistakes were observed.

---

## 3. Pattern Totals  

| Pattern                     | Count | Question IDs |
|-----------------------------|-------|--------------|
| wrong_join_or_table         | 6     | 1855, 1842, 1772, 1862, 1848, 1849 |
| output_shape_mismatch       | 3     | 1782, 1802, 1776 |
| aggregation_or_order_logic  | 1     | 1811 |
| unsupported_dialect_feature | 1     | 1794 |
| predicate_or_filter_error   | 1     | 1784 |
| syntax_error                | 0     | – |
| missing_column              | 0     | – |
| type_mismatch               | 0     | – |
| ambiguous_intent            | 0     | – |
| performance_issue           | 0     | – |
| other                       | 0     | – |

*Sorted by descending count.*

---

## 4. TL;DR  

- The dominant failure mode (6/12 cases) is **missing or incorrect joins**, causing unknown‑column errors or wrong result sets.  
- **Output‑shape mismatches** (extra columns, missing `DISTINCT`) appear in a quarter of the failures, indicating the model struggles with precise projection requirements.  
- All observed errors stem from the **model**; no evaluation‑framework errors were detected.  
- Improving the model’s schema awareness (especially foreign‑key relationships) and enforcing strict projection checks should raise accuracy well above the current 45.7 %.  