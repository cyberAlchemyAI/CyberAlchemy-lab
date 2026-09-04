<!-- GENERATED FILE: edit artifact.json and run generator.py. -->

# Project Identity Artifact Type v1

> Generated from `artifact.json`; this view is explanatory and not canonical.

- Type: `cal.artifact-type.project-identity/v1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic owner: `role:craft-project-owner`
- Canonical instance: `project.json`
- Human projection: `PROJECT.md`

## Semantic Definition bindings

- `CAV2-D60@1.0.0-candidate.1` — `admitted` — `authority/definitions/candidates/0006-craft-identity/definitions/project/v1/definition.json`
- `cal.definition.identity-carrier@1.0.0-candidate.1` — `admitted` — `authority/definitions/candidates/0007-cml07-semantic-closure/definitions/identity-carrier/v1/definition.json`

## Distinct validation purpose

Proves a Project identity and coordination scope without treating the Project as its Product, Method, Goal, Bounded Context, or containing directory.

## Orthogonality rules

- **CML07-PJ-01**: Project identity is supplied only by project_id and never by directory placement.
- **CML07-PJ-02**: A Project coordinates work but does not own Product or Method meaning.
- **CML07-PJ-03**: Product and Goal participation must be expressed through separate identity-graph relations.

## Four facets

- **Classification**: Project Identity is an Artifact Type registration under admitted Artifact Type/v2; its identity, semantic kind, authority kind, and lifecycle posture are explicit independent fields.
- **Schema**: schema.json is a closed Draft 2020-12 contract for project.json; dependent identities are references or graph relations rather than inferred labels.
- **Human Continuation**: PROJECT.md is generated deterministically from the canonical machine instance and adds no canonical field.
- **Machine Checkable**: Schema closure, admitted Definition bindings, explicit identity, hostile collapse/inference rejection, semantic checks, and projection parity are executable.

## Typed residue

- `CML07-PJ-01-R1` (role:artifact-type-owner): No artifact-type-owner decision admits Project Identity/v1. Consequence: Future identity instances cannot rely on Project Identity/v1 as an admitted type.
- `CML07-PJ-01-R2` (role:craft-project-owner): No CML-07 S3 Craft identity carrier has been materialized. Consequence: Fixture validity must not be reported as a real Craft identity or identity-contract conformance.

## Claim ceiling

This package is a Project Identity/v1 Artifact Type candidate. PASS establishes only candidate schema-and-artifact-type-contract conformance for its exact package and fixtures; it does not admit the type or any instance, execute S3, establish identity-contract, implementation, or runtime conformance, publish, deploy, or establish a stable release.
