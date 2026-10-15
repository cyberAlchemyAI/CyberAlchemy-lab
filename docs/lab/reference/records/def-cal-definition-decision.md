[Documentation home](../../README.md)

# Decision

<a id="def-cal-definition-decision"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Decision

# Decision

A recorded authority act selecting an outcome or permitted effect for specified things within stated limits. The choice and evidence that its effect occurred are separate facts.

**When it applies**

A Decision is an attributable authority act that selects an outcome, interpretation, permission, priority, or lifecycle effect for exact subjects within a declared scope and evidence basis.

**Record formats**

[Decision · v2](type-cal-artifact-type-decision-v2.md#type-cal-artifact-type-decision-v2)

**A stated exclusion**

A Decision is distinct from evidence, recommendation, preference, Agent output, execution, and proof that the selected effect occurred.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-decision-section-2"></a>

## Source explanatory wording

A Decision is an attributable authority act that selects an outcome, interpretation, permission, priority, or lifecycle effect for exact subjects within a declared scope and evidence basis. A Decision is distinct from evidence, recommendation, preference, Agent output, execution, and proof that the selected effect occurred.

<a id="def-cal-definition-decision-section-3"></a>

## Exact governing statement

A Decision is an attributable authority act that selects an outcome, interpretation, permission, priority, or lifecycle effect for exact subjects within a declared scope and evidence basis. A Decision is distinct from evidence, recommendation, preference, Agent output, execution, and proof that the selected effect occurred.

````
Decision(x) => governed_identity_or_record(x) and bounded_scope(x); Decision(x) =/=> authority_effect(x).
````

- A Decision is an attributable authority act that selects an outcome, interpretation, permission, priority, or lifecycle effect for exact subjects within a declared scope and evidence basis.
- A Decision is distinct from evidence, recommendation, preference, Agent output, execution, and proof that the selected effect occurred.
- Identity, lifecycle, evidence, authority, and relation effects remain separately governed.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0013-integrated-lab-definition-model/definitions/decision/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.decision@1.0.0-candidate.1

**Content fingerprint · SHA-256**

514f8a33054508ecd7050ddeb5241e3cd55d7ccf7bfd8677323ebea6318627be

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "A Decision is an attributable authority act that selects an outcome, interpretation, permission, priority, or lifecycle effect for exact subjects within a declared scope and evidence basis.",
  "authority_scope_ref": "scope:decision-definition",
  "exclusions": [
    "A Decision is distinct from evidence, recommendation, preference, Agent output, execution, and proof that the selected effect occurred.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
