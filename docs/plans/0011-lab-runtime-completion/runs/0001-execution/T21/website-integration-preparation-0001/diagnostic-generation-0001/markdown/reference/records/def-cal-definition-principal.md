[Documentation home](../../README.md)

# Principal

<a id="def-cal-definition-principal"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Principal

# Principal

An identity recognized within a particular authentication, authorization, ownership or accountability boundary. Recognition at one boundary does not grant rights at others.

**When it applies**

A Principal is a governed identity recognized by an authentication, authorization, ownership, or accountability boundary.

**Record formats**

[Principal · v1](type-cal-artifact-type-principal-v1.md#type-cal-artifact-type-principal-v1)

**A stated exclusion**

Principal identity is recognized only inside exact authentication, authorization, ownership, or accountability boundaries.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-principal-section-2"></a>

## Source explanatory wording

A Principal is a governed identity recognized by an authentication, authorization, ownership, or accountability boundary. Principal identity is recognized only inside exact authentication, authorization, ownership, or accountability boundaries.

<a id="def-cal-definition-principal-section-3"></a>

## Exact governing statement

A Principal is a governed identity recognized by an authentication, authorization, ownership, or accountability boundary. Principal identity does not prove Person identity, Agent capability, Role assignment, or authority beyond exact grants.

````
Principal(x) => governed_identity_or_record(x) and bounded_scope(x); Principal(x) =/=> authority_effect(x).
````

- Principal identity is recognized only inside exact authentication, authorization, ownership, or accountability boundaries.
- Person, Team, service, or Agent subjects represented by a Principal retain independent identities and lifecycles.
- A Principal receives authority only through exact grants; identity alone creates no Role, capability, ownership, or permission.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../assets/60180d24ef3e-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.principal@1.0.0-candidate.1

**Content fingerprint · SHA-256**

60180d24ef3e83c517ea8f51f5ab863801c248ac80d19864353b58f70aaad794

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "A Principal is a governed identity recognized by an authentication, authorization, ownership, or accountability boundary.",
  "authority_scope_ref": "scope:principal-definition",
  "exclusions": [
    "Principal identity is recognized only inside exact authentication, authorization, ownership, or accountability boundaries.",
    "Person, Team, service, or Agent subjects represented by a Principal retain independent identities and lifecycles.",
    "A Principal receives authority only through exact grants; identity alone creates no Role, capability, ownership, or permission.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
