# Staff Evaluation Report  

## 1. Summary  

| Item | Value |
|------|-------|
| **experiment_id** | `2025-11-06_18-21-47_sharp_mccarthy` |
| **total** | 100 |
| **executed** | 97 |
| **correct** | 49 |
| **accuracy** | 0.5051546391752577 |
| **csv_path** | `results/2025-11-06_18-21-47_sharp_mccarthy/all_results.csv` |
| **sample_size** | 20 |
| **filter_by_model** | `llama-4-maverick` |
| **filter_by_dialect** | `sqlite` |

*All fields are taken directly from the supplied metadata; none are missing.*

---

## 2. Failure Patterns  

### 2.1 `predicate_or_filter_error`  (3 occurrences)  

- **Question IDs:** 349, 369, 308  
- **Representative key differences**  
  1. *349*: `Gold: COUNT(School) … FundingType='Directly funded'` vs `Pred: COUNT(CDSCode) … FundingType='Directly Funded'`  
  2. *369*: `Gold: … (no rank filter)` vs `Pred: … AND T2.rank = 1`  
  3. *308*: `Gold: WHERE set_translations.id = 5` vs `Pred: WHERE sets.id = 5`  

**Shared mistake:** The model consistently mis‑specifies predicates or filter columns, either by changing literal case, adding an extra condition, or applying the filter to the wrong table/column. This leads to a result set that does not match the gold‑standard semantics.  

**Error type:** **Model error**  

---

### 2.2 `wrong_join_or_table`  (3 occurrences)  

- **Question IDs:** 296, 372, 373  
- **Representative key differences**  
  1. *296*: `Gold: atom → molecule → bond` vs `Pred: atom → bond + connected (no molecule)`  
  2. *372*: `Gold: sub‑query on cards.id` vs `Pred: join on setCode`  
  3. *373*: `Gold: join sets ↔ set_translations` vs `Pred: no join, wrong aggregation`  

**Shared mistake:** The generated SQL introduces incorrect join paths or omits required tables, thereby altering the relational context of the query. In each case the model either adds an unnecessary table or fails to join the tables that the gold query explicitly requires.  

**Error type:** **Model error**  

---

### 2.3 Other Issues (singleton patterns)  

| Pattern | Question ID | Brief note |
|---------|-------------|------------|
| `output_shape_mismatch` | 335 | Aggregates a column with `SUM` when the gold query returns row‑wise values. |
| `unsupported_dialect_feature` | 318 | Uses multi‑statement syntax and a `WHERE element='f'` filter that the SQLite‑only evaluator cannot run. |

All singleton cases are also **Model errors**; no evaluation‑framework faults were identified.

---

## 3. Pattern Totals  

| Pattern | Count | Question IDs |
|---------|-------|---------------|
| predicate_or_filter_error | 3 | 349, 369, 308 |
| wrong_join_or_table | 3 | 296, 372, 373 |
| output_shape_mismatch | 1 | 335 |
| unsupported_dialect_feature | 1 | 318 |
| syntax_error | 0 | – |
| semantic_error | 0 | – |
| missing_column | 0 | – |
| ambiguous_column | 0 | – |
| type_mismatch | 0 | – |
| aggregation_error | 0 | – |
| order_by_error | 0 | – |

*The table lists all 11 catalog patterns, showing zero counts for those not observed.*

---

## 4. TL;DR  

- The model’s most frequent failures are **predicate/filter mismatches** and **incorrect join/table usage**, each accounting for three out of the eight error cases.  
- Singleton issues involve an unexpected aggregation (`SUM`) and the use of unsupported multi‑statement SQLite syntax.  
- All identified problems stem from the **model**; no evaluation‑framework errors were detected.  
- Overall accuracy (≈ 50 %) suggests the model is roughly at chance level for this SQLite‑dialect task, with systematic weaknesses in predicate handling and relational reasoning.  