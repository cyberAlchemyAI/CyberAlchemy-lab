[Documentation home](../../README.md)

# Generated Output

<a id="def-cal-definition-generated-output"></a>

[Reference catalog](../definitions.md#catalog-definitions) / Exact record

# Generated Output

A reproducible result from exact inputs and a particular generator version, with origin and consistency checks. An explicit type contract can designate it as a canonical record; generation does not make it a second semantic authority.

**When it applies**

A Generated Output is a reproducible product derived from exact canonical inputs by an exact governed generator version and bound to lineage and parity checks.

**Record formats**

[Artifact type registry · v2](type-cal-artifact-type-artifact-type-registry-v2.md#type-cal-artifact-type-artifact-type-registry-v2) · [Generated output · v2](type-cal-artifact-type-generated-output-v2.md#type-cal-artifact-type-generated-output-v2) · [Ontology package · v1](type-cal-artifact-type-ontology-package-v1.md#type-cal-artifact-type-ontology-package-v1)

**A stated exclusion**

It is not a second semantic authority and is canonical only when an explicit Artifact Type contract says so.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

## Source explanatory wording

A Generated Output is a reproducible product derived from exact canonical inputs by an exact governed generator version and bound to lineage and parity checks. It is not a second semantic authority and is canonical only when an explicit Artifact Type contract says so.

## Exact governing statement

A Generated Output is a reproducible product derived from exact canonical inputs by an exact governed generator version and bound to lineage and parity checks. It is not a second semantic authority and is canonical only when an explicit Artifact Type contract says so.

````
GeneratedOutput(x) => governed_identity_or_record(x) and bounded_scope(x); GeneratedOutput(x) =/=> authority_effect(x).
````

- A Generated Output is a reproducible product derived from exact canonical inputs by an exact governed generator version and bound to lineage and parity checks.
- It is not a second semantic authority and is canonical only when an explicit Artifact Type contract says so.
- Identity, lifecycle, evidence, authority, and relation effects remain separately governed.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0013-integrated-lab-definition-model/definitions/generated-output/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.generated-output@1.0.0-candidate.1

**Content fingerprint · SHA-256**

f54b29e0b52ffdc4c57eb5df8525f3c065c1545f664ffd479188657b10d0c9cf

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "A Generated Output is a reproducible product derived from exact canonical inputs by an exact governed generator version and bound to lineage and parity checks.",
  "authority_scope_ref": "scope:generated-output-definition",
  "exclusions": [
    "It is not a second semantic authority and is canonical only when an explicit Artifact Type contract says so.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to this catalog](../definitions.md#catalog-definitions)
