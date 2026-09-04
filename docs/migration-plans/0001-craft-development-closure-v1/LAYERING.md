<!-- Generated Implementation Layering projection from plan.json by tooling/generators/craft_development_migration_plan.py. Do not edit. -->

# Craft development migration implementation layering

- Target: `CAL-CML11-CRAFT-DEVELOPMENT-CLOSURE-0004`
- Layer count: `5`
- Recommended next layer: `L0-HISTORICAL-BASELINE-BRIDGE`
- Boundary heuristic: decision unlocked + visible outcome + risk reduced versus implementation + verification + coordination cost.

## `L0-HISTORICAL-BASELINE-BRIDGE` — Historical baseline bridge

**After this layer, we know whether:** baseline v2 can be preserved locally with exact provenance without importing unrelated development history or claiming it is current

- State: `runnable-after-explicit-implementation-route`
- Minimum working unit: Copy the exact eleven-file allowlist and generate a copy manifest plus independent validation receipt.
- Operator-visible outcome: Craft contains a complete inspectable historical baseline bridge.
- Risk reduced: Loss of provenance and accidental bulk import.
- Main costs: eleven file hashes; collision checks; independent no-effect validation
- Promotion decision: Continue automatically to L1 only when every exit check passes; otherwise stop and repair.

Included:

- six baseline control records
- five missing frozen baseline members
- historical-only status
- rollback map

Deferred:

- 24-member drift resolution
- successor baseline
- ledger rewrite
- EVF
- name rebinding

Exit evidence:

- 11/11 source-manifest-destination hashes match
- source tree unchanged
- baseline v2 marked historical-only
- 24-member drift set unchanged

Non-regression:

- original transplant bytes unchanged
- source remains read-only
- zero authority effect

## `L1-SUCCESSOR-BASELINE-CANDIDATE` — Successor current-baseline candidate

**After this layer, we know whether:** the current 771-member implementation can be represented and reproduced as a successor candidate without rewriting baseline v2

- State: `waiting-on-l0-and-node-profile`
- Minimum working unit: Disposition all 24 drifted members, materialize one new candidate manifest and projections, and replay validators twice.
- Operator-visible outcome: One deterministic current candidate exists alongside immutable baseline v2.
- Risk reduced: Treating current source drift as either silent acceptance or unexplained corruption.
- Main costs: semantic review of 24 members; Node runtime binding; two-run materialization
- Promotion decision: Continue automatically to L2 on PASS; admission remains deferred to its owner.

Included:

- 24 drift dispositions
- candidate baseline
- derived projections
- hostile stale-hash tests

Deferred:

- authority admission
- ledger-wide reference migration
- active EVF migration

Exit evidence:

- 24/24 dispositions recorded
- 771/771 candidate members resolve
- two candidate runs are byte-identical
- old baseline bytes unchanged

Non-regression:

- L0 bridge exact
- baseline v2 historical identity unchanged
- no authority effect

## `L2-LEDGER-REFERENCE-CLOSURE` — Copied-ledger development reference closure

**After this layer, we know whether:** every copied ledger reference has an explicit local, external, or retired disposition without broken implicit paths

- State: `waiting-on-l1`
- Minimum working unit: Classify and validate all 126 development artifact references against a closed disposition registry.
- Operator-visible outcome: The Craft ledger no longer relies on accidental path availability.
- Risk reduced: Silent broken references and evidence/authority collapse.
- Main costs: 126 classifications; owner routing; reference validator
- Promotion decision: Continue automatically to any dependency-ready L3 bundle; unresolved references stop only their dependent bundle.

Included:

- 126-reference denominator
- local/external/retired relation
- owner and evidence locator
- negative unresolved-reference test

Deferred:

- copying every locally selected bundle
- active EVF bytes
- name rebinding

Exit evidence:

- 126/126 references classified exactly once
- zero unresolved local paths
- external references carry source epochs
- retirements carry rationale

Non-regression:

- L0 and L1 identities preserved
- no directory implies a Bounded Context

## `L3-FROZEN-ACTIVE-BUNDLES` — Frozen active development bundles

**After this layer, we know whether:** selected active product/evidence bundles can move without importing live writer changes or generated residue

- State: `waiting-on-owner-freeze`
- Minimum working unit: Migrate one owner-frozen dependency-closed bundle at a time from the L2 registry, starting with EVF only after a stable source epoch exists.
- Operator-visible outcome: Selected active work has one inspectable candidate home in Craft.
- Risk reduced: Freezing an active writer accidentally or migrating local build state.
- Main costs: owner freeze; bundle-specific validators; dependency closure
- Promotion decision: Continue per independent bundle; a blocked bundle does not hide other runnable product work.

Included:

- owner-frozen source-like files
- exact dependency closure
- bundle-local receipts
- per-bundle rollback

Deferred:

- ignored caches
- unselected T2/T3 history
- publication
- source deletion

Exit evidence:

- source epoch stable
- selected bundle hashes exact
- ignored/generated count copied equals zero
- rollback replay passes

Non-regression:

- L0-L2 closure preserved
- active source is never silently canonicalized

## `L4-INTEGRATED-CRAFT-CANDIDATE` — Rebound and integrated Craft candidate

**After this layer, we know whether:** one exact Craft candidate works from final names and paths with complete current product-test evidence

- State: `waiting-on-selected-l3-closure`
- Minimum working unit: Rebind only active selected surfaces, run all required toolchain and hostile checks, freeze one candidate, and present the single final product boundary.
- Operator-visible outcome: One immutable tested Craft candidate is ready for the configured final product decision.
- Risk reduced: Approving partial or stale migration evidence.
- Main costs: toolchain profiles; cross-plane conformance; complete current tests
- Promotion decision: Stop at the single final product-approval boundary.

Included:

- active name/path rebinding
- Lab plane references
- current product tests
- one final product decision

Deferred:

- admission
- activation
- consumer cutover
- publication
- release
- deployment
- legacy deletion

Exit evidence:

- exact candidate manifest
- all acceptance-critical tests PASS
- hostile and rollback tests PASS
- approval evidence current

Non-regression:

- all earlier layer guarantees
- operational authority remains separate
