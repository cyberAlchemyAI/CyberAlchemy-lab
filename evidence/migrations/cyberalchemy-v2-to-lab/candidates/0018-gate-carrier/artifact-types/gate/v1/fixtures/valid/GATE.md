<!-- GENERATED FILE: canonical data is the sibling JSON file. -->

# Gate Fixture

- Identity: `EXAMPLE-CANDIDATE-REVIEW-GATE-001`
- Status: `candidate-unadmitted`
- Authority effect: `none`

## Canonical machine projection

- **Artifact Type Ref**: `cal.artifact-type.gate/v1`
- **Authority Boundary**: `The maintainer must route unresolved outcomes; this computed gate result grants no admission, mutation or execution authority.`
- **Claim Ceiling**: `Exact evidence-field checks only; owner acceptance, evidence truth and authority remain unproven.`
### Criteria

```json
[
  {
    "criterion_id": "validation-passed",
    "description": "The supplied validation record reports PASS.",
    "expected": "PASS",
    "field": "result",
    "on_failure": "block",
    "risk": null
  },
  {
    "criterion_id": "no-authority-effect",
    "description": "The supplied validation record declares no authority effect.",
    "expected": "none",
    "field": "authority_effect",
    "on_failure": "flag",
    "risk": {
      "description": "The evidence records an unexpected authority effect.",
      "follow_up": "Owner reviews the reported effect before accepting a verdict.",
      "owner_ref": "role:gate-owner"
    }
  }
]
```

### Effect Boundary

```json
{
  "effect": "record-review-readiness",
  "from_state": "constructed",
  "to_state": "reviewed"
}
```

- **Escalation Route**: `route:unresolved-validation`
- **Owner Ref**: `role:candidate-maintainer`
- **Profile**: `candidate:bound-json-gate/v1`
- **Record Location**: `route:gate-owner-records`
- **Review Route**: `route:candidate-owner-review`
- **Schema Version**: `cal-gate-record/v1`
- **Scope Ref**: `scope:example-validation-accountability`
### Source Direction

```json
{
  "canonical": "gate-record.json",
  "human_projection": "GATE.md",
  "projection_policy": "generated-only"
}
```

### Subject

```json
{
  "path": "evidence/migrations/cyberalchemy-v2-to-lab/candidates/0017-responsibility-carrier/artifact-types/responsibility/v1/artifact.json",
  "sha256": "02aafb7735e52b997b8c57d36bf46519b2cf03f552a4a13500e305594295058f"
}
```

### Verdicts

```json
[
  "pass",
  "flag",
  "block",
  "defer"
]
```


## Projection boundary

This generated view adds no canonical identity, lifecycle, conformance, or authority field.
