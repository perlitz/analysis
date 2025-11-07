## 1. Summary  

| Item | Value |
|------|-------|
| **experiment_id** | `2025-11-06_18-21-47_sharp_mccarthy` (derived from `csv_path`) |
| **total** | 96 |
| **executed** | 87 |
| **correct** | 35 |
| **accuracy** | 0.4023 |
| **exp_config.csv_path** | `results/2025-11-06_18-21-47_sharp_mccarthy/all_results.csv` |
| **exp_config.sample_size** | 20 |
| **exp_config.filter_by_model** | `gpt-oss-120b` |
| **exp_config.filter_by_dialect** | `sqlite` |

*All fields are taken directly from the supplied metadata; none are missing.*

---

## 2. Failure Patterns  

### 2.1 Wrong Join or Table  *(5 occurrences)*  

**Question IDs:** 180, 173, 100, 130, 185  

**Representative key differences**  

- **180:** `INNER JOIN foreign_data … COUNT(T1.id)` vs. `LEFT JOIN foreign_data … COUNT(DISTINCT c.uuid)`  
- **173:** Gold joins `results` (→ fastest lap) while prediction reads only `lapTimes`.  
- **100:** Gold joins `atom → molecule → bond`; prediction skips the `molecule` join.  
- **130:** Gold selects via `T2.atom_id`; prediction adds a UNION that also uses `T2.atom_id2`.  
- **185:** Gold joins `Patient` ↔ `Laboratory` and filters on `WBC`; prediction omits the join and filter entirely.  

**Shared mistake** – The model consistently selects the wrong tables or joins, either by using a different join type (LEFT vs. INNER), omitting a required table, or adding extra tables/UNIONs. This changes the relational scope of the query, leading to incorrect row counts or missing predicates.

**Error type:** **Model error**  

---

### 2.2 Output Shape Mismatch  *(4 occurrences)*  

**Question IDs:** 169, 110, 118, 104  

**Representative key differences**  

- **169:** Gold `SELECT T2.account_id`; prediction `SELECT a.*` (all columns).  
- **110:** Gold returns `cardKingdomFoilId, cardKingdomId`; prediction aliases them as `foilId, cardId`.  
- **118:** Gold `SELECT t2.name`; prediction `SELECT l.id, l.name` (extra ID column).  
- **104:** Gold `SELECT ID, Admission`; prediction adds `SEX, Birthday, RBC, AdmissionStatus`.  

**Shared mistake** – The model returns a result set whose column list (names or count) does not match the gold specification. Either it selects *more* columns, renames them, or includes derived fields, breaking downstream expectations about schema.

**Error type:** **Model error**  

---

### 2.3 Predicate or Filter Error  *(5 occurrences)*  

**Question IDs:** 142, 131, 126, 112, 153  

**Representative key differences**  

- **142:** Gold `WHERE Name IN ('Supporter','Teacher')`; prediction requires two separate joins and misspells `'Teacher'` as `'Teachers'`.  
- **131:** Gold `CreationDate = '2014-04-23 20:29:39.0'`; prediction uses `'2014/4/23 20:29:39.0'`.  
- **126:** Gold filters on `comments.CreationDate`; prediction filters on `posts.CreaionDate` (typo + wrong table).  
- **112:** Gold `WHERE set_translations.id = 5`; prediction filters on `sets.id = 5` and adds a LEFT JOIN.  
- **153:** Gold `WHERE STRFTIME('%Y', First Date) = '1991'`; prediction uses `Patient.Description` and drops `DISTINCT`.  

**Shared mistake** – The model mis‑specifies the predicate: wrong column/table, wrong literal format, or an extra/incorrect join that changes the logical condition. Consequently the filtered row set diverges from the intended gold result.

**Error type:** **Model error**  

---

### 2.4 Other Issues  *(1 occurrence)*  

**Question ID:** 122  

The predicted SQL is truncated mid‑CTE and ends inside an unfinished `CASE` expression, producing an invalid statement that cannot be executed or compared.

**Error type:** **Model error**  

---

## 3. Pattern Totals  

| Pattern                     | Count | Question IDs |
|-----------------------------|-------|--------------|
| wrong_join_or_table         | 5     | 180, 173, 100, 130, 185 |
| output_shape_mismatch       | 4     | 169, 110, 118, 104 |
| predicate_or_filter_error   | 5     | 142, 131, 126, 112, 153 |
| missing_table               | 0     | – |
| column_type_mismatch        | 0     | – |
| aggregation_error           | 0     | – |
| ordering_error              | 0     | – |
| limit_error                 | 0     | – |
| duplicate_error             | 0     | – |
| syntax_error                | 0     | – |
| other                       | 1     | 122 |

*The table lists all eleven catalog patterns, showing zero for those not observed.*

---

## 4. TL;DR  

- The model’s biggest weaknesses are **wrong joins/tables** (5 cases) and **predicate/filter mistakes** (5 cases); both stem from mis‑identifying the relational scope or filter condition.  
- **Output‑shape mismatches** (4 cases) show a systematic tendency to return extra or renamed columns, breaking downstream schema contracts.  
- No **evaluation‑framework errors** were detected; every flagged issue is attributable to the model’s SQL generation.  
- One isolated case (question 122) produced an incomplete, syntactically invalid query, highlighting a need for better generation termination checks.  