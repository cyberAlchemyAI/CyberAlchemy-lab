[Documentation home](../../README.md)

# Work

<a id="def-cal-definition-work"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Work

# Work

An identified activity with purpose, owner, inputs, participants, expected result, constraints and outcome trace. It does not itself establish permission, completion or benefit.

**When it applies**

When organizing a bounded effort with purpose, inputs, participants, expected result and constraints.

**Record formats**

[Work · v1](type-cal-artifact-type-work-v1.md#type-cal-artifact-type-work-v1)

**[In the Northstar incident](../../tutorials/incident-walkthrough.md)**

Investigate the reported omission with selected inputs, expected results and constraints.

**Common mistake**

Inferring successful outcome or authority from Work completion.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-work-section-2"></a>

## Source explanatory wording

Work is a bounded unit of coordinated effort with a declared purpose, owner, participants, inputs, expected result, constraints, lifecycle, and outcome trace. Work is not necessarily a Project and does not imply authority, completion, successful outcome, or Product value.

<a id="def-cal-definition-work-section-3"></a>

## Exact governing statement

Work is a bounded unit of coordinated effort with a declared purpose, owner, participants, inputs, expected result, constraints, lifecycle, and outcome trace. Work is not necessarily a Project and does not imply authority, completion, successful outcome, or Product value.

````
Work(x) => governed_identity_or_record(x) and bounded_scope(x); Work(x) =/=> authority_effect(x).
````

- Work is a bounded unit of coordinated effort with a declared purpose, owner, participants, inputs, expected result, constraints, lifecycle, and outcome trace.
- Work is not necessarily a Project and does not imply authority, completion, successful outcome, or Product value.
- Identity, lifecycle, evidence, authority, and relation effects remain separately governed.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0013-integrated-lab-definition-model/definitions/work/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.work@1.0.0-candidate.1

**Content fingerprint · SHA-256**

fcae28e30cb7aa64eca252b739ed4401709b7039770a6af52ac2b7a93bcad5b0

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Work is a bounded unit of coordinated effort with a declared purpose, owner, participants, inputs, expected result, constraints, lifecycle, and outcome trace.",
  "authority_scope_ref": "scope:work-definition",
  "exclusions": [
    "Work is not necessarily a Project and does not imply authority, completion, successful outcome, or Product value.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
