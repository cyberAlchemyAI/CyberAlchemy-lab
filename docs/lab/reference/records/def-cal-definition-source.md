[Documentation home](../../README.md)

# Source

<a id="def-cal-definition-source"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Source

# Source

An identifiable origin from which information or a claim was obtained, with a resolvable reference and integrity boundary. Origin alone does not establish truth, freshness or authority.

**When it applies**

When identifying the exact origin of content, data, evidence or a claim.

**Record formats**

[Source · v1](type-cal-artifact-type-source-v1.md#type-cal-artifact-type-source-v1)

**[In the Northstar incident](../../tutorials/incident-walkthrough.md)**

The exact saved S1 input and E12 output provide distinct origins with inspectable integrity boundaries.

**Common mistake**

Assuming source material is true or authoritative merely because it is recorded.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-source-section-2"></a>

## Source explanatory wording

A Source is an exact provenance-bearing origin from which content, evidence, data, or a claim was obtained, identified by a resolvable reference and integrity boundary. Being a Source does not make content true, current, complete, authoritative, admissible, or licensed for every use.

<a id="def-cal-definition-source-section-3"></a>

## Exact governing statement

A Source is an exact provenance-bearing origin from which content, evidence, data, or a claim was obtained, identified by a resolvable reference and integrity boundary. Being a Source does not make content true, current, complete, authoritative, admissible, or licensed for every use.

````
Source(x) => governed_identity_or_record(x) and bounded_scope(x); Source(x) =/=> authority_effect(x).
````

- A Source is an exact provenance-bearing origin from which content, evidence, data, or a claim was obtained, identified by a resolvable reference and integrity boundary.
- Being a Source does not make content true, current, complete, authoritative, admissible, or licensed for every use.
- Identity, lifecycle, evidence, authority, and relation effects remain separately governed.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0013-integrated-lab-definition-model/definitions/source/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.source@1.0.0-candidate.1

**Content fingerprint · SHA-256**

aefe53df65d0697772ccb565ec9c279927b1ace67bfd770d2dd959309f11d63a

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "A Source is an exact provenance-bearing origin from which content, evidence, data, or a claim was obtained, identified by a resolvable reference and integrity boundary.",
  "authority_scope_ref": "scope:source-definition",
  "exclusions": [
    "Being a Source does not make content true, current, complete, authoritative, admissible, or licensed for every use.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
