<!-- GENERATED FILE: canonical data is the sibling JSON file. -->

# Discipline Fixture

- Identity: `CANDIDATE-REPOSITORY-STEWARDSHIP-001`
- Status: `candidate-unadmitted`
- Authority effect: `none`

## Canonical machine projection

- **Artifact Type Ref**: `cal.artifact-type.discipline/v1`
- **Boundaries**: `Evidence supports repeated local validation only. It does not prove continuous stewardship or grant definition, constitution, implementation or promotion authority.`
### Capabilities

```json
[
  {
    "artifact": {
      "path": "evidence/migrations/cyberalchemy-v2-to-lab/candidates/0009-schema-carrier/artifact-types/schema/v1/artifact.json",
      "sha256": "98a2bec254ba7b8fd792d53ae3876d2e60aaf6be5874259da9585174b4110c70"
    },
    "capability_ref": "capability:schema"
  },
  {
    "artifact": {
      "path": "evidence/migrations/cyberalchemy-v2-to-lab/candidates/0011-method-carrier/artifact-types/method/v1/artifact.json",
      "sha256": "48871f5d26f50be07cd8a32c74ac8e2a344d5d339511d3838d3416e866de3d37"
    },
    "capability_ref": "capability:method"
  }
]
```

- **Claim Ceiling**: `Candidate stewardship declaration with exact local validation evidence only; no automatic maturity promotion or hardening completion.`
- **Evidence Profile**: `candidate:validation-material-map/v1`
- **Governance Route Ref**: `route:discipline-governance`
### Hardening Move

```json
{
  "action": "Review coverage of source tracing and validation across remaining capabilities, then record missing checks and owners.",
  "completion_evidence_required": "An exact review record covering the remaining capability inventory and every unresolved obligation.",
  "owner_ref": "role:repository-steward",
  "route_ref": "route:repository-maintenance-review"
}
```

- **Maturity Status**: `candidate`
- **Practice**: `Keep reconstructed repository surfaces traceable, validated and resumable through exact validation records.`
### Recurrence Evidence

```json
[
  {
    "capability_ref": "capability:schema",
    "occurrence_id": "validation:schema",
    "receipt": {
      "path": "evidence/migrations/cyberalchemy-v2-to-lab/candidates/0009-schema-carrier/receipts/validation.json",
      "sha256": "455bf930481d2e415a51880dc6369bf0197fb4a95ca65847226e8594439df64b"
    }
  },
  {
    "capability_ref": "capability:method",
    "occurrence_id": "validation:method",
    "receipt": {
      "path": "evidence/migrations/cyberalchemy-v2-to-lab/candidates/0011-method-carrier/receipts/validation.json",
      "sha256": "66678feadef02f0d7a87911a3d47aa76d785f8f922ee9eb8636e0d4e771b9c40"
    }
  }
]
```

- **Schema Version**: `cal-discipline-record/v1`
- **Scope Ref**: `scope:lab-reconstruction-stewardship`
### Source Direction

```json
{
  "canonical": "discipline-record.json",
  "human_projection": "DISCIPLINE.md",
  "projection_policy": "generated-only"
}
```

- **Steward Ref**: `role:repository-steward`

## Projection boundary

This generated view adds no canonical identity, lifecycle, conformance, or authority field.
