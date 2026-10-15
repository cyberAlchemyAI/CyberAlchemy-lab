[Documentation home](../../README.md)

# Implementation

<a id="def-cal-definition-implementation"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Implementation

# Implementation

A versioned technical realization with sources, owner, interfaces, build or deployment information and evidence. Its existence does not prove live operation, compliance or value.

**When it applies**

When identifying the exact technical realization, its version, owner, interfaces and build or deployment posture.

**Record formats**

[Implementation · v1](type-cal-artifact-type-implementation-v1.md#type-cal-artifact-type-implementation-v1)

**[In the Northstar incident](../../tutorials/incident-walkthrough.md)**

Software revision 7 is the realization used in run 12; revision 8 is proposed.

**Common mistake**

Treating a proposed revision as deployed or proven to repair the omission.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-implementation-section-2"></a>

## Source explanatory wording

An Implementation is a governed technical realization with stable identity, version, owner, lifecycle, source binding, build or deployment posture, interfaces, and evidence bindings. It is distinct from Product, Product Capability, Agent, model, Tool, runtime instance, and proof of conformance or value.

<a id="def-cal-definition-implementation-section-3"></a>

## Exact governing statement

An Implementation is a governed technical realization with stable identity, version, owner, lifecycle, source binding, build or deployment posture, interfaces, and evidence bindings. It is distinct from Product, Product Capability, Agent, model, Tool, runtime instance, and proof of conformance or value.

````
Implementation(x) => governed_identity_or_record(x) and bounded_scope(x); Implementation(x) =/=> authority_effect(x).
````

- An Implementation is a governed technical realization with stable identity, version, owner, lifecycle, source binding, build or deployment posture, interfaces, and evidence bindings.
- It is distinct from Product, Product Capability, Agent, model, Tool, runtime instance, and proof of conformance or value.
- Identity, lifecycle, evidence, authority, and relation effects remain separately governed.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../assets/c25fcb2b31e8-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.implementation@1.0.0-candidate.1

**Content fingerprint · SHA-256**

c25fcb2b31e8fee007261a645627fe8aae61d5778a51781a35cc549dc7aa79c1

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "An Implementation is a governed technical realization with stable identity, version, owner, lifecycle, source binding, build or deployment posture, interfaces, and evidence bindings.",
  "authority_scope_ref": "scope:implementation-definition",
  "exclusions": [
    "It is distinct from Product, Product Capability, Agent, model, Tool, runtime instance, and proof of conformance or value.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
