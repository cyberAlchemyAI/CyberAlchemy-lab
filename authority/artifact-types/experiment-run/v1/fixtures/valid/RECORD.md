<!-- GENERATED FILE: canonical data is the sibling JSON file. -->

# Experiment Run Fixture

- Identity: `experiment-run:definition-normalization-residue:2026-10-05`
- Status: `candidate-unadmitted`
- Authority effect: `none`

## Canonical machine projection

- **Challenge Route**: `route:research-challenge`
- **Claim Ceiling**: `This run records one execution. Completion does not establish a Finding or product value.`
- **Design Ref**: `experiment-design:definition-normalization-residue`
- **Design Version Ref**: `experiment-design:definition-normalization-residue@1.0.0-candidate.1`
### Deviations

```json
[]
```

- **Environment**: `CyberAlchemy Lab local checkout at revision review-2026-10-05`
- **Evidence Set Ref**: `evidence-set:definition-normalization-residue-run-2026-10-05`
### Goal Refs

```json
[
  "goal:reduce-unresolved-definition-residue"
]
```

### Input Refs

```json
[
  "fixture:unresolved-source-terms/v1",
  "vocabulary:normalization-residue-classes/v1"
]
```

### Interventions

```json
[
  "Apply reviewed semantic-key map before residue classification"
]
```

- **Kind**: `experiment-run`
### Measurement Result Refs

```json
[
  "measurement-result:definition-normalization-residue-entropy:2026-10-05"
]
```

### Observation Refs

```json
[
  "observation:definition-normalization-residue-classes"
]
```

- **Owner Ref**: `role:artifact-type-owner`
- **Owner Route**: `role:research-owner`
### Period

```json
{
  "end": "2026-10-05T14:20:00Z",
  "start": "2026-10-05T14:00:00Z"
}
```

### Product Evaluation Context

```json
{
  "evaluation_purpose": "Preserve the exact Product evaluation scope from the design without converting this run into Product evidence acceptance or an owner decision.",
  "product_capability_refs": [
    "capability:craft:governed-definition-admission"
  ],
  "product_ref": "CA2-PRODUCT-CRAFT",
  "product_thesis_ref": "product-thesis:craft",
  "realization_binding_refs": [
    "binding:craft:governed-definition-admission:workflow-v1"
  ],
  "thesis_hypothesis_refs": [],
  "thesis_outcome_refs": [
    "product-thesis:craft#outcome-authoritative-state"
  ]
}
```

- **Project Ref**: `project:lab-semantic-governance`
### Research Refs

```json
[
  "research-inquiry:definition-normalization-residue"
]
```

- **Run State**: `completed`
- **Scope Ref**: `scope:cyberalchemy-lab-model-review`
- **Stop Reason**: `None`

## Projection boundary

This generated view adds no canonical identity, lifecycle, conformance, or authority field.
