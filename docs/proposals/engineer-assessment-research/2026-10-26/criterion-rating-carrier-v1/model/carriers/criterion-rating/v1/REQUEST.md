<!-- GENERATED FILE: canonical data is the sibling JSON file. -->

# Artifact Type Request Fixture

- Identity: `EA-ATR-CRITERION-RATING-001`
- Status: `candidate-unadmitted`
- Authority effect: `none`

## Canonical machine projection

- **Claim Ceiling**: `Artifact Type Request candidate only; no Criterion Rating type admission, real rating instance, scoring validity or hiring use.`
### Compatibility Analysis

```json
[
  {
    "existing_type_ref": "cal.artifact-type.measurement-result/v1",
    "rejection_reason": "The selected Measurement Result carrier is for bounded numeric/residuality observables and requires entropy and method fields; it does not preserve one case/rubric dimension, rater, evidence span, or NA/UNK distinction."
  },
  {
    "existing_type_ref": "cal.artifact-type.evaluation/v1",
    "rejection_reason": "An Evaluation summarizes an assessed subject and decision scope; it is not one independently submitted anchored response-dimension judgment with missingness and source evidence."
  },
  {
    "existing_type_ref": "cal.artifact-type.observation/v1",
    "rejection_reason": "An Observation can record an event but does not enforce the specific rubric anchor, rater independence, evidence citation and missingness contract of a Criterion Rating."
  }
]
```

- **Consumed As Subject**: `False`
### Expiry

```json
{
  "condition": "Resolved, rejected or superseded by an exact Artifact Type candidate after semantic definition and owner review.",
  "superseded_by": null
}
```

- **Owner Ref**: `role:ea-artifact-type-owner-unassigned`
- **Proposed Package Home Ref**: `model/carriers/criterion-rating/v1`
- **Proposed Semantic Kind**: `criterion-rating`
### Representation Proposal

```json
{
  "canonical_filename": "rating.json",
  "human_filename": "RATING.md",
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
  "ea.criterion-rating@0.1.0-candidate.1"
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

- **Validation Purpose**: `Validate one rater or scorer judgment on one fairly elicited rubric dimension of one pinned response, preserving source evidence, independence, missingness and exact versions without inferring stable ability.`
- **Version**: `0.1.0-candidate.1`

## Projection boundary

This generated view adds no canonical identity, lifecycle, conformance, or authority field.
