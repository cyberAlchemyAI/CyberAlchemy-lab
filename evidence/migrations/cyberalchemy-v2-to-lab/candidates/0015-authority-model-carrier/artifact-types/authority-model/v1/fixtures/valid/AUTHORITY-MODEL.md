<!-- GENERATED FILE: canonical data is the sibling JSON file. -->

# Authority Model Fixture

- Identity: `EXAMPLE-RECONSTRUCTION-AUTHORITY-001`
- Status: `candidate-unadmitted`
- Authority effect: `none`

## Canonical machine projection

- **Amendment Route**: `route:authority-model-owner-review`
- **Artifact Type Ref**: `cal.artifact-type.authority-model/v1`
### Authority Kinds

```json
[
  "definition",
  "evidence"
]
```

- **Claim Ceiling**: `Candidate routing map and supplied claim assertions only; no actor authentication, gate verdict or authority grant.`
- **Conflict Rule**: `reject-overlapping-kind-posture-rules`
### Effects

```json
[
  "review",
  "admit"
]
```

### Operations

```json
[
  {
    "effect_ref": "review",
    "operation_id": "request-review"
  },
  {
    "effect_ref": "admit",
    "operation_id": "request-admission"
  }
]
```

- **Owner Ref**: `role:authority-model-owner`
### Postures

```json
[
  "candidate"
]
```

- **Profile**: `candidate:closed-authority-routing/v1`
### Rules

```json
[
  {
    "allowed_effects": [
      "review"
    ],
    "blocked_effects": [
      "admit"
    ],
    "gate_ref": "gate:definition-review",
    "kind_ref": "definition",
    "non_collapse_rules": [
      "Candidate construction is not admission."
    ],
    "owner_route": "route:definition-owner",
    "posture_ref": "candidate",
    "rule_id": "definition-candidate",
    "validation_surface_ref": "surface:definition-validation"
  },
  {
    "allowed_effects": [
      "review"
    ],
    "blocked_effects": [
      "admit"
    ],
    "gate_ref": "gate:evidence-review",
    "kind_ref": "evidence",
    "non_collapse_rules": [
      "Evidence does not become semantic authority by passing a check."
    ],
    "owner_route": "route:evidence-owner",
    "posture_ref": "candidate",
    "rule_id": "evidence-candidate",
    "validation_surface_ref": "surface:evidence-validation"
  }
]
```

- **Schema Version**: `cal-authority-model-record/v1`
- **Scope Ref**: `scope:example-reconstruction`
### Source Direction

```json
{
  "canonical": "authority-model-record.json",
  "human_projection": "AUTHORITY-MODEL.md",
  "projection_policy": "generated-only"
}
```

- **Unknown Kind Rule**: `blocked-until-owner-amends-model`

## Projection boundary

This generated view adds no canonical identity, lifecycle, conformance, or authority field.
