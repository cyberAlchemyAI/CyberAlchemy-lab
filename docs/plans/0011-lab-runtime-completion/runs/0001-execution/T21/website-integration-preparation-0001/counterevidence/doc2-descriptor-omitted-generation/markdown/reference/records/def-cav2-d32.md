[Documentation home](../../README.md)

# Method

<a id="def-cav2-d32"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Method

# Method

A repeatable, governed transformation with inputs, actions and checkable results that preserves unresolved work.

**When it applies**

A governed repeatable way to transform intent, evidence, state, or residue through declared roles, actions, gates, outputs, validation, residue, and recomposition rules.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**A stated exclusion**

A one-off task or technique.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cav2-d32-section-2"></a>

## Source explanatory wording

A Method is a repeatable, governed way of turning intent and evidence into checkable work while preserving what remains unresolved.

<a id="def-cav2-d32-section-3"></a>

## Exact governing statement

A Method is a governed repeatable transformation whose scope, inputs, actions, roles, gates, outputs, evidence, residue rule, validation rule, recomposition rule, and boundary are explicit. A named Method specializes this form without inheriting authority to execute.

````
M = (scope, inputs, actions, roles, gates, outputs, evidence, residue_rule, validation_rule, recomposition_rule, boundary).
````

- Repeatability requires reusable and specialized fields to be identifiable.
- Method admission and Method application are separate decisions.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Semantic foundation admission

**Original definition**

[Read the original record](../../assets/82743cbbac7b-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

CAV2-D32@1.0.0-candidate.1

**Content fingerprint · SHA-256**

82743cbbac7b9ad9f393c56a9efa90aae4acc0d6dff769ddb40fd9b5face1c39

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "authority_scope_ref": "scope:method-definition",
  "applicability": "A governed repeatable way to transform intent, evidence, state, or residue through declared roles, actions, gates, outputs, validation, residue, and recomposition rules.",
  "exclusions": [
    "A one-off task or technique.",
    "A checklist, engine, pipeline, lifecycle label, Product, Project, Goal, or authority grant."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
