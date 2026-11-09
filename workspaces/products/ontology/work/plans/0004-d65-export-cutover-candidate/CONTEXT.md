# Strict context pack: D65 export and cutover candidate

- Task: `CAL-TASK-D65-EXPORT-CUTOVER-PLAN-001`
- Mode: deep
- Strict coverage: PASS
- Selected files: 22
- Handoff type: planning context, not runtime execution evidence
- Authority effect: none

## Obligations

| ID | Obligation | Evidence | Status |
| --- | --- | --- | --- |
| O1 | Bind the exact admitted integration predecessor. | D65-S8 admission decision, manifest, verdict | covered |
| O2 | Preserve event history as the only canonical replay source. | D65-S8 manifest and runtime `lib.rs` | covered |
| O3 | Preserve the admitted v1 map and one-way Governance-to-Ontology-Lifecycle authority boundary. | context-map decision and v1 `map.json` | covered |
| O4 | Use the exact admitted v2 context-language successors. | CTX05 decision and four v2 records | covered |
| O5 | Do not cut over while the successor map is missing. | CTX05 decision and migration manifest | covered |
| O6 | Export adapters only in a separately versioned runtime candidate. | runtime crate, adapters, and tests | covered |
| O7 | Carry the complete D65 definitions-to-conformance chain into the new epoch. | plan 0003 and architecture proposal | covered |
| O8 | Provide deterministic, hostile, rollback, and frozen-predecessor validation. | D65-S8 verdict and migration rollback boundary | covered |
| O9 | Exclude Invoke, publication, deployment, destructive action, and cutover from preparation. | D65-S8 admission and CA2 route boundary | covered |

## Selected evidence

- `docs/decisions/0032-d65-s8-integration-admission/decision.json` — exact admission and preparation authority — O1, O9.
- `ontology-lifecycle/conformance/cal-d65-s8-integration-epoch-001/{manifest.json,verdict.json}` — immutable dependencies, six validations, replay and vacuity evidence — O1, O2, O8.
- `docs/plans/0003-d65-native-ontology-integration/d65-plan.json` — predecessor D65 stage vocabulary and identities — O7.
- `docs/decisions/0024-governance-ontology-lifecycle-context-map-promotion/decision.json` and `contexts/maps/governance-ontology-lifecycle/v1/map.json` — admitted v1 direction and map-local contract — O3.
- `docs/decisions/0025-governance-ontology-lifecycle-successor-promotion/decision.json` — admitted v2 successors and explicit successor-map obligation — O4, O5.
- `contexts/{governance,ontology-lifecycle}/v2/{context.json,language.json}` — exact successor endpoints and language contracts — O4.
- `contexts/migrations/governance-ontology-lifecycle-v1-to-v2/v1/migration.json` — plan-only state, rollback, and execution-authority false — O5, O8.
- `docs/proposals/0001-context-artifact-architecture/PROPOSAL.md` — orthogonality and machine-canonical artifact constraints — O7.
- `ontology-lifecycle/runtime/{Cargo.toml,Cargo.lock,src/lib.rs,src/main.rs,src/context_adapter.rs,src/governance_context_adapter.rs,tests/replay.rs,tests/context_binding.rs}` and `ontology-lifecycle/fixtures/w1/positive-baseline.json` — exact runtime preimages and public-export/test surface — O2, O6.

## Controlling conclusions

1. The admitted v1 Context Map cannot be rewritten to point to v2 endpoints.
2. The admitted v2 contexts still reference the admitted v1 map, while their
   promotion decision requires a successor map before consumer cutover.
3. The current Rust adapters are deliberately isolated and identify the v1
   context versions. Exporting them for v2 is therefore a new implementation
   epoch, not a status-field change.
4. The smallest useful next proof is an additive v2 Context Map candidate with
   deterministic projection and negative tests. Rust mutation comes later.
5. A versioned candidate crate must be constructed outside
   `ontology-lifecycle/runtime/`; cutover is a later exact owner decision.

## Excluded context

Unrelated repositories, ontology records, context families, generated build
output, and ambient dirty bytes were excluded because they close none of O1-O9.

