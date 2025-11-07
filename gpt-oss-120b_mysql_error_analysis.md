# Staff Evaluation Report  

## 1. Summary  

| Metric | Value |
|--------|-------|
| **experiment_id** | `2025-11-06_18-21-47_sharp_mccarthy` |
| **total** | 94 |
| **executed** | 90 |
| **correct** | 40 |
| **accuracy** | 0.4444 |

**Experiment configuration**  

- **csv_path**: `results/2025-11-06_18-21-47_sharp_mccarthy/all_results.csv`  
- **sample_size**: 20  
- **filter_by_model**: `gpt-oss-120b`  
- **filter_by_dialect**: `mysql`  

*All fields were supplied in the metadata; none are missing.*

---

## 2. Failure Patterns  

### 2.1. **output_shape_mismatch**  *(5 occurrences)*  

**Question IDs**: 831, 846, 801, 826, 881  

**Representative key differences**  

1. `Gold: SELECT DISTINCT T3.member_id … ; Predicted: SELECT m.* …` (extra columns, no DISTINCT)  
2. `Gold: SELECT T2.category, T1.type … ; Predicted: SELECT budget.category …` (missing column)  
3. `Gold: SELECT cardKingdomFoilId, cardKingdomId … ; Predicted: SELECT id, card_kingdom_id, …` (extra column, naming mismatch)  
4. `Gold: SELECT forename, surname, … ; Predicted: SELECT CONCAT(forename,' ',surname) AS full_name …` (merged columns)  
5. `Gold: SELECT player_name FROM Player ; Predicted: SELECT player_name AS name, height …` (extra column)  

**Shared mistake** – The model’s projection does not match the gold query’s column list. It either adds columns, drops required ones, or combines them, leading to a different result‑set shape.  

**Error type** – **Model error**  

---

### 2.2. **predicate_or_filter_error**  *(2 occurrences)*  

**Question IDs**: 813, 803  

**Representative key differences**  

1. `Gold: WHERE T2.Date = '201309' ; Predicted: WHERE LEFT(y.date,6) = '201309'` (different predicate)  
2. `Gold WHERE: set_translations.id = 5 ; Predicted WHERE: sets.id = 5` (wrong table/column)  

**Shared mistake** – The WHERE clause filters on an incorrect expression or column, altering the logical condition that selects rows.  

**Error type** – **Model error**  

---

### 2.3. **wrong_join_or_table**  *(3 occurrences)*  

**Question IDs**: 791, 817, 830  

**Representative key differences**  

1. Gold joins `atom → molecule → bond`; Predicted skips the `molecule` join.  
2. Gold selects `GSoffered` directly; Predicted joins `frpm` and concatenates grades.  
3. Gold joins `client` directly to `district`; Predicted adds `disp` and `account` joins, changing row cardinality.  

**Shared mistake** – The generated SQL either omits a required join, adds unnecessary tables, or joins on the wrong relationship, which can produce missing or duplicated rows.  

**Error type** – **Model error**  

---

### 2.4. **Other Issues**  *(3 singleton patterns merged)*  

| Pattern | Question ID | Brief note |
|---------|-------------|------------|
| other | 863 | Unnecessary `DISTINCT` changes duplicate handling. |
| group_by_or_having_mismatch | 874 | GROUP BY omitted; ORDER BY altered. |
| aggregation_or_order_logic | 840 | Extra `ORDER BY year` introduced. |

All three are **Model errors**; no evidence of evaluation‑framework faults.

---

## 3. Pattern Totals  

| Pattern                     | Count | Question IDs |
|-----------------------------|-------|--------------|
| output_shape_mismatch       | 5     | 831, 846, 801, 826, 881 |
| wrong_join_or_table         | 3     | 791, 817, 830 |
| predicate_or_filter_error   | 2     | 813, 803 |
| other                       | 1     | 863 |
| group_by_or_having_mismatch | 1     | 874 |
| aggregation_or_order_logic  | 1     | 840 |
| syntax_error                | 0     | – |
| missing_clause              | 0     | – |
| type_mismatch               | 0     | – |
| performance_issue           | 0     | – |
| security_issue              | 0     | – |

*Sorted by descending count.*

---

## 4. TL;DR  

- The model’s biggest weakness is **output‑shape mismatches** (5/11 failures), where it projects the wrong columns or combines them.  
- **Join logic errors** (3 cases) and **predicate errors** (2 cases) also contribute significantly to the low accuracy (44 %).  
- All identified problems stem from the **model** itself; no evaluation‑framework errors were detected.  
- Improving column‑selection fidelity and ensuring correct join/where clauses should be the primary focus for the next iteration.  