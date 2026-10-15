[Documentation home](../../README.md)

# Policy

<a id="def-cal-definition-policy"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Policy

# Policy

A versioned rule set issued within a particular authority scope, specifying required or prohibited actions and handling. It does not execute itself or grant authority beyond its issuer.

**When it applies**

A Policy is a versioned normative rule set issued within an exact authority scope that constrains or requires decisions, Actions, lifecycle transitions, evidence, or handling.

**Record formats**

[Policy · v2](type-cal-artifact-type-policy-v2.md#type-cal-artifact-type-policy-v2)

**A stated exclusion**

A Policy does not execute itself, grant authority beyond its issuer, prove compliance, or replace a Decision.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-policy-section-2"></a>

## Source explanatory wording

A Policy is a versioned normative rule set issued within an exact authority scope that constrains or requires decisions, Actions, lifecycle transitions, evidence, or handling. A Policy does not execute itself, grant authority beyond its issuer, prove compliance, or replace a Decision.

<a id="def-cal-definition-policy-section-3"></a>

## Exact governing statement

A Policy is a versioned normative rule set issued within an exact authority scope that constrains or requires decisions, Actions, lifecycle transitions, evidence, or handling. A Policy does not execute itself, grant authority beyond its issuer, prove compliance, or replace a Decision.

````
Policy(x) => governed_identity_or_record(x) and bounded_scope(x); Policy(x) =/=> authority_effect(x).
````

- A Policy is a versioned normative rule set issued within an exact authority scope that constrains or requires decisions, Actions, lifecycle transitions, evidence, or handling.
- A Policy does not execute itself, grant authority beyond its issuer, prove compliance, or replace a Decision.
- Identity, lifecycle, evidence, authority, and relation effects remain separately governed.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../assets/04460c28fa56-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.policy@1.0.0-candidate.1

**Content fingerprint · SHA-256**

04460c28fa56271c696786b882bf69e8327e2a22413d796add060f54db3ed660

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "A Policy is a versioned normative rule set issued within an exact authority scope that constrains or requires decisions, Actions, lifecycle transitions, evidence, or handling.",
  "authority_scope_ref": "scope:policy-definition",
  "exclusions": [
    "A Policy does not execute itself, grant authority beyond its issuer, prove compliance, or replace a Decision.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
