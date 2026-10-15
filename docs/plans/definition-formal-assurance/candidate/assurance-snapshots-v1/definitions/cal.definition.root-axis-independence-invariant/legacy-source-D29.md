## CAV2-D29: Axis Orthogonality Invariant

Status: active
Term: axis orthogonality invariant
Aliases: orthogonality, orthogonal-axis invariant, independent-axis invariant, non-implied progress invariant

### Normative Definition

Axis orthogonality invariant is the CyberAlchemy v2 rule that two
authority-bearing dimensions, roles, states, owner lanes, schema or instance
axes, validation concerns, or artifact properties are treated as independently
variable unless an explicit typed relation, gate, schema rule, validator, or
owner decision relates them.

Advancing one axis must not silently advance, validate, authorize, satisfy, or
rewrite another axis. If a decision depends on such co-change, the dependency
must be represented through `CAV2-D16` typed coupling invariant before it can
govern work.

### Formal Interpretation

For a governed context `C`, let:

```text
A(C) = {a_1, a_2, ..., a_n}
```

be the declared axes that matter to a decision. Axes `a_i` and `a_j` are
orthogonal for decision `d` when a valid move on `a_i` does not imply a move on
`a_j` unless there is an explicit bridge:

```text
move(a_i) does not imply move(a_j) unless R_ij is declared
```

where `R_ij` is a typed coupling, gate, schema rule, validator, or owner
decision with named endpoints, direction or symmetry, evidence, and effect.

### Operational Interpretation

Use this invariant before merging or ordering concepts such as maturity and
promotion, evidence confidence and owner commitment, schema residue and
instance residue, role and lane, source evidence and local canon, built status
and authority status, or workflow state and lifecycle status.

When the question is whether a new label or classifier adds independent
information, use `CAV2-D22` orthogonal classification. When the question is
which authority lifecycle component changed, use `CAV2-D23` authority lifecycle
axis. When the axes are not independent, use `CAV2-D16` typed coupling
invariant.

### Plain-Language Intuition

Moving one slider should not secretly move another slider. If it does, name the
wire between them.

### Domain-Context Voice

In CyberAlchemy v2, axis orthogonality is the broader primordial invariant behind
several already promoted local rules. `CAV2-D22` specializes it for
classification admission, `CAV2-D23` applies it to authority lifecycle posture,
and `CAV2-D16` handles the cases where independence fails. It lets the v2 base
separate ontology from authority movement, schema from instance evidence,
promotion from maturity, and source truth from local adoption without pretending
those axes cannot interact.

### Boundary

Axis orthogonality is not isolation, not statistical independence unless a data
model explicitly says so, not Hilbert-space or projector orthogonality, not a
contextuality theorem, and not a consistency guarantee. It is a governance
invariant about non-implied movement between axes. Interactions are allowed, but
they must be explicit.

### Primary Consumers

- [source-clusters/primordial.md](source-clusters/primordial.md)
- [DEFINITION-TOWERS.md](DEFINITION-TOWERS.md)
- [../../CRAFT.md](../../CRAFT.md)
- [../../TO-VLAD/TO-VLAD.md](../../TO-VLAD/TO-VLAD.md)
- [../../../.arcanum/inventory/entries/evidence-cards/2026-06-22-presheaf-vect-novelty-orthogonality-cards.md](../../../.arcanum/inventory/entries/evidence-cards/2026-06-22-presheaf-vect-novelty-orthogonality-cards.md)
