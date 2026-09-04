<!-- GENERATED FILE: edit artifact.json and run generator.py. -->

# Identity Graph Artifact Type v1

> Generated from `artifact.json`; this view is explanatory and not canonical.

- Type: `cal.artifact-type.identity-graph/v1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic owner: `role:identity-graph-owner`
- Canonical instance: `identity-graph.json`
- Human projection: `IDENTITY-GRAPH.md`

## Semantic Definition bindings

- `cal.definition.identity-relation@1.0.0-candidate.1` — `admitted` — `authority/definitions/candidates/0006-craft-identity/definitions/identity-relation/v1/definition.json`
- `cal.definition.identity-carrier@1.0.0-candidate.1` — `admitted` — `authority/definitions/candidates/0007-cml07-semantic-closure/definitions/identity-carrier/v1/definition.json`
- `cal.definition.product@1.0.0-candidate.1` — `admitted` — `authority/definitions/candidates/0006-craft-identity/definitions/product/v1/definition.json`
- `CAV2-D60@1.0.0-candidate.1` — `admitted` — `authority/definitions/candidates/0006-craft-identity/definitions/project/v1/definition.json`
- `CAV2-D32@1.0.0-candidate.1` — `admitted` — `authority/definitions/candidates/0006-craft-identity/definitions/method/v1/definition.json`
- `CAV2-D59@1.0.0-candidate.1` — `admitted` — `authority/definitions/candidates/0006-craft-identity/definitions/goal/v1/definition.json`

## Distinct validation purpose

Proves explicit typed membership and directional relations across independent Product, Project, Method, and Goal identities with resolvable endpoints and valid signatures.

## Orthogonality rules

- **CML07-IG-01**: Every node has exactly one explicit identity kind; duplicate identity refs are rejected.
- **CML07-IG-02**: Every relation has its own identity and both endpoints must resolve to graph nodes.
- **CML07-IG-03**: Relation signatures are closed and directional; reverse labels are generated projections only.

## Four facets

- **Classification**: Identity Graph is an Artifact Type registration under admitted Artifact Type/v2; its identity, semantic kind, authority kind, and lifecycle posture are explicit independent fields.
- **Schema**: schema.json is a closed Draft 2020-12 contract for identity-graph.json; dependent identities are references or graph relations rather than inferred labels.
- **Human Continuation**: IDENTITY-GRAPH.md is generated deterministically from the canonical machine instance and adds no canonical field.
- **Machine Checkable**: Schema closure, admitted Definition bindings, explicit identity, hostile collapse/inference rejection, semantic checks, and projection parity are executable.

## Typed residue

- `CML07-IG-01-R1` (role:artifact-type-owner): No artifact-type-owner decision admits Identity Graph/v1. Consequence: Future identity instances cannot rely on Identity Graph/v1 as an admitted type.
- `CML07-IG-01-R2` (role:identity-graph-owner): No CML-07 S3 Craft identity carrier has been materialized. Consequence: Fixture validity must not be reported as a real Craft identity or identity-contract conformance.

## Claim ceiling

This package is a Identity Graph/v1 Artifact Type candidate. PASS establishes only candidate schema-and-artifact-type-contract conformance for its exact package and fixtures; it does not admit the type or any instance, execute S3, establish identity-contract, implementation, or runtime conformance, publish, deploy, or establish a stable release.
