[Documentation home](../../README.md)

# Classification Orthogonality Invariant

<a id="def-cal-definition-classification-orthogonality-invariant"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Classification Orthogonality Invariant

# Classification Orthogonality Invariant

Requires classification questions to remain distinct, with dependencies stated explicitly. A convenient duplicate label must not become a second source of truth.

**When it applies**

Use orthogonal classification when adding taxonomy, ontology, status, confidence, maturity, source-role, node-type, or task-kind labels. The action must answer what new distinction the classification adds, what existing axes it could be confused with, and whether any unavoidable dependency is explicitly typed.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**A stated exclusion**

Admission, activation, publication, release, deployment, and external effects.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-classification-orthogonality-invariant-section-2"></a>

## Source explanatory wording

Keep classification questions separate, connect dependent answers explicitly, and do not store a convenient duplicate as a new truth.

<a id="def-cal-definition-classification-orthogonality-invariant-section-3"></a>

## Exact governing statement

Classification Orthogonality Invariant is the normalized invariant identified by semantic.classification-orthogonality-invariant, owned within scope.shared-authority, and carried by type.invariant. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D22 without silently merging it with another target.

Target-specific normative meaning:

Classification Orthogonality Invariant requires every canonical classification axis to carry a distinct decision or validation purpose; one axis must not be silently inferred from another, redundant canonical labels must be rejected, dependent classifications must be explicit relations, and convenience labels must remain generated projections.

Bound source-semantic basis:

Orthogonal classification is the CyberAlchemy v2 rule that a governed classification axis, taxonomy label, or ontology grouping is admissible only when it contributes a distinction that is not silently redundant with an existing axis, label, owner lane, lifecycle state, schema field, or typed relation.

A classification is orthogonal when changing it does not secretly change a different authority axis. If a proposed classification cannot stay independent, its dependency must be represented through `CAV2-D16` typed coupling invariant before it can govern downstream work.

````
For a classified artifact `x`, let:

```text
K(x) = (k_1, k_2, ..., k_n)
```

where each `k_i` is an owned classification axis. A proposed axis `k_p` is
admissible when it contributes a unique operational distinction that cannot be
derived from the existing `K(x)`, or when every dependency between `k_p` and an
existing axis is recorded as a typed coupling with direction, owner, evidence,
and effect.

When data exists, an implementation may use mutual-information, entropy, or
retrieval-precision checks as evidence for uniqueness. When data does not
exist, review must name the unique question, routing decision, or validation
effect the classification adds.

In this definition, orthogonality is an admission and compression discipline:
it asks whether a label or axis contributes independent operational
information. It is not Hilbert-space orthogonality, not a contextuality
obstruction, and not a proof that cross-document consistency has been achieved.
Consistency claims must come from typed relations, schema rules, validators, or
owner decisions, not from the word "orthogonal" by itself.
````

- Orthogonal classification is not a requirement that every classifier be statistically proven before exploratory work begins. It is also not isolation: classifications may interact, but the interaction must be represented through a typed coupling, schema rule, or explicit residue. This term does not authorize treating Shannon-style label independence and Hilbert-style projector orthogonality as the same formal object. Any bridge between classification independence and contextuality machinery must be recorded as a separate typed coupling or rejected residue. The imported house_project label system remains source evidence. CyberAlchemy v2 may adopt the orthogonality rule without adopting that source's exact node types, labels, metrics, or status vocabulary.
- This target remains distinct from the sibling targets semantic.classification-axis reconstructed from CAV2-D22; shared source lineage does not merge their identities or validation purposes.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../assets/503e6a257519-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.classification-orthogonality-invariant@1.0.0-candidate.1

**Content fingerprint · SHA-256**

503e6a2575194be2b24d363578b8ab4a92590c88cf1bbeac53065ac4ad16be4a

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Use orthogonal classification when adding taxonomy, ontology, status,\nconfidence, maturity, source-role, node-type, or task-kind labels. The action\nmust answer what new distinction the classification adds, what existing axes it\ncould be confused with, and whether any unavoidable dependency is explicitly\ntyped.",
  "authority_scope_ref": "scope.shared-authority",
  "exclusions": [
    "Admission, activation, publication, release, deployment, and external effects.",
    "Meanings assigned to split or reclassified sibling targets unless explicitly referenced."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
