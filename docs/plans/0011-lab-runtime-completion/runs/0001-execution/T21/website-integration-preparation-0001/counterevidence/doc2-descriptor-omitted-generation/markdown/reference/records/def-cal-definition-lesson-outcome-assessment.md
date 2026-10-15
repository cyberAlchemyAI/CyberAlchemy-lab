[Documentation home](../../README.md)

# Lesson Outcome Assessment

<a id="def-cal-definition-lesson-outcome-assessment"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Lesson Outcome Assessment

# Lesson Outcome Assessment

Compares a lesson’s predicted benefit and contradicting conditions with evidence from a particular application. Task completion or self-report alone does not establish benefit.

**When it applies**

When evaluating whether a used lesson produced its predicted benefit in the later work.

**Record formats**

[Lesson outcome assessment · v1](type-cal-artifact-type-lesson-outcome-assessment-v1.md#type-cal-artifact-type-lesson-outcome-assessment-v1)

**[In the Northstar incident](../../tutorials/incident-walkthrough.md)**

Compare the predicted benefit of a used lesson with the later observed outcome.

**Common mistake**

Concluding benefit from the existence of an application record alone.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-lesson-outcome-assessment-section-2"></a>

## Source explanatory wording

A Lesson Outcome Assessment is an evidence-bounded comparison of one Lesson Application’s predicted benefit or falsifier with its observed outcome. Task completion, repetition, Agent self-report, or absence of correction alone does not prove benefit.

<a id="def-cal-definition-lesson-outcome-assessment-section-3"></a>

## Exact governing statement

A Lesson Outcome Assessment is an evidence-bounded comparison of one Lesson Application’s predicted benefit or falsifier with its observed outcome. Task completion, repetition, Agent self-report, or absence of correction alone does not prove benefit.

````
LessonOutcomeAssessment(x) => governed_identity_or_record(x) and bounded_scope(x); LessonOutcomeAssessment(x) =/=> authority_effect(x).
````

- A Lesson Outcome Assessment is an evidence-bounded comparison of one Lesson Application’s predicted benefit or falsifier with its observed outcome.
- Task completion, repetition, Agent self-report, or absence of correction alone does not prove benefit.
- Identity, lifecycle, evidence, authority, and relation effects remain separately governed.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../assets/c30d2ba5abe8-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.lesson-outcome-assessment@1.0.0-candidate.1

**Content fingerprint · SHA-256**

c30d2ba5abe86179ed27d2265c402224ae640df5ee1899dc889e888766744692

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "A Lesson Outcome Assessment is an evidence-bounded comparison of one Lesson Application’s predicted benefit or falsifier with its observed outcome.",
  "authority_scope_ref": "scope:lesson-outcome-assessment-definition",
  "exclusions": [
    "Task completion, repetition, Agent self-report, or absence of correction alone does not prove benefit.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
