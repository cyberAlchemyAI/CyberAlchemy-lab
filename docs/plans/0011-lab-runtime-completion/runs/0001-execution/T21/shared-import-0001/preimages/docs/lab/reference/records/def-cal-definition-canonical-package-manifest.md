[Documentation home](../../README.md)

# Canonical Package Manifest

<a id="def-cal-definition-canonical-package-manifest"></a>

[Reference catalog](../definitions.md#catalog-definitions) / Exact record

# Canonical Package Manifest

Declares the package’s identity, what changes together, each file’s role and any nested lifecycle boundaries. Folder layout does not substitute for those declarations.

**When it applies**

Declaring one Canonical Package Home, its owner-local aggregate, lifecycle owner, unit of change, governed carriers, facets, and nested package relations.

**Record formats**

[Canonical package manifest · v1](type-cal-artifact-type-canonical-package-manifest-v1.md#type-cal-artifact-type-canonical-package-manifest-v1)

**A stated exclusion**

Making directory placement authoritative.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

## Source explanatory wording

The manifest says what changes together and what every file does, including itself. Nested lifecycles are declared, never guessed from folders.

## Exact governing statement

A Canonical Package Manifest M declares one canonical package home, aggregate, lifecycle owner, unit of change, every governed member's unique surface role, and every independent nested package relation. M must classify its own package.json exactly once as a canonical instance of Canonical Package Manifest/v1. Membership and nesting are explicit data, not directory inference.

````
M=(home,aggregate,owner,unit,members,nested); members[package.json]=(I,CanonicalPackageManifest/v1,1); for all f in governed(home), exists exactly one members[f]; independent(n) => exists manifest(n) and relation(M,n).
````

- Files with different lifecycle owners or recovery boundaries require separate package homes.
- A directory without its own manifest remains a facet of the nearest declared package.
- Manifest membership cannot change Artifact identity or type.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0010-artifact-surface-foundation-revision/definitions/canonical-package-manifest/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.canonical-package-manifest@1.0.0-candidate.2

**Content fingerprint · SHA-256**

2837753f9bbcf00e62edc7ebae07de9724e4eafbcd834d73ba2550ec5e2ba641

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Declaring one Canonical Package Home, its owner-local aggregate, lifecycle owner, unit of change, governed carriers, facets, and nested package relations.",
  "authority_scope_ref": "scope:canonical-package-manifest",
  "exclusions": [
    "Making directory placement authoritative.",
    "Collapsing colocated semantic identities.",
    "Treating every nested directory as a package home."
  ]
}
````

[Return to this catalog](../definitions.md#catalog-definitions)
