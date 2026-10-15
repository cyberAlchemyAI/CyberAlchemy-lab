<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Goal

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `CAV2-D59`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:goal-definition`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

A Goal states a desired future outcome for one Project and becomes achieved only when all required success conditions have adequate evidence and the Goal owner records the lifecycle transition. Progress or passing checks alone do not achieve it.

```text
Goal = (id, project_ref, outcome, rationale, scope, exclusions, owner_route, success_conditions, evidence_requirements, lifecycle_state); achieved only if evidence adequate and owner records achievement.
```

### Notation

| Symbol | Meaning |
| --- | --- |
| Goal | One durable Project-owned outcome record. |

### Boundary conditions

- A Goal belongs to exactly one Project in this contract.
- Evidence supports but does not perform the achievement decision.

### Testable conditions

- Outcome, owner, success conditions, and evidence requirements are explicit.
- Lifecycle change has owner evidence.
- The Goal does not carry execution authority.

## Plain-language voice

A Goal says what future result one Project is pursuing and what evidence will let its owner honestly declare it achieved.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

This candidate preserves CAV2-D59. The first Craft Goal remains distinct from the Craft Project and Product Feature it concerns.

### Examples

- CA2-GOAL-CRAFT-PRODUCT-FEATURE-FOUNDATION belongs to CA2-PROJECT-CRAFT.
- A PASS receipt may satisfy evidence needs but cannot itself mark the Goal achieved.

## Applicability

A durable, attributable desired future outcome for exactly one Project, with rationale, scope, owner, success conditions, evidence requirements, and lifecycle.

### Exclusions

- Intent, Project, plan, task, work pack, evidence, deadline, or execution authority.
- Automatic achievement from activity, progress, validation, or agent assertion.

## Boundaries

- Goal is not Project, Product, Method, plan, task, evidence, or authority.
- Goal membership does not merge the Goal with its Project.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.definition.definition@1.0.0-candidate.1 | whole-json | `eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575` | `admitted` |
| domainspec-core:CAV2-D59 | lines:4443-4521 | `f9589997351dcd40f5c37f970568aab3a09345c1b8ab6331860d5533d2c7a674` | `candidate-unadmitted` |
| domainspec-core:CA2-GOAL-CRAFT-PRODUCT-FEATURE-FOUNDATION | whole-file | `075458bb50e508d00a1124cb43c5952a013657df2e6046b8674f25c44dd350a2` | `candidate-unadmitted` |

## Primary consumers

- authority/artifact-types/goal/v1
- coordination/goals/craft-product-foundation/v1/goal.json

## Lookup and drift

- Index: `authority/definitions/candidates/0006-craft-identity/DEFINITIONS-INDEX.md` / `CAV2-D59`
- Drift owner: `role:definition-owner`
- Audit: `authority/definitions/candidates/0006-craft-identity/drift-audit-postimage.json`
- Challenge route: `route:definition-governance-challenge`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.governed-by | CAV2-D59@1.0.0-candidate.1 | role:definition-owner | role:definition-owner |
| relation.originates-from | CAV2-D59@1.0.0-candidate.1 | domainspec-core:CAV2-D59 | role:definition-owner |

## Evidence

- CAL-CML07-CRAFT-IDENTITY-CHAIN-0001
- CAL-SOURCE-ADMISSIONS-CRAFT-IDENTITY-V1
- CAL-OWNER-BINDINGS-CRAFT-IDENTITY-0004

## Residue

- goal-artifact-type-required
- craft-goal-owner-activation-required

## Claim ceiling

This candidate migrates Goal meaning while preserving CAV2-D59. It does not instantiate, activate, or achieve a Goal or authorize work.
