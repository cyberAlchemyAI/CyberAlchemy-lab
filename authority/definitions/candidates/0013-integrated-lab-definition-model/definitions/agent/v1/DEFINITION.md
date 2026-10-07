<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Agent

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.agent`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:agent-definition`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

An Agent is an Actor that operates within an explicit Session, Context, Assignment, Policy, and authority boundary to perform attributable Actions with declared Capabilities and Tools. Capability does not grant authority, and Agent output is not automatically fact, decision, admission, Project State, or external effect.

```text
Agent(a,s) => Actor(a) and ActiveInstance(a,s) and Assignment(a,s) and ContextBound(s) and PolicyBound(s) and AuthorityBound(s); Capability(a,x) =/=> Authorized(a,x); Output(a,y) =/=> Accepted(y) or AuthorityEffect(y).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| x | One subject evaluated under the Agent Definition. |

### Boundary conditions

- Agent is an operational Actor classification; concrete operation requires an active Agent Instance inside one active Agent Session.
- Agent, Person, Principal, Role, Profile, Instance, Session, Action, model, Implementation, and Tool remain independently identified concepts.
- Agent Capability describes what may be attempted; an Authority Claim or Delegation separately determines what may be done in exact scope.
- An Agent Assignment defines expected participation; it grants no authority and proves no completion or outcome.
- Agent output does not become accepted evidence, Finding, Definition, Policy, Decision, admission, Project State, or external effect without the applicable governed path.
- A Machine Agent owns no durable memory: cross-session continuity comes only from Project State selected through exact Context and Ontology Views.
- A Machine Agent may propose changes to its Profile, Capability, Implementation, Policy, or lesson selection but cannot approve or activate those changes for itself.
- Every consequential Agent Action remains attributable to its exact Agent Instance, Session, accountable Principal, authority evidence, and resulting receipt or residue.

### Testable conditions

- Every performed Agent Action binds an active Agent Instance and its one active Session.
- Every Action resolves an active Assignment, applicable Policy, Context, and exact authority evidence before a governed effect.
- No capability, Assignment, Role, tool access, model output, or prior Session silently supplies authority.
- No Machine Agent Instance predates, outlives, or spans its Session.
- No Session reads hidden prior-session memory; durable inputs resolve to Project State through exact Views.
- No Agent-produced output changes owner-governed state without the required validation and Decision.
- No Agent self-approves a Profile, Capability, Implementation, Policy, Delegation, admission, or lifecycle change.

## Plain-language voice

An Agent is an Actor that operates within an explicit Session, Context, Assignment, Policy, and authority boundary to perform attributable Actions with declared Capabilities and Tools. Agent is an operational Actor classification; concrete operation requires an active Agent Instance inside one active Agent Session.

## Domain-context voice

Workspace: `/home/vlad_/projects/CyberAlchemy-lab`

In the Lab, Agent supplies one distinct semantic responsibility in the integrated model. Its carrier and relations remain separate governed contracts.

### Examples

- A coding Agent reads a Context View, edits a Definition candidate in one Session, and records the Action; the Definition owner still decides admission.

## Applicability

An Agent is an Actor that operates within an explicit Session, Context, Assignment, Policy, and authority boundary to perform attributable Actions with declared Capabilities and Tools.

### Exclusions

- Agent is an operational Actor classification; concrete operation requires an active Agent Instance inside one active Agent Session.
- Agent, Person, Principal, Role, Profile, Instance, Session, Action, model, Implementation, and Tool remain independently identified concepts.
- Agent Capability describes what may be attempted; an Authority Claim or Delegation separately determines what may be done in exact scope.
- An Agent Assignment defines expected participation; it grants no authority and proves no completion or outcome.
- Agent output does not become accepted evidence, Finding, Definition, Policy, Decision, admission, Project State, or external effect without the applicable governed path.
- A Machine Agent owns no durable memory: cross-session continuity comes only from Project State selected through exact Context and Ontology Views.
- A Machine Agent may propose changes to its Profile, Capability, Implementation, Policy, or lesson selection but cannot approve or activate those changes for itself.
- Every consequential Agent Action remains attributable to its exact Agent Instance, Session, accountable Principal, authority evidence, and resulting receipt or residue.
- This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect.

## Boundaries

- Agent is an operational Actor classification; concrete operation requires an active Agent Instance inside one active Agent Session.
- Agent, Person, Principal, Role, Profile, Instance, Session, Action, model, Implementation, and Tool remain independently identified concepts.
- Agent Capability describes what may be attempted; an Authority Claim or Delegation separately determines what may be done in exact scope.
- An Agent Assignment defines expected participation; it grants no authority and proves no completion or outcome.
- Agent output does not become accepted evidence, Finding, Definition, Policy, Decision, admission, Project State, or external effect without the applicable governed path.
- A Machine Agent owns no durable memory: cross-session continuity comes only from Project State selected through exact Context and Ontology Views.
- A Machine Agent may propose changes to its Profile, Capability, Implementation, Policy, or lesson selection but cannot approve or activate those changes for itself.
- Every consequential Agent Action remains attributable to its exact Agent Instance, Session, accountable Principal, authority evidence, and resulting receipt or residue.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.source.actor-model-review@2026-10-05 | whole-file | `cc2fec4a1f9bd7a4796d6735866b16736087e125dcaf23d7fa6abed33862ee42` | `candidate-unadmitted` |

## Primary consumers

- .arcanum/ontology-vault/2026-10-05-lab-integrated-model.md

## Lookup and drift

- Index: `authority/definitions/candidates/0013-integrated-lab-definition-model/DEFINITIONS-INDEX.md` / `cal.definition.agent@1.0.0-candidate.1`
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

This candidate defines Agent for review only. It does not admit the Definition or any carrier, instance, relation, Policy, Decision, runtime behavior, authority, publication, release, deployment, or external effect.
