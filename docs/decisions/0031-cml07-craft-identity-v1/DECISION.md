<!-- GENERATED FILE: canonical source is decision.json. -->

# CML-07 Craft Identity v1 Final Admission

- Decision: `CAL-DECISION-0031-CML07-CRAFT-IDENTITY-V1`
- Status: `owner-admitted`
- Approval interactions: `1`
- Identity carriers admitted: `6`
- Identity relations admitted: `5`
- CML-07 status: `complete-at-identity-contract-boundary`

## Admitted carriers

- `CA2-PRODUCT-CRAFT` — `cal.artifact-type.product-identity/v1` — owner `role:craft-product-owner`
- `CA2-PROJECT-CRAFT` — `cal.artifact-type.project-identity/v1` — owner `role:craft-project-owner`
- `CAL-METHOD-BINDING-CRAFT-PRODUCT-CAV2-D20` — `cal.artifact-type.method-binding/v1` — owner `role:craft-method-owner`
- `CA2-GOAL-CRAFT-PRODUCT-FEATURE-FOUNDATION` — `cal.artifact-type.goal/v1` — owner `role:craft-goal-owner`
- `CAL-LINEAGE-CRAFT-PRODUCT-V1` — `cal.artifact-type.identity-lineage/v1` — owner `role:craft-product-owner`
- `CAL-IDENTITY-GRAPH-CRAFT-V1` — `cal.artifact-type.identity-graph/v1` — owner `role:identity-graph-owner`

## Admitted relations

- `CAL-REL-CYBERALCHEMY-CONTAINS-CRAFT`: `CA2-PRODUCT-CYBERALCHEMY` — **contains_product** → `CA2-PRODUCT-CRAFT`
- `CAL-REL-CRAFT-COORDINATED-BY-PROJECT`: `CA2-PRODUCT-CRAFT` — **coordinated_by** → `CA2-PROJECT-CRAFT`
- `CAL-REL-CRAFT-EMBODIES-METHOD`: `CA2-PRODUCT-CRAFT` — **embodies_method** → `CAV2-D20`
- `CAL-REL-CRAFT-PROJECT-USES-METHOD`: `CA2-PROJECT-CRAFT` — **uses_method** → `CAV2-D20`
- `CAL-REL-CRAFT-PROJECT-PURSUES-FOUNDATION-GOAL`: `CA2-PROJECT-CRAFT` — **pursues_goal** → `CA2-GOAL-CRAFT-PRODUCT-FEATURE-FOUNDATION`

## Scoped conformance recognized

- Validation: `PASS`
- Schema conformance: `PASS`
- Identity-contract conformance: `PASS`
- Implementation conformance: `not_evaluable`
- Runtime conformance: `not_evaluable`

## Preserved boundaries

- Candidate files rewritten: `0`
- Craft root Bounded Context: `absent`
- Goal achievement: `not_proven`
- Migration completion: `not_proven`

## Claim ceiling

This decision admits only the six exact CML-07 Craft identity carriers and five relations bound by the approved manifest, while recognizing the exact schema and identity-contract conformance assessment. It completes CML-07 only at its identity-contract boundary; it does not prove Goal achievement, migration completion, Product Feature or Product Capability admission, implementation or runtime conformance, commit, push, publication, release, deployment, source deletion, or stable-release state.
