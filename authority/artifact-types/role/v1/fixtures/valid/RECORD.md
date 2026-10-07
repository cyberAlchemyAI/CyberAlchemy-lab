<!-- GENERATED FILE: canonical data is the sibling JSON file. -->

# Role Fixture

- Identity: `role:artifact-type-reviewer`
- Status: `candidate-unadmitted`
- Authority effect: `none`

## Canonical machine projection

- **Authority Boundary**: `The role may recommend an admission decision but does not admit, activate, publish, or deploy by itself.`
- **Challenge Route**: `route:role-challenge`
- **Claim Ceiling**: `This Role describes expected work and eligible authority relations; it grants no authority without a separate assignment and authority claim.`
### Eligible Authority Relation Kinds

```json
[
  "relation.claims-authority-over"
]
```

### Exclusions

```json
[
  "No implicit repository-owner authority",
  "No runtime permission grant"
]
```

### Functions

```json
[
  "Compare schema to admitted Definition",
  "Review example and validation receipt",
  "Record unresolved residue"
]
```

- **Kind**: `role`
- **Lifecycle State**: `active`
- **Name**: `Artifact Type Reviewer`
- **Owner Ref**: `role:artifact-type-owner`
- **Owner Route**: `role:role-model-owner`
- **Purpose**: `Review candidate Artifact Type contracts against admitted Definitions and evidence boundaries.`
### Responsibility Refs

```json
[
  "responsibility:artifact-type-review-quality"
]
```

- **Scope Ref**: `scope:cyberalchemy-lab-model-review`
### Successor Refs

```json
[]
```


## Projection boundary

This generated view adds no canonical identity, lifecycle, conformance, or authority field.
