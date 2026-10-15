[Documentation home](../../README.md)

# Schema

<a id="def-cal-definition-schema"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Schema

# Schema

Specifies permitted structure, fields, constraints and connections. Structural validity does not establish truth, ownership, permission or acceptance.

**When it applies**

Use "schema" when asking whether an artifact, record, ledger row, ontology node, event, or route has the **required form**. Three tests:

**Record formats**

[Schema · v1](type-cal-artifact-type-schema-v1.md#type-cal-artifact-type-schema-v1)

**A stated exclusion**

Admission, activation, publication, release, deployment, and external effects.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-schema-section-2"></a>

## Source explanatory wording

The form the evidence must fit. A schema says what kinds of thing there may be, what may go inside them, and how they may be wired together — and nothing at all about whether any of it is true, owned, or approved.

<a id="def-cal-definition-schema-section-3"></a>

## Exact governing statement

Schema is the normalized definition identified by semantic.schema, owned within scope.shared-authority, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D56 without silently merging it with another target.

Bound source-semantic basis:

A schema is an explicit declaration of **admissible structure**. It names four things:

- **kinds** — the sorts of thing that may occur; - **constraints** — what may occupy a kind: a decidable predicate over a *single* occupant's structure; - **relations** — the connections that may hold *between* kinds; - **connection rules** — how those relations may be formed: which kinds they may connect, with what multiplicity, and which composite paths must agree.

Constraints and connection rules are **separate parts and do not reduce to one another**: a constraint on allowed values says nothing about how two kinds may relate, and a rule on relating says nothing about what may fill a slot.

A schema is stated **independently of any particular occupant**, so that conformance is decidable **by inspection alone** — without executing the thing, populating it, or interpreting what it means. Conformance is therefore **shape evidence**, and never by itself authority: a schema-valid artifact has proved its form, not its truth, its ownership, or its promotion.

````
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
````

- A schema is **not a law**: an axiom (`CAV2-D53`) and an invariant (`CAV2-D54`) are separate kinds. A schema may rule on *form*; it can never state what must be **true** of the world or of the system's behavior. A schema is not authority (`CAV2-D34`), not promotion (`CAV2-D48`), and not execution proof. It is not a **contract**: a contract says what the structure *means*, who owns it, and what it proves — the schema says only what it must look like. It is not the **classification facet** (`CAV2-D22`): naming a kind is not declaring its shape. It is not a `CAV2-D31` primitive type, and not a DomainSpec `DS-D1` meta-type — those are kinds *within* a schema, not the schema itself.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../../../evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/definitions/schema/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.schema@1.0.0-candidate.1

**Content fingerprint · SHA-256**

51112f146abdea8b4ea5cf11f200392ca7e67cc1b77589e185855be33597787d

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Use \"schema\" when asking whether an artifact, record, ledger row, ontology node,\nevent, or route has the **required form**. Three tests:\n\n1. Can a machine decide conformance by *looking*? If deciding requires running the\n   thing, populating it, or reading it for meaning, it is not schema — it is\n   validator, execution, or interpretation.\n2. Does a pass confer any authority? If it appears to, the coupling is untyped and\n   must be typed (`CAV2-D16`) — shape never promotes.\n3. Is the rule about **one occupant** or about **how occupants connect**? Those are\n   different parts (`C` vs `N`); do not merge them.",
  "authority_scope_ref": "scope.shared-authority",
  "exclusions": [
    "Admission, activation, publication, release, deployment, and external effects.",
    "Meanings assigned to split or reclassified sibling targets unless explicitly referenced."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
