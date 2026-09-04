<!-- GENERATED FILE: canonical source is decision.json. -->

# CML-07 S2 Identity Artifact Types v1 Admission

- Decision: `CAL-DECISION-0030-CML07-S2-IDENTITY-ARTIFACT-TYPES-V1`
- Status: `owner-admitted`
- Artifact Types admitted: `6`
- Candidate files rewritten: `0`
- S3 posture: `evaluable-not-executed`

## Independently admitted types

- `cal.artifact-type.product-identity/v1`
- `cal.artifact-type.project-identity/v1`
- `cal.artifact-type.method-binding/v1`
- `cal.artifact-type.goal/v1`
- `cal.artifact-type.identity-graph/v1`
- `cal.artifact-type.identity-lineage/v1`

## Separation

One interaction authorizes six independent Artifact Type admission requests. It does not merge their identities, schemas, validation purposes, or authority.

## Claim ceiling

This decision admits only the six exact S2 Artifact Type contracts and their bound schemas by decision overlay. It makes S3 candidate authoring evaluable but does not execute S3, admit an identity carrier, establish identity-contract, implementation, or runtime conformance, commit, push, publish, deploy, or establish a stable release.
