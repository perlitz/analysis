# Staff Evaluation Report  

## 1. Summary  

| Item | Value |
|------|-------|
| **experiment_id** | `2025-11-06_18-21-47_sharp_mccarthy` |
| **total** | 100 |
| **executed** | 93 |
| **correct** | 36 |
| **accuracy** | 0.3871 |
| **csv_path** | `results/2025-11-06_18-21-47_sharp_mccarthy/all_results.csv` |
| **sample_size** | 20 |
| **filter_by_model** | `deepseek-v3` |
| **filter_by_dialect** | `duckdb` |

*All fields are taken directly from the experiment metadata; none are missing.*

---

## 2. Failure Patterns  

### 2.1. **Predicate or Filter Error**  *(2 occurrences)*  

- **Question IDs:** 549, 508  
- **Representative key differences**  
  1. *Q549:* “Gold uses `funding_type = 'Directly funded'`; predicted uses non‑existent `FundingType` column. ”  
  2. *Q508:* “Gold filters on `set_translations.id = 5`; predicted filters on `sets.id = 5`. ”  
- **Shared mistake:** The model selects the wrong column name or the wrong table when forming a `WHERE` predicate, leading to binder errors or logically incorrect filters.  
- **Error type:** **Model error**  

### 2.2. **Wrong Join or Table**  *(5 occurrences)*  

- **Question IDs:** 518, 496, 586, 572, 573  
- **Representative key differences**  
  1. *Q518:* “Gold qualifies columns (`T1.element`, `T2.molecule_id`); predicted uses unqualified `molecule_id` and a `QUALIFY` clause. ”  
  2. *Q496:* “Gold joins `atom → molecule → bond`; predicted joins `atom → connected → bond` (no molecule). ”  
  3. *Q586:* “Gold joins `constructorStandings` with `constructors`; predicted reads only `constructor_results`. ”  
  4. *Q572:* “Gold filters `set_translations` directly; predicted adds an unnecessary join to `sets`. ”  
  5. *Q573:* “Gold joins `sets` with `set_translations`; predicted joins only `sets` and uses `foreign_data`. ”  
- **Shared mistake:** The generated SQL either joins the wrong tables, omits required joins, or uses incorrect join conditions, which changes the semantics of the query and often produces binder or dialect errors.  
- **Error type:** **Model error**  

### 2.3. **Output Shape Mismatch**  *(2 occurrences)*  

- **Question IDs:** 526, 500  
- **Representative key differences**  
  1. *Q526:* “Gold: `SELECT DISTINCT element …`; predicted: `SELECT LIST(DISTINCT element) …` (single row vs many rows). ”  
  2. *Q500:* “Gold uses `SELECT DISTINCT …`; predicted drops `DISTINCT`, allowing duplicate patient rows. ”  
- **Shared mistake:** The model changes the cardinality of the result set—either by aggregating into a single row or by omitting `DISTINCT`—so the output shape no longer matches the gold specification.  
- **Error type:** **Model error**  

### 2.4. **Other Issues** *(singleton patterns merged)*  

| Pattern | Question ID | Key Difference (≤120 chars) |
|---------|-------------|------------------------------|
| Aggregation or Order Logic (Q535) | 535 | Gold returns raw `NumTstTakr`; predicted adds `SUM(num_tst_takr)`. |
| Unsupported Dialect Feature (Q569) | 569 | Gold uses `STRFTIME('%Y', …)`; predicted uses MySQL `YEAR(d.dob)`. |

*Both singletons are also **Model errors**; they do not reach the 2‑occurrence threshold for a dedicated subsection.*

---

## 3. Pattern Totals  

| Pattern | Count | Question IDs |
|---------|-------|--------------|
| wrong_join_or_table | 5 | 518, 496, 586, 572, 573 |
| predicate_or_filter_error | 2 | 549, 508 |
| output_shape_mismatch | 2 | 526, 500 |
| aggregation_or_order_logic | 1 | 535 |
| unsupported_dialect_feature | 1 | 569 |
| missing_column_error | 0 | – |
| syntax_error | 0 | – |
| type_mismatch | 0 | – |
| missing_join | 0 | – |
| duplicate_column | 0 | – |
| other | 0 | – |

*The table lists all eleven catalog patterns, showing zero for those not observed in the current batch.*

---

## 4. TL;DR  

- The model’s biggest weakness is **incorrect joins** (5 out of 11 failures), often omitting required tables or joining the wrong ones.  
- **Predicate/filter mistakes** and **output‑shape mismatches** each appear twice, indicating systematic issues with column naming and result cardinality.  
- No **Evaluation framework errors** were detected; every failure is classified as a **Model error**.  
- Improving schema awareness (column names, table relationships) and preserving the gold query’s result shape should raise accuracy well above the current 38 %.