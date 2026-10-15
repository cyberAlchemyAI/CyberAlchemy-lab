[Documentation home](../../README.md)

# Operational Lesson

<a id="def-cal-definition-operational-lesson"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Operational Lesson

# Operational Lesson

Versioned advice for future project work with evidence, applicability, exclusions, predicted benefit and a result that would contradict it. Saving advice does not turn it into a policy or permission.

**When it applies**

When proposing reusable guidance from experience with evidence, applicability, exclusions, predicted benefit and a falsifier.

**Record formats**

[Operational lesson · v1](type-cal-artifact-type-operational-lesson-v1.md#type-cal-artifact-type-operational-lesson-v1)

**[In the Northstar incident](../../tutorials/incident-walkthrough.md)**

Propose checking export boundaries, with evidence, applicability, exclusions, predicted benefit and a falsifier.

**Common mistake**

Claiming improvement merely because the lesson was saved or presented.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-operational-lesson-section-2"></a>

## Source explanatory wording

An Operational Lesson is a versioned evidence-bounded and scope-limited candidate for how future Project work may be interpreted or performed, with applicability, exclusions, predicted benefit, and falsifier. Persistence does not make it an instruction, Policy, fact, authority grant, or proof of benefit.

<a id="def-cal-definition-operational-lesson-section-3"></a>

## Exact governing statement

An Operational Lesson is a versioned evidence-bounded and scope-limited candidate for how future Project work may be interpreted or performed, with applicability, exclusions, predicted benefit, and falsifier. Persistence does not make it an instruction, Policy, fact, authority grant, or proof of benefit.

````
OperationalLesson(x) => governed_identity_or_record(x) and bounded_scope(x); OperationalLesson(x) =/=> authority_effect(x).
````

- An Operational Lesson is a versioned evidence-bounded and scope-limited candidate for how future Project work may be interpreted or performed, with applicability, exclusions, predicted benefit, and falsifier.
- Persistence does not make it an instruction, Policy, fact, authority grant, or proof of benefit.
- Identity, lifecycle, evidence, authority, and relation effects remain separately governed.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../assets/8149d3123887-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.operational-lesson@1.0.0-candidate.1

**Content fingerprint · SHA-256**

8149d312388778f3d19f1a72cba34d0a172366aa0883ba292ba1f3d5740892a6

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "An Operational Lesson is a versioned evidence-bounded and scope-limited candidate for how future Project work may be interpreted or performed, with applicability, exclusions, predicted benefit, and falsifier.",
  "authority_scope_ref": "scope:operational-lesson-definition",
  "exclusions": [
    "Persistence does not make it an instruction, Policy, fact, authority grant, or proof of benefit.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
