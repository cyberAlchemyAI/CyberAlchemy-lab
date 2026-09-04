<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Decision Checkpoint

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `craft.definition.decision-checkpoint`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:craft-product-owner`
- Authority scope: `scope:craft-product-workflow`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

A Decision Checkpoint is one Workflow-local position at which a closed Decision Request Set may be presented as one human interaction. It carries no authority. Its placement is resolved from the applicable Workflow Decision Profile and User Decision Preference, while every request retains its independently governed owner, scope, exact target, and effect.

```text
Checkpoint(w,c) iff c in Allowed(Profile(Type(w))) and Resolve(Profile(Type(w)),Preference(User(w),Type(w)))=c; Authority(c)=none.
```

### Notation

| Symbol | Meaning |
| --- | --- |
| w | One exact Workflow instance. |
| c | One eligible interaction position in the Workflow. |

### Boundary conditions

- Approval is a possible decision outcome, not the checkpoint.
- Grouping requests does not merge authority.
- A checkpoint cannot bind unknown future bytes when an exact-byte decision is required.

### Testable conditions

- A single-mode Workflow resolves exactly one checkpoint.
- The checkpoint is allowed by the Workflow type's profile.
- The checkpoint record declares authority_effect none.

## Plain-language voice

The one place in a Workflow where the person is asked to decide; it says where the question appears, not what the person may authorize.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

Craft uses the checkpoint to limit a Workflow to one configured human interruption while preserving every underlying governance boundary.

### Examples

- A definition pack may be authored and validated before one admission checkpoint.
- A migration needing approval of future output bytes must use a dependent Workflow after those bytes exist.

## Applicability

Human-decision placement within one exact Craft Workflow instance.

### Exclusions

- The Authority governing a decision.
- The decision outcome.
- Automated validation or generated projection refreshes.

## Boundaries

- Decision Checkpoint is not Gate.
- Decision Checkpoint is not Authority or a decision outcome.
- Workflow position does not imply truth, evidence quality, or permission.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.definition.definition@1.0.0-candidate.1 | whole-json | `eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575` | `admitted` |
| domainspec-core:DS-D1.9 | lines:647-689 | `23835be6442b40136d19c747fdf2ea07f1eae996b33cf0997ace7d9b5f2e4228` | `candidate-unadmitted` |
| domainspec-core:CAV2-D37 | lines:2445-2508 | `e27d4dcb0bf21347c07f04db96f58c5b58d6ccb280097c449017ebf09c376bf4` | `candidate-unadmitted` |

## Primary consumers

- candidate:product/products/craft
- candidate:craft-workflow-runtime
- tooling/validators

## Lookup and drift

- Index: `candidate:authority/definitions/registry.json` / `craft.definition.decision-checkpoint`
- Drift owner: `role:craft-product-owner`
- Audit: `drift-audit-postimage.json`
- Challenge route: `route:definition-governance-challenge`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.governed-by | craft.definition.decision-checkpoint@1.0.0-candidate.1 | role:craft-product-owner | role:craft-product-owner |
| relation.originates-from | craft.definition.decision-checkpoint@1.0.0-candidate.1 | domainspec-core:CAV2-D37 | role:craft-product-owner |

## Evidence

- user-direction:single-configurable-decision-checkpoint
- domainspec-core:CAV2-D37

## Residue

- external-source-admission-required
- craft-product-owner-binding-required
- decision-checkpoint-artifact-type-not-yet-authored

## Claim ceiling

This candidate names Workflow interaction placement only. It does not request, record, approve, reject, or authorize any decision or effect.
