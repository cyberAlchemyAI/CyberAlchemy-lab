<!-- GENERATED FILE: canonical data is record.json. -->

# Challenge Contract fixture

- Identity: `challenge-contract:example-001`
- Kind: `challenge-contract`
- Lifecycle: `candidate`
- Owner: `role:artifact-type-owner`
- Authority effect: `none`

## Semantic payload

```json
{
  "challengeable_subject_kinds": [
    "definition",
    "artifact-type",
    "relation-kind"
  ],
  "eligible_challenger_kinds": [
    "principal",
    "person-reference"
  ],
  "grounds": [
    "evidence-conflict",
    "scope-error",
    "drift"
  ],
  "owner_route": "route:semantic-owner",
  "policy_ref": "policy:contestability@1",
  "required_evidence_kinds": [
    "source",
    "evidence-set"
  ],
  "resolution_gate_ref": "gate:owner-decision",
  "response_modes": [
    "evidence",
    "contradiction",
    "owner-review"
  ],
  "response_period": "owner-defined",
  "unresolved_residue_route": "route:residue-register"
}
```

## Declared relation roles

- `target` on `relation.challenges` with `challenge-event` `challenge-event:example-001`

## Claim ceiling

Realistic Challenge Contract example for candidate review only.

## Projection boundary

This generated view adds no admission, authority, relation, lifecycle, or runtime effect.
