[Documentation home](../../README.md)

# Workflow

<a id="def-ds-d1-9"></a>

[Reference catalog](../definitions.md#catalog-definitions) / Exact record

# Workflow

Coordinates ordered operations within or across product-feature boundaries. Its evaluation can propose recovery; a separate executor invokes the specified operation bindings.

**When it applies**

Multi-step orchestration of Operations within or across Product Feature boundaries in the Craft Product lineage.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**A stated exclusion**

Authority or permission to execute an Operation.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

## Source explanatory wording

A Workflow coordinates several ordered Operations over time and says whether that coordination stays inside one Product Feature or crosses Feature boundaries.

## Exact governing statement

A Workflow is an ordered multi-step orchestration of Operations within or across Product Feature boundaries. It declares exactly one scope from intra-feature or cross-feature and one ownership-boundary scope. Workflow evaluation may emit recovery intent and a plan, but only a separate executor may invoke exact Operation bindings.

````
Workflow(w) = (ordered_operations, scope, ownership_boundary_scope); scope in {intra-feature,cross-feature}; Invoke(w) = none.
````

- Missing, empty, or unknown scope is invalid.
- Workflow coordination does not acquire the business responsibilities of its Operations.
- Workflow evaluation does not itself execute Operations.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Craft foundation admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0005-craft-workflow-interaction/definitions/workflow/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

DS-D1.9@1.0.0-candidate.1

**Content fingerprint · SHA-256**

a66af311589289088c8eb639410abd87d5d080a99fc4bae8d2fa9b0f8939880e

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "authority_scope_ref": "scope:craft-product-workflow",
  "applicability": "Multi-step orchestration of Operations within or across Product Feature boundaries in the Craft Product lineage.",
  "exclusions": [
    "Authority or permission to execute an Operation.",
    "A DDD Bounded Context inferred from workflow placement.",
    "A generic task list without typed Operations and declared scope."
  ]
}
````

[Return to this catalog](../definitions.md#catalog-definitions)
