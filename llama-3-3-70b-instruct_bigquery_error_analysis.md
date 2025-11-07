# Staff Evaluation Report  

## 1. Summary  

| Item | Value |
|------|-------|
| **experiment_id** | `2025-11-06_18-21-47_sharp_mccarthy` |
| **total** | 100 |
| **executed** | 83 |
| **correct** | 29 |
| **accuracy** | 0.3494 |
| **csv_path** | `results/2025-11-06_18-21-47_sharp_mccarthy/all_results.csv` |
| **sample_size** | 20 |
| **filter_by_model** | `llama-3-3-70b-instruct` |
| **filter_by_dialect** | `bigquery` |

*All fields are taken directly from the supplied experiment metadata; any missing field would be reported as “not provided”.*  

---

## 2. Failure Patterns  

### 2.1. **aggregation_or_order_logic**  *(3 occurrences)*  

- **Question IDs:** 2925, 2911, 2949  
- **Representative key differences**  
  1. *2925:* Gold uses `COUNT(School)` with `FundingType='Directly funded'`; predicted uses `COUNT(cds_code)` and a different funding string.  
  2. *2911:* Gold returns raw `NumTstTakr`; predicted adds `SUM(...) AS total_test_takers`.  
  3. *2949:* Predicted nests `AVG(COUNT(...))` (aggregation‑of‑aggregation) – illegal in BigQuery.  

**Shared mistake:** The model consistently mis‑applies aggregation functions or grouping logic, either by counting the wrong column, adding an extra `SUM/AVG` layer, or using an unsupported nested‑aggregate construct. All errors are **Model error**.  

---

### 2.2. **wrong_join_or_table**  *(5 occurrences)*  

- **Question IDs:** 2942, 2894, 2962, 2948, 2884  
- **Representative key differences**  
  1. *2942:* Gold joins `district → account → disp` and filters `disp.type='OWNER'`; predicted skips `disp` and filters `account.frequency='OWNER'`.  
  2. *2894:* Gold qualifies `molecule_id` columns; predicted leaves `molecule_id` ambiguous after a left join.  
  3. *2962:* Gold joins `constructorStandings` directly; predicted joins `constructor_results` and aggregates points.  
  4. *2948:* Gold filters `set_translations.id`; predicted joins `sets` and filters on `set_code`.  
  5. *2884:* Gold joins on `T1.code = T2.setCode` and filters `T2.id = 5`; predicted joins on `set_code` and filters `T1.id = 5`.  

**Shared mistake:** The model either omits required tables, joins on the wrong columns, or adds unnecessary joins, leading to incorrect result sets. All are **Model error**.  

---

### 2.3. **output_shape_mismatch**  *(4 occurrences)*  

- **Question IDs:** 2882, 2902, 2945, 2876  
- **Representative key differences**  
  1. *2882:* Gold selects `cardKingdomFoilId, cardKingdomId`; predicted selects only `id`.  
  2. *2902:* Gold uses `SELECT DISTINCT`; predicted drops `DISTINCT`, allowing duplicates.  
  3. *2945:* Gold column name `driverId`; predicted returns `driver_id`.  
  4. *2876:* Gold returns `ID, Admission`; predicted returns only `admission`.  

**Shared mistake:** The model’s projection does not match the gold schema—either by omitting columns, missing `DISTINCT`, or using different column names—so the output shape diverges. All are **Model error**.  

---

### 2.4. **Other Issues**  

- **unsupported_dialect_feature** *(1 occurrence)* – Question 2955  
  - *Key difference:* Gold uses `CAST(SUM(...)/COUNT)`; predicted uses `DIVIDE(...)`, a function absent in BigQuery.  
  - **Error type:** Model error.  

Because this pattern appears only once, it is grouped under “Other Issues” rather than a dedicated subsection.  

---

## 3. Pattern Totals  

| Pattern                     | Count | Question IDs |
|-----------------------------|-------|--------------|
| aggregation_or_order_logic  | 3     | 2925, 2911, 2949 |
| wrong_join_or_table         | 5     | 2942, 2894, 2962, 2948, 2884 |
| output_shape_mismatch       | 4     | 2882, 2902, 2945, 2876 |
| unsupported_dialect_feature | 1     | 2955 |
| missing_column              | 0     | – |
| syntax_error                | 0     | – |
| ambiguous_column            | 0     | – |
| type_mismatch               | 0     | – |
| performance_issue           | 0     | – |
| security_issue              | 0     | – |
| other                       | 0     | – |

*The table lists all 11 catalog patterns, showing zero for those not observed.*  

---

## 4. TL;DR  

- The model’s **accuracy** on this BigQuery‑filtered sample is **≈ 35 %** (29/83).  
- The most frequent failure modes are **wrong joins/tables** (5 cases) and **output‑shape mismatches** (4 cases).  
- **Aggregation/order logic** errors (3 cases) often involve incorrect counting or illegal nested aggregates.  
- A single **unsupported dialect feature** error was observed; **no evaluation‑framework errors** were detected.  

*Overall, the dominant issues stem from the model mis‑constructing joins and projections rather than from the evaluation harness itself.*  