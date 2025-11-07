## 1. Summary  

| Metric | Value |
|--------|-------|
| **experiment_id** | `2025-11-06_18-21-47_sharp_mccarthy` (derived from `csv_path`) |
| **total** | 100 |
| **executed** | 89 |
| **correct** | 29 |
| **accuracy** | 0.3258426966292135 |

**Experiment configuration**  

- **csv_path**: `results/2025-11-06_18-21-47_sharp_mccarthy/all_results.csv`  
- **sample_size**: 20  
- **filter_by_model**: `llama-4-maverick`  
- **filter_by_dialect**: `bigquery`  

---

## 2. Failure Patterns  

### 2.1 Wrong Join or Table  *(Model error)*  

**Question IDs**: 2455, 2372, 2448, 2449, 2384  

| Example (key_difference) |
|---------------------------|
| Gold uses **INNER JOIN**; predicted uses **LEFT JOIN** (2455) |
| Gold joins **atom → molecule → bond**; predicted joins **atom → connected → bond** (2372) |
| Gold joins on **cards.id**; predicted joins on **cards.set_code** (2448) |
| Gold includes **INNER JOIN set_translations**; predicted omits the join (2449) |
| Gold filters on **set_translations.id = 5**; predicted filters on **sets.id = 5** (2384) |

**Shared mistake** – The model consistently selects the wrong join type or joins on an incorrect column/table, which changes row cardinality or introduces unrelated rows. This leads to result‑set mismatches even when the rest of the query is syntactically correct.

---

### 2.2 Predicate or Filter Error  *(Model error)*  

**Question IDs**: 2425, 2394, 2445, 2384  

| Example (key_difference) |
|---------------------------|
| Gold: `FundingType = 'Directly funded'`; Predicted: `funding_type = 'Directly Funded'` (2425) |
| Gold counts atoms where **element <> 'f'**; Predicted uses a **has_fluorine** boolean and subtracts from 100 (2394) |
| Gold checks **fastestLapTime IS NOT NULL**; Predicted checks **rank = 1** (2445) |
| Gold filters on **set_translations.id = 5**; Predicted filters on **sets.id = 5** (2384) |

**Shared mistake** – The model mis‑spells string literals, uses the wrong column, or applies an unrelated predicate, causing the filter logic to diverge from the gold standard.

---

### 2.3 Output‑Shape Mismatch  *(Model error)*  

**Question IDs**: 2402, 2462, 2376  

| Example (key_difference) |
|---------------------------|
| Gold returns **one column (element)**; Predicted returns **two columns (a1.element, a2.element)** (2402) |
| Gold returns **constructor name only**; Predicted returns **name + points** (2462) |
| Gold uses **SELECT DISTINCT**; Predicted omits **DISTINCT**, risking duplicates (2376) |

**Shared mistake** – The model produces a result set with a different column count or missing `DISTINCT`, violating the expected output schema.

---

### 2.4 Other Issues  

| Pattern | Question ID | Error Type | Representative key_difference |
|---------|-------------|------------|--------------------------------|
| **Other** (evaluation framework) | 2442 | Evaluation framework error | Queries are semantically identical; harness flagged them unequal |
| **Aggregation or Order Logic** (model error) | 2411 | Model error | Gold selects raw column `NumTstTakr`; Predicted aggregates with `COUNT()` |

*These singleton cases were grouped under “Other Issues” because they do not reach the 2‑occurrence threshold for a dedicated subsection.*

---

## 3. Pattern Totals  

| Pattern                     | Count | Question IDs |
|-----------------------------|-------|--------------|
| wrong_join_or_table         | 5     | 2455, 2372, 2448, 2449, 2384 |
| predicate_or_filter_error   | 4     | 2425, 2394, 2445, 2384 |
| output_shape_mismatch       | 3     | 2402, 2462, 2376 |
| other                       | 1     | 2442 |
| aggregation_or_order_logic  | 1     | 2411 |
| syntax_error                | 0     | – |
| missing_column              | 0     | – |
| type_mismatch               | 0     | – |
| subquery_error              | 0     | – |
| ordering_error              | 0     | – |
| limit_error                 | 0     | – |

*The table lists all 11 catalog patterns, showing zero for those not observed in the current batch.*

---

## 4. TL;DR  

- The dominant failure modes are **wrong joins/tables**, **predicate/filter mismatches**, and **output‑shape mismatches** (together accounting for 12 of the 14 errors).  
- All three high‑frequency patterns are **model errors**; the model repeatedly selects incorrect join conditions, mis‑spells or mis‑targets filter values, and returns the wrong column layout.  
- One isolated case (question 2442) appears to be an **evaluation‑framework error** where the harness incorrectly marked two semantically equivalent queries as different.  
- Improving the model’s schema awareness (join keys, column names) and strict adherence to the gold query’s output schema should yield the biggest accuracy gains.