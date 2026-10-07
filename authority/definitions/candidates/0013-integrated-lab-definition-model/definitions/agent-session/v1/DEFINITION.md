<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Agent Session

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.agent-session`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:agent-session-definition`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

An Agent Session is a bounded execution context binding one Agent Instance to one Assignment, Context View, Ontology View, Policy set, authority envelope, inputs, budgets, cursor, Session Memory, and termination state. A Session is neither durable Agent identity nor Project State; terminating a Machine Agent Session also terminates its Machine Agent Instance.

```text
AgentSession(x) => governed_identity_or_record(x) and bounded_scope(x); AgentSession(x) =/=> authority_effect(x).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| x | One subject evaluated under the Agent Session Definition. |

### Boundary conditions

- A Session binds exactly one concrete Agent Instance to exact Assignment, Context View, Ontology View, Policies, authority, inputs, budgets, cursor, and termination state.
- A Session is an execution envelope, not durable Agent identity, Project State, or a source of cross-session authority.
- Session Memory is owned by this Session only and expires at termination.
- Machine Agent Instance termination is coupled to Session termination; persisted outputs require explicit governed Actions before termination.
- Views and authority evidence used by the Session retain exact versions, digests, freshness, expiry, and claim ceilings.

### Testable conditions

- Every Session has exactly one Agent Instance and one explicit termination posture.
- Every Session input is either declared directly or resolved through exact Context and Ontology Views.
- No expired View, grant, Policy, or Delegation is used for an Action.
- On termination, the Machine Agent Instance and Session Memory are no longer active.
- Only explicit persisted artifacts, events, evidence, and receipts remain in Project State.

## Plain-language voice

An Agent Session is a bounded execution context binding one Agent Instance to one Assignment, Context View, Ontology View, Policy set, authority envelope, inputs, budgets, cursor, Session Memory, and termination state. A Session binds exactly one concrete Agent Instance to exact Assignment, Context View, Ontology View, Policies, authority, inputs, budgets, cursor, and termination state.

## Domain-context voice

Workspace: `/home/vlad_/projects/CyberAlchemy-lab`

In the Lab, Agent Session supplies one distinct semantic responsibility in the integrated model. Its carrier and relations remain separate governed contracts.

### Examples

- session:lab-model-2026-10-06 binds the Step 2 assignment, exact repository views, token budget, Actions, and termination receipt.

## Applicability

An Agent Session is a bounded execution context binding one Agent Instance to one Assignment, Context View, Ontology View, Policy set, authority envelope, inputs, budgets, cursor, Session Memory, and termination state.

### Exclusions

- A Session binds exactly one concrete Agent Instance to exact Assignment, Context View, Ontology View, Policies, authority, inputs, budgets, cursor, and termination state.
- A Session is an execution envelope, not durable Agent identity, Project State, or a source of cross-session authority.
- Session Memory is owned by this Session only and expires at termination.
- Machine Agent Instance termination is coupled to Session termination; persisted outputs require explicit governed Actions before termination.
- Views and authority evidence used by the Session retain exact versions, digests, freshness, expiry, and claim ceilings.
- This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect.

## Boundaries

- A Session binds exactly one concrete Agent Instance to exact Assignment, Context View, Ontology View, Policies, authority, inputs, budgets, cursor, and termination state.
- A Session is an execution envelope, not durable Agent identity, Project State, or a source of cross-session authority.
- Session Memory is owned by this Session only and expires at termination.
- Machine Agent Instance termination is coupled to Session termination; persisted outputs require explicit governed Actions before termination.
- Views and authority evidence used by the Session retain exact versions, digests, freshness, expiry, and claim ceilings.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.source.actor-model-review@2026-10-05 | whole-file | `cc2fec4a1f9bd7a4796d6735866b16736087e125dcaf23d7fa6abed33862ee42` | `candidate-unadmitted` |

## Primary consumers

- .arcanum/ontology-vault/2026-10-05-lab-integrated-model.md

## Lookup and drift

- Index: `authority/definitions/candidates/0013-integrated-lab-definition-model/DEFINITIONS-INDEX.md` / `cal.definition.agent-session@1.0.0-candidate.1`
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

This candidate defines Agent Session for review only. It does not admit the Definition or any carrier, instance, relation, Policy, Decision, runtime behavior, authority, publication, release, deployment, or external effect.
