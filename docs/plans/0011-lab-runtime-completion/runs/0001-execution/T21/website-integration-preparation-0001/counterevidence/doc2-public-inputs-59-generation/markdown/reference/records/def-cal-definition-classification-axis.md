[Documentation home](../../README.md)

# Classification Axis

<a id="def-cal-definition-classification-axis"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Classification Axis

# Classification Axis

One declared question used to classify something, such as its kind or lifecycle state. Its answers have a distinct decision or checking purpose.

**When it applies**

Use orthogonal classification when adding taxonomy, ontology, status, confidence, maturity, source-role, node-type, or task-kind labels. The action must answer what new distinction the classification adds, what existing axes it could be confused with, and whether any unavoidable dependency is explicitly typed.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**A stated exclusion**

Admission, activation, publication, release, deployment, and external effects.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-classification-axis-section-2"></a>

## Source explanatory wording

It is one question in a classification, such as what something means or what lifecycle state it has.

<a id="def-cal-definition-classification-axis-section-3"></a>

## Exact governing statement

Classification Axis is the normalized definition identified by semantic.classification-axis, owned within scope.shared-authority, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D22 without silently merging it with another target.

Target-specific normative meaning:

A Classification Axis is one explicitly named, independently valued dimension used to classify an artifact or concept for a distinct decision or validation purpose.

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
- This target remains distinct from the sibling targets semantic.classification-orthogonality-invariant reconstructed from CAV2-D22; shared source lineage does not merge their identities or validation purposes.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../assets/ae1bda239759-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.classification-axis@1.0.0-candidate.1

**Content fingerprint · SHA-256**

ae1bda23975956b56b93d05667071d026feb11b55388346747e4b3d7ef7dce05

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
