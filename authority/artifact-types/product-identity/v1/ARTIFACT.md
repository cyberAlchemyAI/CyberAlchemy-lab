<!-- GENERATED FILE: edit artifact.json and run generator.py. -->

# Product Identity Artifact Type v1

> Generated from `artifact.json`; this view is explanatory and not canonical.

- Type: `cal.artifact-type.product-identity/v1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic owner: `role:craft-product-owner`
- Canonical instance: `product.json`
- Human projection: `PRODUCT.md`

## Semantic Definition bindings

- `cal.definition.product@1.0.0-candidate.1` — `admitted` — `authority/definitions/candidates/0006-craft-identity/definitions/product/v1/definition.json`
- `cal.definition.identity-carrier@1.0.0-candidate.1` — `admitted` — `authority/definitions/candidates/0007-cml07-semantic-closure/definitions/identity-carrier/v1/definition.json`

## Distinct validation purpose

Proves a Product identity carries its own meaning, scope, owner, lineage reference, and evidence without absorbing Project, Method, Goal, context, or directory identity.

## Orthogonality rules

- **CML07-PI-01**: Product identity is supplied only by product_id; directory placement and display name cannot create it.
- **CML07-PI-02**: Product scope cannot canonically embed Project, Method, Goal, or Bounded Context identity.
- **CML07-PI-03**: Product lineage is an explicit reference to a separate lineage carrier, not an inferred rename label.

## Four facets

- **Classification**: Product Identity is an Artifact Type registration under admitted Artifact Type/v2; its identity, semantic kind, authority kind, and lifecycle posture are explicit independent fields.
- **Schema**: schema.json is a closed Draft 2020-12 contract for product.json; dependent identities are references or graph relations rather than inferred labels.
- **Human Continuation**: PRODUCT.md is generated deterministically from the canonical machine instance and adds no canonical field.
- **Machine Checkable**: Schema closure, admitted Definition bindings, explicit identity, hostile collapse/inference rejection, semantic checks, and projection parity are executable.

## Typed residue

- `CML07-PI-01-R1` (role:artifact-type-owner): No artifact-type-owner decision admits Product Identity/v1. Consequence: Future identity instances cannot rely on Product Identity/v1 as an admitted type.
- `CML07-PI-01-R2` (role:craft-product-owner): No CML-07 S3 Craft identity carrier has been materialized. Consequence: Fixture validity must not be reported as a real Craft identity or identity-contract conformance.

## Claim ceiling

This package is a Product Identity/v1 Artifact Type candidate. PASS establishes only candidate schema-and-artifact-type-contract conformance for its exact package and fixtures; it does not admit the type or any instance, execute S3, establish identity-contract, implementation, or runtime conformance, publish, deploy, or establish a stable release.
