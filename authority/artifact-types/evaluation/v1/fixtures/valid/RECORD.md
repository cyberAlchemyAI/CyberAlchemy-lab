<!-- GENERATED FILE: canonical data is record.json. -->

# Evaluation fixture

- Identity: `evaluation:example-001`
- Kind: `evaluation`
- Lifecycle: `candidate`
- Owner: `role:artifact-type-owner`
- Authority effect: `none`

## Semantic payload

```json
{
  "input_state_ref": "digest:candidate-postimage",
  "outcomes": [
    {
      "blocker_ref": "none",
      "check_id": "schema-conformance",
      "evidence_refs": [
        "receipt:implementation-v1"
      ],
      "result": "PASS"
    }
  ],
  "profile_ref": "evaluation-profile:artifact-type-candidate",
  "subject_ref": "artifact-type:implementation/v1"
}
```

## Declared relation roles

- `source` on `relation.evaluates` with `capability-realization-binding` `capability-realization-binding:example-001`

## Claim ceiling

Example Evaluation fixture for schema and relation-role validation only.

## Projection boundary

This generated view adds no admission, authority, relation, lifecycle, or runtime effect.
