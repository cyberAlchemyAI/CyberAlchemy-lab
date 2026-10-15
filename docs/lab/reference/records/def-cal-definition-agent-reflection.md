[Documentation home](../../README.md)

# Agent Reflection

<a id="def-cal-definition-agent-reflection"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Agent Reflection

# Agent Reflection

A revisable diagnostic interpretation of recorded agent work and evidence. It states an interpretation for review, separately from observations, established findings or decisions.

**When it applies**

An Agent Reflection is an attributable revisable diagnostic interpretation of exact Agent Sessions, Actions, outputs, observations, feedback, evidence, and residue.

**Record formats**

[Agent reflection · v1](type-cal-artifact-type-agent-reflection-v1.md#type-cal-artifact-type-agent-reflection-v1)

**A stated exclusion**

It is not hidden chain of thought, Observation, Finding, Decision, Definition, Policy, proof of improvement, or authority.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-agent-reflection-section-2"></a>

## Source explanatory wording

An Agent Reflection is an attributable revisable diagnostic interpretation of exact Agent Sessions, Actions, outputs, observations, feedback, evidence, and residue. It is not hidden chain of thought, Observation, Finding, Decision, Definition, Policy, proof of improvement, or authority.

<a id="def-cal-definition-agent-reflection-section-3"></a>

## Exact governing statement

An Agent Reflection is an attributable revisable diagnostic interpretation of exact Agent Sessions, Actions, outputs, observations, feedback, evidence, and residue. It is not hidden chain of thought, Observation, Finding, Decision, Definition, Policy, proof of improvement, or authority.

````
AgentReflection(x) => governed_identity_or_record(x) and bounded_scope(x); AgentReflection(x) =/=> authority_effect(x).
````

- An Agent Reflection is an attributable revisable diagnostic interpretation of exact Agent Sessions, Actions, outputs, observations, feedback, evidence, and residue.
- It is not hidden chain of thought, Observation, Finding, Decision, Definition, Policy, proof of improvement, or authority.
- Identity, lifecycle, evidence, authority, and relation effects remain separately governed.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0013-integrated-lab-definition-model/definitions/agent-reflection/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.agent-reflection@1.0.0-candidate.1

**Content fingerprint · SHA-256**

59e885c9ba93cc43a7bd9984acbde6818d7a9b5f9b3de07b21266049ce23afa6

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "An Agent Reflection is an attributable revisable diagnostic interpretation of exact Agent Sessions, Actions, outputs, observations, feedback, evidence, and residue.",
  "authority_scope_ref": "scope:agent-reflection-definition",
  "exclusions": [
    "It is not hidden chain of thought, Observation, Finding, Decision, Definition, Policy, proof of improvement, or authority.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
