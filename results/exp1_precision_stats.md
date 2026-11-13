# Exp 1 — Precision results (after human review)

Source: stratified-random sample of 250 triples (100 Upper / 100 Lower / 50 Cross)


## Per-layer + overall

| Layer | Y | N | partial | Total | Strict P | Lenient P |
|---|---:|---:|---:|---:|---:|---:|
| Upper | 90 | 3 | 7 | 100 | 90.0% | 93.5% |
| Lower | 97 | 1 | 2 | 100 | 97.0% | 98.0% |
| Cross | 43 | 1 | 6 | 50 | 86.0% | 92.0% |
| **Overall** | **230** | **5** | **15** | **250** | **92.0%** | **95.0%** |

## Precision definitions

- **Strict** = `Y / total` — partial counted as error (pessimistic).
- **Lenient** = `(Y + 0.5*partial) / total` — partial counted as half correct.

The paper reports the **lenient** value as the headline Precision, with strict
reported in parentheses or a footnote for transparency. Rationale: most `partial`
rows are triples that are semantically plausible but sit on a fuzzy boundary
(e.g., the target is a concrete schema instance rather than one of the 12 abstract
category names, or the source-text evidence is terse). Counting them fully wrong
under-states genuine KG quality.
