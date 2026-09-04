<!-- GENERATED FILE: canonical data is the sibling JSON fixture. -->

# Method Binding Fixture

- Identity: `fixture:binding:craft-method-to-project`
- Status: `candidate-unadmitted`
- Authority effect: `none`

## Canonical field projection

- **Schema Version**: `cyberalchemy-lab-method-binding/v1`
- **Version**: `1.0.0-candidate.1`
- **Name**: `Craft Method applied to migration Project`
### Semantic Definition Refs

```json
[
  "CAV2-D32@1.0.0-candidate.1",
  "CAV2-D20@1.0.0-candidate.1",
  "cal.definition.identity-relation@1.0.0-candidate.1",
  "cal.definition.identity-carrier@1.0.0-candidate.1"
]
```

- **Method Ref**: `CAV2-D20`
- **Subject Ref**: `fixture:project:craft-migration`
- **Subject Kind**: `project`
### Application Scope

```json
{
  "excludes": [
    "Changing Method meaning",
    "Project ownership inference"
  ],
  "includes": [
    "Definition-first migration sequencing"
  ]
}
```

- **Binding Owner Ref**: `role:craft-method-owner`
### Evidence Refs

```json
[
  "fixture:evidence:method-binding"
]
```

- **Challenge Route**: `role:craft-method-owner`
- **Claim Ceiling**: `Fixture only; it does not activate a Method binding or authorize execution.`

## Projection boundary

This document is generated from the canonical machine fixture and adds no identity, relation, lifecycle, conformance, or authority field.
