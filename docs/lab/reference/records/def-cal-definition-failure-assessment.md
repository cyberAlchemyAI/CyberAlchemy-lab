[Documentation home](../../README.md)

# Failure Assessment

<a id="def-cal-definition-failure-assessment"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Failure Assessment

# Failure Assessment

Examines a particular failure or group of failures, keeping occurrence, pattern, cause, impact, containment, recovery and uncertainty distinct. Recovery can coexist with an unresolved cause.

**When it applies**

When evaluating a failure occurrence or declared group while keeping occurrence, mode, cause, impact, containment, recovery and uncertainty independently supported.

**Record formats**

[Failure assessment · v1](type-cal-artifact-type-failure-assessment-v1.md#type-cal-artifact-type-failure-assessment-v1)

**[In the Northstar incident](../../tutorials/incident-walkthrough.md)**

Establish omission in E12 while leaving cause, wider impact and recovery unresolved.

**Common mistake**

Inferring cause or recovery from the occurrence posture.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-failure-assessment-section-2"></a>

## Source explanatory wording

A Failure Assessment is a versioned evidence-bounded evaluation of one Failure Occurrence or declared cohort across independent occurrence, mode, cause, impact, containment, recovery, and uncertainty postures. No posture may be inferred from another; recovery can coexist with unresolved cause and residue.

<a id="def-cal-definition-failure-assessment-section-3"></a>

## Exact governing statement

A Failure Assessment is a versioned evidence-bounded evaluation of one Failure Occurrence or declared cohort across independent occurrence, mode, cause, impact, containment, recovery, and uncertainty postures. No posture may be inferred from another; recovery can coexist with unresolved cause and residue.

````
FailureAssessment(x) => governed_identity_or_record(x) and bounded_scope(x); FailureAssessment(x) =/=> authority_effect(x).
````

- A Failure Assessment is a versioned evidence-bounded evaluation of one Failure Occurrence or declared cohort across independent occurrence, mode, cause, impact, containment, recovery, and uncertainty postures.
- No posture may be inferred from another; recovery can coexist with unresolved cause and residue.
- Identity, lifecycle, evidence, authority, and relation effects remain separately governed.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0013-integrated-lab-definition-model/definitions/failure-assessment/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.failure-assessment@1.0.0-candidate.1

**Content fingerprint · SHA-256**

2cc233702f2c39b3649dc719fc1b1d29c4022a69e93caa6c6721aa037c500bfb

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "A Failure Assessment is a versioned evidence-bounded evaluation of one Failure Occurrence or declared cohort across independent occurrence, mode, cause, impact, containment, recovery, and uncertainty postures.",
  "authority_scope_ref": "scope:failure-assessment-definition",
  "exclusions": [
    "No posture may be inferred from another; recovery can coexist with unresolved cause and residue.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
