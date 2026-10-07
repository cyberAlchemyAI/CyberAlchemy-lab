# C1 — governance graph query and claim contract

Status: candidate specification, 2026-10-06. Authority effect: none. This contract defines expected query behavior and source-grounded examples; it does not report a graph execution. [Machine contract](c1-query-contract.json) contains the request rules, response fields, source bindings, and three acceptance cases. [R0](R0-SOURCE-BASELINE.md) supplies the baseline.

The 50 selected R0 source digests were compared with their local files before preparing C1 and all matched. This supports the examples at this source snapshot. Later responses must perform their own currentness check.

## Common request

A request selects a lens or an exact subject, a declared source scope, an admission epoch, history cursors when relevant, direction, allowed edge types, and traversal limits. The first scope is the D70–D73 repository governance slice and its selected implementation sources. `show Lifecycle` means every declared connection inside that selected scope and traversal budget; it does not mean all repository knowledge has been mapped.

| Request field | Rule |
| --- | --- |
| `query_id` | One of `lifecycle-slice`, `authority-explanation`, or `capability-provenance`. |
| `root` | Lens selector or exact subject identity with version when available. Lens roots are candidate navigation concepts until C2 defines their ontology profile. |
| `scope_ref` | Exact source selection, initially the R0 manifest plus explicitly bound additional sources. |
| `admission_as_of` | Decision 0073 for these examples; this is independent of a Project State's content cursor. |
| `direction` | `outgoing`, `incoming`, or `both`; every actual edge retains its declared direction. |
| `edge_selection` | Explicitly declared global relations or profile-local traceability edges. C1 supplies no new relation meaning or endpoint pair. |
| `limits` | Default depth 4, 100 nodes, 200 edges; result reports reached limits, omitted edges, and continuation or refinement guidance. |

Historical inspection binds the selected historical sources and never presents them as a fresh current view. A query with an unresolved scope cannot return a complete graph.

## Common response

| Field | What the user can inspect |
| --- | --- |
| `query` | The request actually answered, including source scope, epoch, and limits. |
| `result_status` | `complete`, `partial`, or `blocked`, relative to the selected scope and query obligations. |
| `source_snapshot` | Manifest digest, exact per-source path/selector/digest, admission epoch, separate semantic/governance cursors, and source-check time. It is not an Ontology Cut until such a Cut actually exists. |
| `freshness` | Current, historical, stale, or unknown relative to the selected sources; changed, missing, and unchecked inputs are listed. |
| `subjects` | Represented identity/version, source location, copied source status, effective admission, owner route, and independent facets. |
| `state_tracks` | Contract, instance admission, domain, ontology representation, runtime, and Agent Session postures separately; absent evidence is `unknown` or `not-evaluated`. |
| `connections` | Independent edge identity, namespace/mode, exact endpoints, qualifiers, evidence, admission state, and version-resolution result. Diagnostic unresolved edges remain visible but are excluded from confirmed traversal paths. |
| `explanation_paths` | Ordered source-backed paths supporting the answer; every step names its edge and evidence. Reverse navigation preserves the actual edge direction. |
| `claims` | Each assertion names its source, scope, observation basis, and what it establishes. Admission, domain completion, action authorization, and live-runtime claims use their own evidence. |
| `gaps` | Missing coverage, unresolved version labels, missing realization/evaluation/implementation evidence, and the next resolving action. |
| `coverage` | Required obligations met/unmet, mapped and unmapped subject classes, truncation, and excluded source areas. File count is not ontology coverage. |
| `authority_effect`, `replay_source`, `claim_ceiling` | `none`, `false`, and the bounded interpretation of this derived answer. |

Business/system alignment paths require evidence for both endpoints and the alignment assertion. A source file or symbol can appear as discovered material while implementation alignment remains a gap. These response categories are view vocabulary; they do not redefine a subject's canonical lifecycle vocabulary.

## Example 1: show Lifecycle

**Expected answer at the R0 sources:** the most recent Project State admitted in this chain is `project-state:cyberalchemy-v2-to-lab-migration:decision-0072`, admitted by D73. Its content cursor is `decision:0072`. The separate Project semantic and governance histories each end at cursor 2. The two earlier Project States are historical under later overlays.

```text
Lifecycle [candidate lens selector]
  selects Project State transition records
  → current state through D72, admitted by D73
  → two separate Project event histories at cursor 2
  → D72/D73 decisions and predecessor overlays
  → source projector and transition scripts, with alignment to be established in S2/B1

Confirmed D72 successor link:
  state through D71@bootstrap.1 --successor-of→ initial state@foundation.1

Diagnostic D73 successor link:
  state through D72@candidate.1 --successor-of→ state through D71@candidate.1
  target version unresolved: admission overlay names @bootstrap.1
```

**Result status: partial.** Current admission can be reported from D73's overlay even though the exact-version predecessor path is unresolved. The answer displays the [R0 version finding](r0-version-ref-audit.json), the Project-node version discrepancy, and the candidate projector's D71–D72 scope. It reports zero runtime activations by D70–D73; present service liveness remains unobserved. Decision 0073 itself awaits a later Project State successor according to D73's declared obligation.

## Example 2: why may Decision 0073 count?

**Expected answer:** D73 is recorded as owner-admitted, names `role:repository-owner`, binds an exact authorization file, and applies an exact admission bundle and overlays. Its bounded effect admits 22 artifact instances and 23 Typed Relations, adds one event per Project history, makes the prior state and histories historical, and closes the Agent Instance and Session.

```text
D73 Decision
  → exact authorization record
  → admitted bundle
  → artifact and Typed Relation overlays
  → exact admitted records and predecessor effects
```

These arrows explain source citations and recorded effects; C2 will define their ontology-local edge contracts. **Result status: complete for explaining the recorded admission effect.** A request to authorize a new action is a different obligation and returns `not-evaluated` until applicable authority and enforcement evidence exists. D73's zero runtime activations and closed-session disposition describe this decision's effect, not a fresh runtime observation. The relation-version finding appears as related residue when the affected records are expanded; it does not silently change the recorded decision status.

## Example 3: where did the Product Capability come from?

**Expected answer:** `product-capability:cyberalchemy-lab:governed-knowledge-lifecycle@foundation.1` is an admitted D71 record. Its exact admitted `relation.derives-from` points to `product-thesis:cyberalchemy-lab-governed-work@foundation.1` with qualifier `derivation_role: thesis-outcome-realization`.

```text
Capability@foundation.1 --derives-from→ Thesis@foundation.1
  → relation instance, D71 admission overlay, and exact source digests
```

**Result status: complete for this declared one-hop derivation.** The selected capability revision's domain posture is `draft`; its `realization_binding_refs` is empty. Evidence confidence and effectiveness remain unassessed. The derivation qualifier expresses its declared lineage role and does not establish fulfillment. A request for a complete transformation history or realized implementation returns partial until those sources are explicitly mapped and assessed.

## Required failure behavior

| Trigger | Required answer |
| --- | --- |
| Source digest changed or required file missing | Flag affected claims stale or blocked; retain historical provenance and exclude affected edges from confirmed current paths. |
| Subject ID resolves, version label differs | Keep recorded relation/subject state visible; mark version resolution unresolved; no silent alias or rewrite. |
| Candidate navigation/bridge edge has no approved profile | Label the proposal and omit it from confirmed semantic traversal. |
| Type is admitted, instance has no admission evidence | Report the type and instance states independently. |
| Owner text or applicable policy is present | Report the declared route/applicability; authorization remains not-evaluated. |
| A receipt is present | State the exact receipt scope and observed epoch; assess neither general truth nor current liveness by inference. |
| Depth/node/edge limit is reached | Report partial coverage with truncation and stable continuation/refinement information; do not say “all connected objects.” |
| View is expired or its consuming Agent Session is closed | Preserve it for historical inspection; do not treat it as valid context for a new Session without new preparation. |

## Completion and next node

C1 supplies the three expected answers, shared request/response shape, explicit gaps, and bounded failure behavior. The machine contract's sources and expected constants were checked against the inspected local records. Graph execution remains future work. **C2 is next:** define the ontology profile and the exact local/global node and edge contracts that can express these queries. S1 retains responsibility for resolving the R0 version-reference finding before any exact-version path is confirmed.
