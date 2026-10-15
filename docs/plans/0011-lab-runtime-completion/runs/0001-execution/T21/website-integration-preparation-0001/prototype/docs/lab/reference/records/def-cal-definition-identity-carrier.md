[Documentation home](../../README.md)

# Identity Carrier

<a id="def-cal-definition-identity-carrier"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Identity Carrier

# Identity Carrier

The designated record identifying one particular thing. Folder names, ownership and connections cannot silently change that identity.

**When it applies**

A canonical artifact whose distinct validation purpose is to preserve one subject identity, subject kind, owner route, lifecycle identity, and exact semantic Definition bindings across representations and relations.

**Record formats**

[Goal · v1](type-cal-artifact-type-goal-v1.md#type-cal-artifact-type-goal-v1) · [Product identity · v2](type-cal-artifact-type-product-identity-v2.md#type-cal-artifact-type-product-identity-v2) · [Project identity · v1](type-cal-artifact-type-project-identity-v1.md#type-cal-artifact-type-project-identity-v1)

**A stated exclusion**

The subject's semantic Definition.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-identity-carrier-section-2"></a>

## Source explanatory wording

An Identity Carrier is the canonical file that says which exact thing this is. Its folder, name, owner, or connections cannot silently turn it into another thing.

<a id="def-cal-definition-identity-carrier-section-3"></a>

## Exact governing statement

An Identity Carrier K is a canonical artifact for exactly one subject identity. K binds a stable subject identifier, subject kind Definition, owner route, lifecycle identity, and provenance while keeping related identities external through typed relations. Neither placement nor relation membership may synthesize, merge, or replace the carried identity.

````
K = (carrier_id, subject_id, subject_kind_definition_ref, owner_route, lifecycle_ref, provenance_refs); carries(K,x) and related(x,y) does not imply x=y; path(K) =/=> identity(x).
````

- One carrier has one primary subject identity.
- The subject kind resolves through a semantic Definition reference.
- Relations preserve endpoint identity and authority.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Semantic foundation admission

**Original definition**

[Read the original record](../../assets/ddfdb1a06f8c-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.identity-carrier@1.0.0-candidate.1

**Content fingerprint · SHA-256**

ddfdb1a06f8c2bbb751b3dab27d0d72ea0a7189c6c2d3ad95c7244a3d3ac104a

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "authority_scope_ref": "scope:identity-carrier-definition",
  "applicability": "A canonical artifact whose distinct validation purpose is to preserve one subject identity, subject kind, owner route, lifecycle identity, and exact semantic Definition bindings across representations and relations.",
  "exclusions": [
    "The subject's semantic Definition.",
    "A directory, filename, shared label, owner, or relation from which identity is inferred.",
    "A graph index or projection that duplicates or replaces the carrier's canonical identity fields."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
