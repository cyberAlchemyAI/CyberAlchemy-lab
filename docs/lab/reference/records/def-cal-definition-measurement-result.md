[Documentation home](../../README.md)

# Measurement Result

<a id="def-cal-definition-measurement-result"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Measurement Result

# Measurement Result

The saved values and evidence from one execution of a particular measurement method against a particular subject version. It is separate from the method and later interpretation.

**When it applies**

A Measurement Result is an immutable attributable record of one exact Measurement Method execution against one exact subject revision under declared conditions, preserving values, units, uncertainty, raw evidence, Tool and Implementation versions, timestamps, validity posture, owner, and receipt.

**Record formats**

[Measurement result · v1](type-cal-artifact-type-measurement-result-v1.md#type-cal-artifact-type-measurement-result-v1)

**A stated exclusion**

It is not the Measurement Method, subject, Observation narrative, Evidence Set, Finding, causal claim, Decision, accepted fact, or authority effect.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-measurement-result-section-2"></a>

## Source explanatory wording

A Measurement Result is an immutable attributable record of one exact Measurement Method execution against one exact subject revision under declared conditions, preserving values, units, uncertainty, raw evidence, Tool and Implementation versions, timestamps, validity posture, owner, and receipt. It is not the Measurement Method, subject, Observation narrative, Evidence Set, Finding, causal claim, Decision, accepted fact, or authority effect.

<a id="def-cal-definition-measurement-result-section-3"></a>

## Exact governing statement

A Measurement Result is an immutable attributable record of one exact Measurement Method execution against one exact subject revision under declared conditions, preserving values, units, uncertainty, raw evidence, Tool and Implementation versions, timestamps, validity posture, owner, and receipt. It is not the Measurement Method, subject, Observation narrative, Evidence Set, Finding, causal claim, Decision, accepted fact, or authority effect.

````
MeasurementResult(x) => governed(x) and bounded(x); MeasurementResult(x) =/=> authority_effect(x).
````

- The Method defines how measurement is performed; the Result records what one execution produced.
- Corrections create successor Results while preserving the original record and evidence.
- Interpretation, acceptance, and use in a Finding remain separate governed acts.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Definition specialization and resolution admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0014-definition-specialization-resolution/definitions/measurement-result/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.measurement-result@1.0.0-candidate.1

**Content fingerprint · SHA-256**

4bc1e7d96b821dd384cb6ff731d56030a560c00a30ff6415d82d57d9fac89dec

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "A Measurement Result is an immutable attributable record of one exact Measurement Method execution against one exact subject revision under declared conditions, preserving values, units, uncertainty, raw evidence, Tool and Implementation versions, timestamps, validity posture, owner, and receipt.",
  "authority_scope_ref": "scope:measurement-result-definition",
  "exclusions": [
    "It is not the Measurement Method, subject, Observation narrative, Evidence Set, Finding, causal claim, Decision, accepted fact, or authority effect.",
    "A value without exact Method, subject, conditions, units, uncertainty, and provenance is not a conforming Measurement Result.",
    "This Definition does not admit a carrier, instance, relation, runtime, consumer, publication, or deployment."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
