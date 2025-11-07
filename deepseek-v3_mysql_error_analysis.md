# Staff Evaluation Report  

## 1. Summary  

| Metric | Value |
|--------|-------|
| **experiment_id** | `2025-11-06_18-21-47_sharp_mccarthy` |
| **total** | 100 |
| **executed** | 88 |
| **correct** | 40 |
| **accuracy** | 0.4545 |
| **csv_path** | `results/2025-11-06_18-21-47_sharp_mccarthy/all_results.csv` |
| **sample_size** | 20 |
| **filter_by_model** | `deepseek-v3` |
| **filter_by_dialect** | `mysql` |

*All fields are taken directly from the experiment metadata; none are missing.*

---

## 2. Failure Patterns  

### 2.1 Aggregation or Order Logic  *(3 occurrences – Model error)*  

| Question ID | Representative **key_difference** (≤120 chars) |
|-------------|---------------------------------------------------|
| 1368 | Gold uses `CAST(SUM(... ) AS REAL) * 100 / COUNT(id)`; Predicted uses `COUNT(CASE…) / COUNT(CASE…) * 100` without cast. |
| 1324 | Gold: `SELECT NumTstTakr` (row‑wise); Predicted: `SELECT SUM(num_tst_takr)` (single aggregated row). |
| 1307 | Gold counts distinct molecules; Predicted aggregates atoms and subtracts from 100. |

**Shared mistake** – The model consistently mis‑applies aggregation functions (e.g., `SUM` or `COUNT(CASE…)`) or mixes aggregation levels (row‑wise vs. grouped) and often forgets required type casts. This changes the numeric semantics of the result set, producing values that diverge from the gold standard.

### 2.2 Wrong Join or Table  *(4 occurrences – Model error)*  

| Question ID | Representative **key_difference** (≤120 chars) |
|-------------|---------------------------------------------------|
| 1329 | Gold joins `schools` ↔ `frpm` on `CDSCode`; Predicted queries `frpm` only with `school_name`. |
| 1285 | Gold path: `atom → molecule → bond`; Predicted: `atom → connected → bond` (no molecule). |
| 1361 | Gold filters `set_translations` directly; Predicted adds an unnecessary join to `sets`. |
| 1297 | Gold filters on `set_translations.id = 5`; Predicted filters on `sets.id = 5`. |

**Shared mistake** – The model either omits a required join, substitutes the wrong table/column in a predicate, or adds superfluous joins. In each case the relational graph diverges from the gold query, leading to either missing rows or extra rows.

### 2.3 Other Issues  *(4 singleton patterns – Model error)*  

| Question ID | Pattern | Representative **key_difference** |
|-------------|---------|-----------------------------------|
| 1289 | Output‑shape mismatch | Gold: `SELECT DISTINCT ID, Admission`; Predicted adds `sex, rbc`. |
| 1362 | Other | Ambiguous `id` column (both `sets` and `set_translations` have it). |
| 1297 | Predicate or filter error | Already covered under “Wrong Join or Table” (wrong column in WHERE). |
| 1362 (duplicate) | Other | Join condition and GROUP BY differ from gold. |

**Explanation** – These isolated errors involve either returning the wrong columns, causing ambiguous column references, or mis‑specifying predicates. They do not fit cleanly into the two dominant patterns but still reflect model‑level misunderstand‑of‑SQL semantics.

> **Note:** All identified errors are **Model errors**; no evaluation‑framework errors were observed.

---

## 3. Pattern Totals  

| Pattern                     | Count | Question IDs |
|-----------------------------|-------|--------------|
| wrong_join_or_table         | 4     | 1329, 1285, 1361, 1297 |
| aggregation_or_order_logic  | 3     | 1368, 1324, 1307 |
| output_shape_mismatch       | 1     | 1289 |
| predicate_or_filter_error   | 1     | 1297* |
| other                       | 2     | 1362, 1362 |
| syntax_error                | 0     | – |
| missing_column              | 0     | – |
| type_mismatch               | 0     | – |
| logic_error                 | 0     | – |
| performance_issue           | 0     | – |
| security_issue              | 0     | – |

\* Question 1297 appears in both “wrong_join_or_table” and “predicate_or_filter_error”; it is counted under the primary pattern with the larger impact (wrong join).

---

## 4. TL;DR  

- The model’s biggest weaknesses are **incorrect joins** (4 cases) and **mis‑applied aggregation** (3 cases).  
- Errors are uniformly **model‑generated**; the evaluation framework did not mis‑classify any answer.  
- Singleton issues (extra columns, ambiguous identifiers) are isolated but indicate a need for stricter column‑qualification handling.  
- Overall accuracy (≈ 45 %) suggests substantial room for improvement in relational reasoning and type‑casting awareness.  