<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Schema

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.schema`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope.shared-authority`
- Lifecycle posture reference: `candidate:artifact-reconstruction-l1/v1`

## Scientific/formal voice

Schema is the normalized definition identified by semantic.schema, owned within scope.shared-authority, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D56 without silently merging it with another target.

Bound source-semantic basis:

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

```text
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
```

### Notation

| Symbol | Meaning |
| --- | --- |
| semantic.schema | Stable normalized identity for Schema. |
| CAV2-D56 | Bound CyberAlchemy-v2 source-definition identity. |

### Boundary conditions

- A schema is **not a law**: an axiom (`CAV2-D53`) and an invariant (`CAV2-D54`) are
separate kinds. A schema may rule on *form*; it can never state what must be
**true** of the world or of the system's behavior. A schema is not authority
(`CAV2-D34`), not promotion (`CAV2-D48`), and not execution proof. It is not a
**contract**: a contract says what the structure *means*, who owns it, and what it
proves — the schema says only what it must look like. It is not the
**classification facet** (`CAV2-D22`): naming a kind is not declaring its shape. It
is not a `CAV2-D31` primitive type, and not a DomainSpec `DS-D1` meta-type — those
are kinds *within* a schema, not the schema itself.

### Testable conditions

- The candidate identity remains cal.definition.schema.
- Every selected source-section digest remains current.
- The machine record validates against Definition/v1.
- The human projection is regenerated exactly from the machine record.

## Plain-language voice

The form the evidence must fit. A schema says what kinds of thing there may be,
what may go inside them, and how they may be wired together — and nothing at all
about whether any of it is true, owned, or approved.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

In CyberAlchemy-lab migration work, Schema is a prototype meaning reconstructed from CAL-NORMALIZE-01. It remains non-authoritative until the correct Lab owner admits a fully validated candidate.

Source context retained for reconstruction:

In CyberAlchemy v2, schema is the **schema facet** of `CAV2-D21` four-facet action
method — the structural shape a governed action must bind, create, or carry as
typed residue. Its *change* is governed by `CAV2-D25` schema amendment witness;
that definition governs amendment, this one governs content. It is the shape layer
*beneath* the `axiom -> invariant -> constitution -> validator` chain: a validator
may **use** a schema to check an invariant (`CAV2-D54`), but the schema is not the
invariant. Across the umbrella it is instantiated by DomainSpec's per-meta-type
formal criterion (the `C` part) and edge-participation signature (the `N` part),
and by Arcanum's dispatch, ledger, and frontmatter schemas.

### Examples

- Resolve semantic.schema by its machine identity rather than its directory name.
- Challenge source drift through the L1 drift audit before relying on Schema.

## Applicability

Use "schema" when asking whether an artifact, record, ledger row, ontology node,
event, or route has the **required form**. Three tests:

1. Can a machine decide conformance by *looking*? If deciding requires running the
   thing, populating it, or reading it for meaning, it is not schema — it is
   validator, execution, or interpretation.
2. Does a pass confer any authority? If it appears to, the coupling is untyped and
   must be typed (`CAV2-D16`) — shape never promotes.
3. Is the rule about **one occupant** or about **how occupants connect**? Those are
   different parts (`C` vs `N`); do not merge them.

### Exclusions

- Admission, activation, publication, release, deployment, and external effects.
- Meanings assigned to split or reclassified sibling targets unless explicitly referenced.

## Boundaries

- A schema is **not a law**: an axiom (`CAV2-D53`) and an invariant (`CAV2-D54`) are
separate kinds. A schema may rule on *form*; it can never state what must be
**true** of the world or of the system's behavior. A schema is not authority
(`CAV2-D34`), not promotion (`CAV2-D48`), and not execution proof. It is not a
**contract**: a contract says what the structure *means*, who owns it, and what it
proves — the schema says only what it must look like. It is not the
**classification facet** (`CAV2-D22`): naming a kind is not declaring its shape. It
is not a `CAV2-D31` primitive type, and not a DomainSpec `DS-D1` meta-type — those
are kinds *within* a schema, not the schema itself.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cyberalchemy-v2:CAV2-D56 | ## CAV2-D56: Schema | `91f9047e98b7706d11f8baf6e0f919f485f2015f19444a96793da7612451f498` | `candidate-unadmitted` |

## Primary consumers

- semantic.four-facet-artifact-invariant
- semantic.schema-evolution-invariant

## Lookup and drift

- Index: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/registry.json` / `cal.definition.schema@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/drift-audit.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.originates-from | cal.definition.schema | cyberalchemy-v2:CAV2-D56 | role:definition-owner |

## Evidence

- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0003-review-led-reconstruction/target-candidates/semantic/semantic-schema/v1/artifact.json
- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/receipts/validation.json
- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/receipts/validation.json

## Residue

- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/drift-audit.json

## Claim ceiling

Candidate Definition reconstructed from an accepted normalization scaffold and exact CyberAlchemy-v2 source sections. It is not admitted and grants no implementation, migration, registry, publication, release, deployment, or external-effect authority.
