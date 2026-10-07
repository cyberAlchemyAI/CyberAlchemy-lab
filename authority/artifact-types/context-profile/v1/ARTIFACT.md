<!-- GENERATED FILE: edit artifact.json and run generator.py. -->

# Context Profile Artifact Type v1

> Generated from `artifact.json`; this view is explanatory and not canonical.

- Type: `cal.artifact-type.context-profile/v1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Canonical instance: `record.json`
- Human projection: `RECORD.md`

## Semantic bindings

- `cal.definition.context-profile@1.0.0-candidate.1` — `admitted` — `authority/definitions/candidates/0014-definition-specialization-resolution/definitions/context-profile/v1/definition.json`

## Distinct validation purpose

Carries reusable construction and resolution policy derived from the admitted Context contract, including anchor rules, source eligibility, freshness, exclusions, output constraints, and succession, without representing a Context instance.

## Orthogonality rules

- **CONTEXT-PROFILE-POLICY**: A profile defines reusable construction and resolution policy and does not carry Context identity.
- **CONTEXT-PROFILE-SUCCESSION**: Material policy changes create an explicit successor rather than silently changing prior resolutions.

## Four facets

- **Classification**: Candidate Context Profile with explicit source bindings.
- **Human Continuation**: Generated RECORD.md and the complete-model review explain the revised contract, realistic example, dependencies, and claim limits.
- **Machine Checkable**: Schema, typed reference closure and target-specific graph consistency checks.
- **Schema**: Closed target-specific record contract.

## Typed residue

- `STEP5-ADMISSION-R1` (role:artifact-type-owner): Artifact Type owner admission for the exact revised cal.artifact-type.context-profile/v1 candidate. Consequence: The revised carrier remains candidate-only.
- `STEP5-ACTIVATION-R2` (role:migration-consumer-owner): A real instance, bounded consumer integration, and a separate activation decision. Consequence: Validation supplies no runtime, operational, or external effect.

## Claim ceiling

This stable package starts from the migration-selected Artifact Type contract, applies any recorded owner-review refinement, and binds its semantic dependencies to admitted Definitions. It does not admit the Artifact Type, admit any instance, authenticate fixture claims, integrate a consumer, or activate behavior.
