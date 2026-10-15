[Documentation home](../../README.md)

# Agent

<a id="def-cal-definition-agent"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Agent

# Agent

An operational participant that works through an identified instance and session, with a job, prepared information, tools and stated permissions.

**When it applies**

An Agent is an Actor that operates within an explicit Session, Context, Assignment, Policy, and authority boundary to perform attributable Actions with declared Capabilities and Tools.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**A stated exclusion**

Agent is an operational Actor classification; concrete operation requires an active Agent Instance inside one active Agent Session.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-agent-section-2"></a>

## Source explanatory wording

An Agent is an Actor that operates within an explicit Session, Context, Assignment, Policy, and authority boundary to perform attributable Actions with declared Capabilities and Tools. Agent is an operational Actor classification; concrete operation requires an active Agent Instance inside one active Agent Session.

<a id="def-cal-definition-agent-section-3"></a>

## Exact governing statement

An Agent is an Actor that operates within an explicit Session, Context, Assignment, Policy, and authority boundary to perform attributable Actions with declared Capabilities and Tools. Capability does not grant authority, and Agent output is not automatically fact, decision, admission, Project State, or external effect.

````
Agent(a,s) => Actor(a) and ActiveInstance(a,s) and Assignment(a,s) and ContextBound(s) and PolicyBound(s) and AuthorityBound(s); Capability(a,x) =/=> Authorized(a,x); Output(a,y) =/=> Accepted(y) or AuthorityEffect(y).
````

- Agent is an operational Actor classification; concrete operation requires an active Agent Instance inside one active Agent Session.
- Agent, Person, Principal, Role, Profile, Instance, Session, Action, model, Implementation, and Tool remain independently identified concepts.
- Agent Capability describes what may be attempted; an Authority Claim or Delegation separately determines what may be done in exact scope.
- An Agent Assignment defines expected participation; it grants no authority and proves no completion or outcome.
- Agent output does not become accepted evidence, Finding, Definition, Policy, Decision, admission, Project State, or external effect without the applicable governed path.
- A Machine Agent owns no durable memory: cross-session continuity comes only from Project State selected through exact Context and Ontology Views.
- A Machine Agent may propose changes to its Profile, Capability, Implementation, Policy, or lesson selection but cannot approve or activate those changes for itself.
- Every consequential Agent Action remains attributable to its exact Agent Instance, Session, accountable Principal, authority evidence, and resulting receipt or residue.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0013-integrated-lab-definition-model/definitions/agent/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.agent@1.0.0-candidate.1

**Content fingerprint · SHA-256**

d4d37df4348174422e4ca428074a997b80bb6b0ab6eee1efd7721c09a06b70d3

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "An Agent is an Actor that operates within an explicit Session, Context, Assignment, Policy, and authority boundary to perform attributable Actions with declared Capabilities and Tools.",
  "authority_scope_ref": "scope:agent-definition",
  "exclusions": [
    "Agent is an operational Actor classification; concrete operation requires an active Agent Instance inside one active Agent Session.",
    "Agent, Person, Principal, Role, Profile, Instance, Session, Action, model, Implementation, and Tool remain independently identified concepts.",
    "Agent Capability describes what may be attempted; an Authority Claim or Delegation separately determines what may be done in exact scope.",
    "An Agent Assignment defines expected participation; it grants no authority and proves no completion or outcome.",
    "Agent output does not become accepted evidence, Finding, Definition, Policy, Decision, admission, Project State, or external effect without the applicable governed path.",
    "A Machine Agent owns no durable memory: cross-session continuity comes only from Project State selected through exact Context and Ontology Views.",
    "A Machine Agent may propose changes to its Profile, Capability, Implementation, Policy, or lesson selection but cannot approve or activate those changes for itself.",
    "Every consequential Agent Action remains attributable to its exact Agent Instance, Session, accountable Principal, authority evidence, and resulting receipt or residue.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
