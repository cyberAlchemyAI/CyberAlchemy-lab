<!-- GENERATED FILE: edit artifact.json and run generator.py. -->

# Withdrawal Record Artifact Type v1

> Generated from `artifact.json`; this view is explanatory and not canonical.

- Type: `cal.artifact-type.withdrawal-record/v1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Canonical instance: `withdrawal-record.json`
- Human projection: `WITHDRAWAL-RECORD.md`

## Semantic bindings


## Distinct validation purpose

Permanently reserves a retired identifier and names its successor authority.

## Orthogonality rules

- **WITHDRAWAL-01**: Retired identifiers remain permanently reserved and cannot be silently recycled.
- **WITHDRAWAL-02**: A named successor does not inherit authority from the withdrawal record.

## Four facets

- **Classification**: Normalization-supported Withdrawal Record; no standalone Definition binding is asserted.
- **Human Continuation**: Generated WITHDRAWAL-RECORD.md preserves the existing twelve withdrawals and limits.
- **Machine Checkable**: Complete reservation set, successor agreement, permanent reservation and allocation collision checks.
- **Schema**: Exact accepted normalization, complete retired-identifier reservations and named successors.

## Typed residue

- `WITHDRAWAL-R1` (role:migration-owner): Standalone Withdrawal Record Definition, verified successor authority, global allocation registry and enforcement. Consequence: This candidate is supported by normalization only and checks the recorded reservation list locally.

## Claim ceiling

Exact recorded reservations and allocation collision checks only; no new withdrawal, successor authority or global allocation permission.
