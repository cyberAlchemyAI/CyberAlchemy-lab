<!-- GENERATED FILE: canonical data is the sibling JSON file. -->

# Context Profile Fixture

- Identity: `context-profile:governed-review`
- Status: `candidate-unadmitted`
- Authority effect: `none`

## Canonical machine projection

### Allowed Context Kinds

```json
[
  "product",
  "project",
  "goal"
]
```

### Allowed Source Kinds

```json
[
  "admitted authority",
  "digest-bound candidate",
  "validation receipt"
]
```

- **Challenge Route**: `route:context-policy-challenge`
- **Claim Ceiling**: `This profile constrains Context construction and resolution. It is not a Context identity or resolved view.`
### Consumer Requirements

```json
[
  "Name the review consumer",
  "Declare intended use"
]
```

### Exclusion Policy

```json
[
  "Exclude secrets and live operator state",
  "Exclude unbound narrative claims"
]
```

- **Freshness Policy**: `Re-resolve when any bound source digest changes.`
- **Kind**: `context-profile`
- **Lifecycle State**: `active`
- **Name**: `Governed repository review`
### Output Constraints

```json
[
  "Preserve included and excluded material",
  "Expose limitations and expiry"
]
```

- **Owner Ref**: `role:artifact-type-owner`
- **Owner Route**: `role:context-policy-owner`
### Required Anchor Fields

```json
[
  "product_ref",
  "purpose",
  "consumer_refs",
  "subject_scope",
  "source_policy_refs"
]
```

- **Scope Ref**: `scope:cyberalchemy-lab-model-review`
### Successor Refs

```json
[]
```

- **Successor Rule**: `Create a successor when anchor rules, allowed sources, or output obligations change materially.`

## Projection boundary

This generated view adds no canonical identity, lifecycle, conformance, or authority field.
