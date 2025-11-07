## 1. Summary  

| Metric | Value |
|--------|-------|
| **experiment_id** | `2025-11-06_18-21-47_sharp_mccarthy` |
| **total** | 100 |
| **executed** | 84 |
| **correct** | 32 |
| **accuracy** | 0.38095238095238093 |

**exp_config**  

- `csv_path`: `results/2025-11-06_18-21-47_sharp_mccarthy/all_results.csv`  
- `sample_size`: 20  
- `filter_by_model`: `deepseek-coder-33b-instruct`  
- `filter_by_dialect`: `duckdb`  

---

## 2. Failure Patterns  

### 2.1 Wrong Join or Table  *(Model error)*  

**Question IDs:** 3155, 3142, 3072, 3162, 3076, 3148, 3149  

| Example of *key_difference* (≤ 120 chars) |
|-------------------------------------------|
| Gold joins `cards` ↔ `foreign_data`; predicted selects only `cards` and uses `language` without a join. |
| Gold filters on `disp.type = 'OWNER'`; predicted filters on `account.frequency = 'OWNER'` and never joins `disp`. |
| Gold path: `atom → molecule → bond`; predicted path skips `molecule`. |
| Gold selects `constructors.name`; predicted returns `constructor_id` and never joins `constructors`. |
| Gold joins `Patient → Laboratory`; predicted joins `Patient → Examination` and references non‑existent `examination.rbc`. |
| Gold links `cards.id` → `set_translations.id`; predicted joins via `set_code` instead. |
| Gold groups by release date and counts `language`; predicted uses `AVG(id)` and missing join, plus illegal `MAX(COUNT(...))`. |

**Shared mistake:** The model repeatedly omits a required table or uses the wrong join path, leading to missing columns, binder errors, or completely different result sets.  

---

### 2.2 Predicate or Filter Error  *(Model error)*  

**Question IDs:** 3125, 3145, 3084  

| Example of *key_difference* (≤ 120 chars) |
|-------------------------------------------|
| Gold: `FundingType = 'Directly funded'`; predicted: `funding_type = 'Directly Funded'`. |
| Gold: `STRFTIME('%Y', drivers.dob) = '1971'`; predicted: `drivers.dob = '1971-01-01'`. |
| Gold: `set_translations.id = 5`; predicted: `sets.id = 5`. |

**Shared mistake:** The predicate is syntactically correct but semantically wrong—either a case‑sensitive string mismatch, an incorrect column (full date vs. year), or filtering on the wrong table/column.  

---

### 2.3 Other Issues  *(Mixed)*  

| Question ID | Pattern (original) | Error type |
|-------------|--------------------|------------|
| 3111 | aggregation_or_order_logic | Model error |
| 3082 | output_shape_mismatch | Model error |
| 3102 | other | **Evaluation framework error** |

*Brief notes*  

- **3111** – Model added an unnecessary `SUM` aggregation where the gold query simply returned the raw column.  
- **3082** – Model projected an extra `id` column that the task never asked for, changing the output shape.  
- **3102** – The model’s SQL is semantically identical to the gold query; the mismatch is likely a bug in the evaluation harness rather than a model fault.  

---

## 3. Pattern Totals  

| Pattern                     | Count | Question IDs |
|-----------------------------|-------|--------------|
| wrong_join_or_table         | 7 | 3155, 3142, 3072, 3162, 3076, 3148, 3149 |
| predicate_or_filter_error   | 3 | 3125, 3145, 3084 |
| aggregation_or_order_logic  | 1 | 3111 |
| output_shape_mismatch       | 1 | 3082 |
| other                       | 1 | 3102 |
| syntax_error                | 0 | – |
| missing_column              | 0 | – |
| type_mismatch               | 0 | – |
| duplicate_column            | 0 | – |
| limit_offset_error          | 0 | – |
| ordering_error              | 0 | – |

*Sorted by descending count.*  

---

## 4. TL;DR  

- The model’s biggest weakness is **missing or incorrect joins** (7 out of 13 errors), causing binder failures or wrong result sets.  
- **Predicate/filter mismatches** (3 errors) stem from case‑sensitivity, wrong column selection, or improper date handling.  
- Only **one** error (question 3102) appears to be an **evaluation‑framework mistake**; the rest are genuine model faults.  
- Minor issues include unnecessary aggregation and extra output columns, but they are far less frequent than join‑related problems.  

---  