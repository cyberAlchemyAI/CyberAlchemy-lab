<!-- GENERATED FILE: canonical data is the sibling JSON file. -->

# Construction Profile Fixture

- Identity: `profile.d65-prototype-first-construction`
- Status: `candidate-unadmitted`
- Authority effect: `none`

## Canonical machine projection

- **Approval Boundary**: `Product approval is separate from every authority, admission, activation, release, or deployment decision.`
- **Artifact Type Ref**: `cal.artifact-type.construction-profile/v1`
- **Claim Ceiling**: `Fixture proving the Construction Profile schema only; it creates no active workflow or authority.`
- **Ordering Rule**: `Prototype stages may iterate; only one exact frozen product candidate crosses into current product testing.`
- **Owner Ref**: `role:construction-profile-owner`
- **Schema Version**: `cyberalchemy-lab-construction-profile/v1`
### Source Direction

```json
{
  "canonical": "profile.json",
  "human_projection": "PROFILE.md",
  "projection_policy": "generated-only"
}
```

### Stages

```json
[
  {
    "evidence_kind": "prototype",
    "predecessor_refs": [],
    "stage_id": "prototype-definitions"
  },
  {
    "evidence_kind": "prototype",
    "predecessor_refs": [
      "prototype-definitions"
    ],
    "stage_id": "ontology-scaffolds"
  },
  {
    "evidence_kind": "prototype",
    "predecessor_refs": [
      "ontology-scaffolds"
    ],
    "stage_id": "product-prototypes"
  },
  {
    "evidence_kind": "tested-product",
    "predecessor_refs": [
      "product-prototypes"
    ],
    "stage_id": "frozen-product-candidate"
  },
  {
    "evidence_kind": "decision-eligibility",
    "predecessor_refs": [
      "frozen-product-candidate"
    ],
    "stage_id": "product-approval-eligibility"
  }
]
```


## Projection boundary

This generated view adds no canonical identity, lifecycle, conformance, or authority field.
