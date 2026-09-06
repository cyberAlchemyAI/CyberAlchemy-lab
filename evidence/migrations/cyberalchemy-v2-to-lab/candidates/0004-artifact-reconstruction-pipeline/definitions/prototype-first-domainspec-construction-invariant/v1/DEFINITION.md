<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Prototype-First DomainSpec Construction Invariant

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.prototype-first-domainspec-construction-invariant`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:construction`
- Lifecycle posture reference: `candidate:d65-reconstruction-pipeline/v1`

## Scientific/formal voice

An implementation-bearing construction must begin with prototype definitions, use ontology only as non-authoritative navigation scaffolding, iterate product and implementation prototypes, freeze one exact product candidate, obtain current product-test evidence, and become eligible for product approval before any separate authority request. Product approval grants no operational authority.

```text
D -> O_s -> P* -> freeze(P_c@h) -> test(P_c@h) -> eligible(product_approval) -> decision(product_approval) -> eligible(separate_authority_request); O_s.authority=none; product_approval =/=> operational_authority
```

### Notation

| Symbol | Meaning |
| --- | --- |
| D | Prototype definitions. |
| O_s | Agent-facing, non-authoritative ontology scaffolds. |
| P* | Iterative product, business, DomainSpec, compiled-system, and implementation prototypes. |
| P_c@h | One frozen product candidate bound to exact digest h. |

### Boundary conditions

- Prototype epochs may iterate without admission requests.
- Testing binds one exact frozen candidate.
- Changed acceptance-bound bytes require a new test and approval epoch.
- Authority decisions occur only after product approval and remain separate.

### Testable conditions

- Every construction stage has an explicit typed carrier.
- Ontology scaffolds declare authority_effect none.
- Product-test evidence binds the frozen candidate digest.
- No authority request precedes exact product approval evidence.

## Plain-language voice

First learn with explicit prototypes. Freeze and test one exact product only when the model is coherent. Product approval may then be considered, while every real-world authority decision remains separate.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

The CyberAlchemy-v2 reconstruction uses this invariant to turn reviewed source meanings into candidate Lab artifacts without copying source structure or treating tests as admission.

### Examples

- The 176 migration scaffolds remain prototypes until family schemas and tests exist.
- The D65 vertical tests one Definition, Artifact Types, and profiles before wider reconstruction.

## Applicability

Construction of a new or materially revised implementation-bearing system or capability in CyberAlchemy-lab.

### Exclusions

- Purely narrative edits with no implementation-bearing system change.
- Admission, activation, publication, release, deployment, or external-effect decisions.

## Boundaries

- Construction Profile defines stages; it is not the invariant itself.
- Construction Binding binds an exact subject to a construction graph; it is not an implementation binding.
- Implementation Binding maps a system model to implementation targets; it does not prove implementation conformance.
- Evaluation Profile defines checks; Evaluation records results.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cyberalchemy-v2:CAV2-D65 | ## CAV2-D65: DomainSpec-Governed Construction Invariant | `fb6e61c0e31c14f6a6dd6f427bedf1ced7d6db707fc540f6ede11e97ea9facb5` | `candidate-unadmitted` |

## Primary consumers

- cal.artifact-type.construction-profile/v1
- cal.artifact-type.construction-binding/v1
- cal.artifact-type.implementation-binding/v1
- profile.prototype-construction-evaluation
- profile.product-candidate-evaluation

## Lookup and drift

- Index: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/registry.json` / `cal.definition.prototype-first-domainspec-construction-invariant@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/drift-audit.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

No typed relations declared.

## Evidence

- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0003-review-led-reconstruction/decisions/0001-planning-selection/decision.json
- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/receipts/validation.json

## Residue

- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/drift-audit.json

## Claim ceiling

Candidate Definition reconstructed from the selected D65 planning successor. It does not alter CyberAlchemy-v2, enter the admitted Lab Definition registry, activate construction policy, or authorize implementation or migration.
