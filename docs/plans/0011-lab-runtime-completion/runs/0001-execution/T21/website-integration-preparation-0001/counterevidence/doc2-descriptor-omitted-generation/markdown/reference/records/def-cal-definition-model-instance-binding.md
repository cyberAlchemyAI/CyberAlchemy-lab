[Documentation home](../../README.md)

# Model Instance Binding

<a id="def-cal-definition-model-instance-binding"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Model Instance Binding

# Model Instance Binding

Records how one local model instance relates to a particular shared parent model, including inherited requirements, permitted extensions and adoption. Their identities, owners and authority remain separate.

**When it applies**

A Model Instance Binding is a lifecycle-bearing canonical contract separating one exact parent model revision and its authority from one exact local instance revision and its authority while declaring inherited contracts, extension scope, overrides, conformance, adoption, owner, succession, and challenge handling.

**Record formats**

[Model instance binding · v1](type-cal-artifact-type-model-instance-binding-v1.md#type-cal-artifact-type-model-instance-binding-v1)

**A stated exclusion**

It is neither the parent model nor the local instance and transfers no parent ownership or unrestricted authority.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-model-instance-binding-section-2"></a>

## Source explanatory wording

A Model Instance Binding is a lifecycle-bearing canonical contract separating one exact parent model revision and its authority from one exact local instance revision and its authority while declaring inherited contracts, extension scope, overrides, conformance, adoption, owner, succession, and challenge handling. It is neither the parent model nor the local instance and transfers no parent ownership or unrestricted authority.

<a id="def-cal-definition-model-instance-binding-section-3"></a>

## Exact governing statement

A Model Instance Binding is a lifecycle-bearing canonical contract separating one exact parent model revision and its authority from one exact local instance revision and its authority while declaring inherited contracts, extension scope, overrides, conformance, adoption, owner, succession, and challenge handling. It is neither the parent model nor the local instance and transfers no parent ownership or unrestricted authority.

````
ModelInstanceBinding(x) => governed(x) and bounded(x); ModelInstanceBinding(x) =/=> authority_effect(x).
````

- The parent owns its contract; the instance owner controls only the declared extension scope.
- Inherited clauses retain parent provenance and cannot be silently weakened locally.
- A generic relation projection is read-only when the specialized Binding is canonical.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Definition specialization and resolution admission

**Original definition**

[Read the original record](../../assets/f5338122a26e-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.model-instance-binding@1.0.0-candidate.1

**Content fingerprint · SHA-256**

f5338122a26ebbf89d8e1f4b9255ba619d66b59b7542ce88edcd974687550ca3

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "A Model Instance Binding is a lifecycle-bearing canonical contract separating one exact parent model revision and its authority from one exact local instance revision and its authority while declaring inherited contracts, extension scope, overrides, conformance, adoption, owner, succession, and challenge handling.",
  "authority_scope_ref": "scope:model-instance-binding-definition",
  "exclusions": [
    "It is neither the parent model nor the local instance and transfers no parent ownership or unrestricted authority.",
    "Conformance, inheritance, adoption, realization, and identity remain separate claims.",
    "This Definition does not admit a carrier, instance, relation, runtime, consumer, publication, or deployment."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
