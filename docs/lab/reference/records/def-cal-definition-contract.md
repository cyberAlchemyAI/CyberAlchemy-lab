[Documentation home](../../README.md)

# Contract

<a id="def-cal-definition-contract"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Contract

# Contract

A versioned statement of requirements, permissions, prohibitions, interfaces, evidence and breach handling for identified parties or things. The statement is separate from its implementation or proof of compliance.

**When it applies**

A Contract is a versioned governed statement of obligations, permissions, prohibitions, interfaces, boundaries, evidence requirements, parties or subjects, and breach handling.

**Record formats**

[Contract · v1](type-cal-artifact-type-contract-v1.md#type-cal-artifact-type-contract-v1)

**A stated exclusion**

A Contract is neither its implementation, compliance evidence, Policy issuer, nor proof that obligations were satisfied.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-contract-section-2"></a>

## Source explanatory wording

A Contract is a versioned governed statement of obligations, permissions, prohibitions, interfaces, boundaries, evidence requirements, parties or subjects, and breach handling. A Contract is neither its implementation, compliance evidence, Policy issuer, nor proof that obligations were satisfied.

<a id="def-cal-definition-contract-section-3"></a>

## Exact governing statement

A Contract is a versioned governed statement of obligations, permissions, prohibitions, interfaces, boundaries, evidence requirements, parties or subjects, and breach handling. A Contract is neither its implementation, compliance evidence, Policy issuer, nor proof that obligations were satisfied.

````
Contract(x) => governed_identity_or_record(x) and bounded_scope(x); Contract(x) =/=> authority_effect(x).
````

- A Contract is a versioned governed statement of obligations, permissions, prohibitions, interfaces, boundaries, evidence requirements, parties or subjects, and breach handling.
- A Contract is neither its implementation, compliance evidence, Policy issuer, nor proof that obligations were satisfied.
- Identity, lifecycle, evidence, authority, and relation effects remain separately governed.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0013-integrated-lab-definition-model/definitions/contract/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.contract@1.0.0-candidate.1

**Content fingerprint · SHA-256**

dd82c21d332c43d2d9fec50c61b33fa9b9e8751cf8763040cc8da25f680e1008

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "A Contract is a versioned governed statement of obligations, permissions, prohibitions, interfaces, boundaries, evidence requirements, parties or subjects, and breach handling.",
  "authority_scope_ref": "scope:contract-definition",
  "exclusions": [
    "A Contract is neither its implementation, compliance evidence, Policy issuer, nor proof that obligations were satisfied.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
