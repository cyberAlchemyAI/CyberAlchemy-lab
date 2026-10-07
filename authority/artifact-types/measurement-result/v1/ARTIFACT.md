<!-- GENERATED FILE: edit artifact.json and run generator.py. -->

# Measurement Result Artifact Type v1

> Generated from `artifact.json`; this view is explanatory and not canonical.

- Type: `cal.artifact-type.measurement-result/v1`
- Status: `candidate-unadmitted`
- Authority effect: `none`
- Canonical instance: `record.json`
- Human projection: `RECORD.md`

## Semantic bindings

- `cal.definition.measurement-result@1.0.0-candidate.1` — `admitted` — `authority/definitions/candidates/0014-definition-specialization-resolution/definitions/measurement-result/v1/definition.json`

## Distinct validation purpose

Records one attributable residue-entropy result produced by an exact Measurement Method, preserving entropy register, source operation, typed residue, mathematical reading, scope, uncertainty, claim status, authority treatment, evidence, and receipt.

## Orthogonality rules

- **MEASUREMENT-RESULT-METHOD-BINDING**: Every result identifies its exact method, subject, residue, source operation, unit, uncertainty, evidence, and receipt.
- **MEASUREMENT-RESULT-NO-GOVERNANCE**: A measured value does not itself decide authority, admission, adoption, or value.

## Four facets

- **Classification**: Candidate Measurement Result with explicit source bindings.
- **Human Continuation**: Generated RECORD.md and the complete-model review explain the revised contract, realistic example, dependencies, and claim limits.
- **Machine Checkable**: Schema, typed reference closure and target-specific graph consistency checks.
- **Schema**: Closed target-specific record contract.

## Typed residue

- `STEP5-ADMISSION-R1` (role:artifact-type-owner): Artifact Type owner admission for the exact revised cal.artifact-type.measurement-result/v1 candidate. Consequence: The revised carrier remains candidate-only.
- `STEP5-ACTIVATION-R2` (role:migration-consumer-owner): A real instance, bounded consumer integration, and a separate activation decision. Consequence: Validation supplies no runtime, operational, or external effect.

## Claim ceiling

This stable package starts from the migration-selected Artifact Type contract, applies any recorded owner-review refinement, and binds its semantic dependencies to admitted Definitions. It does not admit the Artifact Type, admit any instance, authenticate fixture claims, integrate a consumer, or activate behavior.
