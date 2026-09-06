<!-- GENERATED FILE: canonical data is the sibling JSON file. -->

# Evaluation Profile Fixture

- Identity: `profile.product-candidate-evaluation`
- Status: `candidate-unadmitted`
- Authority effect: `none`

## Canonical machine projection

- **Artifact Type Ref**: `cal.artifact-type.evaluation-profile/v2`
### Checks

```json
[
  {
    "check_id": "PDE-01-FREEZE",
    "depends_on": [],
    "purpose": "Bind one exact product candidate and acceptance-bound byte set."
  },
  {
    "check_id": "PDE-02-TESTS",
    "depends_on": [
      "PDE-01-FREEZE"
    ],
    "purpose": "Require current complete product-test evidence for the frozen candidate."
  },
  {
    "check_id": "PDE-03-ELIGIBILITY",
    "depends_on": [
      "PDE-02-TESTS"
    ],
    "purpose": "Determine product-approval request eligibility without granting approval."
  },
  {
    "check_id": "PDE-04-SEPARATION",
    "depends_on": [],
    "purpose": "Keep product approval separate from later authority, admission, activation, and release decisions."
  }
]
```

- **Claim Ceiling**: `This candidate profile evaluates a frozen product candidate. PASS does not approve the product or authorize admission, activation, release, or deployment.`
- **Decision Rule**: `PASS establishes eligibility for a separate product decision only; it grants no approval or post-approval authority.`
- **Evaluation Kind**: `product-candidate`
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
  "cal.artifact-type.construction-binding/v1",
  "cal.artifact-type.evaluation/v1"
]
```


## Projection boundary

This generated view adds no canonical identity, lifecycle, conformance, or authority field.
