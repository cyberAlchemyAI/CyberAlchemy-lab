<!-- GENERATED FILE: canonical data is the sibling JSON file. -->

# Context Fixture

- Identity: `context:lab-artifact-type-admission`
- Status: `candidate-unadmitted`
- Authority effect: `none`

## Canonical machine projection

### Bounded Context Refs

```json
[
  "bounded-context:semantic-governance"
]
```

- **Challenge Route**: `route:context-challenge`
- **Claim Ceiling**: `This Context defines relevance and interpretation boundaries. It is not a Bounded Context, source assertion, or Context View.`
### Consumer Refs

```json
[
  "consumer:artifact-type-review"
]
```

- **Context Kind**: `project`
- **Goal Ref**: `None`
### Intended Uses

```json
[
  "Artifact Type review",
  "Admission decision preparation"
]
```

- **Kind**: `context`
- **Lifecycle State**: `active`
- **Owner Ref**: `role:artifact-type-owner`
- **Owner Route**: `role:context-owner`
- **Product Ref**: `product:craft`
- **Profile Ref**: `context-profile:governed-review`
- **Project Ref**: `project:lab-semantic-governance`
- **Purpose**: `Resolve evidence needed to review and admit Artifact Type contracts.`
### Revision History

```json
[]
```

- **Scope Ref**: `scope:cyberalchemy-lab-model-review`
### Source Policy Refs

```json
[
  "policy:admitted-authority-first",
  "policy:exact-digest-provenance"
]
```

### Subject Scope

```json
[
  "Definitions",
  "Artifact Type packages",
  "validation receipts",
  "admission decisions"
]
```

### Successor Refs

```json
[]
```


## Projection boundary

This generated view adds no canonical identity, lifecycle, conformance, or authority field.
