[Documentation home](../../README.md)

# Capability Realization Binding

<a id="def-cal-definition-capability-realization-binding"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Capability Realization Binding

# Capability Realization Binding

Links a particular product-capability version to implementation versions and their roles, compatibility, adoption and supporting evidence. The link alone does not prove adoption, deployment or value.

**When it applies**

A Capability Realization Binding is a lifecycle-bearing canonical association between one exact Product Capability revision and one or more exact Implementation revisions, with realization role, adoption posture, compatibility, conformance evidence, deployment applicability, owner, succession, and challenge handling.

**Record formats**

[Capability realization binding · v2](type-cal-artifact-type-capability-realization-binding-v2.md#type-cal-artifact-type-capability-realization-binding-v2)

**A stated exclusion**

It is neither the Product Capability nor an Implementation and does not prove adoption, deployment, conformance, successful operation, or Product value.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-capability-realization-binding-section-2"></a>

## Source explanatory wording

A Capability Realization Binding is a lifecycle-bearing canonical association between one exact Product Capability revision and one or more exact Implementation revisions, with realization role, adoption posture, compatibility, conformance evidence, deployment applicability, owner, succession, and challenge handling. It is neither the Product Capability nor an Implementation and does not prove adoption, deployment, conformance, successful operation, or Product value.

<a id="def-cal-definition-capability-realization-binding-section-3"></a>

## Exact governing statement

A Capability Realization Binding is a lifecycle-bearing canonical association between one exact Product Capability revision and one or more exact Implementation revisions, with realization role, adoption posture, compatibility, conformance evidence, deployment applicability, owner, succession, and challenge handling. It is neither the Product Capability nor an Implementation and does not prove adoption, deployment, conformance, successful operation, or Product value.

````
CapabilityRealizationBinding(x) => governed(x) and bounded(x); CapabilityRealizationBinding(x) =/=> authority_effect(x).
````

- Product Capability states the durable outcome promised; Implementation supplies technical realization; the Binding owns their lifecycle-bearing association.
- The Binding is canonical for specialized realization state and may project one digest-bound Typed Relation.
- Changing either endpoint or adoption posture creates a successor Binding revision.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Definition specialization and resolution admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0014-definition-specialization-resolution/definitions/capability-realization-binding/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.capability-realization-binding@1.0.0-candidate.1

**Content fingerprint · SHA-256**

8a0f907bb854371b8946e071c9d01702de3f35799405cb8b0ee66e546990b1bd

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "A Capability Realization Binding is a lifecycle-bearing canonical association between one exact Product Capability revision and one or more exact Implementation revisions, with realization role, adoption posture, compatibility, conformance evidence, deployment applicability, owner, succession, and challenge handling.",
  "authority_scope_ref": "scope:capability-realization-binding-definition",
  "exclusions": [
    "It is neither the Product Capability nor an Implementation and does not prove adoption, deployment, conformance, successful operation, or Product value.",
    "A generic Typed Relation projection cannot become a second writable authority for the same binding.",
    "This Definition does not admit a carrier, instance, relation, runtime, consumer, publication, or deployment."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
