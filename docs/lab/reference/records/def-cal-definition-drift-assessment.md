[Documentation home](../../README.md)

# Drift Assessment

<a id="def-cal-definition-drift-assessment"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Drift Assessment

# Drift Assessment

Compares declared and observed versions, meanings, connections, behavior or freshness at a specified time. Finding a mismatch does not establish its cause or permission to fix it.

**When it applies**

A Drift Assessment is an evidence-bounded comparison between declared and observed versions, conditions, bindings, meanings, behavior, or currentness at an exact time.

**Record formats**

[Drift assessment · v1](type-cal-artifact-type-drift-assessment-v1.md#type-cal-artifact-type-drift-assessment-v1)

**A stated exclusion**

Mismatch does not by itself establish cause, severity, failure, correction authority, or required remediation.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-drift-assessment-section-2"></a>

## Source explanatory wording

A Drift Assessment is an evidence-bounded comparison between declared and observed versions, conditions, bindings, meanings, behavior, or currentness at an exact time. Mismatch does not by itself establish cause, severity, failure, correction authority, or required remediation.

<a id="def-cal-definition-drift-assessment-section-3"></a>

## Exact governing statement

A Drift Assessment is an evidence-bounded comparison between declared and observed versions, conditions, bindings, meanings, behavior, or currentness at an exact time. Mismatch does not by itself establish cause, severity, failure, correction authority, or required remediation.

````
DriftAssessment(x) => governed_identity_or_record(x) and bounded_scope(x); DriftAssessment(x) =/=> authority_effect(x).
````

- A Drift Assessment is an evidence-bounded comparison between declared and observed versions, conditions, bindings, meanings, behavior, or currentness at an exact time.
- Mismatch does not by itself establish cause, severity, failure, correction authority, or required remediation.
- Identity, lifecycle, evidence, authority, and relation effects remain separately governed.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0013-integrated-lab-definition-model/definitions/drift-assessment/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.drift-assessment@1.0.0-candidate.1

**Content fingerprint · SHA-256**

cf7809fb1928398ad77c3a43fef2f7d57ea8ae075c9c4e4fb0386e18c55aa707

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "A Drift Assessment is an evidence-bounded comparison between declared and observed versions, conditions, bindings, meanings, behavior, or currentness at an exact time.",
  "authority_scope_ref": "scope:drift-assessment-definition",
  "exclusions": [
    "Mismatch does not by itself establish cause, severity, failure, correction authority, or required remediation.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
