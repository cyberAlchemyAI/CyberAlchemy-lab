[Documentation home](../../README.md)

# Challenge Event

<a id="def-cal-definition-challenge-event"></a>

[Reference catalog](../definitions.md#catalog-definitions) / Exact record

# Challenge Event

Records that an eligible challenger contested a particular revision under a particular Challenge Contract. It is not the resolution or an automatic change of status.

**When it applies**

A Challenge Event is an immutable attributable record that an eligible challenger contested one exact subject revision under one exact Challenge Contract with stated grounds and evidence.

**Record formats**

[Challenge event · v1](type-cal-artifact-type-challenge-event-v1.md#type-cal-artifact-type-challenge-event-v1)

**A stated exclusion**

It is neither the challenged subject, a contradiction finding, resolution, Decision, nor automatic lifecycle transition.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

## Source explanatory wording

A Challenge Event is an immutable attributable record that an eligible challenger contested one exact subject revision under one exact Challenge Contract with stated grounds and evidence. It is neither the challenged subject, a contradiction finding, resolution, Decision, nor automatic lifecycle transition.

## Exact governing statement

A Challenge Event is an immutable attributable record that an eligible challenger contested one exact subject revision under one exact Challenge Contract with stated grounds and evidence. It is neither the challenged subject, a contradiction finding, resolution, Decision, nor automatic lifecycle transition.

````
ChallengeEvent(x) => governed_identity_or_record(x) and bounded_scope(x); ChallengeEvent(x) =/=> authority_effect(x).
````

- A Challenge Event is an immutable attributable record that an eligible challenger contested one exact subject revision under one exact Challenge Contract with stated grounds and evidence.
- It is neither the challenged subject, a contradiction finding, resolution, Decision, nor automatic lifecycle transition.
- Identity, lifecycle, evidence, authority, and relation effects remain separately governed.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0013-integrated-lab-definition-model/definitions/challenge-event/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.challenge-event@1.0.0-candidate.1

**Content fingerprint · SHA-256**

1a89a66594c972e1ef6adbf0aacbd92ba0ec974de8aa708aff131747634188e7

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "A Challenge Event is an immutable attributable record that an eligible challenger contested one exact subject revision under one exact Challenge Contract with stated grounds and evidence.",
  "authority_scope_ref": "scope:challenge-event-definition",
  "exclusions": [
    "It is neither the challenged subject, a contradiction finding, resolution, Decision, nor automatic lifecycle transition.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to this catalog](../definitions.md#catalog-definitions)
