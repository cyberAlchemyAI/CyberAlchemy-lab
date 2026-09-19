<!-- GENERATED FILE: canonical data is the sibling JSON file. -->

# Responsibility Fixture

- Identity: `EXAMPLE-CANDIDATE-VALIDATION-001`
- Status: `candidate-unadmitted`
- Authority effect: `none`

## Canonical machine projection

- **Artifact Type Ref**: `cal.artifact-type.responsibility/v1`
- **Authority Boundary**: `The maintainer must route unresolved outcomes; this obligation grants no admission, mutation or execution authority.`
- **Claim Ceiling**: `Exact evidence-field checks only; owner acceptance, evidence truth and authority remain unproven.`
### Criteria

```json
[
  {
    "criterion_id": "validation-passed",
    "description": "The supplied validation record reports PASS.",
    "expected": "PASS",
    "field": "result"
  },
  {
    "criterion_id": "no-authority-effect",
    "description": "The supplied validation record declares no authority effect.",
    "expected": "none",
    "field": "authority_effect"
  }
]
```

- **Escalation Route**: `route:unresolved-validation`
- **Obligation**: `Maintain reviewable validation evidence for the exact candidate and route failures to its owner.`
- **Owner Ref**: `role:candidate-maintainer`
- **Profile**: `candidate:bound-json-obligation/v1`
- **Review Route**: `route:candidate-owner-review`
- **Schema Version**: `cal-responsibility-record/v1`
- **Scope Ref**: `scope:example-validation-accountability`
### Source Direction

```json
{
  "canonical": "responsibility-record.json",
  "human_projection": "RESPONSIBILITY.md",
  "projection_policy": "generated-only"
}
```

### Subject

```json
{
  "path": "evidence/migrations/cyberalchemy-v2-to-lab/candidates/0016-authority-claim-carrier/artifact-types/authority-claim/v1/artifact.json",
  "sha256": "32dab209669292c515c1d562f676f866d731a3449119569df681a53d69689192"
}
```


## Projection boundary

This generated view adds no canonical identity, lifecycle, conformance, or authority field.
