<!-- GENERATED FILE: canonical data is record.json. -->

# Example relation.realizes

- Identity: `typed-relation:example-realizes`
- Kind: `typed-relation`
- Lifecycle: `candidate`
- Owner: `role:relation-owner`
- Authority effect: `none`

## Payload

```json
{
  "qualifiers": {
    "exact_target_version_ref": "example-exact_target_version_ref",
    "realization_role": "example-realization_role"
  },
  "relation_evidence_refs": [
    "evidence:definition-complete-relation-review"
  ],
  "relation_kind_ref": "relation.realizes",
  "relation_lifecycle_state": "candidate",
  "source": {
    "kind": "experiment-run",
    "ref": "experiment-run:example-001",
    "version_ref": "experiment-run:example-001@example-revision-1"
  },
  "target": {
    "kind": "experiment-design",
    "ref": "experiment-design:example-001",
    "version_ref": "experiment-design:example-001@example-revision-1"
  }
}
```

## Claim ceiling

Candidate example for exact schema and semantic validation only; it creates no admission, authority, connection, inference, or runtime effect.
