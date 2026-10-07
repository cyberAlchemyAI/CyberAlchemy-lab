<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Agent Assignment

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.agent-assignment`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:agent-assignment-definition`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

An Agent Assignment is a time-bounded owner-qualified binding of an Agent to an Intent, Goal, Project, Work item, Run, Role, or Responsibility. Assignment establishes expected participation and scope but grants no authority without an exact Authority Claim or Delegation.

```text
AgentAssignment(x) => governed_identity_or_record(x) and bounded_scope(x); AgentAssignment(x) =/=> authority_effect(x).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| x | One subject evaluated under the Agent Assignment Definition. |

### Boundary conditions

- Assignment binds expected participation to exact subjects, scope, owner, period, deliverables or responsibilities, and stop conditions.
- Assignment is distinct from Role, Role Assignment, Authority Claim, Delegation, execution, completion, and outcome.
- Assignment alone grants no permission to use Tools, change Project State, make Decisions, or cause external effects.
- Assignment expiry, cancellation, or supersession ends expected participation without erasing prior Actions.

### Testable conditions

- Every active Assignment names the Agent or eligible Profile, target, scope, owner, start, expiry, and termination rule.
- Every Agent Action falls within an active relevant Assignment or records an explicit exception route.
- No Assignment is accepted as authority evidence.
- Completion and outcome are recorded through separate Action and assessment records.

## Plain-language voice

An Agent Assignment is a time-bounded owner-qualified binding of an Agent to an Intent, Goal, Project, Work item, Run, Role, or Responsibility. Assignment binds expected participation to exact subjects, scope, owner, period, deliverables or responsibilities, and stop conditions.

## Domain-context voice

Workspace: `/home/vlad_/projects/CyberAlchemy-lab`

In the Lab, Agent Assignment supplies one distinct semantic responsibility in the integrated model. Its carrier and relations remain separate governed contracts.

### Examples

- assignment:review-lab-definitions binds one Agent Instance to Step 2 candidate authoring, with no admission permission.

## Applicability

An Agent Assignment is a time-bounded owner-qualified binding of an Agent to an Intent, Goal, Project, Work item, Run, Role, or Responsibility.

### Exclusions

- Assignment binds expected participation to exact subjects, scope, owner, period, deliverables or responsibilities, and stop conditions.
- Assignment is distinct from Role, Role Assignment, Authority Claim, Delegation, execution, completion, and outcome.
- Assignment alone grants no permission to use Tools, change Project State, make Decisions, or cause external effects.
- Assignment expiry, cancellation, or supersession ends expected participation without erasing prior Actions.
- This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect.

## Boundaries

- Assignment binds expected participation to exact subjects, scope, owner, period, deliverables or responsibilities, and stop conditions.
- Assignment is distinct from Role, Role Assignment, Authority Claim, Delegation, execution, completion, and outcome.
- Assignment alone grants no permission to use Tools, change Project State, make Decisions, or cause external effects.
- Assignment expiry, cancellation, or supersession ends expected participation without erasing prior Actions.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.source.actor-model-review@2026-10-05 | whole-file | `cc2fec4a1f9bd7a4796d6735866b16736087e125dcaf23d7fa6abed33862ee42` | `candidate-unadmitted` |

## Primary consumers

- .arcanum/ontology-vault/2026-10-05-lab-integrated-model.md

## Lookup and drift

- Index: `authority/definitions/candidates/0013-integrated-lab-definition-model/DEFINITIONS-INDEX.md` / `cal.definition.agent-assignment@1.0.0-candidate.1`
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

This candidate defines Agent Assignment for review only. It does not admit the Definition or any carrier, instance, relation, Policy, Decision, runtime behavior, authority, publication, release, deployment, or external effect.
