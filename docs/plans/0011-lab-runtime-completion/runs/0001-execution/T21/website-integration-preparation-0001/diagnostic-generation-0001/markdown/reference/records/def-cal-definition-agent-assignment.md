[Documentation home](../../README.md)

# Agent Assignment

<a id="def-cal-definition-agent-assignment"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Agent Assignment

# Agent Assignment

Records the job or responsibility assigned to an agent, including what it concerns, its owner, time limits, expected participation and stopping conditions.

**When it applies**

When specifying an agent’s participation and job in bounded work.

**Record formats**

[Agent assignment · v1](type-cal-artifact-type-agent-assignment-v1.md#type-cal-artifact-type-agent-assignment-v1)

**[In the Northstar incident](../../tutorials/incident-walkthrough.md)**

Assign the agent to the bounded Northstar investigation Work.

**Common mistake**

Treating participation in the Work as permission to deploy code.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-agent-assignment-section-2"></a>

## Source explanatory wording

An Agent Assignment is a time-bounded owner-qualified binding of an Agent to an Intent, Goal, Project, Work item, Run, Role, or Responsibility. Assignment binds expected participation to exact subjects, scope, owner, period, deliverables or responsibilities, and stop conditions.

<a id="def-cal-definition-agent-assignment-section-3"></a>

## Exact governing statement

An Agent Assignment is a time-bounded owner-qualified binding of an Agent to an Intent, Goal, Project, Work item, Run, Role, or Responsibility. Assignment establishes expected participation and scope but grants no authority without an exact Authority Claim or Delegation.

````
AgentAssignment(x) => governed_identity_or_record(x) and bounded_scope(x); AgentAssignment(x) =/=> authority_effect(x).
````

- Assignment binds expected participation to exact subjects, scope, owner, period, deliverables or responsibilities, and stop conditions.
- Assignment is distinct from Role, Role Assignment, Authority Claim, Delegation, execution, completion, and outcome.
- Assignment alone grants no permission to use Tools, change Project State, make Decisions, or cause external effects.
- Assignment expiry, cancellation, or supersession ends expected participation without erasing prior Actions.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../assets/76da61f71e64-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.agent-assignment@1.0.0-candidate.1

**Content fingerprint · SHA-256**

76da61f71e64dee934da3e7c47c1b7188f54b677b38ec8b25647d46ac1b2f4c8

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "An Agent Assignment is a time-bounded owner-qualified binding of an Agent to an Intent, Goal, Project, Work item, Run, Role, or Responsibility.",
  "authority_scope_ref": "scope:agent-assignment-definition",
  "exclusions": [
    "Assignment binds expected participation to exact subjects, scope, owner, period, deliverables or responsibilities, and stop conditions.",
    "Assignment is distinct from Role, Role Assignment, Authority Claim, Delegation, execution, completion, and outcome.",
    "Assignment alone grants no permission to use Tools, change Project State, make Decisions, or cause external effects.",
    "Assignment expiry, cancellation, or supersession ends expected participation without erasing prior Actions.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
