[Documentation home](../../README.md)

# Governed Model

<a id="def-cal-definition-governed-model"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Governed Model

# Governed Model

A versioned model of concepts, rules, structures or behavior with scope, owner, sources, assumptions, checks, lifecycle and challenge handling. It is not automatically an ontology, implementation or accepted truth.

**When it applies**

A Governed Model is a versioned explicit representation of concepts, rules, structures, or behavior with scope, owner, sources, assumptions, validation, lifecycle, and challenge route.

**Record formats**

[Governed model · v1](type-cal-artifact-type-governed-model-v1.md#type-cal-artifact-type-governed-model-v1)

**A stated exclusion**

It is not automatically an Ontology, runtime, Implementation, truth claim, decision, or admitted authority.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-governed-model-section-2"></a>

## Source explanatory wording

A Governed Model is a versioned explicit representation of concepts, rules, structures, or behavior with scope, owner, sources, assumptions, validation, lifecycle, and challenge route. It is not automatically an Ontology, runtime, Implementation, truth claim, decision, or admitted authority.

<a id="def-cal-definition-governed-model-section-3"></a>

## Exact governing statement

A Governed Model is a versioned explicit representation of concepts, rules, structures, or behavior with scope, owner, sources, assumptions, validation, lifecycle, and challenge route. It is not automatically an Ontology, runtime, Implementation, truth claim, decision, or admitted authority.

````
GovernedModel(x) => governed_identity_or_record(x) and bounded_scope(x); GovernedModel(x) =/=> authority_effect(x).
````

- A Governed Model is a versioned explicit representation of concepts, rules, structures, or behavior with scope, owner, sources, assumptions, validation, lifecycle, and challenge route.
- It is not automatically an Ontology, runtime, Implementation, truth claim, decision, or admitted authority.
- Identity, lifecycle, evidence, authority, and relation effects remain separately governed.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0013-integrated-lab-definition-model/definitions/governed-model/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.governed-model@1.0.0-candidate.1

**Content fingerprint · SHA-256**

b53f09b48390daf9477c0d025e9c6f3b15798c82dba093033c03086cd4a4732f

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "A Governed Model is a versioned explicit representation of concepts, rules, structures, or behavior with scope, owner, sources, assumptions, validation, lifecycle, and challenge route.",
  "authority_scope_ref": "scope:governed-model-definition",
  "exclusions": [
    "It is not automatically an Ontology, runtime, Implementation, truth claim, decision, or admitted authority.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
