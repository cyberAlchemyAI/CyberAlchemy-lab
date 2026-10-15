[Documentation home](../../README.md)

# Review

<a id="def-cal-definition-review"></a>

[Reference catalog](../definitions.md#catalog-definitions) / Exact record

# Review

An identifiable assessment of particular versions against stated questions, criteria and evidence. Review is separate from acceptance, execution or permission to apply changes.

**When it applies**

A Review is an attributable bounded assessment of exact subject versions against declared questions, criteria, evidence, alternatives, and a claim ceiling.

**Record formats**

[Review · v1](type-cal-artifact-type-review-v1.md#type-cal-artifact-type-review-v1)

**A stated exclusion**

A Review is not admission, approval, validation, fact, or execution unless a separate Decision grants that effect.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

## Source explanatory wording

A Review is an attributable bounded assessment of exact subject versions against declared questions, criteria, evidence, alternatives, and a claim ceiling. A Review is not admission, approval, validation, fact, or execution unless a separate Decision grants that effect.

## Exact governing statement

A Review is an attributable bounded assessment of exact subject versions against declared questions, criteria, evidence, alternatives, and a claim ceiling. A Review is not admission, approval, validation, fact, or execution unless a separate Decision grants that effect.

````
Review(x) => governed_identity_or_record(x) and bounded_scope(x); Review(x) =/=> authority_effect(x).
````

- A Review is an attributable bounded assessment of exact subject versions against declared questions, criteria, evidence, alternatives, and a claim ceiling.
- A Review is not admission, approval, validation, fact, or execution unless a separate Decision grants that effect.
- Identity, lifecycle, evidence, authority, and relation effects remain separately governed.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0013-integrated-lab-definition-model/definitions/review/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.review@1.0.0-candidate.1

**Content fingerprint · SHA-256**

db548dded27804654bc978da08c3e509920f814399a295ed59cdcc26589f029d

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "A Review is an attributable bounded assessment of exact subject versions against declared questions, criteria, evidence, alternatives, and a claim ceiling.",
  "authority_scope_ref": "scope:review-definition",
  "exclusions": [
    "A Review is not admission, approval, validation, fact, or execution unless a separate Decision grants that effect.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to this catalog](../definitions.md#catalog-definitions)
