# Staff Evaluation Report  

## 1. Summary  

| Metric | Value |
|--------|-------|
| **experiment_id** | `2025-11-06_18-21-47_sharp_mccarthy` (derived from `csv_path`) |
| **total** | 100 |
| **executed** | 86 |
| **correct** | 34 |
| **accuracy** | 0.3953488372093023 |

**Experiment configuration**  

- **csv_path**: `results/2025-11-06_18-21-47_sharp_mccarthy/all_results.csv`  
- **sample_size**: 20  
- **filter_by_model**: `llama-3-3-70b-instruct`  
- **filter_by_dialect**: `snowflake`  

No other metadata were supplied.  

---

## 2. Failure Patterns  

### 2.1. **unsupported_dialect_feature**  *(2 occurrences)*  

- **Question IDs**: 279, 200  
- **Representative key‑differences**  
  1. *279*: “Gold uses CAST × multiplication; predicted uses `DIVIDE` (unsupported in Snowflake).”  
  2. *200*: “Gold uses `STRFTIME` for age; predicted uses `SUBTRACT(year(...), year(...))` (unsupported).”  

**Shared mistake** – The model generated SQL that relies on functions (`DIVIDE`, `SUBTRACT`) that Snowflake does not implement, leading to compilation errors.  

**Error type** – **Model error**  

---

### 2.2. **predicate_or_filter_error**  *(3 occurrences)*  

- **Question IDs**: 249, 218, 208  
- **Representative key‑differences**  
  1. *249*: “Gold filters `FundingType = 'Directly funded'` and counts `School`; predicted uses `'Directly Funded'` and counts `CDS_CODE`. ”  
  2. *218*: “Gold counts rows where `element <> 'f'`; predicted counts where `ELEMENT = 'F'` and subtracts from 100. ”  
  3. *208*: “Gold filters on `SET_TRANSLATIONS.ID = 5`; predicted filters on `SETS.ID = 5`. ”  

**Shared mistake** – The model mis‑specifies the predicate (wrong value, wrong case, or wrong column/table), which changes the logical filter and therefore the result set.  

**Error type** – **Model error**  

---

### 2.3. **wrong_join_or_table**  *(4 occurrences)*  

- **Question IDs**: 266, 286, 272, 273  
- **Representative key‑differences**  
  1. *266*: “Gold joins `DISP` and filters `type = 'OWNER'`; predicted never joins `DISP` and filters `FREQUENCY`. ”  
  2. *286*: “Gold joins `CONSTRUCTOR_STANDINGS`; predicted joins `CONSTRUCTOR_RESULTS` and aggregates points. ”  
  3. *272*: “Gold selects from `SET_TRANSLATIONS` only; predicted adds a join to `SETS`. ”  
  4. *273*: “Gold joins `SETS` ↔ `SET_TRANSLATIONS`; predicted uses unrelated `FOREIGN_DATA` and drops grouping. ”  

**Shared mistake** – The model either omits a required join, joins the wrong table, or adds unnecessary joins, which distorts the row‑level relationships required by the gold query.  

**Error type** – **Model error**  

---

### 2.4. **Other Issues**  *(2 singleton patterns merged)*  

| Pattern | Question ID | Key‑difference (≤120 chars) |
|---------|-------------|------------------------------|
| **aggregation_or_order_logic** | 235 | Gold returns raw `NumTstTakr`; predicted adds `SUM(NUM_TST_TAKR)`. |
| **output_shape_mismatch** | 226 | Gold uses `SELECT DISTINCT`; predicted omits `DISTINCT`. |

Both cases reflect a mismatch in the shape of the result set (aggregation or duplicate rows) rather than a join or predicate problem.  

**Error type** – **Model error**  

No evaluation‑framework errors were identified in the supplied judgments.  

---

## 3. Pattern Totals  

| Pattern                     | Count | Question IDs |
|-----------------------------|-------|--------------|
| wrong_join_or_table         | 4     | 266, 286, 272, 273 |
| predicate_or_filter_error   | 3     | 249, 218, 208 |
| unsupported_dialect_feature | 2     | 279, 200 |
| aggregation_or_order_logic  | 1     | 235 |
| output_shape_mismatch       | 1     | 226 |
| syntax_error                | 0     | – |
| missing_table               | 0     | – |
| type_mismatch               | 0     | – |
| join_condition_error        | 0     | – |
| group_by_error              | 0     | – |
| other                       | 0     | – |

*The last six rows represent catalog patterns that were not observed in this run.*  

---

## 4. TL;DR  

- The model most frequently fails on **wrong joins/tables** (4 cases) and **predicate/filter mismatches** (3 cases).  
- **Unsupported Snowflake functions** appear in 2 queries, causing outright compilation errors.  
- Two isolated issues involve **incorrect aggregation** and **missing DISTINCT**, grouped under “Other Issues”.  
- **All errors are model‑generated; no evaluation‑framework errors were detected.**  

---  