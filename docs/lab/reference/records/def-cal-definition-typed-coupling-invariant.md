[Documentation home](../../README.md)

# Typed Coupling Invariant

<a id="def-cal-definition-typed-coupling-invariant"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Typed Coupling Invariant

# Typed Coupling Invariant

Requires a dependency, influence, constraint or co-change between separately governed subjects to be an explicit typed relation with named endpoints, direction, meaning, owner, evidence and validation or promotion effect.

**When it applies**

Use this invariant when orthogonality fails. If maturity affects promotion, schema affects contract, route affects authority, artifact provenance affects trust, or one owner lane constrains another, the relation must be modeled directly instead of left as prose implication, file adjacency, or remembered context.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**A stated exclusion**

Admission, activation, publication, release, deployment, and external effects.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-typed-coupling-invariant-section-2"></a>

## Source explanatory wording

If two things are wired together, draw the wire and label it.

<a id="def-cal-definition-typed-coupling-invariant-section-3"></a>

## Exact governing statement

Typed Coupling Invariant is the normalized invariant identified by semantic.typed-coupling-invariant, owned within scope.shared-authority, and carried by type.invariant. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D16 without silently merging it with another target.

Bound source-semantic basis:

A typed coupling invariant is the CyberAlchemy v2 rule that any dependency, bridge, constraint, influence, or co-change relation between non-orthogonal artifacts, concepts, stages, authorities, or owners must be represented as an explicit typed relation with named endpoints, direction, relation kind, owner, evidence, and validation or promotion effect.

````
semantic.typed-coupling-invariant := (semantic_kind=invariant, carrier=type.invariant, owner_scope=scope.shared-authority, source_set={CAV2-D16}). Identity, carrier, and owner scope are independent axes; equality of labels does not establish equality of concepts.
````

- This invariant does not require every related idea to be coupled. Orthogonal axes should remain separate. It applies only when a decision, validation, promotion, or implementation would rely on one object constraining or changing with another. A typed relation is also not automatic promotion; it is the minimum representation needed before a coupling can be reviewed.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../../../evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/definitions/typed-coupling-invariant/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.typed-coupling-invariant@1.0.0-candidate.1

**Content fingerprint · SHA-256**

2358180b511b4297dfd53c8942125c811b3495c6fd73ce0b59ea7f68309aaaf1

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Use this invariant when orthogonality fails. If maturity affects promotion,\nschema affects contract, route affects authority, artifact provenance affects\ntrust, or one owner lane constrains another, the relation must be modeled\ndirectly instead of left as prose implication, file adjacency, or remembered\ncontext.",
  "authority_scope_ref": "scope.shared-authority",
  "exclusions": [
    "Admission, activation, publication, release, deployment, and external effects.",
    "Meanings assigned to split or reclassified sibling targets unless explicitly referenced."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
