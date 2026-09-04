<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Decision Checkpoint

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.decision-checkpoint`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:cyberalchemy-lab-workflow-interaction`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

A Decision Checkpoint is one workflow-local position at which a closed set of required Governance Decisions may be presented as one human interaction. It carries no authority by itself. Its placement is resolved from a Workflow Decision Profile and an applicable User Decision Preference, while every decision presented there retains its own Authority Boundary, accountable owner, exact target, and effect.

```text
DecisionCheckpoint(w,c) iff c in Allowed(Profile(Type(w))) and Resolved(Profile(Type(w)),Preference(User(w),Type(w))) = c. Authority(c) = none.
```

### Notation

| Symbol | Meaning |
| --- | --- |
| w | One workflow instance. |
| c | One eligible workflow checkpoint. |

### Boundary conditions

- Approval is one possible decision outcome, not the checkpoint itself.
- Grouping decisions at one checkpoint does not merge their Authority Boundaries.
- A checkpoint cannot bind unknown future bytes when the required decision targets exact output bytes.

### Testable conditions

- An approval-requiring workflow resolves exactly one checkpoint.
- The resolved checkpoint belongs to the workflow type's allowed set.
- The checkpoint record has authority_effect none.

## Plain-language voice

The one place in a workflow where the person is asked to decide. Calling it a checkpoint avoids confusing where the question appears with what the person is allowed to authorize.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

CyberAlchemy Lab workflows should interrupt the user at no more than one configured checkpoint. That interaction can present several exact role-scoped decisions without collapsing them.

### Examples

- A definition pack can be authored and validated before one admission checkpoint.
- A representation migration can present both context-owner selections together only when the same principal holds both roles and both postimages exist.

## Applicability

Human decision placement within one exact workflow instance.

### Exclusions

- The Authority Boundary governing a decision.
- The decision outcome.
- Automated validation or generated projection refreshes.

## Boundaries

- Decision Checkpoint is not Authority Boundary.
- Decision Checkpoint is not Governance Decision or approval outcome.
- Workflow position does not imply greater truth, evidence quality, or authority.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.definition.definition@1.0.0-candidate.1 | whole-json | `eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575` | `admitted` |
| cal.language.governance/v2 | whole-json | `ba84484be3f0d793e935ba4bbf960885ce1adcd2d2763aee940396ff290918d7` | `admitted` |

## Primary consumers

- authority/profiles
- contexts/governance
- tooling/validators

## Lookup and drift

- Index: `candidate:authority/definitions/registry.json` / `cal.definition.decision-checkpoint`
- Drift owner: `role:definition-owner`
- Audit: `drift-audit-postimage.json`
- Challenge route: `route:definition-governance-challenge`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.governed-by | cal.definition.decision-checkpoint@1.0.0-candidate.1 | role:definition-owner | role:definition-owner |

## Evidence

- user-direction:single-configurable-approval-boundary
- CAL-DECISION-0025-GOVERNANCE-ONTOLOGY-LIFECYCLE-SUCCESSOR-PROMOTION

## Residue

- definition-owner-admission-required
- workflow-dependency-unresolved
- workflow-profile-artifact-type-not-yet-authored

## Claim ceiling

This candidate names workflow interaction placement only. It does not request, record, approve, reject, or authorize any decision or effect.
