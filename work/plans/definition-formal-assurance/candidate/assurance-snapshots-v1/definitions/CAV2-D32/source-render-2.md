<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Method

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `CAV2-D32`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:method-definition`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

A Method is a governed repeatable transformation whose scope, inputs, actions, roles, gates, outputs, evidence, residue rule, validation rule, recomposition rule, and boundary are explicit. A named Method specializes this form without inheriting authority to execute.

```text
M = (scope, inputs, actions, roles, gates, outputs, evidence, residue_rule, validation_rule, recomposition_rule, boundary).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| M | One governed Method specification. |

### Boundary conditions

- Repeatability requires reusable and specialized fields to be identifiable.
- Method admission and Method application are separate decisions.

### Testable conditions

- All minimum Method fields are explicit.
- Residue and recomposition rules are present.
- No execution authority is inferred from Method identity.

## Plain-language voice

A Method is a repeatable, governed way of turning intent and evidence into checkable work while preserving what remains unresolved.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

This candidate migrates the generic Method meaning under stable ID CAV2-D32. Craft Method is one separately identified specialization.

### Examples

- CAV2-D20 specializes Method for recursive system building.
- A Method may use workflows and tools without being identical to them.

## Applicability

A governed repeatable way to transform intent, evidence, state, or residue through declared roles, actions, gates, outputs, validation, residue, and recomposition rules.

### Exclusions

- A one-off task or technique.
- A checklist, engine, pipeline, lifecycle label, Product, Project, Goal, or authority grant.

## Boundaries

- Method is not Product, Project, Goal, workflow, engine, or pipeline.
- Method identity does not grant permission to execute.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.definition.definition@1.0.0-candidate.1 | whole-json | `eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575` | `admitted` |
| domainspec-core:CAV2-D32 | lines:2114-2180 | `28608be42869eaf5183bd5b4154d9bded38f1a17ad35c11072b9a49f1e4dc348` | `candidate-unadmitted` |

## Primary consumers

- authority/artifact-types/method-binding/v1
- product/products/craft/v1/method-binding.json

## Lookup and drift

- Index: `authority/definitions/candidates/0006-craft-identity/DEFINITIONS-INDEX.md` / `CAV2-D32`
- Drift owner: `role:definition-owner`
- Audit: `authority/definitions/candidates/0006-craft-identity/drift-audit-postimage.json`
- Challenge route: `route:definition-governance-challenge`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.governed-by | CAV2-D32@1.0.0-candidate.1 | role:definition-owner | role:definition-owner |
| relation.originates-from | CAV2-D32@1.0.0-candidate.1 | domainspec-core:CAV2-D32 | role:definition-owner |

## Evidence

- CAL-CML07-CRAFT-IDENTITY-CHAIN-0001
- CAL-SOURCE-ADMISSIONS-CRAFT-IDENTITY-V1

## Residue

- method-binding-artifact-type-required
- source-admission-required

## Claim ceiling

This candidate migrates Method meaning while preserving CAV2-D32. It does not admit, bind, apply, or execute a Method.
