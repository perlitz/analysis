# 📊 Staff Evaluation Report  

## 1. Summary  

| Metric | Value |
|--------|-------|
| **experiment_id** | `2025-11-06_18-21-47_sharp_mccarthy` (derived from `csv_path`) |
| **total** | 100 |
| **executed** | 72 |
| **correct** | 18 |
| **accuracy** | 0.25 |

**Experiment configuration**  

- **CSV path**: `results/2025-11-06_18-21-47_sharp_mccarthy/all_results.csv`  
- **Sample size**: 20  
- **Filter by model**: `llama-3-1-8b-instruct`  
- **Filter by dialect**: `postgres`  

> *All fields are taken directly from the supplied metadata; any missing field would be reported as “not provided”.*  

---

## 2. Failure Patterns  

### 2.1. `predicate_or_filter_error`  *(3 occurrences)*  

**Question IDs**: 1268, 1238, 1197  

**Representative key‑differences**  

1. `T1.language` used instead of `T2.language` (1268)  
2. `funding_type = 'Directly Funded'` vs. `'Directly funded'` (1238)  
3. Filter on `sets.id` instead of `set_translations.id` (1197)  

**Shared mistake** – The model consistently applied a predicate to the wrong column or with the wrong literal/casing, producing a WHERE clause that does not match the gold‑standard condition.  

**Error source** – **Model error**  

---

### 2.2. `wrong_join_or_table`  *(9 occurrences)*  

**Question IDs**: 1255, 1229, 1207, 1185, 1215, 1258, 1275, 1189, 1262  

**Representative key‑differences**  

1. Omitted `disp` join, filtered `account.frequency` (1255)  
2. No join to `schools`; filtered `school_name` (1229)  
3. Referenced `element` without joining `atom` (1207)  
4. Added extra `connected` table and spurious filter `molecule.label='single bond'` (1185)  
5. Duplicated joins to `CONNECTED`/`BOND` and required two triple bonds (1215)  
6. Used non‑existent `race_id` in `drivers` and missed `results` join (1258)  
7. Ordered by `points` in `constructors` without joining `constructorStandings` (1275)  
8. Referenced `rbc` without joining `laboratory` (1189)  
9. No join between `sets` and `set_translations` (1262)  

**Shared mistake** – The generated SQL either omitted required tables/joins or introduced unrelated tables, leading to missing‑column errors or logically different result sets.  

**Error source** – **Model error**  

---

### 2.3. `output_shape_mismatch`  *(4 occurrences)*  

**Question IDs**: 1224, 1195, 1203, 1261  

**Representative key‑differences**  

1. `COUNT(num_tst_takr)` vs. raw `NumTstTakr` column (1224)  
2. Returns only `id` (self‑join) instead of `cardKingdomFoilId, cardKingdomId` (1195)  
3. Projects `id, name` while gold returns only `name` (1203)  
4. Projects non‑existent `T2.language` from `cards` (1261)  

**Shared mistake** – The model changed the projection (number or names of columns) or added aggregation, so the output schema no longer matches the expected one.  

**Error source** – **Model error**  

---

### 2.4. Other Issues  

**Pattern**: `aggregation_or_order_logic` *(1 occurrence)*  

- **Question ID**: 1216 – Used `COUNT(T2.favorite_count)` and a different date literal instead of returning the raw `FavoriteCount`.  

Because this pattern appears only once, it is grouped under **Other Issues**.  

**Error source** – **Model error**  

---

## 3. Pattern Totals  

| Pattern                     | Count | Question IDs |
|-----------------------------|-------|--------------|
| `wrong_join_or_table`       | 9     | 1255, 1229, 1207, 1185, 1215, 1258, 1275, 1189, 1262 |
| `output_shape_mismatch`     | 4     | 1224, 1195, 1203, 1261 |
| `predicate_or_filter_error`| 3     | 1268, 1238, 1197 |
| `aggregation_or_order_logic`| 1    | 1216 |
| `syntax_error`              | 0     | – |
| `missing_column_error`      | 0     | – |
| `type_mismatch`             | 0     | – |
| `duplicate_column_error`    | 0     | – |
| `missing_table_error`       | 0     | – |
| `ambiguous_column_error`    | 0     | – |
| `other`                     | 0     | – |

*The table lists all 11 catalog patterns; counts of zero indicate that the pattern was not observed in this batch.*  

---

## 4. TL;DR  

- The model’s biggest weakness is **missing or incorrect joins** (9 cases), leading to column‑not‑found errors and wrong logical conditions.  
- **Predicate errors** (3 cases) stem from applying filters to the wrong column or using incorrect literal casing.  
- **Output‑shape mismatches** (4 cases) show the model frequently changes the projection or adds unwanted aggregation.  
- No **evaluation‑framework errors** were detected; every failure is attributable to the model’s SQL generation.  

---  

*End of report.*