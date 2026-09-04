<!-- Generated Work Pack projection from plan.json by tooling/generators/craft_development_migration_plan.py. Do not edit. -->

# Craft development closure work pack

- Plan: `CAL-CML11-CRAFT-DEVELOPMENT-CLOSURE-0004`
- Execution designation: `non-executing-planning-candidate`
- Current frontier: `SWU-CML11-001-HISTORICAL-BASELINE-BRIDGE`
- Internal behavior: continue on PASS and fail closed on a real failure; no intermediate approval requests.

## Exact L0 allowlist

- `projects/domainspec-v2/development/meta-type-instantiation-cli/CANONICAL-IMPLEMENTED-BASELINE.v2.json` → `craft/development/meta-type-instantiation-cli/CANONICAL-IMPLEMENTED-BASELINE.v2.json` (`sha256:7d3b88f6f1f0767c013d6c8fe8a165032dfb0f95e6d0563139026639c20e57ea`)
- `projects/domainspec-v2/development/meta-type-instantiation-cli/OWNER-CANONICAL-DOCS-AND-BASELINE-V2-DECISION.json` → `craft/development/meta-type-instantiation-cli/OWNER-CANONICAL-DOCS-AND-BASELINE-V2-DECISION.json` (`sha256:3b757fd572e4d8db4129e32e921ae37f733fd92067e31443d3db905965896b99`)
- `projects/domainspec-v2/development/meta-type-instantiation-cli/validate-baseline.mjs` → `craft/development/meta-type-instantiation-cli/validate-baseline.mjs` (`sha256:69683f8066447de8d9fffb9b85a72aec0018c01041add99bd765c1ad92429109`)
- `projects/domainspec-v2/development/implementation-conformance/ontology-experiment/ontology.json` → `craft/development/implementation-conformance/ontology-experiment/ontology.json` (`sha256:a00b2ae0b212bc0e1bfc18b8f4ae361083c1e6083972480cdf1a6d906de3e814`)
- `projects/domainspec-v2/development/implementation-conformance/ontology-experiment/domain-meta-types.projection.json` → `craft/development/implementation-conformance/ontology-experiment/domain-meta-types.projection.json` (`sha256:37796a783848f25bc53d159b46d8caf655d56b4518ec417992acba8dc61fb37f`)
- `projects/domainspec-v2/development/implementation-conformance/ontology-experiment/materialize-current-meta-type-state.mjs` → `craft/development/implementation-conformance/ontology-experiment/materialize-current-meta-type-state.mjs` (`sha256:928c907f6d3a8cce2b21d44b9d3675f6fa7d0b21129605a1a951c1611ed4b123`)
- `projects/domainspec-v2/development/backend-meta-type-conformance/evidence/WP-BMC-001/BMC-EVD-001.MATURITY-MATRIX.json` → `craft/development/backend-meta-type-conformance/evidence/WP-BMC-001/BMC-EVD-001.MATURITY-MATRIX.json` (`sha256:fa7d2903c245f2cbce156a86ef662a88b3ec2a3ec91d659f14ec882bb425f5d5`)
- `projects/domainspec-v2/development/implementation-conformance/ontology-experiment/profiles/base-domain.profile.json` → `craft/development/implementation-conformance/ontology-experiment/profiles/base-domain.profile.json` (`sha256:48d0ba174105b020bb6b94c79c27b208a67f7d5f92d4c0c9c3a28c7d91a04d9f`)
- `projects/domainspec-v2/development/implementation-conformance/ontology-experiment/profiles/python-strict.profile.json` → `craft/development/implementation-conformance/ontology-experiment/profiles/python-strict.profile.json` (`sha256:148cd333265563f6591ad6cd1cd7300b2fe0af3b9ec19de84ab4dab3162fbca4`)
- `projects/domainspec-v2/development/implementation-conformance/ontology-experiment/profiles/rust-strict.profile.json` → `craft/development/implementation-conformance/ontology-experiment/profiles/rust-strict.profile.json` (`sha256:f1db01c7219a468bba360232655e7c0aea180cb3b88960ae769dd338d5b37b68`)
- `projects/domainspec-v2/development/implementation-conformance/ontology-experiment/profiles/typescript-strict.profile.json` → `craft/development/implementation-conformance/ontology-experiment/profiles/typescript-strict.profile.json` (`sha256:32cf17b4a0c4d5c36f344d6cec22450a041b52e7a5bdef129a74ac319694b6b0`)

## `TASK-CML11-001` — Copy and validate the historical baseline bridge

- Owner: `role:craft-migration-implementer`
- Lane: `product-construction`
- Status: `ready-after-explicit-implementation-route`
- Next action: Re-hash the eleven sources and copy only the exact allowlist into absent destinations.

### `SWU-CML11-001-HISTORICAL-BASELINE-BRIDGE`

- Primary behavior: Copy exactly eleven immutable historical baseline inputs and prove byte, path, classification, and rollback closure.
- Split analysis: Splitting control records from their five frozen development members loses baseline closure; adding any other directory member introduces unrelated history.
- Acceptance boundary: 11/11 exact copies, zero other craft changes, historical-only status, deterministic receipt, reversible manifest.
- Write scope:

  - `the eleven destination paths in /baseline_bridge/entries`
  - `evidence/migrations/domainspec-v2-to-craft/development-closure/baseline-bridge-manifest.json`
  - `evidence/migrations/domainspec-v2-to-craft/development-closure/receipts/baseline-bridge-validation.json`

Implementation rules:

1. Re-open the canonical development inventory and verify its digest.
2. Re-hash every source allowlist entry and require the recorded digest and byte size.
3. Require every destination to be absent or already byte-identical; reject differing collisions.
4. Copy through a staging directory and rename each file only after verification.
5. Write a machine manifest that labels baseline v2 historical-only and preserves the 24-member drift denominator.
6. Run the independent validator twice and require byte-identical receipts.

Rollback: Remove only manifest-created destinations whose current hash still equals the copied hash; otherwise stop for owner review.

Validations:

- `VAL-CML11-001` — `python3 tooling/validators/craft_development_migration.py --stage baseline-bridge --check-selection` → Exactly eleven ordered entries match source path, destination path, size, and SHA-256.
- `VAL-CML11-002` — `python3 tooling/validators/craft_development_migration.py --stage baseline-bridge --check-bytes` → 11/11 exact; no unmanifested destination and no source mutation.
- `VAL-CML11-003` — `python3 -m unittest tests.conformance.test_craft_development_baseline_bridge` → All positive and hostile fixtures pass twice deterministically.

## `TASK-CML11-002` — Author and test the successor baseline candidate

- Owner: `role:craft-definition-and-realization-owner`
- Lane: `product-construction`
- Status: `blocked`
- Next action: Resolve the Node profile and record 24 explicit drift dispositions after L0 passes.

### `SWU-CML11-002-SUCCESSOR-BASELINE-CANDIDATE`

- Primary behavior: Create one deterministic candidate baseline from current bytes while preserving baseline v2 unchanged.
- Split analysis: A manifest without all drift dispositions hides semantics; admission remains separately splittable and is excluded.
- Acceptance boundary: 771/771 closure, 24/24 dispositions, two-run determinism, old baseline unchanged, no admission claim.
- Write scope:

  - `candidate baseline manifest`
  - `24-row drift disposition`
  - `generated current projections`
  - `candidate validation receipts`

Implementation rules:

1. Bind an exact Node profile.
2. Classify all 24 changed members without inference.
3. Generate one absent successor candidate.
4. Replay materialization and hostile stale-hash tests twice.
5. Keep admission status false.

Rollback: Delete only the absent candidate epoch; baseline v2 remains untouched.

Validations:

- `VAL-CML11-004` — `<node-profile> craft/development/meta-type-instantiation-cli/validate-baseline.mjs --candidate <successor>` → 771/771 current candidate members pass and baseline v2 remains unchanged.
- `VAL-CML11-005` — `python3 tooling/validators/craft_development_migration.py --stage successor-baseline --determinism` → Two candidate bundles are byte-identical and all 24 drift dispositions are closed.

## `TASK-CML11-003` — Close all copied-ledger development references

- Owner: `role:craft-project-owner`
- Lane: `product-construction`
- Status: `blocked`
- Next action: Generate the 126-row disposition registry after the successor baseline candidate is stable.

### `SWU-CML11-003-LEDGER-REFERENCE-CLOSURE`

- Primary behavior: Give every copied-ledger development reference one explicit disposition.
- Split analysis: The 126-row denominator must remain atomic to prove absence of accidental unresolved references.
- Acceptance boundary: 126/126 exactly-once classifications and zero implicit paths.
- Write scope:

  - `canonical development-reference registry`
  - `generated human map`
  - `reference validation receipt`

Implementation rules:

1. Freeze the 126-reference denominator.
2. Assign local, external, or retired exactly once.
3. Bind owners and locators.
4. Reject inferred context membership.
5. Run unresolved-reference mutants.

Rollback: Restore the previous copied ledger and remove only the candidate reference registry.

Validations:

- `VAL-CML11-006` — `python3 tooling/validators/craft_development_migration.py --stage ledger-references` → 126/126 references resolve exactly once with zero implicit paths.

## `TASK-CML11-004` — Migrate frozen active bundles

- Owner: `role:source-bundle-owner`
- Lane: `product-construction`
- Status: `blocked`
- Next action: Obtain a stable exact source epoch for one L2-selected bundle; EVF remains held while its bytes are active.

### `SWU-CML11-004-FROZEN-ACTIVE-BUNDLE`

- Primary behavior: Copy one owner-frozen dependency-closed active bundle without generated residue.
- Split analysis: One bundle is independently verifiable; combining bundles would couple unrelated owners and rollback scopes.
- Acceptance boundary: Stable source epoch, exact allowlist, no ignored/generated files, bundle tests and rollback PASS.
- Write scope:

  - `one future bundle-specific exact manifest`
  - `its selected Craft destinations`
  - `its validation and rollback receipts`

Implementation rules:

1. Require owner-frozen source epoch.
2. Select one dependency-closed bundle.
3. Exclude ignored and generated residue.
4. Copy exact files.
5. Run bundle tests and rollback rehearsal.

Rollback: Rollback only that bundle's manifest-created files.

Validations:

- `VAL-CML11-007` — `python3 tooling/validators/craft_development_migration.py --stage active-bundle --manifest <bundle-manifest>` → Every selected source is stable and dependency-closed; generated residue count is zero.
- `VAL-CML11-008` — `<bundle-specific-test-command>` → Bundle tests and exact rollback rehearsal PASS.

## `TASK-CML11-005` — Rebind, integrate, and test one exact Craft candidate

- Owner: `role:craft-product-owner`
- Lane: `product-construction`
- Status: `blocked`
- Next action: Resume dependency-ordered active-name rebinding only after selected development closures pass.

### `SWU-CML11-005-INTEGRATED-PRODUCT-CANDIDATE`

- Primary behavior: Rebind selected active surfaces and freeze one completely tested Craft candidate.
- Split analysis: Rebinding may be executed in internal dependency slices, but product candidacy requires their exact integrated closure and complete tests.
- Acceptance boundary: One immutable candidate, complete PASS evidence, and one final product decision boundary.
- Write scope:

  - `rebinding manifest-selected Craft files`
  - `Lab reference maps`
  - `product candidate manifest`
  - `current product-test evidence`

Implementation rules:

1. Apply dependency-ordered active-name rebinding.
2. Regenerate human projections from canonical machine sources.
3. Bind explicit Lab planes and contexts.
4. Run complete current tests.
5. Freeze candidate and stop at final product boundary.

Rollback: Apply the exact inverse rebinding map and preserve all historical migration evidence.

Validations:

- `VAL-CML11-009` — `python3 tooling/validators/craft_development_migration.py --stage integrated-candidate` → No active DomainSpec binding remains outside typed history/provenance and all Lab references close.
- `VAL-CML11-010` — `<profile-bound-complete-product-test-command>` → All acceptance-critical checks, hostile tests, determinism, and rollback PASS for one immutable candidate.

## Closeout obligations

- Every layer binds an immutable machine manifest and independently generated validation receipt.
- Changed acceptance-bound bytes create a new candidate epoch; receipts are never refreshed over changed bytes.
- Historical baseline v2 remains inspectable and unchanged.
- The single final product decision binds the exact L4 candidate and complete current tests.
- Operational authority remains a later separate route even after product approval.

## Claim ceiling

This plan selects and sequences candidate migration work. It does not copy development files, resolve the 24 semantic dispositions, admit a successor baseline, rewrite the ledger, freeze active writers, approve the product, activate consumers, publish, release, deploy, or delete source material.
