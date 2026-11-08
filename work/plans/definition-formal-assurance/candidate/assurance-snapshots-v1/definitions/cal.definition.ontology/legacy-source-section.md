## CAV2-D19: Ontology

Status: active
Term: ontology
Aliases: governed meaning layer, ontology candidate, ontology map, ontology branch map, ontology candidate condensation

### Normative Definition

An ontology is a governed meaning layer that represents a domain, workspace,
system, or operation as typed knowledge objects, typed relations, branch or role
assignments, provenance, confidence, promotion state, and use obligations.

In CyberAlchemy v2, an ontology becomes actionable only when it records:

- scope or domain of meaning
- knowledge object types
- typed relations or edge rules
- branch, role, or ownership assignment
- evidence and provenance references
- evidence confidence and commitment confidence when claims are load-bearing
- promotion state and next gate
- contradiction, drift, residue, or invalidation route
- retrieval or use guidance for downstream agents or humans

### Formal Interpretation

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

### Operational Interpretation

Use ontology after source evidence has been located and inventory has made it
findable, when the project needs meaning that agents or humans can actually use:
what a thing is, where it belongs, how it relates to other things, what supports
it, how confident the project is, and when it may guide later work.

Branch-aware ontology separates business or meaning claims, system claims, and
bridge claims so implementation evidence cannot silently redefine intent and
intent cannot pretend implementation exists. Some local systems add further
branches, such as an agent-operation branch or run-context branch, but those are
typed substructures and not aliases for ontology itself.

### Plain-Language Intuition

An ontology is a map of meaning with typed links, receipts, and rules for use.

### Domain-Context Voice

In CyberAlchemy v2, ontology is the layer that condenses scattered repository
knowledge into candidate branch maps, thick knowledge entries, and promotion
requests without making them canonical by proximity. The current
`.arcanum/ontology-vault/` map reduces search and suggests branches; future
`ontology/` project-space material may hold candidate branch maps and promotion
requests. Definitions still become canonical only in this file, and source
authority still comes from the source space unless a promotion gate passes.

Inside the future CyberAlchemy base repository, `ontology/` is the workspace
where authority relations are made explicit, reviewable, and constructible as a
candidate/projection package. It is where v2 fixes the shape of authority for
the base by mapping meaning, evidence, owner routes, promotion requests,
projection boundaries, and residue before any downstream project builds above
that base.

This term connects `CAV2-D16` typed coupling invariant, `CAV2-D18` residue, and
the knowledge-governance tower: an ontology can type relations, preserve
meaningful residue, and route candidate meaning toward context-builder,
decision-gate, definitions-governance, or implementation work.

### Boundary

Ontology is not raw source, not inventory, not a glossary, not memory, not a
session transcript, not a generated search index, and not automatic authority.
Candidate ontology may condense meaning, but it cannot promote definitions,
constitutions, runtime contracts, or public claims by itself. The ontology
package fixes authority by making candidate authority structure explicit; it
does not own authority transitions.

`Operational Ontology` is demoted as a CyberAlchemy v2 definition candidate.
Treat it as source-local shorthand for an operation-facing ontology projection:
a `CAV2-D19` ontology view whose authority posture is governed by `CAV2-D23`.
It is not a primitive, not a peer ontology branch, not a standalone subtype, and
not a `CAV2-D23` alias.

When a source uses `Operational Ontology`, normalize the phrase instead of
promoting it:

- typed meaning, relation, branch, evidence, retrieval, or use obligations route
  to `CAV2-D19` ontology;
- lifecycle posture, status, evidence confidence, commitment, provenance,
  owner, or residue separation routes to `CAV2-D23` authority lifecycle axis;
- agent-operation, run, action, routing, or workflow obligations must be named
  as concrete object, relation, action, run, or schema obligations rather than
  hidden inside the broad phrase;
- if no concrete obligation remains after the D19/D23 split, retire the phrase
  in local wording.

### Primary Consumers

- [DEFINITION-TOWERS.md](DEFINITION-TOWERS.md)
- [../../CRAFT.md](../../CRAFT.md)
- [../../../.arcanum/ontology-vault/map-2026-06-18-dispersed-knowledge.md](../../../.arcanum/ontology-vault/map-2026-06-18-dispersed-knowledge.md)
- [../../development/reviews/2026-06-22-operational-ontology-authority-lifecycle-review/findings.md](../../development/reviews/2026-06-22-operational-ontology-authority-lifecycle-review/findings.md)
- [../../../.arcanum/inventory/entries/evidence-sets/2026-06-22-operational-ontology-authority-lifecycle-sets.md](../../../.arcanum/inventory/entries/evidence-sets/2026-06-22-operational-ontology-authority-lifecycle-sets.md)
