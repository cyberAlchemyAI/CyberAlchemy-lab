<!-- GENERATED FILE: canonical data is the sibling JSON file. -->

# Evaluation Profile Fixture

- Identity: `profile.prototype-construction-evaluation`
- Status: `candidate-unadmitted`
- Authority effect: `none`

## Canonical machine projection

- **Artifact Type Ref**: `cal.artifact-type.evaluation-profile/v2`
### Checks

```json
[
  {
    "check_id": "PCE-01-SOURCES",
    "depends_on": [],
    "purpose": "Resolve exact source and planning-decision bindings."
  },
  {
    "check_id": "PCE-02-GRAPH",
    "depends_on": [
      "PCE-01-SOURCES"
    ],
    "purpose": "Validate stage identity, typed predecessors, and complete bindings."
  },
  {
    "check_id": "PCE-03-PROJECTIONS",
    "depends_on": [
      "PCE-02-GRAPH"
    ],
    "purpose": "Prove every human view is generated from its canonical machine record."
  },
  {
    "check_id": "PCE-04-AUTHORITY",
    "depends_on": [],
    "purpose": "Reject prototype artifacts or receipts that claim admission or operational authority."
  }
]
```

- **Claim Ceiling**: `This candidate profile evaluates prototype construction only. PASS cannot admit artifacts, approve a product, or authorize operation.`
- **Decision Rule**: `PASS requires all independent checks PASS; dependency-blocked checks are NOT_EVALUABLE and never omitted.`
- **Evaluation Kind**: `prototype-construction`
- **Evaluation Mode**: `collect-all`
### Outcomes

```json
[
  "PASS",
  "FAIL",
  "NOT_EVALUABLE"
]
```

- **Owner Ref**: `role:evidence-conformance-owner`
- **Schema Version**: `cyberalchemy-lab-evaluation-profile/v2`
### Source Direction

```json
{
  "canonical": "profile.json",
  "human_projection": "PROFILE.md",
  "projection_policy": "generated-only"
}
```

### Subject Artifact Type Refs

```json
[
  "cal.artifact-type.construction-profile/v1",
  "cal.artifact-type.construction-binding/v1",
  "cal.artifact-type.implementation-binding/v1"
]
```


## Projection boundary

This generated view adds no canonical identity, lifecycle, conformance, or authority field.
