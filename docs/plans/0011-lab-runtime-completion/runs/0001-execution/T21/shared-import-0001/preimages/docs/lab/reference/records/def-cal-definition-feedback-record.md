[Documentation home](../../README.md)

# Feedback Record

<a id="def-cal-definition-feedback-record"></a>

[Reference catalog](../definitions.md#catalog-definitions) / Exact record

# Feedback Record

A saved response such as a correction, rejection, preference or requirement change, with its source, target, time and context identified. Feedback is not automatically fact or permission.

**When it applies**

A Feedback Record is an attributable immutable record of a correction, rejection, edit, preference expression, requirement change, or other response bound to an exact source, target, time, and context.

**Record formats**

[Feedback record · v1](type-cal-artifact-type-feedback-record-v1.md#type-cal-artifact-type-feedback-record-v1)

**A stated exclusion**

Feedback is not automatically fact, Policy, Decision, stable preference, lesson, or permission.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

## Source explanatory wording

A Feedback Record is an attributable immutable record of a correction, rejection, edit, preference expression, requirement change, or other response bound to an exact source, target, time, and context. Feedback is not automatically fact, Policy, Decision, stable preference, lesson, or permission.

## Exact governing statement

A Feedback Record is an attributable immutable record of a correction, rejection, edit, preference expression, requirement change, or other response bound to an exact source, target, time, and context. Feedback is not automatically fact, Policy, Decision, stable preference, lesson, or permission.

````
FeedbackRecord(x) => governed_identity_or_record(x) and bounded_scope(x); FeedbackRecord(x) =/=> authority_effect(x).
````

- A Feedback Record is an attributable immutable record of a correction, rejection, edit, preference expression, requirement change, or other response bound to an exact source, target, time, and context.
- Feedback is not automatically fact, Policy, Decision, stable preference, lesson, or permission.
- Identity, lifecycle, evidence, authority, and relation effects remain separately governed.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0013-integrated-lab-definition-model/definitions/feedback-record/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.feedback-record@1.0.0-candidate.1

**Content fingerprint · SHA-256**

a535d38f37abb8d7061d0f309ee81002036b8d6b6d2a6066b7fbe63f6b07391d

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "A Feedback Record is an attributable immutable record of a correction, rejection, edit, preference expression, requirement change, or other response bound to an exact source, target, time, and context.",
  "authority_scope_ref": "scope:feedback-record-definition",
  "exclusions": [
    "Feedback is not automatically fact, Policy, Decision, stable preference, lesson, or permission.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to this catalog](../definitions.md#catalog-definitions)
