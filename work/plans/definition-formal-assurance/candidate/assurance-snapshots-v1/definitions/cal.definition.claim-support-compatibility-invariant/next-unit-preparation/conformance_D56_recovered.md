## CAV2-D56: Schema

Status: active
Term: schema
Aliases: structural declaration, admissible-structure declaration, shape declaration, schema facet
Promoted: 2026-07-13 (design session; four-part decomposition kinds/constraints/relations/connection-rules, coverage-tested against dispatch YAML, Spivak category, DomainSpec meta-type, and relational table)
Ancestral provenance (non-normative): generic descendant of `DEF-ARC-SCHEMA` ([`arcanum/definitions/DEFINITIONS.md`](../../../arcanum/definitions/DEFINITIONS.md)). Arcanum retains that ID as its public surface; this definition re-authors the local semantic role for the v2 spine.

### Normative Definition

A schema is an explicit declaration of **admissible structure**. It names four
things:

- **kinds** — the sorts of thing that may occur;
- **constraints** — what may occupy a kind: a decidable predicate over a *single*
  occupant's structure;
- **relations** — the connections that may hold *between* kinds;
- **connection rules** — how those relations may be formed: which kinds they may
  connect, with what multiplicity, and which composite paths must agree.

Constraints and connection rules are **separate parts and do not reduce to one
another**: a constraint on allowed values says nothing about how two kinds may
relate, and a rule on relating says nothing about what may fill a slot.

A schema is stated **independently of any particular occupant**, so that
conformance is decidable **by inspection alone** — without executing the thing,
populating it, or interpreting what it means. Conformance is therefore **shape
evidence**, and never by itself authority: a schema-valid artifact has proved its
form, not its truth, its ownership, or its promotion.

### Formal Interpretation

```text
schema S = (K, C, R, N)
  K = kinds              the sorts of thing that may occur
  C = constraints        C_k : occupant -> Bool     decidable, per kind k in K
  R = relations          r : k -> k'                k, k' in K
  N = connection rules   endpoint typing + multiplicity + path equations
                         (which r may connect which k; how many; which composites agree)

conforms(x, S)   decidable by inspection of x against S
                 -- no execution of x, no population of x, no interpretation of x

conforms(x, S)  =/=>  authoritative(x)   (CAV2-D34)
conforms(x, S)  =/=>  promoted(x)        (CAV2-D48)
conforms(x, S)  =/=>  true(x)            (CAV2-D53 / CAV2-D54)
```

The parts are independent. A schema may carry connection rules and no constraints
(a bare category of kinds and arrows holds no values); or constraints and no
relations (a single record type). `C` and `N` are orthogonal (`CAV2-D29`).

A schema is **relative to a level**: it constrains the level below it, and may
itself conform to a schema above it. Every use must declare *relative to which
level* it is the schema — a kind that is an occupant at one level is a schema at
the next.

### Operational Interpretation

Use "schema" when asking whether an artifact, record, ledger row, ontology node,
event, or route has the **required form**. Three tests:

1. Can a machine decide conformance by *looking*? If deciding requires running the
   thing, populating it, or reading it for meaning, it is not schema — it is
   validator, execution, or interpretation.
2. Does a pass confer any authority? If it appears to, the coupling is untyped and
   must be typed (`CAV2-D16`) — shape never promotes.
3. Is the rule about **one occupant** or about **how occupants connect**? Those are
   different parts (`C` vs `N`); do not merge them.

### Plain-Language Intuition

The form the evidence must fit. A schema says what kinds of thing there may be,
what may go inside them, and how they may be wired together — and nothing at all
about whether any of it is true, owned, or approved.

### Domain-Context Voice

In CyberAlchemy v2, schema is the **schema facet** of `CAV2-D21` four-facet action
method — the structural shape a governed action must bind, create, or carry as
typed residue. Its *change* is governed by `CAV2-D25` schema amendment witness;
that definition governs amendment, this one governs content. It is the shape layer
*beneath* the `axiom -> invariant -> constitution -> validator` chain: a validator
may **use** a schema to check an invariant (`CAV2-D54`), but the schema is not the
invariant. Across the umbrella it is instantiated by DomainSpec's per-meta-type
formal criterion (the `C` part) and edge-participation signature (the `N` part),
and by Arcanum's dispatch, ledger, and frontmatter schemas.

### Boundary

A schema is **not a law**: an axiom (`CAV2-D53`) and an invariant (`CAV2-D54`) are
separate kinds. A schema may rule on *form*; it can never state what must be
**true** of the world or of the system's behavior. A schema is not authority
(`CAV2-D34`), not promotion (`CAV2-D48`), and not execution proof. It is not a
**contract**: a contract says what the structure *means*, who owns it, and what it
proves — the schema says only what it must look like. It is not the
**classification facet** (`CAV2-D22`): naming a kind is not declaring its shape. It
is not a `CAV2-D31` primitive type, and not a DomainSpec `DS-D1` meta-type — those
are kinds *within* a schema, not the schema itself.

### Primary Consumers

- [#cav2-d21-four-facet-action-method](#cav2-d21-four-facet-action-method)
- [#cav2-d25-schema-amendment-witness](#cav2-d25-schema-amendment-witness)
- [DEFINITION-SCHEMAS.md](DEFINITION-SCHEMAS.md)
- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- Ontology node schemas, inventory entry schemas, event catalogs, ledger row identity

