[Documentation home](../../README.md)

# Canonical Package Home

<a id="def-cal-definition-canonical-package-home"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Canonical Package Home

# Canonical Package Home

The designated package containing material that changes together. Distinct capabilities, contexts, products and runtime records remain separately identified within it; other catalogs point to it rather than keeping competing master copies.

**When it applies**

Selecting the single governed artifact tree that carries the canonical machine sources of one explicitly declared owner-local aggregate and keeps its related semantic facets cohesive without collapsing their identities.

**Record formats**

[Canonical package manifest · v1](type-cal-artifact-type-canonical-package-manifest-v1.md#type-cal-artifact-type-canonical-package-manifest-v1)

**A stated exclusion**

Inferring semantic identity, context membership, or authority from a directory path.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-canonical-package-home-section-2"></a>

## Source explanatory wording

Keep one thing that changes together in one canonical workshop. The workshop can contain separately labelled capability, context, product, runtime, and evidence benches; putting them together does not make them the same thing. Catalogs elsewhere point to the workshop instead of keeping rival master copies.

<a id="def-cal-definition-canonical-package-home-section-3"></a>

## Exact governing statement

A Canonical Package Home is the unique governed artifact tree H selected for an owner-local aggregate A by an explicit lifecycle-owner binding and unit-of-change declaration. H carries A's canonical machine sources. Capability, bounded-context, product, DomainSpec, implementation, evidence, and projection facets may be colocated in H when they share A's lifecycle, but their identities and authorities remain distinct and are connected by explicit typed relations. Indexes and global views may reference or generate projections of H; they must not duplicate its canonical carriers.

````
CPH(A)=H iff declared_owner(A)=lifecycle_owner(H) and unit_of_change(A)=unit_of_change(H); exists exactly one H for each canonical carrier c in A such that canonical_at(c,H); colocated(x,y,H) =/=> identity(x)=identity(y); classified_as(x,k) =/=> CPH(x)=root(k); indexes(i,c) =/=> canonical_at(c,i).
````

- The lifecycle owner and unit of change select the home; the directory does not select the owner, identity, or context.
- Semantic orthogonality requires distinct identities and typed relations, not separate physical roots.
- A bounded context may be a facet of an aggregate without being the aggregate's directory or owning every colocated artifact.
- Artifacts with different lifecycle owners or independent recovery boundaries require separate canonical homes even when one global index presents them together.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Canonical package organization admission

**Original definition**

[Read the original record](../../assets/c81059796872-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.canonical-package-home@1.0.0-candidate.1

**Content fingerprint · SHA-256**

c810597968723991449fe78458254679cc6dc87b2b81e54e16a9aa599c59f8ca

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "authority_scope_ref": "scope:canonical-package-home-definition",
  "applicability": "Selecting the single governed artifact tree that carries the canonical machine sources of one explicitly declared owner-local aggregate and keeps its related semantic facets cohesive without collapsing their identities.",
  "exclusions": [
    "Inferring semantic identity, context membership, or authority from a directory path.",
    "Requiring every semantic axis or bounded context to have a separate top-level directory.",
    "Colocating artifacts that have different lifecycle owners or independent units of change."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
