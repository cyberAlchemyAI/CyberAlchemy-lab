---
node_type: decision
is_session: false
status: pass
boundary: INTERNAL — DomainSpec v2 modeling responsibility and DS-D8 creates authority
created: 2026-07-22
decision_id: DEC-DSV2-CANONICAL-CREATION-RESPONSIBILITY
target_scope: canonical semantic responsibility, creates authorship, and creates concept cardinality
supersedes: DEC-DSV2-OPERATION-CREATES-ENTITY in part
source: operator choices 1=edge, 2=no, 3=no and confirmed governance package, 2026-07-22
---

# Decision: Canonical creation responsibility

## Consequential work

The initial `creates` admission represented one creation proposition twice: as
an authored edge and as an authored `creation_targets` source attribute. It also
declared `many_to_many` concept connectivity without a plural witness or an
executable cardinality check. The model-orthogonality review showed that
consistency checking did not remove the duplicated authorship.

This decision retains `creates` as a first-class relationship while selecting a
single canonical representation and a unique responsibility owner.

## Owner selections

1. The `creates` edge is the canonical authored creation proposition.
2. An Entity concept may not have more than one incoming `creates` Operation.
3. An Operation concept may not have more than one outgoing `creates` Entity.
4. The resulting graph relation is partial one-to-one: maximum degree one on
   both sides, with no requirement that every Operation or Entity participate.
5. `creation_targets` remains available only as a generated projection derived
   from the canonical edge.

## Governing principle

The owner selected the DomainSpec-local **Canonical Single Responsibility
Principle** (`domainspec-v2-D27`):

> One element owns one primary responsibility; one responsibility has one
> canonical owner; one fact is authored once.

This principle specializes the established software-engineering Single
Responsibility Principle with DomainSpec authority-exclusivity and
single-authorship constraints. Classical SRP alone is not claimed to prove
graph cardinality.

## DS-D8 binding

```text
creates subset_of Operation x Entity

for every Operation O:
  outgoing_creates_targets(O) <= 1

for every Entity E:
  incoming_creates_sources(E) <= 1

creation_targets(O) = sorted(outgoing_creates_targets(O))
  [generated; authored source declarations forbidden]
```

The signature remains same-feature. Update, upsert, read, Event production,
generic persistence, and cross-feature write/projection remain excluded.

## Application examples

Accepted canonical creation:

```text
CreatePlayer --[creates]--> Player
```

Accepted independent relationships around the same responsibility:

```text
CanCreatePlayer --[enforces]--> CreatePlayer
CreatePlayer    --[produces]--> PlayerCreated
FindPlayer      --[queries]---> Player
```

Rejected competing creation owner:

```text
CreatePlayer   --[creates]--> Player
RegisterPlayer --[creates]--> Player
```

Rejected mixed creation responsibility:

```text
CreatePlayer --[creates]--> Player
CreatePlayer --[creates]--> Team
```

Generated, not authored:

```text
CreatePlayer.creation_targets = [Player]
```

One Operation concept may be executed repeatedly and create many runtime Entity
instances. That runtime multiplicity does not change graph concept cardinality.

## Supersession

This decision supersedes only the following clauses of
`DEC-DSV2-OPERATION-CREATES-ENTITY`:

- the independently authored source-effect proof contract;
- the edge/effect biconditional;
- `many_to_many` multiplicity; and
- validators and fixtures whose purpose was to compare two authored creation
  representations.

It preserves the distinct `creates` verb, Operation-to-Entity endpoint types,
same-feature scope, runtime-instance boundary, and separation from
`produces-for` and `produces`.

## Validation and promotion contract

Promotion requires:

1. synchronized D27, DS-D8, relationship registry, human companion, and indexes;
2. rejection of authored `creation_targets` in canonical source surfaces;
3. rejection of multiple outgoing `creates` targets per Operation;
4. rejection of multiple incoming `creates` sources per Entity;
5. deterministic generation of `creation_targets` from the edge;
6. positive and negative Markdown and minted-project fixtures; and
7. passing definition, relationship, content, type, compiler, and generation
   checks.

## Validation evidence

- Definitions Governance: **PASS** — D27 has formal, plain-language,
  domain-context, boundary, challenge, confirmation, and application voices;
  D26 is retained as a superseded stable ID.
- Relationship authority: **PASS** — 31 active signatures; `creates` is
  `one_to_one`, same-feature, edge-canonical, and carries a generated source
  projection contract.
- Relationship/content validation: **PASS** — 5 feature specs, 37 concepts,
  and 34 edges; authored projection and both cardinality violations fail.
- Minted compiler: **PASS** — source `creation_targets` is rejected, generated
  output derives the exact target, and both source/target degree mutants fail.
- Deterministic generation: **PASS** — Create Player regenerated with 17 nodes,
  20 edges, and no orphan required concepts.
- Tooling: **PASS** — TypeScript and 159/159 tooling tests.
- Engine: **PASS** — 107/107 tests.
- Concept Registry: **PASS** — 37 concepts, 34 edges, zero duplicate IDs, and
  zero type drift.

There is no remaining promotion blocker for this decision. Runtime evidence
that implementations create the declared Entity instances remains a separate
conformance concern and is not implied by graph validation.

## Source evidence

- `projects/domainspec-v2/development/research/2026-07-22-model-orthogonality-specialization/findings.md`
- `projects/domainspec-v2/development/research/2026-07-22-model-orthogonality-specialization/research.md`
- `projects/domainspec-v2/definitions/DEFINITIONS.md#domainspec-v2-d27`
- `projects/domainspec-v2/definitions/relationships/relationships.yml`
- Operator choices `1 edge`, `2 no`, `3 no`, followed by `confirmed`, on 2026-07-22.
