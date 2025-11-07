# Staff Evaluation Report  

## 1. Summary  

| Metric | Value |
|--------|-------|
| **experiment_id** | `2025-11-06_18-21-47_sharp_mccarthy` |
| **total** | 100 |
| **executed** | 93 |
| **correct** | 39 |
| **accuracy** | 0.41935483870967744 |

**Experiment configuration**  

- `csv_path`: `results/2025-11-06_18-21-47_sharp_mccarthy/all_results.csv`  
- `sample_size`: 20  
- `filter_by_model`: `llama-3-3-70b-instruct`  
- `filter_by_dialect`: `mysql`  

---

## 2. Failure Patterns  

### 2.1. **aggregation_or_order_logic**  *(2 occurrences)* – **Model error**  

**Question IDs:** 2555, 2494  

**Representative key differences**  

- **Q2555:** `Gold: CAST(... AS REAL) * 100 / COUNT(...); Predicted: CAST(... AS DECIMAL(10,2)) / SUM(1) * 100`  
- **Q2494:** `Gold: COUNT(DISTINCT CASE WHEN element <> 'f' THEN molecule_id END); Predicted: SUM(IF(element='f',1,0))`  

**Shared mistake**  
The model altered the order of arithmetic operations or swapped a distinct‑count for a simple sum, thereby changing the numeric semantics of the calculation. Both cases involve an incorrect casting or aggregation strategy that yields a different result set than the gold standard.

---

### 2.2. **wrong_join_or_table**  *(4 occurrences)* – **Model error**  

**Question IDs:** 2542, 2516, 2548, 2549  

**Representative key differences**  

- **Q2542:** `Gold: joins disp and uses disp.type='OWNER'; Predicted: no join, uses account.frequency='OWNER'`  
- **Q2516:** `Gold: JOIN schools & frpm on CDSCode; Predicted: subquery on school_name, returns pre‑computed column`  
- **Q2548:** `Gold: WHERE id IN (SELECT id FROM cards …); Predicted: joins sets → set_translations via set_code`  
- **Q2549:** `Gold: joins sets & set_translations; Predicted: omits set_translations, queries unrelated foreign_data`  

**Shared mistake**  
The model either omitted required joins, joined the wrong tables, or introduced unnecessary joins, leading to incorrect predicates and missing columns. In each case the relational path that produces the gold answer is broken or altered.

---

### 2.3. **output_shape_mismatch**  *(4 occurrences)* – **Model error**  

**Question IDs:** 2511, 2482, 2562, 2476  

**Representative key differences**  

- **Q2511:** `Gold: SELECT T1.NumTstTakr …; Predicted: SELECT SUM(T1.num_tst_takr) …`  
- **Q2482:** `Gold: SELECT cardKingdomFoilId, cardKingdomId …; Predicted: SELECT id …`  
- **Q2562:** `Gold: SELECT constructors.name …; Predicted: SELECT constructor_id …`  
- **Q2476:** `Gold: SELECT DISTINCT ID, Admission …; Predicted: SELECT admission …`  

**Shared mistake**  
The model changed the projection or aggregation level, returning either a single aggregated value or a different set of columns than required. This mismatch in result shape makes the output incomparable to the gold reference.

---

### 2.4. **Other Issues**  

**Predicate or filter error** – **Model error**  

- **Question ID:** 2484  
- **Key difference:** `Gold: WHERE set_translations.id = 5; Predicted: WHERE sets.id = 5`  

The model applied the filter to the wrong table, causing the query to select an unrelated row.

---

## 3. Pattern Totals  

| Pattern                     | Count | Question IDs                              |
|-----------------------------|-------|-------------------------------------------|
| **output_shape_mismatch**   | 4     | 2511, 2482, 2562, 2476                    |
| **wrong_join_or_table**     | 4     | 2542, 2516, 2548, 2549                    |
| **aggregation_or_order_logic** | 2  | 2555, 2494                                |
| **predicate_or_filter_error** | 1   | 2484                                      |
| syntax_error                | 0     | –                                         |
| missing_column              | 0     | –                                         |
| incorrect_alias             | 0     | –                                         |
| data_type_mismatch          | 0     | –                                         |
| missing_aggregation         | 0     | –                                         |
| ordering_error              | 0     | –                                         |
| unknown_pattern             | 0     | –                                         |

*Sorted by descending count.*

---

## 4. TL;DR  

- The model’s primary failure modes are **output‑shape mismatches** and **incorrect joins**, each accounting for 4 out of the 11 examined errors.  
- **Aggregation/order logic** errors are fewer but systematic: the model often swaps casting precision or aggregates the wrong entity.  
- A single **predicate‑filter** mistake shows the model can mis‑target the wrong table in a WHERE clause.  
- **No evaluation‑framework errors** were detected; all mismatches stem from the model’s SQL generation.  

---  