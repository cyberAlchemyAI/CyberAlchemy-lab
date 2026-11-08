## CAV2-D16: Typed Coupling Invariant

Status: active
Term: typed coupling invariant
Aliases: explicit coupling invariant, typed coupling rule, explicit typed relation rule, non-orthogonality explicitness rule

### Normative Definition

A typed coupling invariant is the CyberAlchemy v2 rule that any dependency,
bridge, constraint, influence, or co-change relation between non-orthogonal
artifacts, concepts, stages, authorities, or owners must be represented as an
explicit typed relation with named endpoints, direction, relation kind, owner,
evidence, and validation or promotion effect.

### Invariant Statement

For any two local objects `A` and `B`, if `A` and `B` cannot vary independently
for the decision being made, then CyberAlchemy v2 must record a typed relation
`R(A, B)` before the coupling can influence authority, routing, validation, or
implementation.

At minimum, `R(A, B)` records:

- source endpoint
- target endpoint
- relation type
- direction or symmetry
- owner route
- evidence reference
- validation, promotion, or blocking effect

If the relation cannot yet be typed, the coupling remains an open question,
residue, blocker, or candidate note rather than a hidden assumption.

### Operational Interpretation

Use this invariant when orthogonality fails. If maturity affects promotion,
schema affects contract, route affects authority, artifact provenance affects
trust, or one owner lane constrains another, the relation must be modeled
directly instead of left as prose implication, file adjacency, or remembered
context.

### Plain-Language Intuition

If two things are wired together, draw the wire and label it.

### Domain-Context Voice

In CyberAlchemy v2, this term sits above the definition towers as a primordial
rule. It explains why framework-unification separates axes, why DomainSpec
requires typed relationships, why provenance cannot live only in memory, and
why non-orthogonal links such as maturity-to-promotion, schema-to-contract, or
source-to-authority must be explicit before they can govern work.

### Boundary

This invariant does not require every related idea to be coupled. Orthogonal
axes should remain separate. It applies only when a decision, validation,
promotion, or implementation would rely on one object constraining or changing
with another. A typed relation is also not automatic promotion; it is the
minimum representation needed before a coupling can be reviewed.

### Primary Consumers

- [DEFINITION-TOWERS.md](DEFINITION-TOWERS.md)
- [source-clusters/primordial.md](source-clusters/primordial.md)
- [../../CRAFT.md](../../CRAFT.md)
