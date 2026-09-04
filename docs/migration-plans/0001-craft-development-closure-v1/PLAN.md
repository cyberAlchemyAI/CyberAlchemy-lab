<!-- Generated Plan projection from plan.json by tooling/generators/craft_development_migration_plan.py. Do not edit. -->

# Craft Development Closure Migration Plan

- Plan: `CAL-CML11-CRAFT-DEVELOPMENT-CLOSURE-0004`
- Status: `candidate-plan-runnable-after-explicit-implementation-route`
- Authority effect: `none`
- Current frontier: `SWU-CML11-001-HISTORICAL-BASELINE-BRIDGE`

## Outcome

Restore dependency closure for the copied Craft workspace by preserving the old development baseline bridge, producing a tested successor current-baseline candidate, resolving every copied-ledger development reference, and migrating only frozen active bundles before name rebinding resumes.

The first migration unit is an eleven-file historical baseline bridge. It is deliberately not the current baseline: twenty-four current source members differ from baseline v2 and require a successor candidate.

## Boundary and next decision

- Plan capability: `flag` — The plan is complete as a Lab planning candidate, but the selected architecture is not an admitted Invoke Design v3 bundle and CyberAlchemy-v2 Goals registration is currently blocked.
- No development file is copied by this plan.
- Next bounded action: explicitly route implementation of `SWU-CML11-001-HISTORICAL-BASELINE-BRIDGE` after refreshing its eleven source hashes.

## Construction rule

Preserve first, distinguish historical from current, validate each dependency-closed layer, and continue automatically through passing internal gates until the configured final product boundary. Internal gates verify evidence but do not request approval or grant authority.

## Migration layers

### `L0-HISTORICAL-BASELINE-BRIDGE` — Historical baseline bridge

- State: `runnable-after-explicit-implementation-route`
- Decision: After this layer, we know whether baseline v2 can be preserved locally with exact provenance without importing unrelated development history or claiming it is current.
- Minimum unit: Copy the exact eleven-file allowlist and generate a copy manifest plus independent validation receipt.
- Exit: 11/11 source-manifest-destination hashes match; source tree unchanged; baseline v2 marked historical-only; 24-member drift set unchanged
- Promotion: Continue automatically to L1 only when every exit check passes; otherwise stop and repair.

### `L1-SUCCESSOR-BASELINE-CANDIDATE` — Successor current-baseline candidate

- State: `waiting-on-l0-and-node-profile`
- Decision: After this layer, we know whether the current 771-member implementation can be represented and reproduced as a successor candidate without rewriting baseline v2.
- Minimum unit: Disposition all 24 drifted members, materialize one new candidate manifest and projections, and replay validators twice.
- Exit: 24/24 dispositions recorded; 771/771 candidate members resolve; two candidate runs are byte-identical; old baseline bytes unchanged
- Promotion: Continue automatically to L2 on PASS; admission remains deferred to its owner.

### `L2-LEDGER-REFERENCE-CLOSURE` — Copied-ledger development reference closure

- State: `waiting-on-l1`
- Decision: After this layer, we know whether every copied ledger reference has an explicit local, external, or retired disposition without broken implicit paths.
- Minimum unit: Classify and validate all 126 development artifact references against a closed disposition registry.
- Exit: 126/126 references classified exactly once; zero unresolved local paths; external references carry source epochs; retirements carry rationale
- Promotion: Continue automatically to any dependency-ready L3 bundle; unresolved references stop only their dependent bundle.

### `L3-FROZEN-ACTIVE-BUNDLES` — Frozen active development bundles

- State: `waiting-on-owner-freeze`
- Decision: After this layer, we know whether selected active product/evidence bundles can move without importing live writer changes or generated residue.
- Minimum unit: Migrate one owner-frozen dependency-closed bundle at a time from the L2 registry, starting with EVF only after a stable source epoch exists.
- Exit: source epoch stable; selected bundle hashes exact; ignored/generated count copied equals zero; rollback replay passes
- Promotion: Continue per independent bundle; a blocked bundle does not hide other runnable product work.

### `L4-INTEGRATED-CRAFT-CANDIDATE` — Rebound and integrated Craft candidate

- State: `waiting-on-selected-l3-closure`
- Decision: After this layer, we know whether one exact Craft candidate works from final names and paths with complete current product-test evidence.
- Minimum unit: Rebind only active selected surfaces, run all required toolchain and hostile checks, freeze one candidate, and present the single final product boundary.
- Exit: exact candidate manifest; all acceptance-critical tests PASS; hostile and rollback tests PASS; approval evidence current
- Promotion: Stop at the single final product-approval boundary.

## Approval boundary

- Mode: `single-final-product-boundary`
- Internal gates: `continue-on-pass-fail-closed-on-failure`
- Eligible after: `L4-INTEGRATED-CRAFT-CANDIDATE`
- Decision: `approve-revise-reject-defer-or-stop`
- Effect: `product-approval-only`
- Later authority: `separate-route-required`

## Two-lane work plan

- Product frontier: `SWU-CML11-001-HISTORICAL-BASELINE-BRIDGE`
- Causal construction blockers: `0`
- Runnable product work:

  - Re-hash and copy the exact eleven-file historical bridge after an explicit implementation-route instruction.

Operational support:

- `Bind an exact Node runtime profile` — owner `role:platform-environment-owner`; affects `L1-SUCCESSOR-BASELINE-CANDIDATE`; posture `future-frontier-exact-prerequisite`
- `Freeze EVF and EVF reference-consumer source epochs` — owner `role:source-bundle-owner`; affects `L3-FROZEN-ACTIVE-BUNDLES`; posture `bundle-local-future-prerequisite`
- `Commit or publish migration bytes` — owner `CA2-ROUTE-PUBLISH`; affects `no construction stage`; posture `deferred-no-construction-block`

## Claim ceiling

This plan selects and sequences candidate migration work. It does not copy development files, resolve the 24 semantic dispositions, admit a successor baseline, rewrite the ledger, freeze active writers, approve the product, activate consumers, publish, release, deploy, or delete source material.
