[Documentation home](../../README.md)

# Tool

<a id="def-cal-definition-tool"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Tool

# Tool

An invocable resource with a versioned interface, input and output requirements, failure limits and evidence route. Availability does not grant permission or prove successful use.

**When it applies**

A Tool is a governed invocable resource used by an Agent Action through a declared interface, version, input/output contract, failure boundary, and evidence route.

**Record formats**

[Tool · v1](type-cal-artifact-type-tool-v1.md#type-cal-artifact-type-tool-v1)

**A stated exclusion**

Tool availability grants neither Agent Capability nor authority and does not prove correct invocation or effect.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-tool-section-2"></a>

## Source explanatory wording

A Tool is a governed invocable resource used by an Agent Action through a declared interface, version, input/output contract, failure boundary, and evidence route. Tool availability grants neither Agent Capability nor authority and does not prove correct invocation or effect.

<a id="def-cal-definition-tool-section-3"></a>

## Exact governing statement

A Tool is a governed invocable resource used by an Agent Action through a declared interface, version, input/output contract, failure boundary, and evidence route. Tool availability grants neither Agent Capability nor authority and does not prove correct invocation or effect.

````
Tool(x) => governed_identity_or_record(x) and bounded_scope(x); Tool(x) =/=> authority_effect(x).
````

- A Tool is a governed invocable resource used by an Agent Action through a declared interface, version, input/output contract, failure boundary, and evidence route.
- Tool availability grants neither Agent Capability nor authority and does not prove correct invocation or effect.
- Identity, lifecycle, evidence, authority, and relation effects remain separately governed.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0013-integrated-lab-definition-model/definitions/tool/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.tool@1.0.0-candidate.1

**Content fingerprint · SHA-256**

47ff8558b24443d223a77f2b19fd0b12111ba2ff1be6049860522af9412981d5

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "A Tool is a governed invocable resource used by an Agent Action through a declared interface, version, input/output contract, failure boundary, and evidence route.",
  "authority_scope_ref": "scope:tool-definition",
  "exclusions": [
    "Tool availability grants neither Agent Capability nor authority and does not prove correct invocation or effect.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
