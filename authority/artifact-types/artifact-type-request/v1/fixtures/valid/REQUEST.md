<!-- GENERATED FILE: canonical data is the sibling JSON file. -->

# Artifact Type Request Fixture

- Identity: `CAL-ATR-FIXTURE-RUNTIME-BINDING`
- Status: `candidate-unadmitted`
- Authority effect: `none`

## Canonical machine projection

- **Schema Version**: `cyberalchemy-lab-artifact-type-request/v1`
- **Version**: `1.0.0-candidate.1`
- **Owner Ref**: `role:artifact-type-owner`
- **Proposed Semantic Kind**: `runtime-binding`
- **Proposed Package Home Ref**: `implementation/bindings/example/v1`
### Resolution Evidence

```json
{
  "matches": [],
  "registry_ref": "candidate:cal.registry.artifact-types/v1"
}
```

### Compatibility Analysis

```json
[
  {
    "existing_type_ref": "cal.artifact-type.method-binding/v1",
    "rejection_reason": "Method Binding relates a method to a subject and does not validate runtime port, implementation, or recovery semantics."
  }
]
```

### Semantic Definition Refs

```json
[
  "cal.definition.artifact-type@1.0.0-candidate.1"
]
```

### Representation Proposal

```json
{
  "canonical_filename": "binding.json",
  "human_filename": "BINDING.md",
  "projection_policy": "generated-only"
}
```

- **Validation Purpose**: `Prove an explicit replaceable runtime implementation binding without transferring Product or source authority.`
- **Consumed As Subject**: `False`
### Expiry

```json
{
  "condition": "Resolved, rejected, or superseded by an exact Artifact Type candidate.",
  "superseded_by": null
}
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

- **Claim Ceiling**: `Candidate intake fixture only; it is not a runtime binding or an Artifact Type.`

## Projection boundary

This generated view adds no canonical identity, lifecycle, conformance, or authority field.
