# DKG Lower Layer Schema: Diagnostic Strategy Graph

> Design reference document for lower-layer node types and relationship types. Not loaded by code.
> Scope: Diagnostic knowledge for automated DPA attacks on symmetric block ciphers.
> Diagnostic chain: Observation → Cause → Action

---

## Node Types

### 1. Observation

Observable phenomenon during attack execution. Entry point of a diagnostic chain.

| Property | Description | Possible Values |
|----------|-------------|-----------------|
| id | Unique identifier | diag_001, diag_002, ... |
| metric | The metric being observed | free text (recommended: cpa_max_correlation, correlation_gap, recovered_bytes, alignment_discard_rate, snr, cpa_completed, execution_error, but extensible) |
| condition | Trigger condition | free text (e.g., "< 0.3", "> 0.3", "equals 0", "< 16 but > 0", "any") |

---

### 2. Cause

Possible reason for the observed phenomenon.

| Property | Description | Possible Values |
|----------|-------------|-----------------|
| name | Cause description | free text |

> Note: Likelihood is stored on the `indicates` relationship, not on the Cause node itself.

---

### 3. Action

Remedial action or verification method.

| Property | Description | Possible Values |
|----------|-------------|-----------------|
| name | **Concise action summary** (verb + object, one sentence max, e.g., "increase max_shift to cover actual offset range") | free text |
| operation | Action type | adjust_param, switch_component, add_step, skip_step, acquire_more_data, verify |
| target | What to operate on | free text (e.g., "alignment.max_shift", "filter.weight", "attack_point", "trace_count") |
| strategy | **Detailed step-by-step instruction** for the agent (e.g., "Observe peak positions across 5+ traces, calculate max-min range, set max_shift to that range") | free text |

> **name vs strategy division of labor**: `name` is a short label for display/search (like a commit message title), `strategy` is the full instruction body (like a commit message body). Do NOT duplicate the same text in both fields. If the action is simple enough to express in one sentence, `strategy` can be null.

---

### 4. Strategy

Complex structured knowledge that does NOT fit the Observation → Cause → Action triangle.

Used for three kinds of knowledge that have internal structure (ordering, bundling, or negation) that would be lost if decomposed into separate triples:

- **Ordered troubleshooting checklists**: priority-ranked investigation steps (e.g., "when CPA fails, check in this order: alignment → filter → attack position → trace count")
- **Anti-pattern sets**: lists of actions to avoid with explanations (e.g., "do NOT do X because Y")
- **Parameter preset bundles**: named combinations of default parameter values meant to be used together (e.g., "for smartcard AES alignment, use length=150 AND max_shift=80 AND threshold=85 together")

| Property | Description | Possible Values |
|----------|-------------|-----------------|
| id | Unique identifier | strat_001, strat_002, ... |
| name | Strategy name | "CPA failure diagnosis priority order", "Smartcard AES alignment preset", "CPA anti-pattern checklist" |
| type | Strategy type | troubleshooting_checklist, anti_pattern_set, parameter_preset_bundle |
| trigger_condition | When to apply this strategy | free text (e.g., "CPA key verification fails", "starting alignment on smartcard AES") |
| content | Structured content, serialized as JSON string | see formats below |
| rationale | Why this strategy works or why these anti-patterns are harmful | free text |

#### Content formats by type

**troubleshooting_checklist** — ordered list of investigation steps:
```json
[
  {"rank": 1, "check": "<what to check>", "action_if_bad": "<what to do>", "proportion_of_failures": "<optional %>"},
  {"rank": 2, "check": "...", "action_if_bad": "..."},
  ...
]
```

**anti_pattern_set** — list of actions to avoid:
```json
[
  {"avoid": "<action to avoid>", "why": "<why it is harmful>", "consequence": "<what happens if done>"},
  ...
]
```

**parameter_preset_bundle** — named combination of default parameter values:
```json
[
  {"param": "<parameter name>", "value": <value>, "min": <optional>, "max": <optional>, "unit": "<optional>"},
  ...
]
```

> **Design rationale**: We intentionally keep the full structured content as a JSON string on a single node rather than decomposing it into multiple linked nodes. This preserves the atomic semantics (ordering for checklists, bundling for presets, negation for anti-patterns) and allows the agent to retrieve the entire structure in one lookup. Decomposition into individual Observation→Cause→Action triples would lose these semantics.

---

## Relationship Types

### 1. indicates

This observation points to this possible cause.

| Property | Description | Possible Values |
|----------|-------------|-----------------|
| likelihood | How likely this cause is given this observation | high, medium, low |
| diagnostic_check | Quick check to confirm or rule out this cause | free text |
| source_papers | List of supporting papers | [...] |
| source_text | Original text excerpt | free text |

**Direction:** Observation → Cause

---

### 2. resolves

This action can resolve this cause.

| Property | Description | Possible Values |
|----------|-------------|-----------------|
| source_papers | List of supporting papers | [...] |
| source_text | Original text excerpt | free text |

**Direction:** Action → Cause

### 3. relates_to

This action relates to a specific upper-layer component (cross-layer link).

| Property | Description | Possible Values |
|----------|-------------|-----------------|
| role | How this action relates to the component. **Aligned with Action.operation values** for consistency. | adjust_param, add_step, switch_component, skip_step, verify |

> **role ↔ operation alignment**: `role` uses the same vocabulary as `Action.operation` to avoid confusion. The mapping is direct: if an Action's `operation` is `adjust_param`, the `relates_to.role` to the corresponding upper entity should also be `adjust_param`. Values `acquire_more_data` is excluded from role because it doesn't target a specific upper-layer component.

**Direction:** Action → any upper-layer node (Algorithm, DeviceClass, AttackPoint, LeakageModel, Preprocessing, StatMethod, Pipeline, DiagnosticMethod, ValidationMethod, RecoveryMethod)

> Note: Generated automatically in Step 3 by LLM matching Action descriptions to upper-layer entity names. One Action may relate to up to 3 entities when semantically justified (e.g., "use middle trace as reference" relates_to both Static Alignment parameter and DeviceClass context).

---

### 4. strategy_applies_to

Links a Strategy to the upper-layer component(s) it is relevant to (cross-layer link).

| Property | Description | Possible Values |
|----------|-------------|-----------------|
| applicability | How specific this strategy is to the target component | "specific" (only for this exact component), "general" (broadly applicable) |
| condition | Additional context (e.g., device category, algorithm family) | free text, optional |
| source_papers | List of supporting papers | [...] |
| source_text | Original text excerpt | free text |

**Direction:** Strategy → any upper-layer node (Algorithm, DeviceClass, AttackPoint, LeakageModel, Preprocessing, StatMethod, Pipeline, DiagnosticMethod, ValidationMethod, RecoveryMethod)

> Note: A single Strategy may apply to multiple upper-layer components simultaneously. For example, an "alignment preset bundle" strategy applies to BOTH the Static Alignment preprocessing node AND the Smartcard device class — both links should be created. Generated automatically in Step 3 by LLM matching Strategy trigger conditions to upper-layer entity names.