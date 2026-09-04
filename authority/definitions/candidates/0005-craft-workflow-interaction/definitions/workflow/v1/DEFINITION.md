<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Workflow

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `DS-D1.9`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:craft-product-owner`
- Authority scope: `scope:craft-product-workflow`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

A Workflow is an ordered multi-step orchestration of Operations within or across Product Feature boundaries. It declares exactly one scope from intra-feature or cross-feature and one ownership-boundary scope. Workflow evaluation may emit recovery intent and a plan, but only a separate executor may invoke exact Operation bindings.

```text
Workflow(w) = (ordered_operations, scope, ownership_boundary_scope); scope in {intra-feature,cross-feature}; Invoke(w) = none.
```

### Notation

| Symbol | Meaning |
| --- | --- |
| w | One exact Workflow declaration. |
| ordered_operations | The ordered Operation references coordinated by the Workflow. |

### Boundary conditions

- Missing, empty, or unknown scope is invalid.
- Workflow coordination does not acquire the business responsibilities of its Operations.
- Workflow evaluation does not itself execute Operations.

### Testable conditions

- The workflow declares exactly one admitted scope.
- All steps reference typed Operations.
- Execution bindings remain external to workflow evaluation.

## Plain-language voice

A Workflow coordinates several ordered Operations over time and says whether that coordination stays inside one Product Feature or crosses Feature boundaries.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

This candidate migrates DomainSpec v2 Workflow into the renamed Craft Product lineage while preserving stable semantic ID DS-D1.9. It does not create a Craft bounded context.

### Examples

- A definition-admission Workflow coordinates authorship, validation, owner review, and registry transition.
- A read-only audit Workflow may coordinate checks without invoking any mutation Operation.

## Applicability

Multi-step orchestration of Operations within or across Product Feature boundaries in the Craft Product lineage.

### Exclusions

- Authority or permission to execute an Operation.
- A DDD Bounded Context inferred from workflow placement.
- A generic task list without typed Operations and declared scope.

## Boundaries

- Workflow is not Gate.
- Workflow is not Authority.
- Workflow is not a Product, Project, Method, or Bounded Context.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.definition.definition@1.0.0-candidate.1 | whole-json | `eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575` | `admitted` |
| domainspec-core:DS-D1.9 | lines:647-689 | `23835be6442b40136d19c747fdf2ea07f1eae996b33cf0997ace7d9b5f2e4228` | `candidate-unadmitted` |
| domainspec-core:CA2-PRODUCT-CRAFT | whole-json | `30ab8d1c7ac2b8f95a950a9cc7b83a2d6f3966e66635311a1e4083cec3be259e` | `candidate-unadmitted` |

## Primary consumers

- candidate:product/products/craft
- candidate:contexts/craft
- tooling/validators

## Lookup and drift

- Index: `candidate:authority/definitions/registry.json` / `DS-D1.9`
- Drift owner: `role:craft-product-owner`
- Audit: `drift-audit-postimage.json`
- Challenge route: `route:definition-governance-challenge`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.governed-by | DS-D1.9@1.0.0-candidate.1 | role:craft-product-owner | role:craft-product-owner |
| relation.originates-from | DS-D1.9@1.0.0-candidate.1 | domainspec-core:DS-D1.9 | role:craft-product-owner |

## Evidence

- CAL-DECISION-0002:RN-2
- domainspec-core:DS-D1.9

## Residue

- external-source-admission-required
- craft-product-owner-binding-required
- craft-bounded-context-not-selected

## Claim ceiling

This candidate migrates Workflow meaning while preserving DS-D1.9. It does not admit the source, select a Craft bounded context, configure a workflow, or authorize execution.
