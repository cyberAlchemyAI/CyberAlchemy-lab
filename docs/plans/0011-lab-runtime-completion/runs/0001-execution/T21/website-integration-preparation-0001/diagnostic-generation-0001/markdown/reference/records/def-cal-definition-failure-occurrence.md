[Documentation home](../../README.md)

# Failure Occurrence

<a id="def-cal-definition-failure-occurrence"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Failure Occurrence

# Failure Occurrence

Records evidence of one actual or suspected failure episode involving a particular version and requirement. The cause and wider consequences may remain uncertain.

**When it applies**

A Failure Occurrence is an immutable attributable episode in which evidence indicates or suspects that an exact subject revision violated an exact expected boundary under declared conditions.

**Record formats**

[Failure occurrence · v1](type-cal-artifact-type-failure-occurrence-v1.md#type-cal-artifact-type-failure-occurrence-v1)

**A stated exclusion**

It may remain suspected or indeterminate and does not by itself prove mode, cause, impact extent, containment, or recovery.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-failure-occurrence-section-2"></a>

## Source explanatory wording

A Failure Occurrence is an immutable attributable episode in which evidence indicates or suspects that an exact subject revision violated an exact expected boundary under declared conditions. It may remain suspected or indeterminate and does not by itself prove mode, cause, impact extent, containment, or recovery.

<a id="def-cal-definition-failure-occurrence-section-3"></a>

## Exact governing statement

A Failure Occurrence is an immutable attributable episode in which evidence indicates or suspects that an exact subject revision violated an exact expected boundary under declared conditions. It may remain suspected or indeterminate and does not by itself prove mode, cause, impact extent, containment, or recovery.

````
FailureOccurrence(x) => governed_identity_or_record(x) and bounded_scope(x); FailureOccurrence(x) =/=> authority_effect(x).
````

- A Failure Occurrence is an immutable attributable episode in which evidence indicates or suspects that an exact subject revision violated an exact expected boundary under declared conditions.
- It may remain suspected or indeterminate and does not by itself prove mode, cause, impact extent, containment, or recovery.
- Identity, lifecycle, evidence, authority, and relation effects remain separately governed.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../assets/4aec8a30eb41-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.failure-occurrence@1.0.0-candidate.1

**Content fingerprint · SHA-256**

4aec8a30eb41b993c8d1e39ddd5703db14dc522f7b223f057ab2a6b554d17bd2

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "A Failure Occurrence is an immutable attributable episode in which evidence indicates or suspects that an exact subject revision violated an exact expected boundary under declared conditions.",
  "authority_scope_ref": "scope:failure-occurrence-definition",
  "exclusions": [
    "It may remain suspected or indeterminate and does not by itself prove mode, cause, impact extent, containment, or recovery.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
