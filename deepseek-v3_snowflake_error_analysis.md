# 📊 Staff Evaluation Report  

## 1. Summary  

| Metric | Value |
|--------|-------|
| **experiment_id** | `2025-11-06_18-21-47_sharp_mccarthy` |
| **total** | 100 |
| **executed** | 84 |
| **correct** | 31 |
| **accuracy** | 0.3690 (≈ 36.9 %) |

**Experiment configuration (`exp_config`)**  

| Parameter | Value |
|-----------|-------|
| `csv_path` | `results/2025-11-06_18-21-47_sharp_mccarthy/all_results.csv` |
| `sample_size` | 20 |
| `filter_by_model` | `deepseek-v3` |
| `filter_by_dialect` | `snowflake` |

*All fields were supplied; none are missing.*

---

## 2. Failure Patterns  

### 2.1. **unsupported_dialect_feature**  *(2 occurrences)*  

- **Question IDs:** 3449, 3388  
- **Representative key‑differences**  
  1. `DIVIDE` function used → not in Snowflake (q3449)  
  2. `DIVIDE(... )` replaces `COUNT(DISTINCT …) * 100 / …` (q3388)  

**Shared mistake:** The model generates calls to a non‑existent `DIVIDE` function (or other dialect‑specific constructs) that Snowflake cannot compile. This is a pure **Model error**.

---

### 2.2. **predicate_or_filter_error**  *(3 occurrences)*  

- **Question IDs:** 3419, 3410, 3378  
- **Representative key‑differences**  
  1. Wrong case/value for `FUNDING_TYPE` and uses `COUNT(*)` instead of `COUNT(School)` (q3419)  
  2. Combines first‑name and last‑name into a single string (`'Kacey Gibson'`) (q3410)  
  3. Filters on `SETS.ID` instead of `SET_TRANSLATIONS.ID` and switches join type (q3378)  

**Shared mistake:** The model mis‑specifies predicates—either by using the wrong column, wrong literal/value, or wrong case—leading to logically incorrect filtering. All are **Model errors**.

---

### 2.3. **wrong_join_or_table**  *(4 occurrences)*  

- **Question IDs:** 3405, 3366, 3442, 3443  
- **Representative key‑differences**  
  1. References `SCHOOLS.ENROLL12` (non‑existent) and drops required join to `SATSCORES` (q3405)  
  2. Adds an unnecessary `CONNECTED` join, altering the relationship chain (q3366)  
  3. Joins `SETS` then `SET_TRANSLATIONS` via `SET_CODE` instead of filtering directly (q3442)  
  4. Joins on mismatched columns (`SETS.CODE = SET_TRANSLATIONS.SET_CODE`) and groups by wrong attribute (q3443)  

**Shared mistake:** The generated SQL either joins the wrong tables, uses incorrect join keys, or omits required joins, thereby changing the relational semantics. All are **Model errors**.

---

### 2.4. **output_shape_mismatch**  *(2 occurrences)*  

- **Question IDs:** 3396, 3370  
- **Representative key‑differences**  
  1. Returns two columns (`ELEMENT, ELEMENT`) instead of one (`ELEMENT`) (q3396)  
  2. Adds extra column `RBC` and drops `DISTINCT`, changing result shape (q3370)  

**Shared mistake:** The projection (SELECT list) does not match the gold query’s column count or distinctness, producing a different output schema. **Model error**.

---

### 2.5. **Other Issues**  *(1 occurrence)*  

- **Question ID:** 3399 – **other** pattern  
- **Key difference:** Quoted identifiers (`"MEMBER"."POSITION"`) become case‑sensitive in Snowflake, causing “invalid identifier” errors.  

**Explanation:** This is a dialect‑specific identifier handling problem that does not fit the main catalog patterns. It is still a **Model error**.

---

## 3. Pattern Totals  

| Pattern                     | Count | Question IDs |
|-----------------------------|-------|--------------|
| **wrong_join_or_table**     | 4     | 3405, 3366, 3442, 3443 |
| **predicate_or_filter_error** | 3   | 3419, 3410, 3378 |
| **unsupported_dialect_feature** | 2 | 3449, 3388 |
| **output_shape_mismatch**   | 2     | 3396, 3370 |
| **other**                   | 1     | 3399 |
| syntax_error                | 0     | – |
| missing_clause              | 0     | – |
| ambiguous_column            | 0     | – |
| incorrect_aggregation       | 0     | – |
| invalid_identifier          | 0     | – |
| type_mismatch               | 0     | – |

*Sorted by descending count.*

---

## 4. TL;DR  

- The model’s **overall accuracy** on the Snowflake‑filtered subset is **≈ 37 %**, indicating substantial room for improvement.  
- The most frequent failure mode is **wrong joins or tables** (4/12 errors), followed by **predicate/filter mistakes** (3/12).  
- **Unsupported dialect features** (use of `DIVIDE`) and **output‑shape mismatches** each appear twice, showing the model still struggles with Snowflake‑specific syntax and result‑set shaping.  
- **No evaluation‑framework errors** were detected; all issues stem from the **model** itself.  

---  

*End of report.*