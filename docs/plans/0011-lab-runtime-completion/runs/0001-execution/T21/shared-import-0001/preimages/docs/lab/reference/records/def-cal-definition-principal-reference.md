[Documentation home](../../README.md)

# Principal Reference

<a id="def-cal-definition-principal-reference"></a>

[Reference catalog](../definitions.md#catalog-definitions) / Exact record

# Principal Reference

A minimal reference allowing a record to resolve the relevant principal identity and integrity information without copying the full identity record.

**When it applies**

A Principal Reference is a minimal governed reference to one Principal used by artifacts that need accountability or authorization linkage without copying the Principal’s identity record.

**Record formats**

[Principal reference · v1](type-cal-artifact-type-principal-reference-v1.md#type-cal-artifact-type-principal-reference-v1)

**A stated exclusion**

A Principal Reference contains only the minimum stable identifier, kind, issuer or registry, resolution route, and integrity data needed by the consumer.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

## Source explanatory wording

A Principal Reference is a minimal governed reference to one Principal used by artifacts that need accountability or authorization linkage without copying the Principal’s identity record. A Principal Reference contains only the minimum stable identifier, kind, issuer or registry, resolution route, and integrity data needed by the consumer.

## Exact governing statement

A Principal Reference is a minimal governed reference to one Principal used by artifacts that need accountability or authorization linkage without copying the Principal’s identity record. It is not the Principal, an authentication credential, a Person Reference, a Role assignment, or proof of authority.

````
PrincipalReference(x) => governed_identity_or_record(x) and bounded_scope(x); PrincipalReference(x) =/=> authority_effect(x).
````

- A Principal Reference contains only the minimum stable identifier, kind, issuer or registry, resolution route, and integrity data needed by the consumer.
- The referenced Principal remains the identity authority; the reference cannot copy, mutate, authenticate, or replace it.
- A Principal Reference contains no reusable credential and proves no Person identity, Role, Assignment, or authority grant.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0013-integrated-lab-definition-model/definitions/principal-reference/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.principal-reference@1.0.0-candidate.1

**Content fingerprint · SHA-256**

7ca6bd645843a17ac21936da623f7ccff6b011f4d7051ad6e4ffd19121b1a16e

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "A Principal Reference is a minimal governed reference to one Principal used by artifacts that need accountability or authorization linkage without copying the Principal’s identity record.",
  "authority_scope_ref": "scope:principal-reference-definition",
  "exclusions": [
    "A Principal Reference contains only the minimum stable identifier, kind, issuer or registry, resolution route, and integrity data needed by the consumer.",
    "The referenced Principal remains the identity authority; the reference cannot copy, mutate, authenticate, or replace it.",
    "A Principal Reference contains no reusable credential and proves no Person identity, Role, Assignment, or authority grant.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to this catalog](../definitions.md#catalog-definitions)
