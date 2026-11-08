## CAV2-D22: Orthogonal Classification

Status: active
Term: orthogonal classification
Aliases: orthogonal ontology basis, orthogonal label discipline, retrieval-entropy classification, unique-information classification

### Normative Definition

Orthogonal classification is the CyberAlchemy v2 rule that a governed
classification axis, taxonomy label, or ontology grouping is admissible only
when it contributes a distinction that is not silently redundant with an
existing axis, label, owner lane, lifecycle state, schema field, or typed
relation.

A classification is orthogonal when changing it does not secretly change a
different authority axis. If a proposed classification cannot stay independent,
its dependency must be represented through `CAV2-D16` typed coupling invariant
before it can govern downstream work.

### Formal Interpretation

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

### Operational Interpretation

Use orthogonal classification when adding taxonomy, ontology, status,
confidence, maturity, source-role, node-type, or task-kind labels. The action
must answer what new distinction the classification adds, what existing axes it
could be confused with, and whether any unavoidable dependency is explicitly
typed.

### Plain-Language Intuition

Do not add another label unless it tells the project something new. If the label
depends on another label, name that dependency instead of pretending the labels
are independent.

### Domain-Context Voice

In CyberAlchemy v2, this definition promotes the imported vault's orthogonality
and retrieval-entropy evidence into a project-local classification rule. It
supports ontology work, definition towers, authority lifecycle work, and the
four-facet action method by keeping classification separate from schema,
promotion, confidence, evidence, and implementation state.

### Boundary

Orthogonal classification is not a requirement that every classifier be
statistically proven before exploratory work begins. It is also not isolation:
classifications may interact, but the interaction must be represented through a
typed coupling, schema rule, or explicit residue.

This term does not authorize treating Shannon-style label independence and
Hilbert-style projector orthogonality as the same formal object. Any bridge
between classification independence and contextuality machinery must be
recorded as a separate typed coupling or rejected residue.

The imported house_project label system remains source evidence. CyberAlchemy
v2 may adopt the orthogonality rule without adopting that source's exact node
types, labels, metrics, or status vocabulary.

### Primary Consumers

- [../imports/house_project/docs/vault/ontology-conventions.md](../imports/house_project/docs/vault/ontology-conventions.md)
- [../imports/house_project/docs/vault/axiom/ontology-axioms.md](../imports/house_project/docs/vault/axiom/ontology-axioms.md)
- [../../../.arcanum/inventory/entries/evidence-cards/2026-06-21-house-project-vault-cards.md](../../../.arcanum/inventory/entries/evidence-cards/2026-06-21-house-project-vault-cards.md)
- [source-clusters/primordial.md](source-clusters/primordial.md)
- [DEFINITION-TOWERS.md](DEFINITION-TOWERS.md)
