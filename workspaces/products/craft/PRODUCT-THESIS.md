---
document_id: domainspec-product-thesis/v1
status: canonical
owner: DomainSpec v2 owner
visibility: private
authority_scope: product-positioning
updated_at: 2026-08-29
---

# DomainSpec Product Thesis

## Thesis

Software should not be built from prose, naming conventions, and architectural memory alone.
DomainSpec makes the intended system an explicit typed graph, selects an exact implementation
realization for every supported concept, materializes that realization deterministically, and
compares the resulting project with the selected intent using bounded evidence.

```text
domain intent
  -> typed concepts and relationships
  -> selected architecture profile and exact realizations
  -> deterministic target artifacts
  -> independent observations
  -> non-inflating conformance evidence
  -> an external owner decision
```

The product is the machinery that preserves meaning across this chain. A DomainSpec document,
generated file, validator, receipt, or ontology projection is one part of that machinery; no
single artifact is the product by itself.

## The problem

Teams routinely agree on what a feature means, then lose that agreement while translating it
through architecture, implementation, testing, and release. The loss appears as several familiar
failures:

- the same domain concept is implemented in incompatible shapes;
- relationships exist in diagrams but have no executable consequence;
- generated code resembles the intended architecture without being bound to it;
- tests pass without proving the business obligation they are assumed to cover;
- evidence from one language, tool, or snapshot is stretched into a broader claim; and
- a successful technical check is mistaken for approval to publish, deploy, or release.

The underlying defect is missing continuity between declared meaning and observed reality.

## The product promise

For one exact DomainSpec source, profile, baseline, target snapshot, and toolchain, DomainSpec can
answer five questions without silently substituting one for another:

1. **Meaning:** Which concepts exist and what roles do they play?
2. **Structure:** Which typed relationships between those concepts are allowed?
3. **Realization:** Which exact implementation form was selected for each concept and language?
4. **Observation:** What did the target project actually contain and do at the admitted observation boundary?
5. **Evidence:** Which claims are supported, failed, unsupported, or stale for those exact inputs?

The result is not universal correctness. It is a reproducible, inspectable statement whose claim
cannot be stronger than its sources and observations.

## The product model

DomainSpec has six cooperating layers:

| Layer | Canonical responsibility |
| --- | --- |
| Language | Define meta-types, formation criteria, and typed relationship signatures. |
| Source | Record project-owned concepts, intent, properties, and relationships. |
| Profiles and realizations | Select portable architecture constraints and exact language-specific implementation forms. |
| Instantiation | Produce a contained deterministic artifact plan, publish it atomically, and emit a baseline-bound receipt. |
| Conformance | Observe the generated or existing target independently and compare it with the selected realization. |
| Evidence and decision | Preserve gaps and claim ceilings; leave acceptance, publication, deployment, and release to their explicit owners. |

The canonical vocabulary lives in [`definitions/`](definitions/). This thesis explains why the
parts exist and how they compose; it does not redefine their formal semantics.

## Three separations that must hold

### Meaning, evidence, and decision

The source owns intended domain meaning. Providers and tests produce evidence about exact inputs.
An owner makes the bounded decision. Evidence may support a decision but cannot make itself authoritative.

### Meta-type, realization, and instance

A meta-type defines a semantic role such as Operation or Workflow. A realization selects the exact
language and architecture form for that role. An instance is a project concept materialized using
that selection. Similar names or syntax cannot collapse these three identities.

### Generation, conformance, and release

Generation answers what DomainSpec wrote. Conformance answers whether the observed target matches
the selected contract. Release answers whether an authorized owner permits broader use. Passing one
stage never grants the next stage implicitly.

## Compensation demonstrates the model

Workflow compensation is forward recovery after partial completion. It is not a database rollback,
not time reversal, and not a new meta-type.

- A Workflow records completed steps and emits a recovery intent and ordered plan.
- Every recovery target is an ordinary Operation already connected through
  `Workflow --[orchestrates]--> Operation`.
- A separate executor preflights every exact Operation binding before the first invocation.
- Each Operation retains its own reads, writes, effects, guard, atomic state-and-outbox behavior,
  idempotency, events, and failure continuation.
- Conformance rejects direct Workflow execution, undeclared targets, dependency cycles, missing
  bindings, and substituted Operation identities.

This preserves the central boundary: Workflow owns orchestration; Operation owns state-changing
behavior; the executor owns only exact recovery ordering and invocation.

## What is canonical now

- Thirteen backend meta-types are active.
- Each has one selected TypeScript, Python, and Rust realization: 39 exact realization rows.
- DS-D8 owns the active relationship signatures and endpoint constraints.
- The private CLI can decode supported DomainSpec nodes, select the admitted realization, build and
  publish a deterministic contained plan, emit a receipt, reread the target, and run bounded static
  conformance checks.
- Workflow compensation planning and external execution are implemented across the generated
  TypeScript, Python, and Rust profiles.
- The product ontology records the business, system, and bridge views of this state.

Canonical project-local evidence does not mean the product is published, released, deployed, or
production-ready. Durable compensation dispatch, runtime observation beyond admitted providers,
and a released external installation remain separate frontiers.

## The moat

The durable advantage is not code generation alone. Templates are easy to copy. The moat is the
closed continuity loop:

```text
typed meaning
  + exact realization selection
  + relationship-aware composition
  + deterministic materialization
  + hostile target observation
  + evidence that cannot inflate its own claim
```

This makes architecture a testable product contract instead of a convention that slowly decays.

## Product success criterion

DomainSpec succeeds when a consuming project can declare a supported domain graph, instantiate the
selected realizations in a clean target, reproduce the same artifact and receipt identities, and
obtain independent conformance evidence that either proves the bounded contract or names every
unsupported obligation—without requiring an agent to rediscover the architecture from repository prose.

## Non-goals

DomainSpec does not:

- invent missing business meaning;
- decide that a requirement is desirable or correct;
- replace an application framework or run the application;
- turn static conformance into production behavior proof;
- convert unsupported evidence into PASS;
- publish, deploy, or release by implication; or
- replace the human or system owner responsible for the next effect.

## Canonical anchors

- [`definitions/DEFINITIONS.md`](definitions/DEFINITIONS.md) owns critical term semantics.
- [`definitions/meta-types/meta-types.md`](definitions/meta-types/meta-types.md) owns the human DS-D1 cards.
- [`definitions/relationships/relationships.yml`](definitions/relationships/relationships.yml) owns DS-D8 relationship signatures.
- [`ontology/README.md`](ontology/README.md) navigates the canonical product ontology package.
- [`ARCHITECTURE.md`](ARCHITECTURE.md) explains the complete system structure and current joins.
- [`COMPLETE-GUIDE.md`](COMPLETE-GUIDE.md) teaches the system through worked examples.

Changes to product positioning belong here. Changes to term meaning belong in definitions. Changes
to system structure belong in architecture. Changes to current implementation evidence require a new
immutable baseline and refreshed ontology source bindings.
