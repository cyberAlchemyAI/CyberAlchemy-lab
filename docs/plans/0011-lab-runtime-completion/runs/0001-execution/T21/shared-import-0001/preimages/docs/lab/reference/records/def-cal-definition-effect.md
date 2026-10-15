[Documentation home](../../README.md)

# Effect

<a id="def-cal-definition-effect"></a>

[Reference catalog](../definitions.md#catalog-definitions) / Exact record

# Effect

A stated change to state, rights, obligations, external conditions or interpretation. Intending, authorizing, attempting and observing that change are separate facts.

**When it applies**

An Effect is a declared change in governed state, rights, obligations, external condition, or interpretation that a Decision or Action intends, authorizes, records, or observes under an exact effect kind.

**Record formats**

[Effect · v1](type-cal-artifact-type-effect-v1.md#type-cal-artifact-type-effect-v1)

**A stated exclusion**

Declaring, authorizing, attempting, delivering, and observing an Effect are separate facts.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

## Source explanatory wording

An Effect is a declared change in governed state, rights, obligations, external condition, or interpretation that a Decision or Action intends, authorizes, records, or observes under an exact effect kind. Declaring, authorizing, attempting, delivering, and observing an Effect are separate facts.

## Exact governing statement

An Effect is a declared change in governed state, rights, obligations, external condition, or interpretation that a Decision or Action intends, authorizes, records, or observes under an exact effect kind. Declaring, authorizing, attempting, delivering, and observing an Effect are separate facts.

````
Effect(x) => governed_identity_or_record(x) and bounded_scope(x); Effect(x) =/=> authority_effect(x).
````

- An Effect is a declared change in governed state, rights, obligations, external condition, or interpretation that a Decision or Action intends, authorizes, records, or observes under an exact effect kind.
- Declaring, authorizing, attempting, delivering, and observing an Effect are separate facts.
- Identity, lifecycle, evidence, authority, and relation effects remain separately governed.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0013-integrated-lab-definition-model/definitions/effect/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.effect@1.0.0-candidate.1

**Content fingerprint · SHA-256**

f6d1e16142583a10b039890409b494338b5879cac63da31cab75d633667a08c1

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "An Effect is a declared change in governed state, rights, obligations, external condition, or interpretation that a Decision or Action intends, authorizes, records, or observes under an exact effect kind.",
  "authority_scope_ref": "scope:effect-definition",
  "exclusions": [
    "Declaring, authorizing, attempting, delivering, and observing an Effect are separate facts.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to this catalog](../definitions.md#catalog-definitions)
