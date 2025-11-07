# 📊 Staff Evaluation Report  

## 1. Summary  

| Metric | Value |
|--------|-------|
| **experiment_id** | `2025-11-06_18-21-47_sharp_mccarthy` |
| **total** | 100 |
| **executed** | 73 |
| **correct** | 27 |
| **accuracy** | 0.3699 (≈ 37 %) |

**Experiment configuration**  

- **CSV path**: `results/2025-11-06_18-21-47_sharp_mccarthy/all_results.csv`  
- **Sample size**: 20  
- **Filter by model**: `llama-3-1-8b-instruct`  
- **Filter by dialect**: `mysql`  

> *All fields are taken directly from the supplied metadata; none are missing.*

---

## 2. Failure Patterns  

The judges identified **11** catalogued error patterns. Patterns that appear **two or more times** are detailed below. All observed errors are **model errors** (no evaluation‑framework faults were reported).

### 2.1. Unsupported Dialect Feature  *(2 occurrences)*  

| Question ID | Representative key‑difference (≤ 120 chars) |
|-------------|----------------------------------------------|
| 679 | “Gold uses CASTed SUM/CASE; prediction uses DIVIDE() (SQLite‑unsupported) and omits required join.” |
| 669 | “Gold uses STRFTIME; prediction uses MySQL‑only YEAR() and an illegal HAVING clause.” |

**Shared mistake** – The model generated SQL that relies on functions or syntax (e.g., `DIVIDE`, back‑ticks, `YEAR()`) that are **not available in the target SQLite dialect**, leading to runtime or parse errors.

**Label**: **Model error**

---

### 2.2. Wrong Join or Table  *(7 occurrences)*  

| Question ID | Representative key‑difference |
|-------------|--------------------------------|
| 666 | “Extra `client` join; ambiguous `account_id`; wrong predicate column.” |
| 640 | “No join to `frpm`; selects `school_name` instead of free‑meal rate.” |
| 596 | “Adds `connected`/`connected2` tables; gold joins only atom‑molecule‑bond.” |
| 626 | “Multiple unnecessary aliases (connected2, atom2, …); deviates from simple bond‑connected‑atom path.” |
| 672 | “Joins `sets` and matches on `set_code`; gold only filters `set_translations` via sub‑query.” |
| 673 | “Never joins `sets` with `set_translations`; missing join prevents language association.” |
| 608 | “Omits join to `set_translations`; references non‑existent `translation` column in `sets`.” |

**Shared mistake** – The model repeatedly **adds superfluous tables or omits required ones**, often using incorrect join keys or aliases. This changes the relational graph, produces ambiguous columns, or yields completely unrelated result sets.

**Label**: **Model error**

---

### 2.3. Aggregation or Order Logic  *(3 occurrences)*  

| Question ID | Representative key‑difference |
|-------------|--------------------------------|
| 635 | “Gold selects raw `NumTstTakr`; prediction adds `COUNT(num_tst_takr)` aggregation.” |
| 618 | “Gold counts distinct `molecule_id`; prediction counts distinct `atom_id`.” |
| 627 | “Gold returns `FavoriteCount` column; prediction returns `COUNT(favorite_count)`.” |

**Shared mistake** – The model **introduces or misplaces aggregation functions** (e.g., `COUNT`, `SUM`) where the gold query expects raw values or a different aggregation scope, thereby altering the output shape and semantics.

**Label**: **Model error**

---

### 2.4. Output‑Shape Mismatch  *(2 occurrences)*  

| Question ID | Representative key‑difference |
|-------------|--------------------------------|
| 614 | “Gold selects only `t2.name`; prediction also returns `league.id`.” |
| 600 | “Gold returns just `ID` and `Admission`; prediction returns many patient fields and extra joins.” |

**Shared mistake** – The model **projects extra columns** (or an entirely different set of columns) beyond what the task specification requires, leading to a mismatched result schema.

**Label**: **Model error**

---

### 2.5. Other Issues  

| Question ID | Pattern (merged) | Reason for merging |
|-------------|------------------|--------------------|
| 649 | **Predicate / Filter Error** (singleton) | Only one occurrence; grouped under “Other Issues” for completeness. |

*No evaluation‑framework errors were detected in any judgment.*

---

## 3. Pattern Totals  

| Pattern | Count | Question IDs |
|---------|-------|--------------|
| wrong_join_or_table | **7** | 666, 640, 596, 626, 672, 673, 608 |
| unsupported_dialect_feature | **2** | 679, 669 |
| aggregation_or_order_logic | **3** | 635, 618, 627 |
| output_shape_mismatch | **2** | 614, 600 |
| predicate_or_filter_error | **1** | 649 |
| syntax_error | **0** | – |
| missing_table | **0** | – |
| incorrect_alias | **0** | – |
| type_mismatch | **0** | – |
| invalid_subquery | **0** | – |
| performance_issue | **0** | – |

*Sorted by descending count.*

---

## 4. TL;DR  

- The model’s **major weakness** is incorrect join logic, accounting for **7 out of 15** errors.  
- **Dialect mismatches** (SQLite vs. MySQL) appear in **2 cases**, showing a need for stricter dialect awareness.  
- **Aggregation misuse** and **output‑shape mismatches** together contribute another **5 errors**, indicating the model often changes the result schema unintentionally.  
- **No evaluation‑framework errors** were found; all failures stem from the model’s SQL generation.  

*Improving join selection, dialect‑specific function handling, and strict adherence to the requested projection should raise accuracy substantially.*