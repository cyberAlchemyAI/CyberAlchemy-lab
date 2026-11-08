<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Principal

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.principal`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:principal-definition`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

A Principal is a governed identity recognized by an authentication, authorization, ownership, or accountability boundary. Principal identity does not prove Person identity, Agent capability, Role assignment, or authority beyond exact grants.

```text
Principal(x) => governed_identity_or_record(x) and bounded_scope(x); Principal(x) =/=> authority_effect(x).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| x | One subject evaluated under the Principal Definition. |

### Boundary conditions

- Principal identity is recognized only inside exact authentication, authorization, ownership, or accountability boundaries.
- Person, Team, service, or Agent subjects represented by a Principal retain independent identities and lifecycles.
- A Principal receives authority only through exact grants; identity alone creates no Role, capability, ownership, or permission.

### Testable conditions

- Every Principal reference resolves to one governed Principal identity and issuer boundary.
- Every consequential authorization cites an exact current grant and scope.
- No Principal identity is treated as proof of Person identity, Agent capability, Role, or unrestricted authority.

## Plain-language voice

A Principal is a governed identity recognized by an authentication, authorization, ownership, or accountability boundary. Principal identity is recognized only inside exact authentication, authorization, ownership, or accountability boundaries.

## Domain-context voice

Workspace: `/home/vlad_/projects/CyberAlchemy-lab`

In the Lab, Principal supplies one distinct semantic responsibility in the integrated model. Its carrier and relations remain separate governed contracts.

### Examples

- principal:person-vlad authorizes a Definition admission while an Agent Instance performs the file update on that Principal’s behalf.

## Applicability

A Principal is a governed identity recognized by an authentication, authorization, ownership, or accountability boundary.

### Exclusions

- Principal identity is recognized only inside exact authentication, authorization, ownership, or accountability boundaries.
- Person, Team, service, or Agent subjects represented by a Principal retain independent identities and lifecycles.
- A Principal receives authority only through exact grants; identity alone creates no Role, capability, ownership, or permission.
- This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect.

## Boundaries

- Principal identity is recognized only inside exact authentication, authorization, ownership, or accountability boundaries.
- Person, Team, service, or Agent subjects represented by a Principal retain independent identities and lifecycles.
- A Principal receives authority only through exact grants; identity alone creates no Role, capability, ownership, or permission.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.source.actor-model-review@2026-10-05 | whole-file | `cc2fec4a1f9bd7a4796d6735866b16736087e125dcaf23d7fa6abed33862ee42` | `candidate-unadmitted` |

## Primary consumers

- .arcanum/ontology-vault/2026-10-05-lab-integrated-model.md

## Lookup and drift

- Index: `authority/definitions/candidates/0013-integrated-lab-definition-model/DEFINITIONS-INDEX.md` / `cal.definition.principal@1.0.0-candidate.1`
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

This candidate defines Principal for review only. It does not admit the Definition or any carrier, instance, relation, Policy, Decision, runtime behavior, authority, publication, release, deployment, or external effect.
