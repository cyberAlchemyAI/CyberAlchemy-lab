[Documentation home](../../README.md)

# Measurement Method

<a id="def-cal-definition-measurement-method"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Measurement Method

# Measurement Method

A reproducible procedure for measuring a property under stated conditions, with units, tools, calibration, computation and uncertainty handling identified.

**When it applies**

A Measurement Method is a versioned reproducible procedure for measuring one declared property of a subject under stated conditions, with units, instruments or Tools, Implementation, calibration, sampling, computation, uncertainty treatment, evidence, applicability, owner, and failure boundaries.

**Record formats**

[Measurement method · v1](type-cal-artifact-type-measurement-method-v1.md#type-cal-artifact-type-measurement-method-v1)

**A stated exclusion**

It is not a Measurement Result, Observation, metric value, Finding, Evidence Set, Decision, or authority rule.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-measurement-method-section-2"></a>

## Source explanatory wording

A Measurement Method is a versioned reproducible procedure for measuring one declared property of a subject under stated conditions, with units, instruments or Tools, Implementation, calibration, sampling, computation, uncertainty treatment, evidence, applicability, owner, and failure boundaries. It is not a Measurement Result, Observation, metric value, Finding, Evidence Set, Decision, or authority rule.

<a id="def-cal-definition-measurement-method-section-3"></a>

## Exact governing statement

A Measurement Method is a versioned reproducible procedure for measuring one declared property of a subject under stated conditions, with units, instruments or Tools, Implementation, calibration, sampling, computation, uncertainty treatment, evidence, applicability, owner, and failure boundaries. It is not a Measurement Result, Observation, metric value, Finding, Evidence Set, Decision, or authority rule.

````
MeasurementMethod(x) => governed(x) and bounded(x); MeasurementMethod(x) =/=> authority_effect(x).
````

- Residue Measurement is one semantic use of Measurement Method; the positive Method Definition also supports other governed properties.
- Each execution binds exact subject, conditions, Method version, Tool and Implementation versions, and calibration state.
- Changing the procedure or uncertainty treatment requires a new Method version.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Definition specialization and resolution admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0014-definition-specialization-resolution/definitions/measurement-method/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.measurement-method@1.0.0-candidate.1

**Content fingerprint · SHA-256**

b63f9192cc3141856e89aa9d603f16dac04d3530df27082486f999a0dc6f7b94

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "A Measurement Method is a versioned reproducible procedure for measuring one declared property of a subject under stated conditions, with units, instruments or Tools, Implementation, calibration, sampling, computation, uncertainty treatment, evidence, applicability, owner, and failure boundaries.",
  "authority_scope_ref": "scope:measurement-method-definition",
  "exclusions": [
    "It is not a Measurement Result, Observation, metric value, Finding, Evidence Set, Decision, or authority rule.",
    "Method admission does not prove calibration, correct execution, suitability for a subject, or acceptance of a result.",
    "This Definition does not admit a carrier, instance, relation, runtime, consumer, publication, or deployment."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
