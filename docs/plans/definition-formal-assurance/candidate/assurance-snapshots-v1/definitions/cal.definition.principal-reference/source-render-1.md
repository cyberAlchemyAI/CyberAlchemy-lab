<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Principal Reference

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.principal-reference`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:principal-reference-definition`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

A Principal Reference is a minimal governed reference to one Principal used by artifacts that need accountability or authorization linkage without copying the Principal’s identity record. It is not the Principal, an authentication credential, a Person Reference, a Role assignment, or proof of authority.

```text
PrincipalReference(x) => governed_identity_or_record(x) and bounded_scope(x); PrincipalReference(x) =/=> authority_effect(x).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| x | One subject evaluated under the Principal Reference Definition. |

### Boundary conditions

- A Principal Reference contains only the minimum stable identifier, kind, issuer or registry, resolution route, and integrity data needed by the consumer.
- The referenced Principal remains the identity authority; the reference cannot copy, mutate, authenticate, or replace it.
- A Principal Reference contains no reusable credential and proves no Person identity, Role, Assignment, or authority grant.

### Testable conditions

- Every Principal Reference resolves to exactly one governed Principal or becomes explicitly unresolved.
- No secret, credential, or excess identity data is embedded.
- Every authority decision resolves separate current grant evidence rather than inferring it from the reference.

## Plain-language voice

A Principal Reference is a minimal governed reference to one Principal used by artifacts that need accountability or authorization linkage without copying the Principal’s identity record. A Principal Reference contains only the minimum stable identifier, kind, issuer or registry, resolution route, and integrity data needed by the consumer.

## Domain-context voice

Workspace: `/home/vlad_/projects/CyberAlchemy-lab`

In the Lab, Principal Reference supplies one distinct semantic responsibility in the integrated model. Its carrier and relations remain separate governed contracts.

### Examples

- principal-ref:def-owner points to principal:person-vlad and records issuer and resolution route without embedding personal identity data.

## Applicability

A Principal Reference is a minimal governed reference to one Principal used by artifacts that need accountability or authorization linkage without copying the Principal’s identity record.

### Exclusions

- A Principal Reference contains only the minimum stable identifier, kind, issuer or registry, resolution route, and integrity data needed by the consumer.
- The referenced Principal remains the identity authority; the reference cannot copy, mutate, authenticate, or replace it.
- A Principal Reference contains no reusable credential and proves no Person identity, Role, Assignment, or authority grant.
- This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect.

## Boundaries

- A Principal Reference contains only the minimum stable identifier, kind, issuer or registry, resolution route, and integrity data needed by the consumer.
- The referenced Principal remains the identity authority; the reference cannot copy, mutate, authenticate, or replace it.
- A Principal Reference contains no reusable credential and proves no Person identity, Role, Assignment, or authority grant.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.source.actor-model-review@2026-10-05 | whole-file | `cc2fec4a1f9bd7a4796d6735866b16736087e125dcaf23d7fa6abed33862ee42` | `candidate-unadmitted` |

## Primary consumers

- .arcanum/ontology-vault/2026-10-05-lab-integrated-model.md

## Lookup and drift

- Index: `authority/definitions/candidates/0013-integrated-lab-definition-model/DEFINITIONS-INDEX.md` / `cal.definition.principal-reference@1.0.0-candidate.1`
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

This candidate defines Principal Reference for review only. It does not admit the Definition or any carrier, instance, relation, Policy, Decision, runtime behavior, authority, publication, release, deployment, or external effect.
