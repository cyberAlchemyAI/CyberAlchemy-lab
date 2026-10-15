# Permanent local operator and recovery instructions

Status: candidate instructions for A02. C11 rehearses disposable branches only.

## Select the operational boundary

At S02/R08, name the actual operator principal, authorization source, exact local store identity, selected implementation/profile digests, allowed categories/effects, explicit expiry/revocation rules and recovery owner. Confirm the final admitted implementation and its actual capability scope. A role or ontology connection does not supply a signing grant.

Select a new location under `.local/lab-runtime/<explicit-store-id>/` or an operator-owned location outside the repository. Select a separate private-key location outside both repository and store. These paths and the actual operator are unresolved in this candidate run; no permanent store has been provisioned.

Bind the operation authorization separately from software/type/instance admission. No service start, external publication or deployment follows from local provisioning.

## Private custody and initialization

Generate a fresh Ed25519 key exclusively at the selected private location; never reuse a fixture key. Create the private file exclusively with mode 0600. Keep only the raw public key in public store configuration. Reject any existing output/store path. Do not overwrite an old store or amend its baseline.

Before initialization, verify the final implementation closure, exact capture profile/policy, current source cut and all selected categories/effects. Initialize only the reviewed compatible engine/profile. Inspect store identity, public key, scope, policy, allowed effects, baseline digest and genesis HEAD. Record external configuration, baseline and HEAD pins separately from the store's self-seals.

C11's Project engine is the pinned frozen v2 candidate, and its separate catalog uses the S01 format. The read-only successor adapter does not provision or append; catalog bootstrap does not widen the Project dispatcher. A02 must select the actual admitted engine and adapters explicitly.

The frozen engine configures carrier categories, such as `artifact-instance`, rather than semantic kinds, such as Work. C11 selects only the `admit` effect for that category. Bounded Work selection remains an explicit caller obligation; this category setting does not prove a Work-only authority adapter. W02 owns the broader trusted authority interface.

## Export, rollback and recovery

Freeze writes and record the committed HEAD before exporting. Export configuration, original baseline and all committed transactions to a new destination, preserving original bytes. Exclude private keys and Session short memory. Replay from independently recorded pins in a fresh process, then compare the exported committed file digests and Project projection to the source. An exported directory or a self-seal alone is insufficient verification.

Preserve the old branch and key custody. Rollback selects its separately pinned read scope; do not copy old approvals or admit old records into a new profile implicitly. Source/profile changes require explicit carry/exclusion and a new authorization.

After interruption, verify the committed HEAD and transaction chain first. Reconcile recognized pending/uncommitted files using the selected engine's exact recovery contract and expected HEAD. Preserve unknown or mismatched files for inspection. Recovery cannot change the baseline, target bytes or operation scope, and cannot redispatch an uncertain external effect.

The replay bridge currently performs full uncached verification. It does not activate SQLite or a persistent checkpoint. Process interruption evidence does not establish power-loss durability or a Product SLA.

## Completion record

Record public configuration/pins, currentness, recovery/export evidence, actual operator/action authorization and exclusions. Check Git ignores `.local/` and private custody remains outside repository. An admitted implementation, provisioned store, Capability adoption and completed Work have distinct evidence and effects.
