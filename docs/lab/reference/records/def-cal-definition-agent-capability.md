[Documentation home](../../README.md)

# Agent Capability

<a id="def-cal-definition-agent-capability"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Agent Capability

# Agent Capability

Describes a class of attempts an agent can technically make, with input, output, evidence and failure requirements. Ability does not itself grant permission.

**When it applies**

An Agent Capability is a bounded class of action or interpretation that an Agent may be technically able to attempt under exact input, output, evidence, and failure contracts.

**Record formats**

[Agent capability · v1](type-cal-artifact-type-agent-capability-v1.md#type-cal-artifact-type-agent-capability-v1)

**A stated exclusion**

Agent Capability states a bounded class of attempt and must declare inputs, outputs, evidence, failure modes, and implementation bindings.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-agent-capability-section-2"></a>

## Source explanatory wording

An Agent Capability is a bounded class of action or interpretation that an Agent may be technically able to attempt under exact input, output, evidence, and failure contracts. Agent Capability states a bounded class of attempt and must declare inputs, outputs, evidence, failure modes, and implementation bindings.

<a id="def-cal-definition-agent-capability-section-3"></a>

## Exact governing statement

An Agent Capability is a bounded class of action or interpretation that an Agent may be technically able to attempt under exact input, output, evidence, and failure contracts. Agent Capability is distinct from Product Capability, Tool, Implementation, Role, authority, and successful performance.

````
AgentCapability(x) => governed_identity_or_record(x) and bounded_scope(x); AgentCapability(x) =/=> authority_effect(x).
````

- Agent Capability states a bounded class of attempt and must declare inputs, outputs, evidence, failure modes, and implementation bindings.
- Agent Capability is independent from Product Capability, Tool, model, Implementation, Role, Assignment, authority, and observed success.
- Possessing or advertising a Capability never authorizes its use in a particular Session or scope.
- Capability revision and activation require governed owner action; an Agent cannot self-upgrade by claiming a new Capability.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0013-integrated-lab-definition-model/definitions/agent-capability/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.agent-capability@1.0.0-candidate.1

**Content fingerprint · SHA-256**

9b9c7ad71ad4aef681504fc5be27de8770876a72f0e59b7ee8eba7fc6fd76a2a

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "An Agent Capability is a bounded class of action or interpretation that an Agent may be technically able to attempt under exact input, output, evidence, and failure contracts.",
  "authority_scope_ref": "scope:agent-capability-definition",
  "exclusions": [
    "Agent Capability states a bounded class of attempt and must declare inputs, outputs, evidence, failure modes, and implementation bindings.",
    "Agent Capability is independent from Product Capability, Tool, model, Implementation, Role, Assignment, authority, and observed success.",
    "Possessing or advertising a Capability never authorizes its use in a particular Session or scope.",
    "Capability revision and activation require governed owner action; an Agent cannot self-upgrade by claiming a new Capability.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
