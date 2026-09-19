<!-- GENERATED FILE: canonical data is the sibling JSON file. -->

# Authority Claim Fixture

- Identity: `EXAMPLE-DEFINITION-REVIEW-CLAIM-001`
- Status: `candidate-unadmitted`
- Authority effect: `none`

## Canonical machine projection

- **Artifact Type Ref**: `cal.artifact-type.authority-claim/v1`
### Authority Surface

```json
{
  "path": "evidence/migrations/cyberalchemy-v2-to-lab/candidates/0015-authority-model-carrier/artifact-types/authority-model/v1/fixtures/valid/authority-model-record.json",
  "sha256": "4006b2717bc881871e19acb1d8d7cb6be4f8b33174dfd7e1cc15bf7938c19448"
}
```

### Basis

```json
[
  {
    "basis_kind": "evidence",
    "binding": {
      "path": "evidence/migrations/cyberalchemy-v2-to-lab/candidates/0015-authority-model-carrier/receipts/validation.json",
      "sha256": "3855d59404d6a616ba2768714b2692fd33335f22d2723f221f2c95d9ebb06fc0"
    },
    "supports": "The illustrative model and its routing checker passed local validation; this does not establish owner authority."
  }
]
```

- **Challenge Route**: `route:definition-governance-challenge`
- **Claim Ceiling**: `Illustrative claim with exact content bindings and model routing only. No authenticated owner, valid grant, gate verdict or execution authority.`
### Governed Object

```json
{
  "binding": {
    "path": "evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/definitions/authority-claim/v1/definition.json",
    "sha256": "16bcdd31f45a34fc062a8a316e5cc83814f1662049bb3d1f133329e746b83db4"
  },
  "object_ref": "cal.definition.authority-claim@1.0.0-candidate.1"
}
```

- **Intended Effect**: `review`
- **Kind Ref**: `definition`
- **Operation Ref**: `request-review`
- **Owner Ref**: `role:definition-owner`
- **Owner Route**: `route:definition-owner`
- **Posture Ref**: `candidate`
- **Profile**: `candidate:definition-authority-claim/v1`
- **Schema Version**: `cal-authority-claim-record/v1`
- **Scope Ref**: `scope:example-reconstruction`
### Source Direction

```json
{
  "canonical": "authority-claim-record.json",
  "human_projection": "AUTHORITY-CLAIM.md",
  "projection_policy": "generated-only"
}
```


## Projection boundary

This generated view adds no canonical identity, lifecycle, conformance, or authority field.
