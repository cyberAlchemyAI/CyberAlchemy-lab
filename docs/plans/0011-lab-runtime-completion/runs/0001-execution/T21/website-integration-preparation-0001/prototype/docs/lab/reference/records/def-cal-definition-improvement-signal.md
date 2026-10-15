[Documentation home](../../README.md)

# Improvement Signal

<a id="def-cal-definition-improvement-signal"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Improvement Signal

# Improvement Signal

An identifiable indication of a possible weakness or opportunity that can be grouped, assessed and routed. It does not yet establish recurrence, cause, benefit or permission.

**When it applies**

An Improvement Signal is a provenance-bound indication of a possible recurring weakness or opportunity that can be deduplicated, assessed, and routed.

**Record formats**

[Improvement signal · v1](type-cal-artifact-type-improvement-signal-v1.md#type-cal-artifact-type-improvement-signal-v1)

**A stated exclusion**

It asserts neither cause, recurrence, expected benefit, priority, permission, nor an Improvement Target.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-improvement-signal-section-2"></a>

## Source explanatory wording

An Improvement Signal is a provenance-bound indication of a possible recurring weakness or opportunity that can be deduplicated, assessed, and routed. It asserts neither cause, recurrence, expected benefit, priority, permission, nor an Improvement Target.

<a id="def-cal-definition-improvement-signal-section-3"></a>

## Exact governing statement

An Improvement Signal is a provenance-bound indication of a possible recurring weakness or opportunity that can be deduplicated, assessed, and routed. It asserts neither cause, recurrence, expected benefit, priority, permission, nor an Improvement Target.

````
ImprovementSignal(x) => governed_identity_or_record(x) and bounded_scope(x); ImprovementSignal(x) =/=> authority_effect(x).
````

- An Improvement Signal is a provenance-bound indication of a possible recurring weakness or opportunity that can be deduplicated, assessed, and routed.
- It asserts neither cause, recurrence, expected benefit, priority, permission, nor an Improvement Target.
- Identity, lifecycle, evidence, authority, and relation effects remain separately governed.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../assets/35cb82b2c8c1-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.improvement-signal@1.0.0-candidate.1

**Content fingerprint · SHA-256**

35cb82b2c8c1873d430ac31c68517b0649fbae8cffdaac96e5ba7b89393b6b29

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "An Improvement Signal is a provenance-bound indication of a possible recurring weakness or opportunity that can be deduplicated, assessed, and routed.",
  "authority_scope_ref": "scope:improvement-signal-definition",
  "exclusions": [
    "It asserts neither cause, recurrence, expected benefit, priority, permission, nor an Improvement Target.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
