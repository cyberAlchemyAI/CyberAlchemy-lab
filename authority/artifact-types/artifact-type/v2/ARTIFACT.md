<!-- GENERATED FILE: edit artifact.json and run generator.py. -->

# Artifact Type v2

> Generated from `artifact.json`; this view is not canonical.

- Status: `candidate-unadmitted`
- Authority effect: `none`
- Owner: `role:artifact-type-owner`
- Predecessor: `cal.artifact-type.artifact-type/v1`

## Semantic Definition bindings

- `cal.definition.artifact-type@1.0.0-candidate.1` — `candidate-unadmitted` — `authority/definitions/candidates/0007-cml07-semantic-closure/definitions/artifact-type/v1/definition.json`

## Registration policy

- **Legacy Registration Rule**: The eight registrations admitted under Artifact Type/v1 remain governed by their exact v1 bytes and decision; v2 references but does not rewrite them.
- **New Registration Rule**: Every Artifact Type registration authored under v2 must carry one or more semantic_definition_refs whose meanings establish its semantic kind and distinct validation purpose.
- **Candidate Rule**: Candidate Artifact Types may bind candidate Definition versions, but their unresolved posture must remain explicit and blocks Artifact Type admission.
- **Admission Rule**: Every semantic Definition reference must resolve to an admitted current version before the corresponding Artifact Type registration can be admitted.
- **Non Effect**: Registration, schema validation, and projection parity do not admit an Artifact Type or any instance.

## Registrations authored under v2

| Type | Semantic kind | Definition refs | Schema | Purpose |
| --- | --- | --- | --- | --- |
| `cal.artifact-type.artifact-type/v2` | `artifact-type` | `cal.definition.artifact-type@1.0.0-candidate.1` | `authority/artifact-types/artifact-type/v2/schema.json` | Enforces semantic Definition bindings for Artifact Type registrations authored under v2 while preserving v1 registrations without retroactive mutation. |

## Claim ceiling

Artifact Type/v2 is a candidate successor contract. It preserves admitted v1 bytes and requires Definition references for new registrations, but neither its schema PASS nor its candidate Definition binding admits v2 or authorizes CML-07 S2.
