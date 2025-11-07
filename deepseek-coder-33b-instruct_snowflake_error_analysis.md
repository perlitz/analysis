# Staff Evaluation Report  

## 1. Summary  

| Metric | Value |
|--------|-------|
| **experiment_id** | `2025-11-06_18-21-47_sharp_mccarthy` |
| **total** | 100 |
| **executed** | 73 |
| **correct** | 26 |
| **accuracy** | 0.3562 |

**Experiment configuration**  

- **csv_path**: `results/2025-11-06_18-21-47_sharp_mccarthy/all_results.csv`  
- **sample_size**: 20  
- **filter_by_model**: `deepseek-coder-33b-instruct`  
- **filter_by_dialect**: `snowflake`  

The model answered 73 out of 100 sampled questions, of which only 26 matched the gold standard, yielding an accuracy of roughly **35.6 %**.

---

## 2. Failure Patterns  

### 2.1 Wrong Join or Table  

- **Question IDs**: 3055, 3042, 2972, 3002, 3045, 3048, 3049  
- **Representative key differences**  
  1. *3055*: Gold joins `CARDS` → `FOREIGN_DATA` for `LANGUAGE`; predicted uses `CARDS.LANGUAGE` (non‑existent).  
  2. *3042*: Gold `JOIN DISP … WHERE DISP.type='OWNER'`; predicted filters `ACCOUNT.FREQUENCY='OWNER'` with no `DISP` join.  
- **Shared mistake**: The model either omits a required table join or joins the wrong table, leading to missing columns or incorrect semantics.  
- **Error type**: **Model error**  

### 2.2 Predicate or Filter Error  

- **Question IDs**: 3025, 2984  
- **Representative key differences**  
  1. *3025*: Gold extracts year via `strftime('%Y', OpenDate)`; predicted uses a full date range `OPEN_DATE BETWEEN …`.  
  2. *2984*: Gold filters on `SET_TRANSLATIONS.ID = 5`; predicted filters on `SETS.ID = 5`.  
- **Shared mistake**: The predicate logic (date handling, column choice, literal case) does not match the gold specification, producing either over‑ or under‑filtered result sets.  
- **Error type**: **Model error**  

### 2.3 Aggregation or Order Logic  

- **Question IDs**: 3011, 2994  
- **Representative key differences**  
  1. *3011*: Gold selects `NumTstTakr` directly; predicted wraps it in `SUM(...)`.  
  2. *2994*: Gold counts distinct molecules; predicted counts distinct atoms and uses a different denominator.  
- **Shared mistake**: The model applies an aggregation (SUM, COUNT) where none is required, or aggregates over the wrong entity, altering the numeric meaning of the result.  
- **Error type**: **Model error**  

### 2.4 Output‑Shape Mismatch  

- **Question IDs**: 2982, 2976  
- **Representative key differences**  
  1. *2982*: Gold returns two ID columns; predicted adds `CARDS.ID` as a third column.  
  2. *2976*: Gold selects `DISTINCT ID, Admission`; predicted also returns `SEX, BIRTHDAY, RBC`.  
- **Shared mistake**: The model includes extra columns that were not requested, causing downstream pipelines that expect a fixed schema to fail.  
- **Error type**: **Model error**  

### 2.5 Other Issues  

- **Question IDs**: 3016 (other), 3052 (unsupported_dialect_feature)  
- **Explanation**  
  - *3016*: Uses column names with spaces/parentheses that do not exist in the schema.  
  - *3052*: Quotes column names in lower‑case, making them case‑sensitive identifiers that Snowflake cannot resolve.  
- Both are **Model errors** stemming from schema‑awareness problems.

---

## 3. Pattern Totals  

| Pattern | Count | Question IDs |
|---------|-------|--------------|
| wrong_join_or_table | 7 | 3055, 3042, 2972, 3002, 3045, 3048, 3049 |
| predicate_or_filter_error | 2 | 3025, 2984 |
| aggregation_or_order_logic | 2 | 3011, 2994 |
| output_shape_mismatch | 2 | 2982, 2976 |
| other | 1 | 3016 |
| unsupported_dialect_feature | 1 | 3052 |
| syntax_error | 0 |  |
| missing_column | 0 |  |
| type_mismatch | 0 |  |
| ambiguous_intent | 0 |  |
| performance_issue | 0 |  |

*The table lists all 11 catalog patterns, showing zero for those not observed.*

---

## 4. TL;DR  

- The model’s **overall accuracy is low (≈35 %)**, with the majority of failures stemming from **incorrect joins or missing tables**.  
- **Predicate/filter mismatches** and **wrong aggregation logic** each account for multiple errors, indicating a systematic misunderstanding of query intent.  
- **Output‑shape mismatches** and **schema‑related identifier errors** are also present but less frequent.  
- **No evaluation‑framework errors** were detected; all issues are attributable to the model’s generation logic.  

---  

*End of report.*