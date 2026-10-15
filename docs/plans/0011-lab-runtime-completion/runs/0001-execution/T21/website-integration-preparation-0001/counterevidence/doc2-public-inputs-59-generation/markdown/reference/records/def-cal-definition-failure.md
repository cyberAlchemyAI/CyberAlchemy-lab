[Documentation home](../../README.md)

# Failure

<a id="def-cal-definition-failure"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Failure

# Failure

An evidence-supported inability of a particular thing and version to meet a specified requirement under stated conditions. It does not alone establish cause, blame or permission to change the system.

**When it applies**

A Failure is an attributable evidence-bounded inability of one exact subject revision to satisfy one exact required boundary, obligation, or expected condition under declared conditions.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**A stated exclusion**

Failure alone establishes neither cause, blame, severity, recurrence, Incident status, nor permission to retry or change the system.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-failure-section-2"></a>

## Source explanatory wording

A Failure is an attributable evidence-bounded inability of one exact subject revision to satisfy one exact required boundary, obligation, or expected condition under declared conditions. Failure alone establishes neither cause, blame, severity, recurrence, Incident status, nor permission to retry or change the system.

<a id="def-cal-definition-failure-section-3"></a>

## Exact governing statement

A Failure is an attributable evidence-bounded inability of one exact subject revision to satisfy one exact required boundary, obligation, or expected condition under declared conditions. Failure alone establishes neither cause, blame, severity, recurrence, Incident status, nor permission to retry or change the system.

````
Failure(x) => governed_identity_or_record(x) and bounded_scope(x); Failure(x) =/=> authority_effect(x).
````

- A Failure is an attributable evidence-bounded inability of one exact subject revision to satisfy one exact required boundary, obligation, or expected condition under declared conditions.
- Failure alone establishes neither cause, blame, severity, recurrence, Incident status, nor permission to retry or change the system.
- Identity, lifecycle, evidence, authority, and relation effects remain separately governed.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../assets/083f62ef0a56-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.failure@1.0.0-candidate.1

**Content fingerprint · SHA-256**

083f62ef0a56f74826ff147cb1fd35a53e771cf508a4d842cf9156d931fd991b

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "A Failure is an attributable evidence-bounded inability of one exact subject revision to satisfy one exact required boundary, obligation, or expected condition under declared conditions.",
  "authority_scope_ref": "scope:failure-definition",
  "exclusions": [
    "Failure alone establishes neither cause, blame, severity, recurrence, Incident status, nor permission to retry or change the system.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
