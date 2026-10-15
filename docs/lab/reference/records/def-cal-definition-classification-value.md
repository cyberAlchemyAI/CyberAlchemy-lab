[Documentation home](../../README.md)

# Classification Value

<a id="def-cal-definition-classification-value"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Classification Value

# Classification Value

One allowed answer within a particular classification question and scheme version. A similar label elsewhere does not make it the same value.

**When it applies**

A Classification Value is one governed allowed answer under one exact Classification Axis and Scheme version, with stable identity, meaning, applicability, exclusions, and mappings.

**Record formats**

[Classification value · v1](type-cal-artifact-type-classification-value-v1.md#type-cal-artifact-type-classification-value-v1)

**A stated exclusion**

Its label is not its identity, and similar labels across axes do not collapse their meanings.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-classification-value-section-2"></a>

## Source explanatory wording

A Classification Value is one governed allowed answer under one exact Classification Axis and Scheme version, with stable identity, meaning, applicability, exclusions, and mappings. Its label is not its identity, and similar labels across axes do not collapse their meanings.

<a id="def-cal-definition-classification-value-section-3"></a>

## Exact governing statement

A Classification Value is one governed allowed answer under one exact Classification Axis and Scheme version, with stable identity, meaning, applicability, exclusions, and mappings. Its label is not its identity, and similar labels across axes do not collapse their meanings.

````
ClassificationValue(x) => governed_identity_or_record(x) and bounded_scope(x); ClassificationValue(x) =/=> authority_effect(x).
````

- A Classification Value is one governed allowed answer under one exact Classification Axis and Scheme version, with stable identity, meaning, applicability, exclusions, and mappings.
- Its label is not its identity, and similar labels across axes do not collapse their meanings.
- Identity, lifecycle, evidence, authority, and relation effects remain separately governed.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0013-integrated-lab-definition-model/definitions/classification-value/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.classification-value@1.0.0-candidate.1

**Content fingerprint · SHA-256**

593e299c5074eda1546717ebf79bbe1a3591891a3c685cd324f16b857be7709c

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "A Classification Value is one governed allowed answer under one exact Classification Axis and Scheme version, with stable identity, meaning, applicability, exclusions, and mappings.",
  "authority_scope_ref": "scope:classification-value-definition",
  "exclusions": [
    "Its label is not its identity, and similar labels across axes do not collapse their meanings.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
