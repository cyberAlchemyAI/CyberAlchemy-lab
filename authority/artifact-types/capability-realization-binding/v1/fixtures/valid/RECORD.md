<!-- GENERATED FILE: canonical data is the sibling JSON file. -->

# Capability Realization Binding Fixture

- Identity: `binding:craft:governed-definition-admission:workflow-v1`
- Status: `candidate-unadmitted`
- Authority effect: `none`

## Canonical machine projection

- **Adoption Decision Ref**: `None`
- **Binding State**: `candidate`
- **Binding Version**: `1.0.0-candidate.1`
- **Capability Ref**: `capability:craft:governed-definition-admission`
- **Capability Version Ref**: `capability:craft:governed-definition-admission@1.0.0-candidate.1`
- **Challenge Route**: `route:definition-governance-challenge`
### Conformance Refs

```json
[]
```

### Contract

```json
{
  "context_policy_refs": [
    "policy:definition-authority-separation",
    "policy:no-consumer-activation-by-admission"
  ],
  "input_contract_refs": [
    "contract:definition-candidate",
    "contract:source-admission-selection"
  ],
  "output_contract_refs": [
    "contract:definition-admission-decision",
    "contract:definition-registry-postimage"
  ]
}
```

- **Kind**: `capability-realization-binding`
### Limitations

```json
[
  "Candidate binding does not adopt or activate the workflow",
  "Schema conformance does not prove runtime or Product outcome conformance"
]
```

### Observation Refs

```json
[]
```

- **Owner Ref**: `role:definition-owner`
- **Owner Route**: `role:definition-owner`
### Realization Refs

```json
[
  {
    "contract_ref": "contract:definition-admission-workflow/v1",
    "owner_ref": "role:definition-owner",
    "realization_kind": "workflow",
    "realization_ref": "workflow:definition-admission:v1"
  }
]
```

- **Scope Ref**: `scope:craft-semantic-governance`
### Successor Refs

```json
[]
```


## Projection boundary

This generated view adds no canonical identity, lifecycle, conformance, or authority field.
