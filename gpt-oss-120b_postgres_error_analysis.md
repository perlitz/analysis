## 1. Summary  

| Item | Value |
|------|-------|
| **experiment_id** | not provided |
| **total** | 98 |
| **executed** | 91 |
| **correct** | 30 |
| **accuracy** | 0.3297 (≈ 33 %) |
| **csv_path** | `results/2025-11-06_18-21-47_sharp_mccarthy/all_results.csv` |
| **sample_size** | 20 |
| **filter_by_model** | `gpt‑oss‑120b` |
| **filter_by_dialect** | `postgres` |

The run evaluated 91 generated SQL statements; only 30 matched the gold‑standard results, yielding an accuracy of roughly one‑third.

---

## 2. Failure Patterns  

### 2.1 Wrong Join or Table  (**Model error**)  

- **Question IDs:** 3506, 3466, 3541, 3488  
- **Representative key differences**  
  1. `Gold: … FROM post_history JOIN badges …` vs `Predicted: FROM users JOIN posts JOIN badges …`  
  2. `Gold: atom → molecule → bond` vs `Predicted: atom filtered by bond only (no molecule join)`  
  3. `Gold: WHERE id IN (SELECT id FROM cards …)` vs `Predicted: JOIN cards ON c.set_code = st.set_code`  
  4. `Gold: atom INNER JOIN molecule … WHERE label = '+'` vs `Predicted: SELECT COUNT(*)` (no join, no filter)  

**Shared mistake:** The model consistently selects the wrong tables or omits required joins, thereby altering the logical relationships that the gold query relies on. This leads to completely different result sets even when the rest of the syntax looks plausible.

---

### 2.2 Output Shape Mismatch  (**Model error**)  

- **Question IDs:** 3560, 3484, 3549, 3508, 3513, 3539  
- **Representative key differences**  
  1. `Gold: SELECT player_name …` vs `Predicted: SELECT player_name, height …`  
  2. `Gold: SELECT t2.name` vs `Predicted: SELECT l.id, l.name`  
  3. `Gold: SELECT DISTINCT borderColor …` vs `Predicted: SELECT border_color …` (no DISTINCT)  
  4. `Gold: SELECT DISTINCT T3.member_id …` vs `Predicted: SELECT m.*` (extra columns)  
  5. `Gold: list of event_name …` vs `Predicted: SELECT COUNT(*) …` (different projection & cardinality)  
  6. `Gold: forename, surname, fastestLapTime` vs `Predicted: forename, surname` (missing column, different source table)  

**Shared mistake:** The generated queries return a different column set (extra columns, missing columns, or different aggregation) than the reference, causing a shape mismatch that the evaluation harness flags as incorrect.

---

### 2.3 Predicate or Filter Error  (**Model error**)  

- **Question IDs:** 3492, 3478  
- **Representative key differences**  
  1. `Gold: WHERE comments.creation_date = …` vs `Predicted: WHERE posts.creaion_date = …` (wrong table)  
  2. `Gold: WHERE set_translations.id = 5` vs `Predicted: WHERE sets.id = 5` (filter on wrong table, extra column selected)  

**Shared mistake:** The WHERE clause (or equivalent filter) is applied to the wrong relation, which changes the subset of rows that survive the query.

---

### 2.4 Other Issues  

| Question ID | Pattern (singleton) | Brief description |
|-------------|--------------------|-------------------|
| 3547 | **Subquery Logic Error** (Model error) | CTE is left unfinished; missing SELECT list and closing parenthesis → parsing failure. |
| 3530 | **Other** (Evaluation framework error) | Identical semantics; harness incorrectly penalised case‑sensitive identifier differences. |
| 3470 | **Unsupported Dialect Feature** (Model error) | Uses PostgreSQL `date_part` in a SQLite‑targeted task; function not available, causing syntax error. |

These isolated problems do not form a recurring pattern but are worth noting for future model improvements and evaluation‑harness robustness.

---

## 3. Pattern Totals  

| Pattern | Count | Question IDs |
|---------|-------|--------------|
| output_shape_mismatch | 6 | 3560, 3484, 3549, 3508, 3513, 3539 |
| wrong_join_or_table | 4 | 3506, 3466, 3541, 3488 |
| predicate_or_filter_error | 2 | 3492, 3478 |
| subquery_logic_error | 1 | 3547 |
| unsupported_dialect_feature | 1 | 3470 |
| other | 1 | 3530 |
| syntax_error | 0 | – |
| semantic_error | 0 | – |
| type_mismatch | 0 | – |
| missing_clause | 0 | – |
| duplicate_column | 0 | – |

*Sorted by descending count.*

---

## 4. TL;DR  

- The model’s biggest weaknesses are **output‑shape mismatches** (6 cases) and **wrong joins/tables** (4 cases).  
- Predicate/filter errors also appear (2 cases), all stemming from applying conditions to the wrong relation.  
- Only **one** evaluation‑framework error was detected (case‑sensitivity issue on Q3530).  
- Singleton issues (unfinished CTE, unsupported dialect function) are isolated but highlight the need for better syntax‑aware generation and dialect‑specific handling.  

Overall, the model frequently produces syntactically valid SQL that is *logically* incorrect, leading to the low 33 % accuracy observed. Improving table‑join reasoning and strict adherence to the required output schema should be primary targets for the next iteration.