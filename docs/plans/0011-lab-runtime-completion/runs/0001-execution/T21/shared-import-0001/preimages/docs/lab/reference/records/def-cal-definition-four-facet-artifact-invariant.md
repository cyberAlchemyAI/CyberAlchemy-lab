[Documentation home](../../README.md)

# Four-Facet Artifact Invariant

<a id="def-cal-definition-four-facet-artifact-invariant"></a>

[Reference catalog](../definitions.md#catalog-definitions) / Exact record

# Four-Facet Artifact Invariant

Requires governed actions to identify classification, schema, a human-continuation view and a machine-checkable view. Missing aspects must be recorded with an owner and whether work may continue, wait or is blocked.

**When it applies**

Use this method before or during any CyberAlchemy v2 action that may matter later: definition work, constitution work, axiom work, discipline work, Craft state changes, ontology projections, task execution, workflow design, system design, validation, or implementation routing.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**A stated exclusion**

Admission, activation, publication, release, deployment, and external effects.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

## Source explanatory wording

Before an action is allowed to matter, it must answer four questions: what kind of thing is this, what shape governs it, how can a human continue it, and how can a machine check it? If one answer is missing, write down the missing piece, who owns it, and whether the action can continue.

## Exact governing statement

Four-Facet Artifact Invariant is the normalized invariant identified by semantic.four-facet-artifact-invariant, owned within scope.shared-authority, and carried by type.invariant. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D21 without silently merging it with another target.

Bound source-semantic basis:

Four-facet action method is the CyberAlchemy v2 primitive action rule that every governed action must explicitly bind, create, or record typed residue for four facets before the action can govern downstream work:

- classification or taxonomy facet - schema facet - human-continuation view - machine-checkable view

A governed action is any CyberAlchemy v2 action that creates, changes, routes, validates, promotes, implements, or interprets load-bearing artifacts, state, meaning, or authority posture. The action is admissible only when each facet is declared or when its absence is carried as typed residue.

At minimum:

- the classification or taxonomy facet states what kind of thing or action is involved and which classification catalog, taxonomy, or source vocabulary owns that assignment - the schema facet states the structural shape, field set, relation shape, or validation surface that governs the action or artifact - the human-continuation view states how a human can understand the action's purpose, status, trust boundary, blockers, residue, next route, and evidence - the machine-checkable view states how a machine can parse or check the action state, including identifiers, kind, schema reference, classification reference, source of truth, validator or proof handle, projection status, and residue

If a facet is missing, impossible, or intentionally deferred, the action must record typed residue naming the missing facet, the reason or impossibility, the owner route, the evidence reference, and the action effect: continue, defer, or block. If the action later asks to promote something, the same residue must also state the promotion effect.

````
For a governed action `a`, let:

```text
F(a) = (K_a, S_a, H_a, M_a, R_a)
```

where:

- `K_a` is the classification or taxonomy facet
- `S_a` is the schema facet
- `H_a` is the human-continuation view
- `M_a` is the machine-checkable view
- `R_a` is typed residue for any missing, impossible, or deferred facet

The action satisfies the four-facet action method when each of `K_a`, `S_a`,
`H_a`, and `M_a` is either bound to an existing governed surface, created by the
action, or represented in `R_a` with owner route and effect. The method forbids
silent absence; it does not require perfect completion before exploratory work
can begin.
````

- Four-facet action method is not a promotion gate by itself, not proof of authority, not a requirement that all exploratory work have perfect schemas before it starts, and not a single required file format. It allows an action to create missing facets or carry typed residue. Generic `schema` semantics are defined locally by `CAV2-D56`; `DEF-ARC-SCHEMA` remains Arcanum's public surface and this definition's non-normative ancestor. A classification facet is not ontology membership or promotion. A human-continuation view is not canonical merely because it is readable. A machine-checkable view is not authority and is not proof beyond the named checks it can actually run.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../../../evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/definitions/four-facet-artifact-invariant/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.four-facet-artifact-invariant@1.0.0-candidate.1

**Content fingerprint · SHA-256**

0950ccce0030dbd4fe8eab26ca6955ab0df1acae5e22dbb50a34e3e3a81c7af7

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Use this method before or during any CyberAlchemy v2 action that may matter\nlater: definition work, constitution work, axiom work, discipline work, Craft\nstate changes, ontology projections, task execution, workflow design, system\ndesign, validation, or implementation routing.\n\nThe method lets the system act without pretending the four facets already\nexist. An action may instantiate existing taxonomy, schema, human view, and\nmachine view; create one or more missing facets; or declare typed residue for\nthe missing facets. What is forbidden is a silent action that later relies on an\nunstated kind, shape, human continuation path, or machine-checkable state.",
  "authority_scope_ref": "scope.shared-authority",
  "exclusions": [
    "Admission, activation, publication, release, deployment, and external effects.",
    "Meanings assigned to split or reclassified sibling targets unless explicitly referenced."
  ]
}
````

[Return to this catalog](../definitions.md#catalog-definitions)
