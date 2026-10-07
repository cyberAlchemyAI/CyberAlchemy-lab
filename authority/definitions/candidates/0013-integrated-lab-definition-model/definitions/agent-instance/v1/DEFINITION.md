<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Agent Instance

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.agent-instance`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:agent-instance-definition`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

An Agent Instance is one time-bounded concrete realization of Agent, bound to a Profile, Implementation, capability set, accountable Principal, owner route, and lifecycle. It is not a Person, model, Implementation, Session, or authority grant; a Machine Agent Instance cannot outlive or span Sessions.

```text
MachineInstance(i,s) => AgentInstance(i) and exactlyOneSession(i,s) and born(i)=start(s) and expires(i)=end(s); i1.session != i2.session => i1 != i2.
```

### Notation

| Symbol | Meaning |
| --- | --- |
| x | One subject evaluated under the Agent Instance Definition. |

### Boundary conditions

- Agent Instance is the concrete time-bounded operational identity; it is not its Person, Principal, Profile, model, Implementation, Session, or authority grant.
- Every Instance binds exact Profile, Implementation, capability-set, accountable-Principal, owner-route, and lifecycle versions.
- A Machine Agent Instance belongs to exactly one Session, begins no earlier than that Session, ends with it, and cannot resume in a later Session.
- Equal Profile, model, Implementation, or inputs across Sessions do not create Agent Instance identity continuity.
- An Instance may act only through its Session, Assignment, Policies, Context, and authority envelope.

### Testable conditions

- Every Machine Agent Instance has exactly one Agent Session reference.
- The Machine Agent Instance active interval is contained in and terminates with the Session interval.
- No later Session reuses the expired Instance identity.
- Every Action attributed to the Instance falls inside its active Session and cites exact authority evidence.
- No Instance identity is inferred from a model, process, API credential, or Profile alone.

## Plain-language voice

An Agent Instance is one time-bounded concrete realization of Agent, bound to a Profile, Implementation, capability set, accountable Principal, owner route, and lifecycle. Agent Instance is the concrete time-bounded operational identity; it is not its Person, Principal, Profile, model, Implementation, Session, or authority grant.

## Domain-context voice

Workspace: `/home/vlad_/projects/CyberAlchemy-lab`

In the Lab, Agent Instance supplies one distinct semantic responsibility in the integrated model. Its carrier and relations remain separate governed contracts.

### Examples

- agent-instance:step2-review exists only for session:lab-model-2026-10-06 and terminates with it.

## Applicability

An Agent Instance is one time-bounded concrete realization of Agent, bound to a Profile, Implementation, capability set, accountable Principal, owner route, and lifecycle.

### Exclusions

- Agent Instance is the concrete time-bounded operational identity; it is not its Person, Principal, Profile, model, Implementation, Session, or authority grant.
- Every Instance binds exact Profile, Implementation, capability-set, accountable-Principal, owner-route, and lifecycle versions.
- A Machine Agent Instance belongs to exactly one Session, begins no earlier than that Session, ends with it, and cannot resume in a later Session.
- Equal Profile, model, Implementation, or inputs across Sessions do not create Agent Instance identity continuity.
- An Instance may act only through its Session, Assignment, Policies, Context, and authority envelope.
- This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect.

## Boundaries

- Agent Instance is the concrete time-bounded operational identity; it is not its Person, Principal, Profile, model, Implementation, Session, or authority grant.
- Every Instance binds exact Profile, Implementation, capability-set, accountable-Principal, owner-route, and lifecycle versions.
- A Machine Agent Instance belongs to exactly one Session, begins no earlier than that Session, ends with it, and cannot resume in a later Session.
- Equal Profile, model, Implementation, or inputs across Sessions do not create Agent Instance identity continuity.
- An Instance may act only through its Session, Assignment, Policies, Context, and authority envelope.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.source.actor-model-review@2026-10-05 | whole-file | `cc2fec4a1f9bd7a4796d6735866b16736087e125dcaf23d7fa6abed33862ee42` | `candidate-unadmitted` |

## Primary consumers

- .arcanum/ontology-vault/2026-10-05-lab-integrated-model.md

## Lookup and drift

- Index: `authority/definitions/candidates/0013-integrated-lab-definition-model/DEFINITIONS-INDEX.md` / `cal.definition.agent-instance@1.0.0-candidate.1`
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

This candidate defines Agent Instance for review only. It does not admit the Definition or any carrier, instance, relation, Policy, Decision, runtime behavior, authority, publication, release, deployment, or external effect.
