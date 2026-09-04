<!-- GENERATED FILE: edit artifact.json and run generator.py. -->

# Goal Artifact Type v1

> Generated from `artifact.json`; this view is explanatory and not canonical.

- Type: `cal.artifact-type.goal/v1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Semantic owner: `role:craft-goal-owner`
- Canonical instance: `goal.json`
- Human projection: `GOAL.md`

## Semantic Definition bindings

- `CAV2-D59@1.0.0-candidate.1` — `admitted` — `authority/definitions/candidates/0006-craft-identity/definitions/goal/v1/definition.json`
- `cal.definition.identity-carrier@1.0.0-candidate.1` — `admitted` — `authority/definitions/candidates/0007-cml07-semantic-closure/definitions/identity-carrier/v1/definition.json`

## Distinct validation purpose

Proves a Goal carries an intended outcome and evidence obligations without absorbing Project or Product identity and without representing validation as achievement.

## Orthogonality rules

- **CML07-GO-01**: Goal identity is independent from the Project that pursues it and the Product it may benefit.
- **CML07-GO-02**: Success conditions define evaluation obligations; they do not encode achieved state.
- **CML07-GO-03**: Project pursuit is an explicit identity-graph relation, not a canonical Goal field.

## Four facets

- **Classification**: Goal is an Artifact Type registration under admitted Artifact Type/v2; its identity, semantic kind, authority kind, and lifecycle posture are explicit independent fields.
- **Schema**: schema.json is a closed Draft 2020-12 contract for goal.json; dependent identities are references or graph relations rather than inferred labels.
- **Human Continuation**: GOAL.md is generated deterministically from the canonical machine instance and adds no canonical field.
- **Machine Checkable**: Schema closure, admitted Definition bindings, explicit identity, hostile collapse/inference rejection, semantic checks, and projection parity are executable.

## Typed residue

- `CML07-GO-01-R1` (role:artifact-type-owner): No artifact-type-owner decision admits Goal/v1. Consequence: Future identity instances cannot rely on Goal/v1 as an admitted type.
- `CML07-GO-01-R2` (role:craft-goal-owner): No CML-07 S3 Craft identity carrier has been materialized. Consequence: Fixture validity must not be reported as a real Craft identity or identity-contract conformance.

## Claim ceiling

This package is a Goal/v1 Artifact Type candidate. PASS establishes only candidate schema-and-artifact-type-contract conformance for its exact package and fixtures; it does not admit the type or any instance, execute S3, establish identity-contract, implementation, or runtime conformance, publish, deploy, or establish a stable release.
