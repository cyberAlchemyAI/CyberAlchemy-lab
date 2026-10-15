[Documentation home](../../README.md)

# Artifact Type Registry

<a id="def-cal-definition-artifact-type-registry"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Artifact Type Registry

# Artifact Type Registry

The catalog identifying record-type contracts, exact source locations and whether particular versions have been accepted. It supports explicit type selection.

**When it applies**

Maintaining one exact machine registry that maps Artifact Type identities and instance discriminators to immutable contracts and owner decisions.

**Record formats**

[Artifact type registry · v2](type-cal-artifact-type-artifact-type-registry-v2.md#type-cal-artifact-type-artifact-type-registry-v2)

**A stated exclusion**

Replacing admission decisions.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-artifact-type-registry-section-2"></a>

## Source explanatory wording

The registry is the single catalog that tells tools which file contracts really exist, where their exact bytes live, and which decision—if any—made each one usable.

<a id="def-cal-definition-artifact-type-registry-section-3"></a>

## Exact governing statement

An Artifact Type Registry R is a canonical reference index over immutable Artifact Type contracts and lifecycle-decision overlays. Each entry binds one type version to its exact artifact, schema, discriminator, semantic definitions, lifecycle state, and decision evidence. R references but does not redefine or admit its entries.

````
entry_R(t)=(artifact@digest,schema@digest,discriminator,definitions,decision,state); registered_R(t) =/=> admitted(t); current_R(t) only by exact owner decision overlay.
````

- Candidate and admitted entries are never collapsed.
- Historical admitted versions remain visible when a successor becomes current.
- Shared bootstrap schema selectors are valid exact bindings and need not be moved.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0009-artifact-surface-foundation/definitions/artifact-type-registry/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.artifact-type-registry@1.0.0-candidate.1

**Content fingerprint · SHA-256**

e554069c42d0ee17d4df65a0de2b0bba998933622aa9aba296671a01dd273e81

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "authority_scope_ref": "scope:artifact-type-registry",
  "applicability": "Maintaining one exact machine registry that maps Artifact Type identities and instance discriminators to immutable contracts and owner decisions.",
  "exclusions": [
    "Replacing admission decisions.",
    "Registering a candidate as admitted.",
    "Duplicating canonical Artifact Type package bytes."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
