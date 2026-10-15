[Documentation home](../../README.md)

# Operational Observation

<a id="def-cal-definition-operational-observation"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Operational Observation

# Operational Observation

A record of information observed during ordinary project work outside research or experiment-specific observations. It does not alone establish cause or the required response.

**When it applies**

When recording an attributable, bounded datum from ordinary Project work outside the research- or experiment-specific Observation boundary.

**Record formats**

[Operational observation · v1](type-cal-artifact-type-operational-observation-v1.md#type-cal-artifact-type-operational-observation-v1)

**[In the Northstar incident](../../tutorials/incident-walkthrough.md)**

Record the 200 missing required identifiers during ordinary Project investigation work.

**Common mistake**

Recording “pagination caused the incident” as though it followed from the identifier comparison.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-operational-observation-section-2"></a>

## Source explanatory wording

An Operational Observation is an attributable bounded datum recorded during ordinary Project work outside the Research or Experiment-specific Observation boundary. It records what was observed, not its cause, importance, correctness, lesson, failure classification, or required response.

<a id="def-cal-definition-operational-observation-section-3"></a>

## Exact governing statement

An Operational Observation is an attributable bounded datum recorded during ordinary Project work outside the Research or Experiment-specific Observation boundary. It records what was observed, not its cause, importance, correctness, lesson, failure classification, or required response.

````
OperationalObservation(x) => governed_identity_or_record(x) and bounded_scope(x); OperationalObservation(x) =/=> authority_effect(x).
````

- An Operational Observation is an attributable bounded datum recorded during ordinary Project work outside the Research or Experiment-specific Observation boundary.
- It records what was observed, not its cause, importance, correctness, lesson, failure classification, or required response.
- Identity, lifecycle, evidence, authority, and relation effects remain separately governed.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../assets/c27d5546bea1-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.operational-observation@1.0.0-candidate.1

**Content fingerprint · SHA-256**

c27d5546bea18d0abb9ef1bf851232d57fc286f9c6c4019d02322eff858859b0

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "An Operational Observation is an attributable bounded datum recorded during ordinary Project work outside the Research or Experiment-specific Observation boundary.",
  "authority_scope_ref": "scope:operational-observation-definition",
  "exclusions": [
    "It records what was observed, not its cause, importance, correctness, lesson, failure classification, or required response.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
