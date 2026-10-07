<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Session Memory

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.session-memory`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:session-memory-definition`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

Session Memory is ephemeral working state owned by exactly one Agent Session and used only to continue that Session. It has no authority effect, cannot be canonical Project State, cannot silently survive termination, and cannot become hidden cross-session Machine Agent memory.

```text
SessionMemory(m,s) => exactlyOneSession(m,s) and lifetime(m) subseteq lifetime(s) and authorityEffect(m)=none; end(s) => expired(m).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| x | One subject evaluated under the Session Memory Definition. |

### Boundary conditions

- Session Memory belongs to exactly one Agent Session and cannot be shared as private state with another Session.
- It has no authority effect and cannot satisfy a canonical dependency, evidence obligation, Decision basis, or Project State reference after expiry.
- Material survives only when an attributable Agent Action writes a separate governed artifact, event, evidence record, or receipt.
- Copying Session Memory into a later Session without governed persistence and new View selection is forbidden.

### Testable conditions

- Every Session Memory record names exactly one active Session and expiry condition.
- Termination of the Session makes all its Session Memory inactive.
- No later Session directly resolves a dependency to expired Session Memory.
- Every surviving item has a separate governed identity, owner, provenance, and persistence Action in Project State.

## Plain-language voice

Session Memory is ephemeral working state owned by exactly one Agent Session and used only to continue that Session. Session Memory belongs to exactly one Agent Session and cannot be shared as private state with another Session.

## Domain-context voice

Workspace: `/home/vlad_/projects/CyberAlchemy-lab`

In the Lab, Session Memory supplies one distinct semantic responsibility in the integrated model. Its carrier and relations remain separate governed contracts.

### Examples

- A temporary list of unresolved Definition wording stays in Session Memory until an Agent Action writes a governed candidate artifact.

## Applicability

Session Memory is ephemeral working state owned by exactly one Agent Session and used only to continue that Session.

### Exclusions

- Session Memory belongs to exactly one Agent Session and cannot be shared as private state with another Session.
- It has no authority effect and cannot satisfy a canonical dependency, evidence obligation, Decision basis, or Project State reference after expiry.
- Material survives only when an attributable Agent Action writes a separate governed artifact, event, evidence record, or receipt.
- Copying Session Memory into a later Session without governed persistence and new View selection is forbidden.
- This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect.

## Boundaries

- Session Memory belongs to exactly one Agent Session and cannot be shared as private state with another Session.
- It has no authority effect and cannot satisfy a canonical dependency, evidence obligation, Decision basis, or Project State reference after expiry.
- Material survives only when an attributable Agent Action writes a separate governed artifact, event, evidence record, or receipt.
- Copying Session Memory into a later Session without governed persistence and new View selection is forbidden.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.source.actor-model-review@2026-10-05 | whole-file | `cc2fec4a1f9bd7a4796d6735866b16736087e125dcaf23d7fa6abed33862ee42` | `candidate-unadmitted` |

## Primary consumers

- .arcanum/ontology-vault/2026-10-05-lab-integrated-model.md

## Lookup and drift

- Index: `authority/definitions/candidates/0013-integrated-lab-definition-model/DEFINITIONS-INDEX.md` / `cal.definition.session-memory@1.0.0-candidate.1`
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

This candidate defines Session Memory for review only. It does not admit the Definition or any carrier, instance, relation, Policy, Decision, runtime behavior, authority, publication, release, deployment, or external effect.
