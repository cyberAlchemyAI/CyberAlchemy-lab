<!-- GENERATED FILE: edit the bound JSON source and rerun render.py. -->

# Foundation-01 accountable owners

> Generated from `owners.json`; this view is not canonical.

- Status: `candidate-unadmitted`
- Authority effect: `none`
- Owner: `person:<vrondelli>`

## Principals

- `person:<vrondelli>` — vrondelli (`owner-declared`)

## Separate role assignments

| Role | Principal | Scope |
| --- | --- | --- |
| `artifact-mechanics-owner` | `person:<vrondelli>` | Source direction, schema and generator binding mechanics; excludes semantic and admission decisions. |
| `artifact-type-owner` | `person:<vrondelli>` | Artifact Type/v1 contracts and registered type bindings; excludes source and definition admission. |
| `definition-owner` | `person:<vrondelli>` | Definition meaning, stable identity, registry postimages, and definition lifecycle decisions. |
| `source-admission-owner` | `person:<vrondelli>` | Exact external source selector admission; excludes semantic promotion and evidence validation. |
| `evidence-conformance-owner` | `person:<vrondelli>` | Independent evaluation contracts and receipts; excludes selecting semantic truth or granting admission. |

## Separation rule

One principal may hold multiple roles, but each role retains its own scope, decision record, evidence requirements, and claim ceiling. A decision made under one role cannot satisfy another role's gate by identity alone.

## Claim ceiling

This candidate records the exact principal supplied by the user and five separate proposed role assignments. It does not admit the owner registry, grant credentials, prove external identity, or let one role bypass another role's decision.
