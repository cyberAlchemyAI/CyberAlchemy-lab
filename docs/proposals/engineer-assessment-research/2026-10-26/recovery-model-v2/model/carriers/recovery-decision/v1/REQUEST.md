<!-- GENERATED FILE: canonical data is the sibling JSON file. -->

# Artifact Type Request Fixture

- Identity: `EA-ATR-RECOVERY-DECISION-001`
- Status: `candidate-unadmitted`
- Authority effect: `none`

## Canonical machine projection

- **Claim Ceiling**: `Candidate request only; no Lab type admission, operational decision, media receipt or participant authority.`
### Compatibility Analysis

```json
[
  {
    "existing_type_ref": "cal.artifact-type.decision/v2",
    "rejection_reason": "The Lab Decision carrier is an authority act; this operational receipt evaluates an administration rule and cannot admit policy, authorize recruitment or replace an owner decision."
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
- **Proposed Package Home Ref**: `model/carriers/recovery-decision/v1`
- **Proposed Semantic Kind**: `recovery-decision`
### Representation Proposal

```json
{
  "canonical_filename": "decision.json",
  "human_filename": "DECISION.md",
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
  "ea.recovery-decision@0.1.0-candidate.1"
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

- **Validation Purpose**: `Validate one runtime disposition of an affected session against pinned failure evidence and recovery rule, including same-slot successor and non-scoring boundaries.`
- **Version**: `0.1.0-candidate.1`

## Projection boundary

This generated view adds no canonical identity, lifecycle, conformance, or authority field.
