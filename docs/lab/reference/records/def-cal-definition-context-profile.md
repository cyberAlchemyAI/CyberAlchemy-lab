[Documentation home](../../README.md)

# Context Profile

<a id="def-cal-definition-context-profile"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Context Profile

# Context Profile

Reusable rules for constructing and resolving contexts, including allowed anchors, sources, freshness and succession. It is not a particular product- or project-bound context or a resolved view.

**When it applies**

A Context Profile is a reusable versioned policy contract that constrains how purpose-bound Contexts may be constructed and resolved through permitted anchor kinds, cardinalities, identity fields, source rules, freshness, exclusions, succession, and challenge handling.

**Record formats**

[Context profile · v1](type-cal-artifact-type-context-profile-v1.md#type-cal-artifact-type-context-profile-v1)

**A stated exclusion**

It is not a Context instance and carries no Product, Project, Goal, purpose-bound Context identity, resolved source selection, or consumer-specific view.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-context-profile-section-2"></a>

## Source explanatory wording

A Context Profile is a reusable versioned policy contract that constrains how purpose-bound Contexts may be constructed and resolved through permitted anchor kinds, cardinalities, identity fields, source rules, freshness, exclusions, succession, and challenge handling. It is not a Context instance and carries no Product, Project, Goal, purpose-bound Context identity, resolved source selection, or consumer-specific view.

<a id="def-cal-definition-context-profile-section-3"></a>

## Exact governing statement

A Context Profile is a reusable versioned policy contract that constrains how purpose-bound Contexts may be constructed and resolved through permitted anchor kinds, cardinalities, identity fields, source rules, freshness, exclusions, succession, and challenge handling. It is not a Context instance and carries no Product, Project, Goal, purpose-bound Context identity, resolved source selection, or consumer-specific view.

````
ContextProfile(x) => governed(x) and bounded(x); ContextProfile(x) =/=> authority_effect(x).
````

- Context supplies the purpose-specific relevance boundary; Context Profile supplies reusable construction and resolution policy.
- A Profile can govern many Contexts while retaining its own owner, version, lifecycle, and challenge route.
- Profile revisions do not silently reinterpret existing Context versions.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Definition specialization and resolution admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0014-definition-specialization-resolution/definitions/context-profile/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.context-profile@1.0.0-candidate.1

**Content fingerprint · SHA-256**

4b8ef4c933df08cfc3f7e15a80f635d5ea5fe5adbe77b33364a309cf6ed199d6

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "A Context Profile is a reusable versioned policy contract that constrains how purpose-bound Contexts may be constructed and resolved through permitted anchor kinds, cardinalities, identity fields, source rules, freshness, exclusions, succession, and challenge handling.",
  "authority_scope_ref": "scope:context-profile-definition",
  "exclusions": [
    "It is not a Context instance and carries no Product, Project, Goal, purpose-bound Context identity, resolved source selection, or consumer-specific view.",
    "Profile conformance does not create a Context or prove that resolution inputs are current.",
    "This Definition does not admit a carrier, instance, relation, runtime, consumer, publication, or deployment."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
