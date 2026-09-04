<!-- GENERATED FILE: edit artifact.json and run generator.py. -->

# Method Binding Artifact Type v1

> Generated from `artifact.json`; this view is explanatory and not canonical.

- Type: `cal.artifact-type.method-binding/v1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic owner: `role:craft-method-owner`
- Canonical instance: `method-binding.json`
- Human projection: `METHOD-BINDING.md`

## Semantic Definition bindings

- `CAV2-D32@1.0.0-candidate.1` — `admitted` — `authority/definitions/candidates/0006-craft-identity/definitions/method/v1/definition.json`
- `CAV2-D20@1.0.0-candidate.1` — `admitted` — `authority/definitions/candidates/0006-craft-identity/definitions/craft-method/v1/definition.json`
- `cal.definition.identity-relation@1.0.0-candidate.1` — `admitted` — `authority/definitions/candidates/0006-craft-identity/definitions/identity-relation/v1/definition.json`
- `cal.definition.identity-carrier@1.0.0-candidate.1` — `admitted` — `authority/definitions/candidates/0007-cml07-semantic-closure/definitions/identity-carrier/v1/definition.json`

## Distinct validation purpose

Proves one independently identified Method Binding connects an exact Method to one Product or Project scope without changing either endpoint meaning or granting execution authority.

## Orthogonality rules

- **CML07-MB-01**: The binding, Method, and subject retain three distinct identities.
- **CML07-MB-02**: subject_kind classifies the explicit subject_ref and cannot be inferred from its path or label.
- **CML07-MB-03**: A Method Binding applies a Method; it neither redefines the Method nor grants execution authority.

## Four facets

- **Classification**: Method Binding is an Artifact Type registration under admitted Artifact Type/v2; its identity, semantic kind, authority kind, and lifecycle posture are explicit independent fields.
- **Schema**: schema.json is a closed Draft 2020-12 contract for method-binding.json; dependent identities are references or graph relations rather than inferred labels.
- **Human Continuation**: METHOD-BINDING.md is generated deterministically from the canonical machine instance and adds no canonical field.
- **Machine Checkable**: Schema closure, admitted Definition bindings, explicit identity, hostile collapse/inference rejection, semantic checks, and projection parity are executable.

## Typed residue

- `CML07-MB-01-R1` (role:artifact-type-owner): No artifact-type-owner decision admits Method Binding/v1. Consequence: Future identity instances cannot rely on Method Binding/v1 as an admitted type.
- `CML07-MB-01-R2` (role:craft-method-owner): No CML-07 S3 Craft identity carrier has been materialized. Consequence: Fixture validity must not be reported as a real Craft identity or identity-contract conformance.

## Claim ceiling

This package is a Method Binding/v1 Artifact Type candidate. PASS establishes only candidate schema-and-artifact-type-contract conformance for its exact package and fixtures; it does not admit the type or any instance, execute S3, establish identity-contract, implementation, or runtime conformance, publish, deploy, or establish a stable release.
