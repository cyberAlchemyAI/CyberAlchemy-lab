<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Project State

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.project-state`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:project-state-definition`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

Project State is the durable governed external state of a Project, including versioned artifacts, Definitions, decisions, evidence, event histories, relations, and other records. Project State is not owned by an Agent and is not hidden cross-session Machine Agent memory.

```text
ProjectState(P,t) = governed durable records admitted or retained by P at t; AgentMemoryLongTerm(a,s) := Select(ProjectState(P,t), ContextView(s), OntologyView(s)); owns(a,ProjectState)=false.
```

### Notation

| Symbol | Meaning |
| --- | --- |
| x | One subject evaluated under the Project State Definition. |

### Boundary conditions

- Project State belongs to the governed Project and its artifact owners, never to an Agent or model.
- Only explicit governed writes of artifacts, events, evidence, receipts, Decisions, and relations change Project State.
- Context Views and Ontology Views select Project State for a consumer; they do not create a competing canonical store.
- Hidden model state, caches, conversation recall, and expired Session Memory are excluded unless explicitly persisted through the governed Project path.

### Testable conditions

- Every durable state element resolves to a canonical carrier or declared event history with owner and lifecycle.
- Every Agent-produced state change resolves to an attributable Action and the required validation or Decision.
- No Machine Agent or Session is declared owner of Project State.
- A later Session reconstructs inputs from exact Views rather than an earlier Session’s private state.

## Plain-language voice

Project State is the durable governed external state of a Project, including versioned artifacts, Definitions, decisions, evidence, event histories, relations, and other records. Project State belongs to the governed Project and its artifact owners, never to an Agent or model.

## Domain-context voice

Workspace: `/home/vlad_/projects/CyberAlchemy-lab`

In the Lab, Project State supplies one distinct semantic responsibility in the integrated model. Its carrier and relations remain separate governed contracts.

### Examples

- The admitted Definition registry, candidate pack, decisions, evidence, and relation contracts form durable Lab Project State.

## Applicability

Project State is the durable governed external state of a Project, including versioned artifacts, Definitions, decisions, evidence, event histories, relations, and other records.

### Exclusions

- Project State belongs to the governed Project and its artifact owners, never to an Agent or model.
- Only explicit governed writes of artifacts, events, evidence, receipts, Decisions, and relations change Project State.
- Context Views and Ontology Views select Project State for a consumer; they do not create a competing canonical store.
- Hidden model state, caches, conversation recall, and expired Session Memory are excluded unless explicitly persisted through the governed Project path.
- This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect.

## Boundaries

- Project State belongs to the governed Project and its artifact owners, never to an Agent or model.
- Only explicit governed writes of artifacts, events, evidence, receipts, Decisions, and relations change Project State.
- Context Views and Ontology Views select Project State for a consumer; they do not create a competing canonical store.
- Hidden model state, caches, conversation recall, and expired Session Memory are excluded unless explicitly persisted through the governed Project path.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.source.actor-model-review@2026-10-05 | whole-file | `cc2fec4a1f9bd7a4796d6735866b16736087e125dcaf23d7fa6abed33862ee42` | `candidate-unadmitted` |

## Primary consumers

- .arcanum/ontology-vault/2026-10-05-lab-integrated-model.md

## Lookup and drift

- Index: `authority/definitions/candidates/0013-integrated-lab-definition-model/DEFINITIONS-INDEX.md` / `cal.definition.project-state@1.0.0-candidate.1`
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

This candidate defines Project State for review only. It does not admit the Definition or any carrier, instance, relation, Policy, Decision, runtime behavior, authority, publication, release, deployment, or external effect.
