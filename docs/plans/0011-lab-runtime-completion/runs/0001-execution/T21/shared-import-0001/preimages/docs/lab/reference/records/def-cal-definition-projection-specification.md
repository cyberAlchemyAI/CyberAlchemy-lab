[Documentation home](../../README.md)

# Projection Specification

<a id="def-cal-definition-projection-specification"></a>

[Reference catalog](../definitions.md#catalog-definitions) / Exact record

# Projection Specification

Identifies when a concept needs a governed view to preserve its evidence, relationships, lifecycle, ownership and challenge behavior. That view does not itself decide authority.

**When it applies**

Use view-bearing concept when a concept starts carrying enough work that future agents need a dedicated lens over its meaning, system structure, run evidence, residue, or promotion status. The view should make the concept inspectable and usable without loading the whole repository.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**A stated exclusion**

Admission, activation, publication, release, deployment, and external effects.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

## Source explanatory wording

Some ideas become important enough to need their own dashboard, but the dashboard still does not get to make the decision.

## Exact governing statement

Projection Specification is the normalized definition identified by semantic.projection-specification, owned within scope.shared-authority, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D44 without silently merging it with another target.

Bound source-semantic basis:

A view-bearing concept is a load-bearing concept that needs its own governed view or tree because it has distinct evidence, lifecycle posture, owner route, reuse surface, and challenge/drift behavior that cannot be safely handled as ordinary narrative vocabulary.

Not every term deserves a view. A concept may become view-bearing only when the view helps preserve evidence, relations, lifecycle, owner route, reuse, or challenge behavior without pretending to decide authority by itself.

````
For concept `c`, `view_bearing(c)` is admissible when:

```text
view_bearing(c) =
  distinct_evidence(c)
  and lifecycle_posture_needed(c)
  and owner_route(c)
  and reuse_surface(c)
  and challenge_or_drift_route(c)
```

The view attached to `c` must declare allowed readings and forbidden authority
moves. If those fields are absent, `c` remains a term, candidate, or local
concept rather than a view-bearing concept.
````

- View-bearing concept is not a vault node type, not an ontology branch by itself, not a lifecycle state, not a promotion state, and not a reason to create a new tree for every term. It names the threshold where a concept needs a governed view because ordinary prose is no longer safe enough.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../../../evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/definitions/projection-specification/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.projection-specification@1.0.0-candidate.1

**Content fingerprint · SHA-256**

42cff2435ac4e732bf0ea45a2e0f5d6fcdf2921f17b18bbd1b1adcc4e643eb24

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Use view-bearing concept when a concept starts carrying enough work that future\nagents need a dedicated lens over its meaning, system structure, run evidence,\nresidue, or promotion status. The view should make the concept inspectable and\nusable without loading the whole repository.",
  "authority_scope_ref": "scope.shared-authority",
  "exclusions": [
    "Admission, activation, publication, release, deployment, and external effects.",
    "Meanings assigned to split or reclassified sibling targets unless explicitly referenced."
  ]
}
````

[Return to this catalog](../definitions.md#catalog-definitions)
