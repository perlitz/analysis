# Evaluation Report  

## 1. Summary  

| Item | Value |
|------|-------|
| **experiment_id** | `2025-11-06_18-21-47_sharp_mccarthy` |
| **total** | 100 |
| **executed** | 78 |
| **correct** | 28 |
| **accuracy** | 0.358974358974359 |

**Experiment configuration**  

- `csv_path`: `results/2025-11-06_18-21-47_sharp_mccarthy/all_results.csv`  
- `sample_size`: 20  
- `filter_by_model`: `llama-3-1-8b-instruct`  
- `filter_by_dialect`: `sqlite`  

---

## 2. Failure Patterns  

### 2.1 Wrong Join or Table  *(Model error)*  

**Question IDs:** 2755, 2742, 2716, 2672, 2702, 2748  

**Representative key differences**  

- *2755*: Gold uses `T2.language`; predicted uses `T1.language`.  
- *2742*: Gold joins `district → account → disp`; predicted selects from `account` only and filters `frequency`.  
- *2716*: Gold joins `schools` & `frpm`; predicted references non‑existent columns (`FreeMealCount`).  
- *2672*: Gold: `atom → molecule → bond`; predicted adds `connected` and duplicate `bond` joins.  
- *2702*: Gold uses a single `bond → connected → atom` chain; predicted joins `connected` twice and omits `DISTINCT`.  
- *2748*: Gold filters `set_translations` directly; predicted joins `sets` and matches on `setCode`.  

**Shared mistake** – The model repeatedly selects from the wrong table or omits required joins, leading to column‑not‑found errors or completely different result sets.  

---

### 2.2 Predicate or Filter Error  *(Model error)*  

**Question IDs:** 2725, 2749, 2684  

**Representative key differences**  

- *2725*: Gold `FundingType = 'Directly funded'`; predicted capitalises the “F”.  
- *2749*: Gold filters on `sets.releaseDate`; predicted references `set_translations.releaseDate` (non‑existent).  
- *2684*: Gold `WHERE set_translations.id = 5`; predicted `WHERE sets.id = 5` and drops `GROUP BY`.  

**Shared mistake** – Incorrect column references or case‑sensitive string literals cause the filter condition to diverge from the gold query, producing either empty results or wrong aggregations.  

---

### 2.3 Aggregation or Order Logic  *(Model error)*  

**Question IDs:** 2711, 2694, 2703  

**Representative key differences**  

- *2711*: Gold selects `NumTstTakr` directly; predicted adds `SUM(...)` and uses `GLOB`.  
- *2694*: Gold counts distinct molecules; predicted sums rows and counts atoms (no `DISTINCT`).  
- *2703*: Gold returns `FavoriteCount`; predicted returns `SUM(FavoriteCount)`.  

**Shared mistake** – The model injects unnecessary aggregate functions (e.g., `SUM`) or drops required `DISTINCT`/`GROUP BY`, altering the semantics of the query.  

---

### 2.4 Output Shape Mismatch  *(Model error)*  

**Question IDs:** 2682, 2676  

**Representative key differences**  

- *2682*: Gold `SELECT cardKingdomFoilId, cardKingdomId`; predicted `SELECT id` with a self‑join.  
- *2676*: Gold `SELECT DISTINCT ID, Admission`; predicted only a derived `AdmissionStatus` column.  

**Shared mistake** – The result column list does not match the gold specification, either by omitting required columns or by adding extra ones, leading to a shape mismatch.  

---

### 2.5 Other Issues  

**Question ID:** 2745  

- **Pattern:** `other` (Evaluation framework error)  
- **Explanation:** The predicted query is semantically equivalent to the gold query; the evaluation harness incorrectly flagged `results_equal = false`.  

---

## 3. Pattern Totals  

| Pattern                     | Count | Question IDs |
|-----------------------------|-------|--------------|
| wrong_join_or_table         | 6 | 2755, 2742, 2716, 2672, 2702, 2748 |
| predicate_or_filter_error   | 3 | 2725, 2749, 2684 |
| aggregation_or_order_logic  | 3 | 2711, 2694, 2703 |
| output_shape_mismatch       | 2 | 2682, 2676 |
| other                       | 1 | 2745 |
| syntax_error                | 0 | – |
| missing_column              | 0 | – |
| type_mismatch               | 0 | – |
| ordering_error              | 0 | – |
| limit_error                 | 0 | – |
| duplicate_rows              | 0 | – |

*Sorted by descending count.*

---

## 4. TL;DR  

- The majority of failures (6/15) stem from **wrong join/table** selections, indicating the model struggles with correctly navigating relational schemas.  
- **Predicate/filter** and **aggregation** mistakes each affect three queries, often due to case‑sensitivity, wrong column names, or unnecessary `SUM`/`DISTINCT` usage.  
- **Output‑shape mismatches** appear in two cases, where the projected column list does not align with the gold query.  
- One **evaluation‑framework error** was detected (question 2745); the model’s answer was correct but the harness mis‑labelled it.  

Overall, the model’s accuracy of **≈ 36 %** reflects systematic issues with join logic and column handling rather than isolated syntax problems.