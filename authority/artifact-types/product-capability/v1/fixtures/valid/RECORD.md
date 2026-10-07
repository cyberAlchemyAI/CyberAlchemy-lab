<!-- GENERATED FILE: canonical data is the sibling JSON file. -->

# Product Capability Fixture

- Identity: `capability:craft:governed-definition-admission`
- Status: `candidate-unadmitted`
- Authority effect: `none`

## Canonical machine projection

### Acceptance Conditions

```json
[
  "Every admitted Definition version is bound by exact path and digest",
  "The canonical registry and human index agree on admitted current versions",
  "Admission does not activate downstream consumers"
]
```

- **Challenge Route**: `route:definition-governance-challenge`
### Consumer Refs

```json
[
  "consumer:definition-registry",
  "consumer:repository-inventory"
]
```

### Context Policy Refs

```json
[
  "policy:definition-authority-separation",
  "policy:no-consumer-activation-by-admission"
]
```

### Evidence Refs

```json
[]
```

### Exclusions

```json
[
  "Runtime activation",
  "Artifact Type admission",
  "Authentication of external identity claims"
]
```

### Input Contract Refs

```json
[
  "contract:definition-candidate",
  "contract:source-admission-selection"
]
```

- **Kind**: `product-capability`
### Lifecycle Posture

```json
{
  "commitment_ref": null,
  "evidence_refs": [],
  "kind": "product-capability",
  "owner_ref": "role:definition-owner",
  "provenance_refs": [
    "migration-contract:type.product-capability"
  ],
  "residue_refs": [
    "residue:capability-owner-adoption-required"
  ],
  "status": "draft",
  "status_vocabulary_ref": "profile.capability-lifecycle"
}
```

- **Name**: `Governed Definition Admission`
- **Outcome**: `Repository owners can admit exact semantic Definitions while preserving provenance, review authority, drift visibility, and separation from consumer activation.`
### Output Contract Refs

```json
[
  "contract:definition-admission-decision",
  "contract:definition-registry-postimage"
]
```

- **Owner Ref**: `role:definition-owner`
### Owner Routes

```json
[
  "role:definition-owner",
  "route:definition-governance-challenge"
]
```

### Participant Refs

```json
[
  "role:definition-owner",
  "role:source-admission-owner"
]
```

- **Product Ref**: `CA2-PRODUCT-CRAFT`
- **Product Thesis Ref**: `product-thesis:craft`
### Realization Binding Refs

```json
[
  "binding:craft:governed-definition-admission:workflow-v1"
]
```

### Revision History

```json
[]
```

- **Scope Ref**: `scope:craft-semantic-governance`
### Successor Refs

```json
[]
```

### Thesis Outcome Refs

```json
[
  "product-thesis:craft#outcome-authoritative-state"
]
```


## Projection boundary

This generated view adds no canonical identity, lifecycle, conformance, or authority field.
