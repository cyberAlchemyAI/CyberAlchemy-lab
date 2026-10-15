[Documentation home](../../README.md)

# Decision Scope

<a id="def-cal-definition-decision-scope"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Decision Scope

# Decision Scope

The specified subjects, actions, effects, time limits and exclusions covered by one decision. Similar names or shared ownership do not broaden it.

**When it applies**

Decision Scope is the closed set of exact subjects, action or effect kinds, time bounds, authority boundary, and exclusions to which one Decision may apply.

**Record formats**

[Decision scope · v2](type-cal-artifact-type-decision-scope-v2.md#type-cal-artifact-type-decision-scope-v2)

**A stated exclusion**

Shared ownership, batch presentation, or similar subject labels do not expand the scope.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-decision-scope-section-2"></a>

## Source explanatory wording

Decision Scope is the closed set of exact subjects, action or effect kinds, time bounds, authority boundary, and exclusions to which one Decision may apply. Shared ownership, batch presentation, or similar subject labels do not expand the scope.

<a id="def-cal-definition-decision-scope-section-3"></a>

## Exact governing statement

Decision Scope is the closed set of exact subjects, action or effect kinds, time bounds, authority boundary, and exclusions to which one Decision may apply. Shared ownership, batch presentation, or similar subject labels do not expand the scope.

````
DecisionScope(x) => governed_identity_or_record(x) and bounded_scope(x); DecisionScope(x) =/=> authority_effect(x).
````

- Decision Scope is the closed set of exact subjects, action or effect kinds, time bounds, authority boundary, and exclusions to which one Decision may apply.
- Shared ownership, batch presentation, or similar subject labels do not expand the scope.
- Identity, lifecycle, evidence, authority, and relation effects remain separately governed.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0013-integrated-lab-definition-model/definitions/decision-scope/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.decision-scope@1.0.0-candidate.1

**Content fingerprint · SHA-256**

1bc60f945b301ebede21fd1aae5f3bf12eff021437dc253b6bce1a772223f1f5

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Decision Scope is the closed set of exact subjects, action or effect kinds, time bounds, authority boundary, and exclusions to which one Decision may apply.",
  "authority_scope_ref": "scope:decision-scope-definition",
  "exclusions": [
    "Shared ownership, batch presentation, or similar subject labels do not expand the scope.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
