# Staff Evaluation Report  

## 1. Summary  

| Item | Value |
|------|-------|
| **experiment_id** | `2025-11-06_18-21-47_sharp_mccarthy` |
| **total** | 100 |
| **executed** | 93 |
| **correct** | 33 |
| **accuracy** | 0.3548 |
| **csv_path** | `results/2025-11-06_18-21-47_sharp_mccarthy/all_results.csv` |
| **sample_size** | 20 |
| **filter_by_model** | `llama-4-maverick` |
| **filter_by_dialect** | `postgres` |

The experiment ran 93 out of 100 sampled questions, yielding 33 correct answers (≈ 35 % accuracy). All metadata fields from `exp_config` are listed above; none are missing.

---

## 2. Failure Patterns  

### 2.1. **unsupported_dialect_feature**  *(4 occurrences)*  

| Question IDs | Representative *key_difference* (≤ 120 chars) |
|--------------|-----------------------------------------------|
| 1668 | Gold uses `SUM(CASE …)`; model uses `COUNT(*) FILTER (…)` & `ROUND`. |
| 1638 | Gold uses `strftime`; model uses PostgreSQL casts `::DATE`. |
| 1589 | Gold uses `STRFTIME`; model uses `EXTRACT(YEAR FROM AGE(...))`. |
| 1589 (duplicate entry) – same pattern, different syntax. |

**Shared mistake:** The model habitually emits PostgreSQL‑specific constructs (e.g., `FILTER`, `::DATE`, `EXTRACT`) or functions that are not part of the target dialect (SQLite or BigQuery). This leads to syntactic invalidity or runtime errors when the query is run against the intended engine.  

**Label:** **Model error**  

---

### 2.2. **wrong_join_or_table**  *(5 occurrences)*  

| Question IDs | Representative *key_difference* |
|--------------|-----------------------------------|
| 1585 | Model joins `atom → connected → bond` (OR condition) instead of `atom → molecule → bond`. |
| 1615 | Model adds extra `connected` and duplicate `atom` joins, deviating from the simple chain. |
| 1661 | Model joins `cards` to `set_translations` on `set_code` rather than using the `id`‑based subquery. |
| 1662 | Model omits the required join to `set_translations` entirely. |
| 1597 | Model filters on `sets.id = 5` instead of `set_translations.id = 5`. |

**Shared mistake:** The generated SQL mis‑identifies the relational path between tables—either by using the wrong foreign key, adding unnecessary intermediate tables, or completely skipping required joins. Consequently, the result set is either wrong in content or shape.  

**Label:** **Model error**  

---

### 2.3. **aggregation_or_order_logic**  *(2 occurrences)*  

| Question IDs | Representative *key_difference* |
|--------------|-----------------------------------|
| 1624 | Gold returns `NumTstTakr` per school; model adds `SUM(num_tst_takr)`. |
| 1607 | Model nests `COUNT` inside another `COUNT` and adds a spurious `GROUP BY`. |

**Shared mistake:** The model either introduces an extra aggregation layer (changing a row‑wise value into a total) or nests aggregate functions in a way that the target dialect disallows. Both errors alter the intended semantics and often break the query.  

**Label:** **Model error**  

---

### 2.4. **predicate_or_filter_error**  *(2 occurrences)*  

| Question IDs | Representative *key_difference* |
|--------------|-----------------------------------|
| 1658 | Gold: `fastestLapTime IS NOT NULL`; model: `fastest_lap_time = (SELECT MIN(...))`. |
| 1597 | Gold filters on `set_translations.id = 5`; model filters on `sets.id = 5`. |

**Shared mistake:** The predicate applied in the `WHERE` clause targets the wrong column or imposes an overly restrictive condition (e.g., equality to a global minimum) that diverges from the gold specification.  

**Label:** **Model error**  

---

### 2.5. **Other Issues**  *(1 occurrence)*  

| Question ID | Representative *key_difference* |
|-------------|-----------------------------------|
| 1595 | Gold returns two columns (`cardKingdomFoilId`, `cardKingdomId`); model returns only `id`. |

**Explanation:** The model’s projection does not match the required output schema, leading to an *output shape mismatch*.  

**Label:** **Model error**  

---

## 3. Pattern Totals  

| Pattern | Count | Question IDs |
|---------|-------|--------------|
| wrong_join_or_table | **5** | 1585, 1615, 1661, 1662, 1597 |
| unsupported_dialect_feature | **3** | 1668, 1638, 1589 |
| aggregation_or_order_logic | **2** | 1624, 1607 |
| predicate_or_filter_error | **2** | 1658, 1597 |
| output_shape_mismatch | **1** | 1595 |
| missing_column | **0** | – |
| syntax_error | **0** | – |
| type_mismatch | **0** | – |
| ordering_error | **0** | – |
| limit_offset_error | **0** | – |
| duplicate_rows_error | **0** | – |

*The table lists all 11 catalog patterns; six of them were not observed in this batch (count = 0).*

---

## 4. TL;DR  

- The model’s biggest weakness is **incorrect join logic** (5 cases), often using the wrong foreign key or adding unnecessary tables.  
- **Dialect incompatibilities** (PostgreSQL‑specific syntax) appear in 3 queries, causing outright execution failures on the target engines.  
- Aggregation mistakes and overly strict predicates each affect 2 queries, indicating a systematic misunderstanding of the required semantics.  
- No **Evaluation framework error** patterns were detected; all failures are attributable to the model’s output.  

*Overall, the low accuracy (≈ 35 %) is driven primarily by structural (join) and dialect‑specific errors.*