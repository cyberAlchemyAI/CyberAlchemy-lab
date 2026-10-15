[Documentation home](../../README.md)

# Classification Assignment

<a id="def-cal-definition-classification-assignment"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Classification Assignment

# Classification Assignment

Records a particular classification value for a particular subject version under an identified scheme and axis, with its basis. Correction creates a successor assignment.

**When it applies**

A Classification Assignment is an immutable attributable binding of one exact subject revision to one exact Scheme version, Axis, and Value with basis, evidence, lifecycle, owner, and challenge route.

**Record formats**

[Classification assignment · v1](type-cal-artifact-type-classification-assignment-v1.md#type-cal-artifact-type-classification-assignment-v1)

**A stated exclusion**

Correction creates a successor assignment; the assignment does not change subject identity or imply facts from other axes.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-classification-assignment-section-2"></a>

## Source explanatory wording

A Classification Assignment is an immutable attributable binding of one exact subject revision to one exact Scheme version, Axis, and Value with basis, evidence, lifecycle, owner, and challenge route. Correction creates a successor assignment; the assignment does not change subject identity or imply facts from other axes.

<a id="def-cal-definition-classification-assignment-section-3"></a>

## Exact governing statement

A Classification Assignment is an immutable attributable binding of one exact subject revision to one exact Scheme version, Axis, and Value with basis, evidence, lifecycle, owner, and challenge route. Correction creates a successor assignment; the assignment does not change subject identity or imply facts from other axes.

````
ClassificationAssignment(x) => governed_identity_or_record(x) and bounded_scope(x); ClassificationAssignment(x) =/=> authority_effect(x).
````

- A Classification Assignment is an immutable attributable binding of one exact subject revision to one exact Scheme version, Axis, and Value with basis, evidence, lifecycle, owner, and challenge route.
- Correction creates a successor assignment; the assignment does not change subject identity or imply facts from other axes.
- Identity, lifecycle, evidence, authority, and relation effects remain separately governed.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../assets/f4e7dd203f1d-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.classification-assignment@1.0.0-candidate.1

**Content fingerprint · SHA-256**

f4e7dd203f1d24342a265dedcb0fb7f194983d8ce1f84d62371f5009bd90652e

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "A Classification Assignment is an immutable attributable binding of one exact subject revision to one exact Scheme version, Axis, and Value with basis, evidence, lifecycle, owner, and challenge route.",
  "authority_scope_ref": "scope:classification-assignment-definition",
  "exclusions": [
    "Correction creates a successor assignment; the assignment does not change subject identity or imply facts from other axes.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
