<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Decision Request Set

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `craft.definition.decision-request-set`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:craft-product-owner`
- Authority scope: `scope:craft-product-workflow`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

A Decision Request Set is a closed ordered set of exact decision requests presented at one Decision Checkpoint. Every member retains its independent decision identity, authority scope, owner, target, digest when bytes exist, requested effect, outcome, and invalidation conditions. Presentation reduces interaction count but cannot merge authority, infer authorization between members, or let one outcome satisfy another gate.

```text
RequestSet(R,c) iff FiniteClosed(R) and forall r in R: Checkpoint(r)=c and ExactOwner(r) and ExactTarget(r) and ExactEffect(r); Authorized(R) iff forall r in R: Authorized(r).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| R | One closed presentation set of decision requests. |
| r | One independently governed request member. |
| c | The single Decision Checkpoint presenting the set. |

### Boundary conditions

- A shared principal does not collapse member roles.
- One approved member does not approve another.
- A request without its exact target cannot enter the set.

### Testable conditions

- Every member has a unique decision identity.
- Every member binds owner, target, effect, and scope.
- All members name the same checkpoint without merging authority.

## Plain-language voice

Several exact questions shown together once. The user sees one interaction, but every question keeps its own owner, target, and consequence.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

Craft may present definition and registry decisions together when all exact targets exist, without pretending they are one governance decision.

### Examples

- Present independently identified definition and registry-postimage decisions at one checkpoint.
- Do not include exact-output publication approval before the output bytes exist.

## Applicability

A closed presentation set of independently governed decision requests at one Decision Checkpoint.

### Exclusions

- A merged authority grant.
- A replacement for individual decision records.
- Requests whose exact targets do not yet exist.

## Boundaries

- Decision Request Set is interaction aggregation, not authority aggregation.
- Every request remains independently challengeable and invalidatable.
- The set cannot contain an inferred decision.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.definition.definition@1.0.0-candidate.1 | whole-json | `eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575` | `admitted` |
| domainspec-core:CAV2-D34 | lines:2252-2315 | `baa33a7047a1c1d512fce513c22134b377587d9acf77b2797412d2cd97118ef1` | `candidate-unadmitted` |
| domainspec-core:CAV2-D37 | lines:2445-2508 | `e27d4dcb0bf21347c07f04db96f58c5b58d6ccb280097c449017ebf09c376bf4` | `candidate-unadmitted` |

## Primary consumers

- candidate:product/products/craft
- candidate:craft-workflow-runtime
- tooling/validators

## Lookup and drift

- Index: `candidate:authority/definitions/registry.json` / `craft.definition.decision-request-set`
- Drift owner: `role:craft-product-owner`
- Audit: `drift-audit-postimage.json`
- Challenge route: `route:definition-governance-challenge`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.governed-by | craft.definition.decision-request-set@1.0.0-candidate.1 | role:craft-product-owner | role:craft-product-owner |
| relation.originates-from | craft.definition.decision-request-set@1.0.0-candidate.1 | domainspec-core:CAV2-D37 | role:craft-product-owner |

## Evidence

- user-direction:one-human-decision-boundary
- ownership-review:decision-bundle-split

## Residue

- external-source-admission-required
- craft-product-owner-binding-required
- decision-request-set-artifact-type-not-yet-authored

## Claim ceiling

This candidate defines presentation aggregation only. It does not create, approve, combine, or execute any authority-bearing decision.
