<!-- GENERATED FILE: canonical data is the sibling JSON file. -->

# Artifact Type Request Fixture

- Identity: `CAL-ATR-FIXTURE-RUNTIME-BINDING`
- Status: `candidate-unadmitted`
- Authority effect: `none`

## Canonical machine projection

- **Claim Ceiling**: `Candidate intake fixture only; it is not a runtime binding or an Artifact Type.`
### Compatibility Analysis

```json
[
  {
    "existing_type_ref": "cal.artifact-type.method-binding/v1",
    "rejection_reason": "Method Binding relates a method to a subject and does not validate runtime port, implementation, or recovery semantics."
  }
]
```

- **Consumed As Subject**: `False`
### Expiry

```json
{
  "condition": "Resolved, rejected, or superseded by an exact Artifact Type candidate.",
  "superseded_by": null
}
```

- **Owner Ref**: `role:artifact-type-owner`
### Proposed Discriminator

```json
{
  "path": "/schema_version",
  "value": "cyberalchemy-lab-ontology-product-runtime-binding/v1"
}
```

- **Proposed Package Home Ref**: `implementation/bindings/example/v1`
- **Proposed Semantic Kind**: `runtime-binding`
### Representation Proposal

```json
{
  "canonical_filename": "binding.json",
  "human_filename": "BINDING.md",
  "projection_policy": "generated-only"
}
```

### Resolution Evidence

```json
{
  "matches": [],
  "registry_ref": "candidate:cal.registry.artifact-types/v1"
}
```

- **Schema Version**: `cyberalchemy-lab-artifact-type-request/v1`
### Semantic Definition Refs

```json
[
  "cal.definition.artifact-type@1.0.0-candidate.1"
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

- **Validation Purpose**: `Prove an explicit replaceable runtime implementation binding without transferring Product or source authority.`
- **Version**: `1.0.0-candidate.1`

## Projection boundary

This generated view adds no canonical identity, lifecycle, conformance, or authority field.
