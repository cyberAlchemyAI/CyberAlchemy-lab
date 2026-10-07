<!-- GENERATED FILE: canonical data is record.json. -->

# Challenge Event fixture

- Identity: `challenge-event:example-001`
- Kind: `challenge-event`
- Lifecycle: `candidate`
- Owner: `role:artifact-type-owner`
- Authority effect: `none`

## Semantic payload

```json
{
  "challenge_contract_ref": "challenge-contract:semantic-governance@1",
  "challenger_ref": "principal-reference:lab-owner",
  "evidence_refs": [
    "evidence:definition-mismatch"
  ],
  "ground": "scope-error",
  "residue_refs": [],
  "resolution_decision_ref": "none",
  "response_state": "open",
  "subject_ref": "artifact-type:agent-session/v1",
  "subject_version_ref": "artifact-type:agent-session/v1@1.0.0-candidate.1",
  "submitted_at": "2026-10-06T00:00:00-03:00"
}
```

## Declared relation roles

- `source` on `relation.challenges` with `agent-action` `agent-action:example-001`

## Claim ceiling

Realistic Challenge Event example for candidate review only.

## Projection boundary

This generated view adds no admission, authority, relation, lifecycle, or runtime effect.
