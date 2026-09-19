<!-- GENERATED FILE: canonical data is the sibling JSON file. -->

# Policy Fixture

- Identity: `EXAMPLE-CANDIDATE-CHALLENGE-001`
- Status: `candidate-unadmitted`
- Authority effect: `none`

## Canonical machine projection

- **Artifact Type Ref**: `cal.artifact-type.policy/v1`
### Blocking Questions

```json
[
  {
    "question": "Has evidence for the challenge been attached?",
    "question_id": "evidence-attached"
  },
  {
    "question": "Has the exact challenged subject been confirmed?",
    "question_id": "subject-confirmed"
  }
]
```

- **Challenge Residue Route**: `route:unresolved-challenge`
- **Challenge Response**: `Preserve the challenged record and submit the challenge evidence to its owner.`
- **Claim Ceiling**: `Candidate routing preview from supplied answers only. No verdict, confidence change, gate completion or authority grant.`
### Contradiction Edges

```json
[]
```

- **Owner Ref**: `role:artifact-owner`
- **Owner Route**: `route:artifact-owner-review`
- **Profile**: `candidate:contestability-routing/v1`
- **Resolution Gate**: `gate:owner-challenge-resolution`
- **Schema Version**: `cal-policy-record/v1`
- **Scope Ref**: `scope:example-candidate-review`
### Source Direction

```json
{
  "canonical": "policy-record.json",
  "human_projection": "POLICY.md",
  "projection_policy": "generated-only"
}
```

- **Subject Ref**: `candidate:example-1`
### Valid Challenge Modes

```json
[
  "contradict",
  "request-validation"
]
```

### Validation Edges

```json
[]
```


## Projection boundary

This generated view adds no canonical identity, lifecycle, conformance, or authority field.
