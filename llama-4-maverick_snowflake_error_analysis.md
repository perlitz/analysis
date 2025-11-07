# 📊 Staff Evaluation Report  

## 1. Summary  

| Metric | Value |
|--------|-------|
| **experiment_id** | `2025-11-06_18-21-47_sharp_mccarthy` |
| **total** | 100 |
| **executed** | 92 |
| **correct** | 32 |
| **accuracy** | 0.3478 |

**Experiment configuration**  

- **csv_path**: `results/2025-11-06_18-21-47_sharp_mccarthy/all_results.csv`  
- **sample_size**: 20  
- **filter_by_model**: `llama-4-maverick`  
- **filter_by_dialect**: `snowflake`  

---

## 2. Failure Patterns  

The judges identified five distinct pattern categories. Only those with **two or more** occurrences are expanded below; the single‑occurrence pattern is placed in **Other Issues**.

### 2.1. aggregation_or_order_logic  *(Model error)*  

- **Question IDs**: 2355, 2311, 2294  

| ID | Representative *key_difference* (≤120 chars) |
|----|-----------------------------------------------|
| 2355 | Gold uses `SUM(CASE…) / COUNT(*)`; Pred uses `COUNT(CASE…) / COUNT(CASE…)`. |
| 2311 | Gold selects `NumTstTakr`; Pred uses `SUM(NUM_TST_TAKR)`. |
| 2294 | Gold: `COUNT(DISTINCT … NOT 'f') / COUNT(DISTINCT molecule_id)`; Pred: `100 - (SUM(CASE…) *100 / COUNT(DISTINCT atom_id))`. |

**Shared mistake** – The model consistently altered the aggregation strategy (e.g., swapping `SUM` for `COUNT`, adding unnecessary `SUM`, or computing percentages via subtraction). This changes the mathematical intent of the query, producing numerically different results even when the underlying filters are correct.

---

### 2.2. predicate_or_filter_error  *(Model error)*  

- **Question IDs**: 2325, 2284  

| ID | Representative *key_difference* |
|----|-----------------------------------|
| 2325 | Gold: `FundingType = 'Directly funded'` & `strftime('%Y', OpenDate)`; Pred: `FundingType = 'Directly Funded'` & `OPEN_DATE BETWEEN …`. |
| 2284 | Gold filters on `SET_TRANSLATIONS.ID = 5`; Pred filters on `SETS.ID = 5`. |

**Shared mistake** – The model mis‑specified filter predicates: case‑sensitive string literals, wrong date extraction functions, or filtering the wrong column/table. These errors shift the row set that the query operates on.

---

### 2.3. output_shape_mismatch  *(Model error)*  

- **Question IDs**: 2316, 2302, 2276  

| ID | Representative *key_difference* |
|----|-----------------------------------|
| 2316 | Gold selects a computed free‑rate; Pred selects `SNAME` (non‑existent) and a raw column. |
| 2302 | Gold returns one column (`element`); Pred returns two columns (`a1.ELEMENT, a2.ELEMENT`). |
| 2276 | Gold selects `ID, Admission`; Pred selects only `Admission` and uses unsupported `TIMESTAMPDIFF`. |

**Shared mistake** – The model either referenced columns that do not exist in the schema or projected a different column set (extra or missing columns). This leads to schema‑validation failures or mismatched result shapes.

---

### 2.4. wrong_join_or_table  *(Model error)*  

- **Question IDs**: 2272, 2362, 2348, 2349  

| ID | Representative *key_difference* |
|----|-----------------------------------|
| 2272 | Gold: `ATOM → MOLECULE → BOND`; Pred: `ATOM → CONNECTED → BOND` (missing MOLECULE). |
| 2362 | Gold joins `CONSTRUCTOR_STANDINGS`; Pred joins `CONSTRUCTOR_RESULTS` and adds `POINTS`. |
| 2348 | Gold filters `SET_TRANSLATIONS` via sub‑query; Pred joins `SETS` and matches on `SET_CODE`. |
| 2349 | Gold joins `SETS` ↔ `SET_TRANSLATIONS`; Pred never joins them, using an unrelated sub‑query. |

**Shared mistake** – The model either omitted a required join, joined the wrong table, or introduced unnecessary joins. Consequently, the relational path diverges from the reference solution, yielding incorrect row sets or extra columns.

---

### 2.5. Other Issues  

- **unsupported_dialect_feature** (question 2345) – The model used `YEAR()` which SQLite does not support; the gold query correctly used `STRFTIME`. This is a **Model error**.

---

## 3. Pattern Totals  

| Pattern                     | Count | Question IDs |
|-----------------------------|-------|--------------|
| aggregation_or_order_logic  | 3 | 2355, 2311, 2294 |
| predicate_or_filter_error   | 2 | 2325, 2284 |
| output_shape_mismatch       | 3 | 2316, 2302, 2276 |
| wrong_join_or_table         | 4 | 2272, 2362, 2348, 2349 |
| unsupported_dialect_feature | 1 | 2345 |
| syntax_error                | 0 | — |
| type_mismatch               | 0 | — |
| missing_column              | 0 | — |
| ambiguous_column            | 0 | — |
| invalid_identifier          | 0 | — |
| other                       | 0 | — |

*Counts are sorted descending.*

---

## 4. TL;DR  

- **Model‑generated SQL frequently mis‑applies aggregation logic** (3 cases) and **joins the wrong tables** (4 cases), the two biggest error clusters.  
- **Predicate/filter mismatches** and **output‑shape mismatches** also appear repeatedly, indicating systematic issues with column naming and filter formulation.  
- Only **one dialect‑specific mistake** (unsupported `YEAR()` function) was observed; no evaluation‑framework errors were detected.  
- Overall accuracy is low (≈ 35 %); the majority of failures stem from **model errors** rather than flaws in the evaluation harness.  