[Documentation home](../../README.md)

# Lesson Application

<a id="def-cal-definition-lesson-application"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Lesson Application

# Lesson Application

Records use or deliberate non-use of one lesson version in later work. Showing, selecting, using and benefiting from the lesson are separate facts.

**When it applies**

When recording actual use of an exact lesson in later work.

**Record formats**

[Lesson application · v1](type-cal-artifact-type-lesson-application-v1.md#type-cal-artifact-type-lesson-application-v1)

**[In the Northstar incident](../../tutorials/incident-walkthrough.md)**

A later export investigation records the exact lesson it actually uses.

**Common mistake**

Counting a lesson displayed in context as demonstrated use.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-lesson-application-section-2"></a>

## Source explanatory wording

A Lesson Application is an immutable record that one exact Operational Lesson revision was selected and actually used or deliberately not used for one later Session or Action. Selection, presentation, applicability, use, compliance, and success are separate facts.

<a id="def-cal-definition-lesson-application-section-3"></a>

## Exact governing statement

A Lesson Application is an immutable record that one exact Operational Lesson revision was selected and actually used or deliberately not used for one later Session or Action. Selection, presentation, applicability, use, compliance, and success are separate facts.

````
LessonApplication(x) => governed_identity_or_record(x) and bounded_scope(x); LessonApplication(x) =/=> authority_effect(x).
````

- A Lesson Application is an immutable record that one exact Operational Lesson revision was selected and actually used or deliberately not used for one later Session or Action.
- Selection, presentation, applicability, use, compliance, and success are separate facts.
- Identity, lifecycle, evidence, authority, and relation effects remain separately governed.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0013-integrated-lab-definition-model/definitions/lesson-application/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.lesson-application@1.0.0-candidate.1

**Content fingerprint · SHA-256**

bbbbe11f3e1a608b82e8100bb95fef6b6d3d1feafa35e2af0c0486eef4742542

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "A Lesson Application is an immutable record that one exact Operational Lesson revision was selected and actually used or deliberately not used for one later Session or Action.",
  "authority_scope_ref": "scope:lesson-application-definition",
  "exclusions": [
    "Selection, presentation, applicability, use, compliance, and success are separate facts.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
