<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Delegation

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.delegation`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:delegation-definition`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

A Delegation is an explicit scope-bounded and time-bounded authorization from a Principal or authority owner to an Agent or Agent Instance for named action kinds under exact Policies, gates, evidence, revocation, and claim ceilings. Delegation transfers neither identity nor ownership and creates no authority outside its exact envelope.

```text
Delegation(d,p,a,q,t) => Authority(p,q,t) and scope(d)=q and recipient(d)=a and active(d,t); Delegation(d,...) =/=> identityTransfer or ownershipTransfer.
```

### Notation

| Symbol | Meaning |
| --- | --- |
| x | One subject evaluated under the Delegation Definition. |

### Boundary conditions

- The delegator must possess delegable authority for every included action kind, subject, scope, and time interval.
- Delegation names the eligible Agent Profile or concrete Agent Instance, exact action kinds, Policies, approval gates, evidence, claim ceiling, period, revocation, and residue handling.
- Delegation transfers neither identity nor ownership and grants nothing outside its exact envelope.
- Redelegation is forbidden unless explicitly included and independently bounded.
- Expiry or revocation prevents later Actions from relying on the Delegation while preserving the historical record.

### Testable conditions

- Every Delegation resolves current delegator authority covering the entire delegated scope.
- Every use matches recipient, action kind, subject, time, Policy, gate, and evidence constraints.
- No expired, revoked, superseded, or out-of-scope Delegation authorizes an Action.
- No Delegation implies owner status, Decision authority, or redelegation unless explicitly enumerated.

## Plain-language voice

A Delegation is an explicit scope-bounded and time-bounded authorization from a Principal or authority owner to an Agent or Agent Instance for named action kinds under exact Policies, gates, evidence, revocation, and claim ceilings. The delegator must possess delegable authority for every included action kind, subject, scope, and time interval.

## Domain-context voice

Workspace: `/home/vlad_/projects/CyberAlchemy-lab`

In the Lab, Delegation supplies one distinct semantic responsibility in the integrated model. Its carrier and relations remain separate governed contracts.

### Examples

- The Definition owner delegates candidate materialization and validation but retains the admission decision.

## Applicability

A Delegation is an explicit scope-bounded and time-bounded authorization from a Principal or authority owner to an Agent or Agent Instance for named action kinds under exact Policies, gates, evidence, revocation, and claim ceilings.

### Exclusions

- The delegator must possess delegable authority for every included action kind, subject, scope, and time interval.
- Delegation names the eligible Agent Profile or concrete Agent Instance, exact action kinds, Policies, approval gates, evidence, claim ceiling, period, revocation, and residue handling.
- Delegation transfers neither identity nor ownership and grants nothing outside its exact envelope.
- Redelegation is forbidden unless explicitly included and independently bounded.
- Expiry or revocation prevents later Actions from relying on the Delegation while preserving the historical record.
- This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect.

## Boundaries

- The delegator must possess delegable authority for every included action kind, subject, scope, and time interval.
- Delegation names the eligible Agent Profile or concrete Agent Instance, exact action kinds, Policies, approval gates, evidence, claim ceiling, period, revocation, and residue handling.
- Delegation transfers neither identity nor ownership and grants nothing outside its exact envelope.
- Redelegation is forbidden unless explicitly included and independently bounded.
- Expiry or revocation prevents later Actions from relying on the Delegation while preserving the historical record.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.source.actor-model-review@2026-10-05 | whole-file | `cc2fec4a1f9bd7a4796d6735866b16736087e125dcaf23d7fa6abed33862ee42` | `candidate-unadmitted` |

## Primary consumers

- .arcanum/ontology-vault/2026-10-05-lab-integrated-model.md

## Lookup and drift

- Index: `authority/definitions/candidates/0013-integrated-lab-definition-model/DEFINITIONS-INDEX.md` / `cal.definition.delegation@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `authority/definitions/candidates/0013-integrated-lab-definition-model/drift-audit-postimage.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

No typed relations declared.

## Evidence

- .arcanum/ontology-vault/2026-10-05-actor-agent-model-review.md
- .arcanum/ontology-vault/2026-10-05-lab-integrated-model.md
- .arcanum/ontology-vault/2026-10-06-lab-semantic-gap-audit.md

## Residue

- Definition-owner review and exact admission remain required.
- Artifact Type carrier, relation, qualifier, ontology, runtime, and consumer decisions remain separate.

## Claim ceiling

This candidate defines Delegation for review only. It does not admit the Definition or any carrier, instance, relation, Policy, Decision, runtime behavior, authority, publication, release, deployment, or external effect.
