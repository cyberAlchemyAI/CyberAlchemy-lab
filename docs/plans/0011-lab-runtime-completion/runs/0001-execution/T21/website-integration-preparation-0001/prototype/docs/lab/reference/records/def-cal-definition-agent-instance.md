[Documentation home](../../README.md)

# Agent Instance

<a id="def-cal-definition-agent-instance"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Agent Instance

# Agent Instance

One concrete operational agent, with its behavior profile, implementation, capabilities and accountability identified. A machine instance belongs to one session and ends with it.

**When it applies**

When identifying the concrete agent performing attributable actions; a machine instance belongs to one session.

**Record formats**

[Agent instance · v1](type-cal-artifact-type-agent-instance-v1.md#type-cal-artifact-type-agent-instance-v1)

**[In the Northstar incident](../../tutorials/incident-walkthrough.md)**

One temporary machine-agent instance performs session 12; a later session uses a new instance.

**Common mistake**

Making the machine instance the durable owner of project knowledge.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-agent-instance-section-2"></a>

## Source explanatory wording

An Agent Instance is one time-bounded concrete realization of Agent, bound to a Profile, Implementation, capability set, accountable Principal, owner route, and lifecycle. Agent Instance is the concrete time-bounded operational identity; it is not its Person, Principal, Profile, model, Implementation, Session, or authority grant.

<a id="def-cal-definition-agent-instance-section-3"></a>

## Exact governing statement

An Agent Instance is one time-bounded concrete realization of Agent, bound to a Profile, Implementation, capability set, accountable Principal, owner route, and lifecycle. It is not a Person, model, Implementation, Session, or authority grant; a Machine Agent Instance cannot outlive or span Sessions.

````
MachineInstance(i,s) => AgentInstance(i) and exactlyOneSession(i,s) and born(i)=start(s) and expires(i)=end(s); i1.session != i2.session => i1 != i2.
````

- Agent Instance is the concrete time-bounded operational identity; it is not its Person, Principal, Profile, model, Implementation, Session, or authority grant.
- Every Instance binds exact Profile, Implementation, capability-set, accountable-Principal, owner-route, and lifecycle versions.
- A Machine Agent Instance belongs to exactly one Session, begins no earlier than that Session, ends with it, and cannot resume in a later Session.
- Equal Profile, model, Implementation, or inputs across Sessions do not create Agent Instance identity continuity.
- An Instance may act only through its Session, Assignment, Policies, Context, and authority envelope.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../assets/21d331a24a6f-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.agent-instance@1.0.0-candidate.1

**Content fingerprint · SHA-256**

21d331a24a6fb7420c2bc59fe504c0701708bd6685925d7dba1a92791070adcd

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "An Agent Instance is one time-bounded concrete realization of Agent, bound to a Profile, Implementation, capability set, accountable Principal, owner route, and lifecycle.",
  "authority_scope_ref": "scope:agent-instance-definition",
  "exclusions": [
    "Agent Instance is the concrete time-bounded operational identity; it is not its Person, Principal, Profile, model, Implementation, Session, or authority grant.",
    "Every Instance binds exact Profile, Implementation, capability-set, accountable-Principal, owner-route, and lifecycle versions.",
    "A Machine Agent Instance belongs to exactly one Session, begins no earlier than that Session, ends with it, and cannot resume in a later Session.",
    "Equal Profile, model, Implementation, or inputs across Sessions do not create Agent Instance identity continuity.",
    "An Instance may act only through its Session, Assignment, Policies, Context, and authority envelope.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
