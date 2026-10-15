[Documentation home](../../README.md)

# Ontology

<a id="def-cal-definition-ontology"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Ontology

# Ontology

A governed structured model of concepts, things and relationships, with rules for representation, evidence, lifecycle and use.

**When it applies**

When organizing meaning, typed subjects, relationships, evidence and limits into a usable connected model.

**Record formats**

[Ontology package · v1](type-cal-artifact-type-ontology-package-v1.md#type-cal-artifact-type-ontology-package-v1) · [Ontology · v1](type-cal-artifact-type-ontology-v1.md#type-cal-artifact-type-ontology-v1)

**[In the Northstar incident](../../tutorials/incident-walkthrough.md)**

Organize typed meanings, subjects, connections and evidence so the investigation can recover their context.

**Common mistake**

Promoting meaning or granting permission because a node appears in a graph.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-ontology-section-2"></a>

## Source explanatory wording

An ontology is a map of meaning with typed links, receipts, and rules for use.

<a id="def-cal-definition-ontology-section-3"></a>

## Exact governing statement

Ontology is the normalized definition identified by semantic.ontology, owned within scope.shared-authority, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D19 without silently merging it with another target.

Bound source-semantic basis:

An ontology is a governed meaning layer that represents a domain, workspace, system, or operation as typed knowledge objects, typed relations, branch or role assignments, provenance, confidence, promotion state, and use obligations.

In CyberAlchemy v2, an ontology becomes actionable only when it records:

- scope or domain of meaning - knowledge object types - typed relations or edge rules - branch, role, or ownership assignment - evidence and provenance references - evidence confidence and commitment confidence when claims are load-bearing - promotion state and next gate - contradiction, drift, residue, or invalidation route - retrieval or use guidance for downstream agents or humans

````
Given source evidence `S`, inventory evidence layer `I`, and intended use `U`,
an ontology `O` is a typed structure over selected evidence:

```text
O_U = (N, E, B, R, C, P, G)
```

where:

- `N` is a set of typed knowledge objects or nodes
- `E` is a set of typed relations or edges over `N`
- `B` assigns branch, role, or ownership context
- `R` links ontology claims back to source or inventory evidence
- `C` records confidence, scope, validity, and expiry where relevant
- `P` records candidate, reviewed, promoted, demoted, or deferred state
- `G` records gates, contradiction paths, drift routes, and use obligations

An ontology may be graph-shaped, tree-shaped, branch-aware, entry-based, or
artifact-tree-shaped, but it must keep typed meaning, evidence, and authority
posture together. A pointer list without usable content, typed relations, and
governance state is inventory or index material, not ontology.
````

- Ontology is not raw source, not inventory, not a glossary, not memory, not a session transcript, not a generated search index, and not automatic authority. Candidate ontology may condense meaning, but it cannot promote definitions, constitutions, runtime contracts, or public claims by itself. The ontology package fixes authority by making candidate authority structure explicit; it does not own authority transitions. `Operational Ontology` is demoted as a CyberAlchemy v2 definition candidate. Treat it as source-local shorthand for an operation-facing ontology projection: a `CAV2-D19` ontology view whose authority posture is governed by `CAV2-D23`. It is not a primitive, not a peer ontology branch, not a standalone subtype, and not a `CAV2-D23` alias. When a source uses `Operational Ontology`, normalize the phrase instead of promoting it: - typed meaning, relation, branch, evidence, retrieval, or use obligations route to `CAV2-D19` ontology; - lifecycle posture, status, evidence confidence, commitment, provenance, owner, or residue separation routes to `CAV2-D23` authority lifecycle axis; - agent-operation, run, action, routing, or workflow obligations must be named as concrete object, relation, action, run, or schema obligations rather than hidden inside the broad phrase; - if no concrete obligation remains after the D19/D23 split, retire the phrase in local wording.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../../../evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/definitions/ontology/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.ontology@1.0.0-candidate.1

**Content fingerprint · SHA-256**

2f14c4861b7d5b9b22768fdd6d56df8dfce08f6557594046c7842dee46f884b8

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Use ontology after source evidence has been located and inventory has made it\nfindable, when the project needs meaning that agents or humans can actually use:\nwhat a thing is, where it belongs, how it relates to other things, what supports\nit, how confident the project is, and when it may guide later work.\n\nBranch-aware ontology separates business or meaning claims, system claims, and\nbridge claims so implementation evidence cannot silently redefine intent and\nintent cannot pretend implementation exists. Some local systems add further\nbranches, such as an agent-operation branch or run-context branch, but those are\ntyped substructures and not aliases for ontology itself.",
  "authority_scope_ref": "scope.shared-authority",
  "exclusions": [
    "Admission, activation, publication, release, deployment, and external effects.",
    "Meanings assigned to split or reclassified sibling targets unless explicitly referenced."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
