<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Authority Boundary

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.authority-boundary`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:cyberalchemy-lab-shared-governance`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

An Authority Boundary is the explicit owner-scoped limit within which one role may make Governance Decisions about named meanings, targets, and effects. It binds an owner role, an accountable principal binding, an authority scope, allowed effects, excluded effects, and a challenge route. An Authority Boundary is independent of where a workflow requests a decision, and no workflow profile or user preference may create, move, merge, or widen it.

```text
AuthorityBoundary(b) = (owner_role, principal_binding, authority_scope, allowed_effects, excluded_effects, challenge_route). MayDecide(p,d,b) iff Holds(p,b.owner_role) and Target(d) in b.authority_scope and Effect(d) in b.allowed_effects and Effect(d) not in b.excluded_effects.
```

### Notation

| Symbol | Meaning |
| --- | --- |
| b | One exact Authority Boundary. |
| d | One exact Governance Decision. |
| p | The accountable principal acting under an owner role. |

### Boundary conditions

- One principal holding multiple roles does not merge their Authority Boundaries.
- A Decision Checkpoint does not grant authority.
- Validation evidence cannot substitute for an owner decision.

### Testable conditions

- Every decision resolves an explicit owner role and principal binding.
- Every decision target and effect are within the selected Authority Boundary.
- No workflow or preference field changes authority scope or allowed effects.

## Plain-language voice

The exact limit around what a particular owner is allowed to decide. It says who can decide what; it does not say when a workflow asks them.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

In CyberAlchemy Lab, definition, context, artifact-type, evidence, migration, and publication owners may resolve to the same person while retaining separate scopes and decisions.

### Examples

- The definition owner may admit a term but cannot thereby admit a Bounded Context.
- Selecting an earlier Decision Checkpoint cannot expand a context owner's authority.

## Applicability

Owner-scoped semantic and effect authority used by CyberAlchemy Lab workflows and governance decisions.

### Exclusions

- Workflow interaction placement.
- Evidence quality or validation outcomes.
- Authority inferred from repository location, automation, or principal identity alone.

## Boundaries

- Authority Boundary is not Decision Checkpoint.
- Shared principal identity is not shared authority scope.
- Authority is not inferred from evidence, workflow position, implementation, or filesystem placement.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.definition.definition@1.0.0-candidate.1 | whole-json | `eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575` | `admitted` |
| cal.language.governance/v2 | whole-json | `ba84484be3f0d793e935ba4bbf960885ce1adcd2d2763aee940396ff290918d7` | `admitted` |
| CAL-OWNERS-FOUNDATION-01 | whole-json | `bb20cdc8ed61decba43977fafc4d04052cb59bb8e4402d6419a3d85776a3422d` | `admitted` |

## Primary consumers

- contexts/governance
- authority/decisions
- authority/profiles

## Lookup and drift

- Index: `candidate:authority/definitions/registry.json` / `cal.definition.authority-boundary`
- Drift owner: `role:definition-owner`
- Audit: `drift-audit-postimage.json`
- Challenge route: `route:definition-governance-challenge`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.governed-by | cal.definition.authority-boundary@1.0.0-candidate.1 | role:definition-owner | role:definition-owner |
| relation.originates-from | cal.definition.authority-boundary@1.0.0-candidate.1 | cal.language.governance/v2 | role:definition-owner |

## Evidence

- user-direction:single-configurable-approval-boundary
- CAL-DECISION-0013-FOUNDATION-01-ADMISSION
- CAL-DECISION-0025-GOVERNANCE-ONTOLOGY-LIFECYCLE-SUCCESSOR-PROMOTION

## Residue

- definition-owner-admission-required
- governance-rule-not-yet-authored

## Claim ceiling

This candidate clarifies Authority Boundary semantics only. It does not grant authority, assign an owner, create a decision, adopt a rule, or authorize any effect.
