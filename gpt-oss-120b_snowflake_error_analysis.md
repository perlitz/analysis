# Staff Evaluation Report  

## 1. Summary  

| Item | Value |
|------|-------|
| **experiment_id** | `2025-11-06_18-21-47_sharp_mccarthy` |
| **total** | 87 |
| **executed** | 73 |
| **correct** | 24 |
| **accuracy** | 0.3288 |
| **csv_path** | `results/2025-11-06_18-21-47_sharp_mccarthy/all_results.csv` |
| **sample_size** | 20 |
| **filter_by_model** | `gpt-oss-120b` |
| **filter_by_dialect** | `snowflake` |

*The experiment ran 73 out of 87 possible cases; only 24 matched the gold‑standard, yielding an accuracy of roughly **33 %**.*

---

## 2. Failure Patterns  

### 2.1 Wrong Join or Table  *(Model error)*  

- **Question IDs:** 1761, 1685, 1707, 1752, 1749  
- **Representative key differences**  
  1. `Gold: INNER JOIN Patient‑Laboratory, COUNT(*)` – `Pred: LEFT JOIN, COUNT(DISTINCT p.ID)`  
  2. `Gold: ATOM → MOLECULE → BOND` – `Pred: ATOM filtered by IN (SELECT MOLECULE_ID FROM BOND)`  
  3. `Gold: JOIN FRPM … CHARTER_FUNDING_TYPE='Directly funded'` – `Pred: JOIN SCHOOLS … CHARTER=1`  
  4. `Gold: JOIN RESULTS, select fastestLapTime` – `Pred: JOIN LAP_TIMES, omit fastestLapTime`  
  5. `Gold: JOIN DISTRICT → ACCOUNT → DISP` – `Pred: JOIN DISTRICT → ACCOUNT → CARD (truncated)`  

**Shared mistake:** The model consistently selects the wrong table or join path, often dropping a required table or substituting a semantically different one. This changes the row set (or even makes the query invalid) because the join conditions no longer enforce the same relational constraints as the gold query.

---

### 2.2 Unsupported Dialect Feature  *(Model error)*  

- **Question IDs:** 1711, 1689  
- **Representative key differences**  
  1. `Gold: strftime('%Y', First Date) > '1990'` – `Pred: YEAR(First_Date) >= 1990`  
  2. `Gold: STRFTIME('%Y', CURRENT_TIMESTAMP) - STRFTIME('%Y', Birthday) >= 50` – `Pred: DATEDIFF('year', Birthday, CURRENT_DATE()) >= 50`  

**Shared mistake:** The model uses functions (`YEAR()`, `DATEDIFF()`) that are not part of the target SQLite‑style dialect. The generated SQL therefore either fails to parse or yields different semantics.

---

### 2.3 Predicate or Filter Error  *(Model error)*  

- **Question IDs:** 1697, 1695, 1753  
- **Representative key differences**  
  1. `Gold: WHERE T2.id = 5` – `Pred: WHERE s.ID = 5` (wrong column)  
  2. `Gold: WHERE cardKingdomFoilId IS NOT NULL AND …` – `Pred: WHERE "CARD_KINGDOM_FOIL_ID" IS NOT` (incomplete)  
  3. `Gold: WHERE text LIKE '%http://%'` – `Pred: WHERE text ILIKE '%http://%'` (case‑insensitive, adds DISTINCT)  

**Shared mistake:** The WHERE clause is either referencing the wrong column, is syntactically incomplete, or alters the logical condition (e.g., case‑sensitivity, missing predicates). These errors directly affect which rows are returned.

---

### 2.4 Output‑Shape Mismatch  *(Model error)*  

- **Question IDs:** 1703, 1738, 1768, 1718  
- **Representative key differences**  
  1. `Gold: SELECT name` – `Pred: SELECT ID, NAME` (extra column)  
  2. `Gold: SELECT DISTINCT molecule_id` – `Pred: SELECT DISTINCT MOLECULE_ID, LABEL` (extra column)  
  3. `Gold: SELECT player_name` – `Pred: SELECT PLAYER_NAME, HEIGHT` (extra column)  
  4. `Gold: SELECT forename, surname, url, dob` – `Pred: SELECT CONCAT(forename, ' ', surname) AS FULL_NAME, …` (different column set)  

**Shared mistake:** The model adds, removes, or reshapes columns compared with the gold query, producing a result set whose schema does not match the expected one.

---

### 2.5 Other Issues  *(Model error)*  

- **Question ID:** 1764  
- **Problem:** The generated SQL is truncated and missing essential syntax (`END` for CASE, FROM clause, joins). This leads to a parse error rather than a logical mismatch.

---

## 3. Pattern Totals  

| Pattern                     | Count | Question IDs |
|-----------------------------|-------|--------------|
| wrong_join_or_table         | 5     | 1761, 1685, 1707, 1752, 1749 |
| unsupported_dialect_feature| 2     | 1711, 1689 |
| predicate_or_filter_error   | 3     | 1697, 1695, 1753 |
| output_shape_mismatch       | 4     | 1703, 1738, 1768, 1718 |
| other                       | 1     | 1764 |
| syntax_error                | 0     | – |
| semantic_error              | 0     | – |
| missing_clause              | 0     | – |
| type_mismatch               | 0     | – |
| aggregation_error           | 0     | – |
| join_order_error            | 0     | – |

*The table lists all 11 catalog patterns; six of them were not observed in this run.*

---

## 4. TL;DR  

- The model’s **accuracy is low (≈33 %)**, with most failures stemming from **incorrect joins/tables** and **output‑shape mismatches**.  
- **Unsupported dialect functions** (e.g., `YEAR()`, `DATEDIFF()`) appear in two cases, causing syntax/runtime errors.  
- **Predicate errors** (wrong columns, incomplete WHERE clauses) affect three queries, directly altering result rows.  
- **No evaluation‑framework errors** were detected; all mismatches are attributable to the model’s SQL generation.  

---  