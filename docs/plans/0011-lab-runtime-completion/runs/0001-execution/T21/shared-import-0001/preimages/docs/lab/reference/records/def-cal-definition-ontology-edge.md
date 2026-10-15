[Documentation home](../../README.md)

# Ontology Edge

<a id="def-cal-definition-ontology-edge"></a>

[Reference catalog](../definitions.md#catalog-definitions) / Exact record

# Ontology Edge

An independently identified graph connection representing a particular global Typed Relation or a separately declared ontology-local relationship. A local edge does not become a global connection.

**When it applies**

An Ontology Edge is an independently identified governed connection between Ontology Nodes that is either a digest-bound projection of one global Typed Relation or an explicitly ontology-local interpretation.

**Record formats**

[Ontology edge · v1](type-cal-artifact-type-ontology-edge-v1.md#type-cal-artifact-type-ontology-edge-v1)

**A stated exclusion**

A local edge is not a global connection; a projected edge cannot override or become a second writable authority for its Typed Relation.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

## Source explanatory wording

An Ontology Edge is an independently identified governed connection between Ontology Nodes that is either a digest-bound projection of one global Typed Relation or an explicitly ontology-local interpretation. A local edge is not a global connection; a projected edge cannot override or become a second writable authority for its Typed Relation.

## Exact governing statement

An Ontology Edge is an independently identified governed connection between Ontology Nodes that is either a digest-bound projection of one global Typed Relation or an explicitly ontology-local interpretation. A local edge is not a global connection; a projected edge cannot override or become a second writable authority for its Typed Relation.

````
OntologyEdge(x) => governed_identity_or_record(x) and bounded_scope(x); OntologyEdge(x) =/=> authority_effect(x).
````

- An Ontology Edge is an independently identified governed connection between Ontology Nodes that is either a digest-bound projection of one global Typed Relation or an explicitly ontology-local interpretation.
- A local edge is not a global connection; a projected edge cannot override or become a second writable authority for its Typed Relation.
- Identity, lifecycle, evidence, authority, and relation effects remain separately governed.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0013-integrated-lab-definition-model/definitions/ontology-edge/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.ontology-edge@1.0.0-candidate.1

**Content fingerprint · SHA-256**

c5eeab76f0ba40c769256c0709206282bcb18ab05a0cdfd311208cf5927b0844

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "An Ontology Edge is an independently identified governed connection between Ontology Nodes that is either a digest-bound projection of one global Typed Relation or an explicitly ontology-local interpretation.",
  "authority_scope_ref": "scope:ontology-edge-definition",
  "exclusions": [
    "A local edge is not a global connection; a projected edge cannot override or become a second writable authority for its Typed Relation.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to this catalog](../definitions.md#catalog-definitions)
