[Documentation home](../../README.md)

# Intent Resolution

<a id="def-cal-definition-intent-resolution"></a>

[Reference catalog](../definitions.md#catalog-definitions) / Exact record

# Intent Resolution

An owner’s choice of how to address one intent and how satisfaction will be assessed. Selection does not prove delivery or authorize unrelated work.

**When it applies**

When selecting a response to an intent and stating how its satisfaction will be assessed.

**Record formats**

[Intent resolution · v1](type-cal-artifact-type-intent-resolution-v1.md#type-cal-artifact-type-intent-resolution-v1)

**[In the Northstar incident](../../tutorials/incident-walkthrough.md)**

Choose an investigation as the response to the reported need and declare how satisfaction will be assessed.

**Common mistake**

Assuming a chosen response has already satisfied the intent.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

## Source explanatory wording

An Intent Resolution is an attributable owner decision selecting which governed Product, Project, Goal, Research, Capability, or other output will address one exact Intent and under what satisfaction test. It does not embed Implementation in Intent, prove delivery or satisfaction, or authorize unrelated work.

## Exact governing statement

An Intent Resolution is an attributable owner decision selecting which governed Product, Project, Goal, Research, Capability, or other output will address one exact Intent and under what satisfaction test. It does not embed Implementation in Intent, prove delivery or satisfaction, or authorize unrelated work.

````
IntentResolution(x) => governed_identity_or_record(x) and bounded_scope(x); IntentResolution(x) =/=> authority_effect(x).
````

- An Intent Resolution is an attributable owner decision selecting which governed Product, Project, Goal, Research, Capability, or other output will address one exact Intent and under what satisfaction test.
- It does not embed Implementation in Intent, prove delivery or satisfaction, or authorize unrelated work.
- Identity, lifecycle, evidence, authority, and relation effects remain separately governed.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0013-integrated-lab-definition-model/definitions/intent-resolution/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.intent-resolution@1.0.0-candidate.1

**Content fingerprint · SHA-256**

cf84080dba84433926c7f11759057ca4277458152518aaa243d61a948e96c136

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "An Intent Resolution is an attributable owner decision selecting which governed Product, Project, Goal, Research, Capability, or other output will address one exact Intent and under what satisfaction test.",
  "authority_scope_ref": "scope:intent-resolution-definition",
  "exclusions": [
    "It does not embed Implementation in Intent, prove delivery or satisfaction, or authorize unrelated work.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to this catalog](../definitions.md#catalog-definitions)
