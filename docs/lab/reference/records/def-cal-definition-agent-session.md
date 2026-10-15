[Documentation home](../../README.md)

# Agent Session

<a id="def-cal-definition-agent-session"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Agent Session

# Agent Session

One temporary working period that identifies the agent instance, assignment, information views, policies, permissions, resources and termination conditions. It owns that instance’s working memory.

**When it applies**

When binding one instance to its exact assignment, views, permissions, inputs, budgets, working memory and termination conditions.

**Record formats**

[Agent session · v1](type-cal-artifact-type-agent-session-v1.md#type-cal-artifact-type-agent-session-v1)

**[In the Northstar incident](../../tutorials/incident-walkthrough.md)**

Bind the instance to its exact assignment, views, permissions, inputs, budgets and termination conditions.

**Common mistake**

Continuing on an expired view because the agent remembers its contents.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-agent-session-section-2"></a>

## Source explanatory wording

An Agent Session is a bounded execution context binding one Agent Instance to one Assignment, Context View, Ontology View, Policy set, authority envelope, inputs, budgets, cursor, Session Memory, and termination state. A Session binds exactly one concrete Agent Instance to exact Assignment, Context View, Ontology View, Policies, authority, inputs, budgets, cursor, and termination state.

<a id="def-cal-definition-agent-session-section-3"></a>

## Exact governing statement

An Agent Session is a bounded execution context binding one Agent Instance to one Assignment, Context View, Ontology View, Policy set, authority envelope, inputs, budgets, cursor, Session Memory, and termination state. A Session is neither durable Agent identity nor Project State; terminating a Machine Agent Session also terminates its Machine Agent Instance.

````
AgentSession(x) => governed_identity_or_record(x) and bounded_scope(x); AgentSession(x) =/=> authority_effect(x).
````

- A Session binds exactly one concrete Agent Instance to exact Assignment, Context View, Ontology View, Policies, authority, inputs, budgets, cursor, and termination state.
- A Session is an execution envelope, not durable Agent identity, Project State, or a source of cross-session authority.
- Session Memory is owned by this Session only and expires at termination.
- Machine Agent Instance termination is coupled to Session termination; persisted outputs require explicit governed Actions before termination.
- Views and authority evidence used by the Session retain exact versions, digests, freshness, expiry, and claim ceilings.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0013-integrated-lab-definition-model/definitions/agent-session/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.agent-session@1.0.0-candidate.1

**Content fingerprint · SHA-256**

71fbd822757e8e83e4072faf16e2d14c96148e6f24adbed4f225d03c4c48d9e7

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "An Agent Session is a bounded execution context binding one Agent Instance to one Assignment, Context View, Ontology View, Policy set, authority envelope, inputs, budgets, cursor, Session Memory, and termination state.",
  "authority_scope_ref": "scope:agent-session-definition",
  "exclusions": [
    "A Session binds exactly one concrete Agent Instance to exact Assignment, Context View, Ontology View, Policies, authority, inputs, budgets, cursor, and termination state.",
    "A Session is an execution envelope, not durable Agent identity, Project State, or a source of cross-session authority.",
    "Session Memory is owned by this Session only and expires at termination.",
    "Machine Agent Instance termination is coupled to Session termination; persisted outputs require explicit governed Actions before termination.",
    "Views and authority evidence used by the Session retain exact versions, digests, freshness, expiry, and claim ceilings.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
