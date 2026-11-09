<!-- GENERATED FILE: canonical data is the sibling JSON file. -->

# Artifact Type Request Fixture

- Identity: `EA-ATR-UPLOAD-ATTEMPT-001`
- Status: `candidate-unadmitted`
- Authority effect: `none`

## Canonical machine projection

- **Claim Ceiling**: `Candidate request only; no Lab type admission, operational decision, media receipt or participant authority.`
### Compatibility Analysis

```json
[
  {
    "existing_type_ref": "cal.artifact-type.operational-observation/v1",
    "rejection_reason": "An Operational Observation is an attributable datum; a resumable upload needs an idempotent transfer state machine, part lineage and completion/abort invariants."
  }
]
```

- **Consumed As Subject**: `False`
### Expiry

```json
{
  "condition": "Resolved, rejected or superseded after exact semantic and Artifact Type owner review.",
  "superseded_by": null
}
```

- **Owner Ref**: `role:ea-artifact-type-owner-unassigned`
- **Proposed Package Home Ref**: `model/carriers/upload-attempt/v1`
- **Proposed Semantic Kind**: `upload-attempt`
### Representation Proposal

```json
{
  "canonical_filename": "upload.json",
  "human_filename": "UPLOAD.md",
  "projection_policy": "generated-only"
}
```

### Resolution Evidence

```json
{
  "matches": [],
  "registry_ref": "authority/admissions/governance-transaction-surface/v1/registries/artifact-type-registry.json#sha256=b2a34b5e27d49d94ee41c139ead7f66fcdc5cef163bced4d86d2c2bf03ab3390"
}
```

- **Schema Version**: `cyberalchemy-lab-artifact-type-request/v1`
### Semantic Definition Refs

```json
[
  "ea.upload-attempt@0.1.0-candidate.1"
]
```

### Source Direction

```json
{
  "canonical": "request.json",
  "generator_ref": "cal.generator.artifact-surface/v1",
  "human_projection": "REQUEST.md",
  "projection_policy": "generated-only"
}
```

- **Validation Purpose**: `Validate one resumable private media transfer with part receipts, source digest, session pin and final verification state, without equating upload with accepted response.`
- **Version**: `0.1.0-candidate.1`

## Projection boundary

This generated view adds no canonical identity, lifecycle, conformance, or authority field.
