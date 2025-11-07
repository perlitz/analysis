# The DIVIDE() Hallucination: Evidence of Underrepresentation and Generalization Failure

## Dialect-Specific Hallucinations Rather Than Cross-Dialect Confusion

A particularly revealing error pattern emerges in BigQuery and Snowflake queries: models across multiple architectures (deepseek-v3, llama-3-1-8b, llama-3-3-70b) consistently generate calls to a `DIVIDE()` function that **does not exist in any SQL dialect**. For example, when asked to compute a percentage in BigQuery, models produce `DIVIDE(COUNTIF(condition), COUNTIF(total))` instead of the correct `CAST(COUNTIF(condition) AS FLOAT64) / COUNTIF(total)`. Critically, this is not a case of cross-dialect contamination—our analysis confirms that `DIVIDE()` is not a function in PostgreSQL, MySQL, SQLite, DuckDB, BigQuery, or Snowflake. Instead, this represents a **pure hallucination** where models invent plausible-sounding functions based on semantic reasoning (division → DIVIDE) and likely interference from programming languages that do provide `divide()` methods. This pattern appears almost exclusively for BigQuery (2-3 occurrences per model) and Snowflake (2 occurrences per model), the two dialects with the lowest overall accuracy (30-37%), while being completely absent from higher-accuracy dialects like SQLite (47%) and MySQL (44%). This asymmetry strongly suggests that the error stems from **insufficient exposure to authentic BigQuery and Snowflake SQL during training** rather than confusion between dialects. When models have seen adequate examples of a dialect's actual syntax, they correctly use the `/` operator; when training data is sparse, they fall back on generalized semantic reasoning that produces syntactically invalid but semantically coherent constructs. The DIVIDE() hallucination thus serves as a diagnostic marker for training data gaps: it reveals not just what models don't know, but that they lack the distributional knowledge needed to distinguish between what *could* exist in a language and what *actually does* exist.

---

## Example Case

**Question ID**: deepseek-v3 BigQuery #1955

**Gold Query**:
```sql
SELECT CAST(SUM(CASE WHEN some_condition THEN 1 ELSE 0 END) AS FLOAT64) * 100
       / COUNT(*) AS percentage
FROM table_name;
```

**Predicted Query**:
```sql
SELECT DIVIDE(COUNTIF(some_condition), COUNTIF(TRUE)) AS percentage
FROM table_name;
```

**Error**: `Unrecognized name: DIVIDE at [1:8]`

**Analysis**: The model correctly understands the task (calculate a percentage) and even recognizes BigQuery-specific constructs like `COUNTIF()`. However, it invents a `DIVIDE()` function that would semantically accomplish the goal but is syntactically invalid. The fact that the model successfully uses `COUNTIF()` (a real BigQuery function) while simultaneously hallucinating `DIVIDE()` demonstrates selective knowledge gaps rather than complete ignorance of the dialect.

---

## Implications for Model Development

1. **Training Data Composition**: The 18-point accuracy gap between SQLite (50%) and BigQuery (33%) in llama-4-maverick directly reflects the frequency of these dialects in training corpora. Cloud-specific dialects (BigQuery, Snowflake) are underrepresented relative to open-source databases (SQLite, MySQL).

2. **Generalization vs. Memorization**: Models that generalize from semantic understanding ("division needs a function") without sufficient distributional evidence ("but SQL uses / not DIVIDE()") produce plausible but incorrect outputs. This suggests that for low-resource dialects, models rely more heavily on cross-domain generalization from programming languages rather than dialect-specific patterns.

3. **Diagnostic Value**: Function hallucinations serve as clearer indicators of training data gaps than other error types. Join logic errors could reflect reasoning failures, but inventing non-existent functions can only result from insufficient exposure to real SQL from that dialect.

4. **Mitigation Strategy**: Unlike cross-dialect contamination (which might be addressed through better dialect separation during training), hallucinations require direct data augmentation. Models need more authentic BigQuery and Snowflake SQL to learn what functions exist in these dialects' namespaces.
