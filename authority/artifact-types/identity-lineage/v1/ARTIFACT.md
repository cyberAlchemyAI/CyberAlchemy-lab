<!-- GENERATED FILE: edit artifact.json and run generator.py. -->

# Identity Lineage Artifact Type v1

> Generated from `artifact.json`; this view is explanatory and not canonical.

- Type: `cal.artifact-type.identity-lineage/v1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic owner: `role:craft-product-owner`
- Canonical instance: `lineage.json`
- Human projection: `LINEAGE.md`

## Semantic Definition bindings

- `cal.definition.identity-lineage@1.0.0-candidate.1` — `admitted` — `authority/definitions/candidates/0007-cml07-semantic-closure/definitions/identity-lineage/v1/definition.json`
- `cal.definition.identity-carrier@1.0.0-candidate.1` — `admitted` — `authority/definitions/candidates/0007-cml07-semantic-closure/definitions/identity-carrier/v1/definition.json`
- `cal.definition.product@1.0.0-candidate.1` — `admitted` — `authority/definitions/candidates/0006-craft-identity/definitions/product/v1/definition.json`

## Distinct validation purpose

Proves an explicit same-Product rename claim through separate predecessor, successor, continuity, change, owner, and evidence fields without substituting Context lineage or admission.

## Orthogonality rules

- **CML07-IL-01**: Lineage identity remains distinct from predecessor and successor identity.
- **CML07-IL-02**: A same-Product rename requires explicit preserved assertions and changed attributes.
- **CML07-IL-03**: Product lineage cannot be inferred from Context lineage, directory movement, or a name match.

## Four facets

- **Classification**: Identity Lineage is an Artifact Type registration under admitted Artifact Type/v2; its identity, semantic kind, authority kind, and lifecycle posture are explicit independent fields.
- **Schema**: schema.json is a closed Draft 2020-12 contract for lineage.json; dependent identities are references or graph relations rather than inferred labels.
- **Human Continuation**: LINEAGE.md is generated deterministically from the canonical machine instance and adds no canonical field.
- **Machine Checkable**: Schema closure, admitted Definition bindings, explicit identity, hostile collapse/inference rejection, semantic checks, and projection parity are executable.

## Typed residue

- `CML07-IL-01-R1` (role:artifact-type-owner): No artifact-type-owner decision admits Identity Lineage/v1. Consequence: Future identity instances cannot rely on Identity Lineage/v1 as an admitted type.
- `CML07-IL-01-R2` (role:craft-product-owner): No CML-07 S3 Craft identity carrier has been materialized. Consequence: Fixture validity must not be reported as a real Craft identity or identity-contract conformance.

## Claim ceiling

This package is a Identity Lineage/v1 Artifact Type candidate. PASS establishes only candidate schema-and-artifact-type-contract conformance for its exact package and fixtures; it does not admit the type or any instance, execute S3, establish identity-contract, implementation, or runtime conformance, publish, deploy, or establish a stable release.
