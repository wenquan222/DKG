# Exp 1 — Schema Coverage

Coverage measures whether our 12-upper / 4-lower ontology can absorb the in-scope domain knowledge extracted from the 166-document corpus, without frequently routing items to a `truly_unknown` bucket.


## Definitions (three variants)

- **Strict**:    $\text{Cov}_{\text{strict}} = 1 - |T_{\text{unclassified}}| / |T_{\text{total}}|$ — every Step-1 reroute counts as a miss.
- **Lenient**:   $\text{Cov}_{\text{lenient}} = 1 - (|T_{\text{truly\_unknown}}| + |T_{\text{out\_of\_scope}}|) / |T_{\text{total}}|$ — cross-layer reroute counts as covered.
- **In-scope** (PAPER HEADLINE): $\text{Cov}_{\text{in-scope}} = 1 - |T_{\text{truly\_unknown}}| / (|T_{\text{total}}| - |T_{\text{out\_of\_scope}}|)$ — items the LLM correctly identified as deliberately-excluded scope (PQC/RSA/profiled/DL-only/etc.) are NOT in the ontology's responsibility, so they are dropped from the denominator. This is the standard OntoQA-style measure of ontology completeness for the *declared* scope.


## Overall

| Metric | Count |
|---|---:|
| Documents scanned | 167 |
| In-scope upper items (specific_experiments + canonical_pipelines) | 224 |
| In-scope lower items (diagnostic_triples + strategies) | 312 |
| Unclassified items (upper-pass) | 590 |
| Unclassified items (lower-pass) | 395 |
| → rerouted to lower / strategy / other layer | 654 |
| → out_of_scope (deliberately rejected: PQC/RSA/profiled/DL-only) | 213 |
| → **truly_unknown (genuine ontology gap)** | **118** |
| **Total extracted** | **1521** |
| In-scope denominator (total − out_of_scope) | 1308 |
| **Coverage (strict)** | **35.2%** |
| **Coverage (lenient)** | **78.2%** |
| **Coverage (in-scope, paper headline)** | **91.0%** |

## Route distribution of unclassified items

| route_to | count |
|---|---:|
| `out_of_scope` | 213 |
| `lower` | 207 |
| `lower_strategy` | 186 |
| `upper` | 165 |
| `truly_unknown` | 118 |
| `upper_pipeline` | 96 |