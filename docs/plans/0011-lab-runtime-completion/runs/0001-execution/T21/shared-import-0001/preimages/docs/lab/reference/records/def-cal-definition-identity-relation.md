[Documentation home](../../README.md)

# Identity Relation

<a id="def-cal-definition-identity-relation"></a>

[Reference catalog](../definitions.md#catalog-definitions) / Exact record

# Identity Relation

An explicit relationship between separately identified things. Linking them does not make them identical or transfer authority.

**When it applies**

An explicit, typed, owner-accountable statement connecting two independently identified endpoints for a declared purpose.

**Record formats**

[Identity graph · v1](type-cal-artifact-type-identity-graph-v1.md#type-cal-artifact-type-identity-graph-v1) · [Method binding · v1](type-cal-artifact-type-method-binding-v1.md#type-cal-artifact-type-method-binding-v1)

**A stated exclusion**

An inferred relation from names, paths, co-location, shared owners, or field resemblance.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

## Source explanatory wording

An Identity Relation says exactly how two separate things are connected. The connection never turns them into the same thing and never gives one the other's authority.

## Exact governing statement

An Identity Relation is a separately governed typed edge with relation identity, kind, source endpoint, target endpoint, owner, evidence, and lifecycle. It preserves endpoint identity and authority, and dependent classifications are expressed through such relations instead of inferred duplicate labels.

````
R = (relation_id, kind, from_ref, to_ref, owner_ref, evidence_refs, lifecycle); R(a,b) does not imply a = b or authority(a) = authority(b).
````

- Both endpoints resolve independently.
- The relation kind has a declared interpretation and direction.
- Shared principal or directory placement cannot synthesize a relation.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Semantic foundation admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0006-craft-identity/definitions/identity-relation/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.identity-relation@1.0.0-candidate.1

**Content fingerprint · SHA-256**

cf6a40999ffab4e25f8766d1cd3f6085b7b3ab9468828539521c18e9ca30f28e

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "authority_scope_ref": "scope:identity-relation-definition",
  "applicability": "An explicit, typed, owner-accountable statement connecting two independently identified endpoints for a declared purpose.",
  "exclusions": [
    "An inferred relation from names, paths, co-location, shared owners, or field resemblance.",
    "A mechanism that merges endpoints, transfers their authority, or silently creates a classification axis."
  ]
}
````

[Return to this catalog](../definitions.md#catalog-definitions)
