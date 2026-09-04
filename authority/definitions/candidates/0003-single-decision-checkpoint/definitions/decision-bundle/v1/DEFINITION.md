<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Decision Bundle

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.decision-bundle`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:cyberalchemy-lab-workflow-interaction`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

A Decision Bundle is a closed ordered set of exact Governance Decision requests presented at one Decision Checkpoint. Every member retains an independent decision identity, Authority Boundary, owner role, accountable principal, immutable target, digest when bytes exist, requested effect, scope, outcome, and invalidation conditions. Bundling reduces human interaction count but cannot merge roles, infer authorization between members, or make one member's outcome satisfy another member's gate.

```text
DecisionBundle(B,c) iff FiniteClosed(B) and forall d in B: Checkpoint(d)=c and ExactTarget(d) and ExactOwner(d) and ExactEffect(d). Authority(B) = union of no implicit authority; Authorized(B) iff forall d in B: Authorized(d).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| B | One closed Decision Bundle. |
| d | One independently governed decision member. |
| c | The single Decision Checkpoint presenting B. |

### Boundary conditions

- A shared principal does not collapse member owner roles.
- One approved member does not approve another member.
- A member whose exact target does not yet exist cannot enter the bundle.

### Testable conditions

- Every member has an exact unique decision identity.
- Every member binds an owner, target, effect, and scope.
- All members name the same checkpoint while preserving separate Authority Boundaries.

## Plain-language voice

Several exact decisions shown together once. The person sees one interaction, but each decision keeps its own owner, target, and consequence.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

The definition owner, artifact-type owner, and evidence owner may be the same person. A single checkpoint can present their decisions together without pretending those roles or effects are the same.

### Examples

- One admission interaction may bind separately identified definition and registry-postimage decisions.
- Source release and exact-output publication cannot share a bundle when the output does not yet exist at source-release time.

## Applicability

A closed presentation set of independently scoped Governance Decisions at one Decision Checkpoint.

### Exclusions

- A merged authority grant.
- A replacement for individual decision records.
- A bundle containing unresolved or future decision targets.

## Boundaries

- Decision Bundle is an interaction aggregation, not an authority aggregation.
- Every bundled decision remains independently challengeable and invalidatable.
- A bundle cannot contain an inferred decision.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.language.governance/v2 | whole-json | `ba84484be3f0d793e935ba4bbf960885ce1adcd2d2763aee940396ff290918d7` | `admitted` |
| CAL-OWNERS-FOUNDATION-01 | whole-json | `bb20cdc8ed61decba43977fafc4d04052cb59bb8e4402d6419a3d85776a3422d` | `admitted` |

## Primary consumers

- authority/decisions
- authority/profiles
- tooling/validators

## Lookup and drift

- Index: `candidate:authority/definitions/registry.json` / `cal.definition.decision-bundle`
- Drift owner: `role:definition-owner`
- Audit: `drift-audit-postimage.json`
- Challenge route: `route:definition-governance-challenge`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.governed-by | cal.definition.decision-bundle@1.0.0-candidate.1 | role:definition-owner | role:definition-owner |

## Evidence

- user-direction:one-approval-boundary
- CAL-DECISION-0013-FOUNDATION-01-ADMISSION

## Residue

- definition-owner-admission-required
- decision-artifact-contract-not-yet-authored

## Claim ceiling

This candidate defines one-interaction decision aggregation only. It does not create, approve, combine, or execute any Governance Decision.
