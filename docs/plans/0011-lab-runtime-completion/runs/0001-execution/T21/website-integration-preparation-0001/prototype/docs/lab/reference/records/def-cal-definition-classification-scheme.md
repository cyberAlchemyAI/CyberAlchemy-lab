[Documentation home](../../README.md)

# Classification Scheme

<a id="def-cal-definition-classification-scheme"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Classification Scheme

# Classification Scheme

Defines the classification questions, allowed values, applicability and assignment rules. A revised scheme does not silently reinterpret older assignments.

**When it applies**

A Classification Scheme is a versioned governed contract of axes, allowed values, definitions, cardinality, applicability, exclusions, assignment and evidence rules, hierarchy, mappings, compatibility, owner, and challenge route.

**Record formats**

[Classification scheme · v1](type-cal-artifact-type-classification-scheme-v1.md#type-cal-artifact-type-classification-scheme-v1)

**A stated exclusion**

A new Scheme version does not silently reinterpret or reclassify assignments made under an older version.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-classification-scheme-section-2"></a>

## Source explanatory wording

A Classification Scheme is a versioned governed contract of axes, allowed values, definitions, cardinality, applicability, exclusions, assignment and evidence rules, hierarchy, mappings, compatibility, owner, and challenge route. A new Scheme version does not silently reinterpret or reclassify assignments made under an older version.

<a id="def-cal-definition-classification-scheme-section-3"></a>

## Exact governing statement

A Classification Scheme is a versioned governed contract of axes, allowed values, definitions, cardinality, applicability, exclusions, assignment and evidence rules, hierarchy, mappings, compatibility, owner, and challenge route. A new Scheme version does not silently reinterpret or reclassify assignments made under an older version.

````
ClassificationScheme(x) => governed_identity_or_record(x) and bounded_scope(x); ClassificationScheme(x) =/=> authority_effect(x).
````

- A Classification Scheme is a versioned governed contract of axes, allowed values, definitions, cardinality, applicability, exclusions, assignment and evidence rules, hierarchy, mappings, compatibility, owner, and challenge route.
- A new Scheme version does not silently reinterpret or reclassify assignments made under an older version.
- Identity, lifecycle, evidence, authority, and relation effects remain separately governed.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../assets/5bdc6c0bcb7f-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.classification-scheme@1.0.0-candidate.1

**Content fingerprint · SHA-256**

5bdc6c0bcb7fa0a01c3f07eff5601830411a1d8c0e386e2f457ce58ce6e046c7

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "A Classification Scheme is a versioned governed contract of axes, allowed values, definitions, cardinality, applicability, exclusions, assignment and evidence rules, hierarchy, mappings, compatibility, owner, and challenge route.",
  "authority_scope_ref": "scope:classification-scheme-definition",
  "exclusions": [
    "A new Scheme version does not silently reinterpret or reclassify assignments made under an older version.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
