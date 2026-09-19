# CyberAlchemy v2 Definitions

Status: active local source
Owner: definitions-governance
Canonical source: `authority/definitions/DEFINITIONS.md`
Lookup index: `authority/definitions/DEFINITIONS-INDEX.md`

## Authority Rule

Only this file defines normative semantics for CyberAlchemy v2 terms it
contains. Downstream artifacts may explain, apply, or reference these terms, but
should not redefine them as project authority.

Arcanum-wide terms remain owned by [../../arcanum/definitions/DEFINITIONS.md](../../../arcanum/definitions/DEFINITIONS.md).
CyberAlchemy v2 definitions are local until a later promotion route says
otherwise.

## CAV2-D1: Stable Repository

Status: active
Term: stable repository
Aliases: stable repo, next stable repository, base repository, downloadable base repository

### Normative Definition

A stable repository is a maintainable repository surface whose authority,
source evidence, promoted contracts, validation evidence, implementation work,
and operating traces can be understood without hidden conversation context, and
whose exported base can support downstream construction without requiring users
to rediscover or re-promote its foundation.

### Operational Interpretation

Use this term when deciding whether CyberAlchemy v2 is ready to move from a
project folder inside `domainspec-core` into its own repository. The repository
is not stable merely because files exist; it is stable when its authority model,
source spine, promotion gates, and validation surfaces are navigable and
reviewable. When CyberAlchemy v2 is extracted, the stable repository objective
is that a user can download CyberAlchemy as this governed base and build project
or domain towers above it.

### Plain-Language Intuition

A stable repository is the trustworthy base someone can download, understand,
and build on without guessing what counts.

### Domain-Context Voice

In CyberAlchemy v2, this term names the target state for extracting this project
from the private `domainspec-core` umbrella into a repository with its own
authority imports, definitions, constitutions, validation, and operating trace.
That extracted repository is intended to become the next owner of the
CyberAlchemy base authority: it should preserve what has been settled here and
leave clear construction surfaces for downstream users to extend above the base.

### Boundary

This term does not mean finished product, public repository, automatic ownership
of every historical CyberAlchemy source, or implementation complete. Standalone
extraction and any transfer of authority from older source spaces remain
promotion decisions.

### Primary Consumers

- [../../README.md](../../README.md)
- [../promotion-policy.md](../promotion-policy.md)
- [../../development/constitution-pack.md](../../development/constitution-pack.md)

## CAV2-D2: Source-Ledgered Amalgamation

Status: active
Term: source-ledgered amalgamation
Aliases: governed amalgamation, source-ledgered consolidation

### Normative Definition

Source-ledgered amalgamation is the practice of consolidating dispersed work by
recording source cohorts, authority posture, and promotion routes instead of
copying every source into one folder or treating synthesis as authority.

### Operational Interpretation

Use this term when CyberAlchemy v2 gathers material from inventory,
ontology-vault, CyberAlchemy, Arcanum, framework-unification, DomainSpec, and
validation sources. The consolidation should preserve source links, evidence
confidence, commitment confidence, and owner routes.

### Plain-Language Intuition

It is an amalgamation with receipts.

### Domain-Context Voice

In CyberAlchemy v2, this term describes the move from scattered source systems
into import manifests, source maps, candidate ontology, and later promoted
authority without flattening the original source ownership.

### Boundary

This term does not authorize private-to-public conversion, global term
promotion, or implementation mutation.

### Primary Consumers

- [../../SOURCE-MAP.md](../../SOURCE-MAP.md)
- [../../disciplines/cards/stable-repository-stewardship.md](../../disciplines/cards/stable-repository-stewardship.md)
- [../constitutions/STABLE-REPOSITORY-CONSTITUTION.md](../constitutions/STABLE-REPOSITORY-CONSTITUTION.md)

## CAV2-D3: Authority Layer

Status: active
Term: authority layer
Aliases: local authority surface, authority surface

### Normative Definition

An authority layer is a project-local surface that is allowed to define
normative meaning, structural rules, promotion decisions, or contracts for a
specific scope.

### Operational Interpretation

Use authority layers to prevent research, inventory, ontology, observability,
memory, generated projections, and implementation evidence from silently
rewriting definitions or rules.

### Plain-Language Intuition

An authority layer says which document is allowed to count.

### Domain-Context Voice

In CyberAlchemy v2, the authority layers are currently
`authority/definitions/`, `authority/constitutions/`, `disciplines/`,
`authority/decisions/`, and later promoted `specs/`.

### Boundary

An authority layer can cite evidence, but evidence does not become authority
unless the responsible owner promotes it.

### Primary Consumers

- [../README.md](../README.md)
- [../boundaries.md](../boundaries.md)
- [../promotion-policy.md](../promotion-policy.md)

## CAV2-D4: Source Spine

Status: active
Term: source spine
Aliases: first source spine, bootstrap source spine

### Normative Definition

A source spine is the selected, minimal set of source cohorts used to orient a
project phase, with each cohort assigned a role and authority posture.

### Operational Interpretation

Use the source spine to decide where an agent should look first and what it may
infer from each source. A source spine narrows search without pretending that
excluded sources are irrelevant forever.

### Plain-Language Intuition

It is the starting bibliography with boundaries attached.

### Domain-Context Voice

In CyberAlchemy v2, the source spine is smaller than the import corpus. It helps
orientation, while [../imports/](../imports/README.md) stages the broader
definition and constitution source set.

### Boundary

A source spine is not a full inventory, complete literature review, or final
architecture decision.

### Primary Consumers

- [../../SOURCE-MAP.md](../../SOURCE-MAP.md)
- [../../research/README.md](../../research/README.md)

## CAV2-D5: Promotion Gate

Status: active
Term: promotion gate
Aliases: owner gate, authority gate

### Normative Definition

A promotion gate is an explicit owner route that decides whether evidence,
candidate meaning, a recurring practice, or a structural rule may become local
authority, implementation work, or standalone repository material.

### Operational Interpretation

Use a promotion gate whenever a claim would cross from source evidence,
inventory, ontology, research, observability, or memory into definitions,
constitutions, specs, capabilities, implementation, or public-facing material.

### Plain-Language Intuition

A promotion gate is the moment the project asks, "is this allowed to count now?"

### Domain-Context Voice

In CyberAlchemy v2, promotion gates decide when imported definitions,
constitutions, ontology candidates, inventory cards, research findings, or
validation evidence become local authority or implementation work.

### Boundary

The gate may return pass, flag, or block. A flag is not a silent pass; it carries
named risk and follow-up.

### Primary Consumers

- [../promotion-policy.md](../promotion-policy.md)
- [../constitutions/STABLE-REPOSITORY-CONSTITUTION.md](../constitutions/STABLE-REPOSITORY-CONSTITUTION.md)

## CAV2-D6: Stable Repository Stewardship

Status: active
Term: stable repository stewardship
Aliases: repository stewardship, stewardship discipline

### Normative Definition

Stable repository stewardship is the recurring practice of keeping a repository
surface source-ledgered, authority-bounded, navigable, validated, and ready for
future extraction or maintenance.

### Operational Interpretation

Use this term for the project-local discipline that keeps CyberAlchemy v2 from
becoming another pile of true but unowned documents.

### Plain-Language Intuition

It is the habit that keeps the repo understandable after the exciting part.

### Domain-Context Voice

In CyberAlchemy v2, stable repository stewardship now includes maintaining the
authority import ledgers, not only maintaining the skeleton folders created in
the first pass.

### Boundary

The discipline recommends hardening routes. It does not promote definitions,
constitutions, specs, ontology, or implementation by itself.

### Primary Consumers

- [../../disciplines/DISCIPLINES.md](../../disciplines/DISCIPLINES.md)
- [../../disciplines/cards/stable-repository-stewardship.md](../../disciplines/cards/stable-repository-stewardship.md)

## CAV2-D7: Authority Import

Status: active
Term: authority import
Aliases: authority import ledger, import ledger

### Normative Definition

An authority import is a staged capture of source paths that may contain
definitions, constitutions, axioms, rules, or other authority-bearing material,
with enough classification to preserve source posture and route later promotion.

### Operational Interpretation

Use authority imports before consolidating scattered repository vocabulary or
rules into CyberAlchemy v2. The import records what exists and where it lives
without copying authority into the local canonical source.

### Plain-Language Intuition

An authority import is a shelf of candidates with labels.

### Domain-Context Voice

In CyberAlchemy v2, authority imports live under [../imports/](../imports/README.md)
and currently stage 149 definition-like candidates plus 106 constitution/axiom
candidates from the broader `domainspec-core` checkout.

### Boundary

An authority import is not promotion. It does not make a source term or rule
canonical for CyberAlchemy v2.

### Primary Consumers

- [../imports/README.md](../imports/README.md)
- [../imports/definitions/MANIFEST.md](../imports/definitions/MANIFEST.md)
- [../imports/constitutions/MANIFEST.md](../imports/constitutions/MANIFEST.md)

## CAV2-D8: Import Candidate

Status: active
Term: import candidate
Aliases: staged candidate, authority candidate

### Normative Definition

An import candidate is a source path captured by an authority import that may
contain a locally owned definition, rule, method, specification, architecture
pattern, or other reusable knowledge, together with evidence such as tests,
observations, examples, or formal proofs, but has not been promoted into
CyberAlchemy v2 authority.

### Operational Interpretation

Use import candidates as the first review queue for scattered definitions and
constitutions. Classify their source family, authority posture, reuse value,
conflicts, and promotion owner before extracting content.

When the source belongs to an independently owned domain, bind its exact owner,
version, local authority posture, and proposed CAV2 abstraction before
extracting anything. Importing the path records a candidate for review; it does
not adopt the source or transfer its meaning to CAV2.

### Plain-Language Intuition

A domain's reusable idea can enter CAV2 review without surrendering its local
meaning or authority.

### Domain-Context Voice

In CyberAlchemy v2, import candidates are recorded in the definition and
constitution manifests. They should be clustered and deduplicated before any
new canonical term or constitution rule is added. Domain packages and local
proof or validation methods proposed for wider reuse enter through the same
candidate posture.

### Boundary

An import candidate may be source-of-truth for its original project while still
remaining candidate-only for CyberAlchemy v2. Capture by CAV2 transfers neither
the source owner's semantic authority nor its lifecycle decisions.

### Primary Consumers

- [../imports/definitions/MANIFEST.md](../imports/definitions/MANIFEST.md)
- [../imports/constitutions/MANIFEST.md](../imports/constitutions/MANIFEST.md)
- [../promotion-policy.md](../promotion-policy.md)

## CAV2-D9: CyberAlchemy v2

Status: active
Term: CyberAlchemy v2
Aliases: CyberAlchemy stable repository candidate, v2 consolidation surface, CyberAlchemy base repository, CyberAlchemy base

### Normative Definition

CyberAlchemy v2 is the project-local stable repository candidate that organizes
the dispersed CyberAlchemy, Arcanum, DomainSpec, inventory, ontology, research,
validation, and operations material into source-ledgered authority layers,
candidate towers, promotion queues, and execution surfaces so it can become the
downloadable CyberAlchemy base repository after owner review and extraction.

### Operational Interpretation

Use this term for the local consolidation project at `cyberAlchemy-v2/`, not for
all CyberAlchemy work everywhere. CyberAlchemy v2 owns local definitions,
constitutions, source maps, Craft state, and promotion routes for this stable
repository effort. Its objective is to become the base repository users receive
when they download CyberAlchemy, with enough authority, ontology, inventory, and
runtime projection structure for others to construct above it.

### Plain-Language Intuition

CyberAlchemy v2 is the home base: the repo you can download, trust, and build
above.

### Domain-Context Voice

In this workspace, CyberAlchemy v2 currently lives inside the private
`domainspec-core` umbrella as a project folder. It is not yet a standalone
repository, but it now has local authority imports, definitions, definition
towers, a Craft ledger, ontology package research, and extraction blockers.
The project objective is to make this folder the governed CyberAlchemy base:
settled authority is preserved here, unresolved authority is routed through
owner gates, and downstream projects can extend the base without inheriting
private source ambiguity.

### Boundary

CyberAlchemy v2 is not the same as public Arcanum, private DomainSpec, the
older `cyberAlchemy/` source folder, or a finished standalone product. It may
reference those sources, but it does not automatically absorb their authority.
It becomes the owner of CyberAlchemy base authority only through import,
promotion, boundary review, and standalone extraction decisions.

### Primary Consumers

- [../../README.md](../../README.md)
- [../../CRAFT.md](../../CRAFT.md)
- [DEFINITION-TOWERS.md](DEFINITION-TOWERS.md)

## CAV2-D10: Definition Tower

Status: active
Term: definition tower
Aliases: semantic tower, term tower

### Normative Definition

A definition tower is a bounded cluster of related terms arranged by conceptual
altitude, source posture, authority boundary, owner route, and next review
action so that local definitions can be promoted deliberately instead of copied
from scattered sources.

### Operational Interpretation

Use definition towers to organize top-level anchors, framework references,
private DomainSpec references, knowledge-governance terms, research/product
terms, and execution-evidence terms before adding or updating canonical
definitions.

### Plain-Language Intuition

A definition tower is a stack of terms with a map, a boundary, and a next
review step.

### Domain-Context Voice

In CyberAlchemy v2, definition towers are mapped in
[DEFINITION-TOWERS.md](DEFINITION-TOWERS.md) and executed through the Craft
context `CTX-CAV2-DEF-TOWERS`. They are the first ordering surface for the 149
definition import candidates.

### Boundary

A definition tower is a classification and routing surface, not canonical
definition authority by itself. Authority lives in this file after
definitions-governance promotion.

### Primary Consumers

- [DEFINITION-TOWERS.md](DEFINITION-TOWERS.md)
- [../../CRAFT.md](../../CRAFT.md)
- [../imports/definitions/MANIFEST.md](../imports/definitions/MANIFEST.md)

## CAV2-D11: Tower Space

Status: active
Term: tower space
Aliases: tower-bearing space, definition space

### Normative Definition

A tower space is a project, source, or execution area that can own, supply,
consume, or route content for one or more definition towers while preserving its
own authority posture.

### Operational Interpretation

Use tower spaces to distinguish CyberAlchemy v2 project folders from external
source spaces such as Arcanum, DomainSpec, prior CyberAlchemy material,
framework-unification, research towers, and validation evidence.

### Plain-Language Intuition

A tower space is where tower content comes from, lives, or gets worked on.

### Domain-Context Voice

In CyberAlchemy v2, tower spaces are grouped as project spaces, source spaces,
and Craft execution spaces in [DEFINITION-TOWERS.md](DEFINITION-TOWERS.md).
This lets `inventory/`, `ontology/`, `authority/`, `research/`, `ops/`, and
external source folders stay distinct.

### Boundary

A tower space does not become authoritative because it is listed in a tower map.
Each space keeps its own owner, source posture, and promotion gate.

### Primary Consumers

- [DEFINITION-TOWERS.md](DEFINITION-TOWERS.md)
- [../../SOURCE-MAP.md](../../SOURCE-MAP.md)
- [../../CRAFT.md](../../CRAFT.md)

## CAV2-D12: Craft Execution Surface

Status: active
Term: Craft execution surface
Aliases: Craft surface, local Craft surface, Craft ledger surface

### Normative Definition

A Craft execution surface is the project-local Craft ledger, derived index, and
linked human view used to record recursive work state, blockers, decisions,
candidate definitions, gaps, artifacts, next moves, and recomposition evidence
for a bounded project scope.

### Operational Interpretation

Use the Craft execution surface when continuing CyberAlchemy v2 work from
structured state. The source of truth is `.craft/ledger.yml`; `CRAFT.md` and
`.craft/index.json` are derived navigation surfaces.

### Plain-Language Intuition

It is the workbench where the project remembers what is open and what happens
next.

### Domain-Context Voice

In CyberAlchemy v2, the Craft execution surface owns contexts such as
`CTX-CAV2-DEF-TOWERS`, `CTX-CAV2-AUTHORITY-IMPORTS`, and
`CTX-CAV2-CONSTITUTION-TOWERS`. It records the route memory for definitions and
constitution work, but the owner sigils still govern promotion.

### Boundary

Craft can carry local candidate definitions and receipts, but it does not make
terms canonical and does not replace definitions-governance,
constitution-governance, decision-gate, or task-session.

### Primary Consumers

- [../../CRAFT.md](../../CRAFT.md)
- [../../.craft/ledger.yml](../../.craft/ledger.yml)
- [DEFINITION-TOWERS.md](DEFINITION-TOWERS.md)

## CAV2-D13: Authority Promotion Queue

Status: active
Term: authority promotion queue
Aliases: promotion queue, definition promotion queue, rule promotion queue

### Normative Definition

An authority promotion queue is the ordered set of candidate terms, rules,
claims, or artifacts awaiting owner classification, duplicate/conflict review,
boundary review, and explicit promotion decision before entering a canonical
authority layer.

When a queued proposal asks CAV2 to generalize a domain-owned object under
`CAV2-D48`, its queue entry must preserve the originating owner and version,
the proposed CAV2 abstraction, any changed or lost meaning, cross-context
evidence and contrary evidence, the challenge contract, and the CAV2 promotion
owner.

### Operational Interpretation

Use an authority promotion queue to decide what should be reviewed next without
allowing queue position to imply approval. The queue can include definition
candidates, constitution candidates, ontology candidates, or extraction
readiness items.

### Plain-Language Intuition

It is the review line for things that might be allowed to count.

### Domain-Context Voice

In CyberAlchemy v2, the first authority promotion queue is Q1 in
[DEFINITION-TOWERS.md](DEFINITION-TOWERS.md): top anchors before framework
references, DomainSpec references, imported term clusters, constitution
clusters, and execution readiness.

### Boundary

An authority promotion queue is not a promotion gate result. Items in the queue
remain candidate-only until the responsible owner records a pass, flag, block,
deferral, or rejection.

### Primary Consumers

- [DEFINITION-TOWERS.md](DEFINITION-TOWERS.md)
- [../promotion-policy.md](../promotion-policy.md)
- [../../CRAFT.md](../../CRAFT.md)
- [../../goals/bindings/authority-claims.json](../../goals/bindings/authority-claims.json)

## CAV2-D14: Source Space

Status: active
Term: source space
Aliases: source evidence space, external source space

### Normative Definition

A source space is a repository area outside the current CyberAlchemy v2
authority surface that supplies candidate evidence, vocabulary, rules, examples,
or operating precedent for review.

### Operational Interpretation

Use source spaces when tracing imported definitions, constitutions, ontology
branches, research towers, validation evidence, or implementation patterns back
to their originating folders and owner boundaries.

### Plain-Language Intuition

A source space is where a candidate came from before CyberAlchemy v2 decides
what to do with it.

### Domain-Context Voice

In CyberAlchemy v2, source spaces include public Arcanum, private DomainSpec,
the older `cyberAlchemy/` source folder, framework-unification, research
folders, project glossaries, and validation evidence.

### Boundary

A source space may be authoritative for itself while remaining candidate-only
for CyberAlchemy v2. Source-space evidence requires import classification and
promotion before becoming local authority.

### Primary Consumers

- [../../SOURCE-MAP.md](../../SOURCE-MAP.md)
- [DEFINITION-TOWERS.md](DEFINITION-TOWERS.md)
- [../imports/definitions/MANIFEST.md](../imports/definitions/MANIFEST.md)

## CAV2-D15: Project Space

Status: active
Term: project space
Aliases: local project space, CyberAlchemy v2 project area

### Normative Definition

A project space is a folder or surface inside CyberAlchemy v2 that has a
declared project-local role for authority, candidate synthesis, research,
architecture, capabilities, specifications, implementation, validation,
inventory, ontology, observability, operations, or Craft state.

### Operational Interpretation

Use project spaces to decide where CyberAlchemy v2 should place work after
promotion or routing. Project spaces are local homes such as `authority/`,
`research/`, `architecture/`, `specs/`, `validation/`, `ops/`, `inventory/`,
`ontology/`, and `.craft/`.

### Plain-Language Intuition

A project space is a room inside CyberAlchemy v2 with a declared job.

### Domain-Context Voice

In CyberAlchemy v2, project spaces make the future stable repository navigable
while it is still staged inside `domainspec-core`. Some spaces, especially
`inventory/` and `ontology/`, remain under review before standalone extraction.

### Boundary

A project space can hold authority only when its role permits it. Research,
inventory, ontology, observability, operations, and Craft surfaces may preserve
evidence or route work without becoming canonical definition sources.

### Primary Consumers

- [../../README.md](../../README.md)
- [DEFINITION-TOWERS.md](DEFINITION-TOWERS.md)
- [../../CRAFT.md](../../CRAFT.md)

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

## CAV2-D17: Reflection Tower Method

Status: active
Term: reflection tower method
Aliases: reflection tower, reflection-tower method, residue climb, tower climb method, residue escalation method

### Normative Definition

A reflection tower method is the CyberAlchemy v2 primitive method that handles
structural residue by turning unresolved residue from one schema/data layer into
the seed for a higher explanatory layer with its own objective, schema, target
data, validation, and recomposition path.

### Formal Step

Given a layer `L_n` with schema `S_n`, data or instance surface `D_n`, translator
or operation `T_n`, and residue `R_n`, the method first attempts local repair.
If `R_n` cannot be closed inside `L_n` without increasing residue or breaking
recomposition, then:

```text
R_n -> seed(L_n+1)
```

The next layer must name what the lower layer could not name, then route the new
schema, validation, owner, and recomposition obligation back to the tower.

When the DomainSpec formalization evidence applies, the preferred formal reading
is:

```text
L1^(n+1) := L1^n + Carrier(mu_n)
```

where `Carrier(mu_n)` records the residue's failure-locus and the promotion
`P_n : L1^n -> L1^(n+1)` preserves prior distinctions while adding new
vocabulary. CyberAlchemy v2 uses this as the governing shape of the method, not
as a requirement that every operational use materialize a Lean-level category.

### Operational Interpretation

Use this method when a task, definition, schema, artifact, or governance route is
already reduced to a responsible unit, but residue still remains because the
current layer lacks a schema, relation, taxonomy, validation rule, authority
rule, or owner route. The answer is not more splitting by default; the answer is
to name the missing layer that would make the residue intelligible.

### Plain-Language Intuition

When the current floor cannot explain the leftover problem, build the next floor
from that leftover problem and make it explain its way back down.

### Domain-Context Voice

In CyberAlchemy v2, reflection tower method sits beside orthogonality,
recursivity, and typed coupling as a primordial method. It explains how Craft
turns persistent residue into higher-layer work, why DomainSpec evidence treats
residue promotion as vertical growth rather than a third peer layer, and why v2
must keep ontology towers, capability towers, and reflection towers distinct
unless a typed coupling explicitly relates them.

### Boundary

The reflection tower method is not ordinary recursion, not endless
decomposition, not folder nesting, and not automatic promotion. It applies only
when local repair fails and the residue indicates a missing higher schema or
owner layer. It must stop by explicit closure, gate, or owner decision; it does
not promise total final closure at a finite rung. The existence of an omega-level
substrate does not by itself authorize fixed-point or absorption claims; those
remain construction-sensitive and must be stated only at the strength supported
by the current evidence.

### Primary Consumers

- [DEFINITION-TOWERS.md](DEFINITION-TOWERS.md)
- [source-clusters/primordial.md](source-clusters/primordial.md)
- [../../CRAFT.md](../../CRAFT.md)

## CAV2-D18: Residue

Status: active
Term: residue
Aliases: typed residue, residue signal, residual remainder, unpreserved structure

### Normative Definition

Residue is the typed remainder exposed by a transformation, translation,
promotion, validation, or governance operation when the target representation,
layer, or decision path does not preserve, name, justify, validate, or carry all
source structure required by the operation's intended use.

A residue becomes actionable in CyberAlchemy v2 only when it records:

- source operation or transformation
- expected preservation or closure condition
- observed remainder or failure-locus
- residue type
- evidence reference
- owner route
- treatment: repair, type, gate, climb, accept, or defer

### Formal Interpretation

For an operation `F : A -> B` with an intended preservation condition `P`, the
residue of `F` is the evidence-bearing part of `A` that `B` cannot preserve,
name, reconstruct, justify, or validate under `P`.

In DomainSpec formalization contexts, this umbrella has several non-identical
readings:

- schema residue: a schema-level unit failure or missing faithful shadow
- instance residue: an instance-level round-trip or migration failure
- `ResidueObject`: a finite probabilistic residue object with entropy
- `ResidueStructure`: a carrier/schema/signal/noise/refinement structure
- `ResidueCat`: a category of bundled residue structures and monotone morphisms
- `Carrier(mu_n)`: the reflection-tower carrier that turns level `n` residue
  into level `n+1` vocabulary

These readings may inform each other, but CyberAlchemy v2 must not treat them as
interchangeable without a typed coupling.

### Operational Interpretation

Use residue when something meaningful remains after a local operation has done
what it knows how to do. The remainder may be information loss, untyped noise,
missing vocabulary, failed validation, a broken recomposition path, an authority
gap, or an unresolved owner route.

First type the residue. Then either repair it locally, record a typed coupling,
route it through a gate, promote it through the reflection tower method, accept
it as tolerated residue, or defer it as an open question.

### Plain-Language Intuition

Residue is the meaningful leftover: the part the current representation could
not carry.

### Domain-Context Voice

In CyberAlchemy v2, residue is the reason the system cannot stop at clean
summaries, folders, or pass/fail checks. It is the evidence that tells Craft
when a unit needs repair, when a relation needs typing, when authority needs a
gate, and when a reflection tower climb is justified. It sits between
`CAV2-D16` typed coupling invariant and `CAV2-D17` reflection tower method:
couplings label cross-object residue, while reflection tower method promotes
structural residue into a higher explanatory layer.

### Boundary

Residue is not any bug, not any uncertainty, not proof of novelty, and not
automatic promotion. Some residue is acceptable, some is repairable, some is a
blocker, and some is the seed for a higher layer. The imported term
`TranslationResidue` remains a source-specific candidate until a later pass
decides whether it is a subtype, alias, or separate term.

### Primary Consumers

- [DEFINITION-TOWERS.md](DEFINITION-TOWERS.md)
- [source-clusters/primordial.md](source-clusters/primordial.md)
- [../../CRAFT.md](../../CRAFT.md)

## CAV2-D19: Ontology

Status: active
Term: ontology
Aliases: governed meaning layer, ontology candidate, ontology map, ontology branch map, ontology candidate condensation

### Normative Definition

An ontology is a governed meaning layer that represents a domain, workspace,
system, or operation as typed knowledge objects, typed relations, branch or role
assignments, provenance, confidence, promotion state, and use obligations.

In CyberAlchemy v2, an ontology becomes actionable only when it records:

- scope or domain of meaning
- knowledge object types
- typed relations or edge rules
- branch, role, or ownership assignment
- evidence and provenance references
- evidence confidence and commitment confidence when claims are load-bearing
- promotion state and next gate
- contradiction, drift, residue, or invalidation route
- retrieval or use guidance for downstream agents or humans

### Formal Interpretation

Given source evidence `S`, inventory evidence layer `I`, and intended use `U`,
an ontology `O` is a typed structure over selected evidence:

```text
O_U = (N, E, B, R, C, P, G)
```

where:

- `N` is a set of typed knowledge objects or nodes
- `E` is a set of typed relations or edges over `N`
- `B` assigns branch, role, or ownership context
- `R` links ontology claims back to source or inventory evidence
- `C` records confidence, scope, validity, and expiry where relevant
- `P` records candidate, reviewed, promoted, demoted, or deferred state
- `G` records gates, contradiction paths, drift routes, and use obligations

An ontology may be graph-shaped, tree-shaped, branch-aware, entry-based, or
artifact-tree-shaped, but it must keep typed meaning, evidence, and authority
posture together. A pointer list without usable content, typed relations, and
governance state is inventory or index material, not ontology.

### Operational Interpretation

Use ontology after source evidence has been located and inventory has made it
findable, when the project needs meaning that agents or humans can actually use:
what a thing is, where it belongs, how it relates to other things, what supports
it, how confident the project is, and when it may guide later work.

Branch-aware ontology separates business or meaning claims, system claims, and
bridge claims so implementation evidence cannot silently redefine intent and
intent cannot pretend implementation exists. Some local systems add further
branches, such as an agent-operation branch or run-context branch, but those are
typed substructures and not aliases for ontology itself.

### Plain-Language Intuition

An ontology is a map of meaning with typed links, receipts, and rules for use.

### Domain-Context Voice

In CyberAlchemy v2, ontology is the layer that condenses scattered repository
knowledge into candidate branch maps, thick knowledge entries, and promotion
requests without making them canonical by proximity. The current
`.arcanum/ontology-vault/` map reduces search and suggests branches; future
`ontology/` project-space material may hold candidate branch maps and promotion
requests. Definitions still become canonical only in this file, and source
authority still comes from the source space unless a promotion gate passes.

Inside the future CyberAlchemy base repository, `ontology/` is the workspace
where authority relations are made explicit, reviewable, and constructible as a
candidate/projection package. It is where v2 fixes the shape of authority for
the base by mapping meaning, evidence, owner routes, promotion requests,
projection boundaries, and residue before any downstream project builds above
that base.

This term connects `CAV2-D16` typed coupling invariant, `CAV2-D18` residue, and
the knowledge-governance tower: an ontology can type relations, preserve
meaningful residue, and route candidate meaning toward context-builder,
decision-gate, definitions-governance, or implementation work.

### Boundary

Ontology is not raw source, not inventory, not a glossary, not memory, not a
session transcript, not a generated search index, and not automatic authority.
Candidate ontology may condense meaning, but it cannot promote definitions,
constitutions, runtime contracts, or public claims by itself. The ontology
package fixes authority by making candidate authority structure explicit; it
does not own authority transitions.

`Operational Ontology` is demoted as a CyberAlchemy v2 definition candidate.
Treat it as source-local shorthand for an operation-facing ontology projection:
a `CAV2-D19` ontology view whose authority posture is governed by `CAV2-D23`.
It is not a primitive, not a peer ontology branch, not a standalone subtype, and
not a `CAV2-D23` alias.

When a source uses `Operational Ontology`, normalize the phrase instead of
promoting it:

- typed meaning, relation, branch, evidence, retrieval, or use obligations route
  to `CAV2-D19` ontology;
- lifecycle posture, status, evidence confidence, commitment, provenance,
  owner, or residue separation routes to `CAV2-D23` authority lifecycle axis;
- agent-operation, run, action, routing, or workflow obligations must be named
  as concrete object, relation, action, run, or schema obligations rather than
  hidden inside the broad phrase;
- if no concrete obligation remains after the D19/D23 split, retire the phrase
  in local wording.

### Primary Consumers

- [DEFINITION-TOWERS.md](DEFINITION-TOWERS.md)
- [../../CRAFT.md](../../CRAFT.md)
- [../../../.arcanum/ontology-vault/map-2026-06-18-dispersed-knowledge.md](../../../.arcanum/ontology-vault/map-2026-06-18-dispersed-knowledge.md)
- [../../development/reviews/2026-06-22-operational-ontology-authority-lifecycle-review/findings.md](../../development/reviews/2026-06-22-operational-ontology-authority-lifecycle-review/findings.md)
- [../../../.arcanum/inventory/entries/evidence-sets/2026-06-22-operational-ontology-authority-lifecycle-sets.md](../../../.arcanum/inventory/entries/evidence-sets/2026-06-22-operational-ontology-authority-lifecycle-sets.md)

## CAV2-D20: Craft Method

Status: active
Term: Craft method
Aliases: CyberAlchemy building method, governed system-building method, recursive residue-carrying building method, Craft recursive method

### Normative Definition

Craft method is CyberAlchemy's governed recursive system-building method. It
turns owner-controlled Product intent into an evidence-bounded working system by
preserving one explicit chain through context, definitions, product and business
meaning, system specification, exact realization selection, deterministic
construction, independent conformance, bounded operation, recovery, evolution,
and owner continuation.

The method uses a source-of-truth ledger to preserve state across that chain. It
records contexts, candidate definitions, blockers, enablers, decisions, gaps,
artifacts, next moves, validation evidence, residue, and recomposition
obligations. Ledgering is the method's continuity mechanism; it is not the whole
method.

In CyberAlchemy v2, Craft method is valid only when it preserves these
boundaries:

- a Product and its Product Thesis own product purpose and value propositions
- a Project coordinates the goals, owners, evidence, decisions, and work used to
  develop or evolve the Product
- Product Features and Product Capabilities remain distinct from the Product,
  Project, Method, and their realizations
- canonical definitions, product and business ontology, DomainSpec source,
  generated system ontology, realization selection, construction, conformance,
  runtime evidence, and owner decisions remain separately identifiable
- every implementation-bearing construction follows the exact
  `CAV2-D65` DomainSpec-governed construction chain or carries typed residue for
  the missing prerequisite
- `.craft/ledger.yml` or an equivalent declared ledger is the source of truth
  for Craft state
- `CRAFT.md`, `.craft/index.json`, projections, and status output are derived
  views
- residue is typed and carried forward instead of hidden
- schema-level and instance-level validation are not collapsed
- child contexts recompose into their parent through evidence
- closure happens by owner decision, gate, or accepted residue, not by a claim
  of total final completion
- Craft state can carry local candidate definitions and receipts but cannot
  make terms canonical without definitions-governance

### Formal Interpretation

For a bounded Product and Project scope `S`, the Craft method has the minimum
governed shape:

```text
M_Craft(S) =
  (context, product_intent, domain_meaning, system_specification,
   realization_selection, construction, conformance, operation,
   recovery_and_evolution, owner_continuation, ledger_state)

L_S = (C, B, E, D, G, A, N, R)
```

where:

- `context` resolves the Product, Project, Goal, participants, consumers, and
  source policies relevant to the bounded work
- `product_intent` carries the Product Thesis plus selected Product Feature or
  Product Capability obligations
- `domain_meaning` carries canonical definitions and product/business ontology
- `system_specification` carries DomainSpec and generated system-ontology state
- `realization_selection` identifies exact architecture and language-profile
  realizations
- `construction` materializes the selected contained target deterministically
- `conformance` independently evaluates declared static and relational
  obligations
- `operation` supplies bounded runtime evidence without becoming authority
- `recovery_and_evolution` preserves compensation, recovery, migration,
  rollback, compatibility, and successor-state obligations
- `owner_continuation` routes an evidenced next state to its explicit owner
- `C` is the set of contexts or child contexts
- `B` is blockers
- `E` is enablers or available evidence
- `D` is decisions
- `G` is gaps or unresolved obligations
- `A` is artifacts and source references
- `N` is next moves or route obligations
- `R` is typed residue plus recomposition evidence

A Craft step is admissible when it preserves typed identity and source
authority, records the operation that changed state, keeps generated views
derivative, validates every reachable declared consumer, and either repairs,
types, routes, accepts, or defers residue with an owner. Construction does not
establish conformance; conformance does not establish runtime truth; evidence
does not establish owner adoption or permission.

Formal-foundations evidence supports this shape by treating residue as typed and
composable, by separating schema-fidelity from instance-fidelity, by showing
that reflection towers assemble without finite total closure, and by justifying
stop criteria based on decision and residue plateau rather than completion. This
is support evidence for the method; it does not prove that an LLM-centered Craft
run achieved a clean functor, kernel, or zero-residue translation.

### Operational Interpretation

Use Craft method whenever CyberAlchemy builds or materially evolves a Product,
Product Feature, Product Capability, system, or implementation-bearing
capability. Begin from the Product and Project context, define the meaning,
model the product and business obligations, author or update the DomainSpec
source, select exact realizations, construct the target, independently check it,
observe bounded runtime behavior, preserve recovery and evolution obligations,
and route the evidenced state to its owner.

The same method provides durable work memory across sessions, definition towers,
authority imports, constitution towers, research packets, promotion queues, and
nested project spaces. A human or agent should be able to continue without
guessing what is blocked, what is merely candidate, what has evidence, what was
constructed, and what must recompose upward.

### Plain-Language Intuition

Craft method is how CyberAlchemy builds a system without losing why it should
exist: define the meaning, choose exactly how it will be built, build it, check
it independently, observe it, and carry every leftover problem to the next
owner instead of pretending the work is finished.

### Domain-Context Voice

Inside CyberAlchemy v2, the Craft Product embodies this method and the Craft
Project coordinates its development and evolution. Product Features are shaped
inside the Craft Product context; Product Capabilities state stable outcomes;
DomainSpec expresses system intent; architecture and language profiles select
exact realizations; construction and conformance provide separate evidence; and
the Craft ledger preserves continuity and residue across the whole path.

The method connects `CAV2-D12` Craft execution surface, `CAV2-D17` reflection
tower method, `CAV2-D18` residue, and `CAV2-D65` DomainSpec-governed
construction invariant. The execution surface is where Craft state lives; the
method is the broader discipline for carrying meaning, realization,
construction, evidence, recovery, residue, and recomposition through recursive
system work.

The public Arcanum `craft` capability is one narrower repository-ledger
realization used by this private method. It does not own the private Craft
Product, Project, Product Thesis, Product Features, or method semantics.

### Boundary

Craft method is not the Craft Product, Craft Project, a Product Feature, Product
Capability, Product Thesis, DomainSpec model, architecture pattern, generator,
runtime, public Arcanum capability, `.craft` state, generic task runner, or
replacement for task-session. It is not a source of canonical definitions and
does not authorize implementation or prove that a translation, construction,
conformance assessment, operation, recovery, or migration is complete.

It may use formal foundations as support evidence, but it must preserve their
honesty boundary: formal cousins describe the structure Craft operates inside;
they do not certify that a particular Craft run achieved the clean formal case.

Craft method also does not promote `ledger` as a cross-method primitive by
itself. Ledger remains separately flagged for review until recursivity, relation
inheritance, and local Craft ledger conformance are settled.

### Primary Consumers

- [DEFINITION-TOWERS.md](DEFINITION-TOWERS.md)
- [source-clusters/primordial.md](source-clusters/primordial.md)
- [../../CRAFT.md](../../CRAFT.md)
- [../../.craft/ledger.yml](../../.craft/ledger.yml)
- [../../product/craft/README.md](../../product/craft/README.md)
- [../../goals/projects/craft/README.md](../../goals/projects/craft/README.md)
- [../../../arcanum/arcana/craft/SKILL.md](../../../arcanum/arcana/craft/SKILL.md)
- [../../../arcanum/development/craft/CRAFT-FORMAL-FOUNDATIONS.md](../../../arcanum/development/craft/CRAFT-FORMAL-FOUNDATIONS.md)

## CAV2-D21: Four-Facet Action Method

Status: active
Term: four-facet action method
Aliases: governed action facet obligation, governed action facets, action facet obligations, four-facet action primitive, taxonomy-schema-human-machine obligation

### Normative Definition

Four-facet action method is the CyberAlchemy v2 primitive action rule that every
governed action must explicitly bind, create, or record typed residue for four
facets before the action can govern downstream work:

- classification or taxonomy facet
- schema facet
- human-continuation view
- machine-checkable view

A governed action is any CyberAlchemy v2 action that creates, changes, routes,
validates, promotes, implements, or interprets load-bearing artifacts, state,
meaning, or authority posture. The action is admissible only when each facet is
declared or when its absence is carried as typed residue.

At minimum:

- the classification or taxonomy facet states what kind of thing or action is
  involved and which classification catalog, taxonomy, or source vocabulary owns
  that assignment
- the schema facet states the structural shape, field set, relation shape, or
  validation surface that governs the action or artifact
- the human-continuation view states how a human can understand the action's
  purpose, status, trust boundary, blockers, residue, next route, and evidence
- the machine-checkable view states how a machine can parse or check the action
  state, including identifiers, kind, schema reference, classification
  reference, source of truth, validator or proof handle, projection status, and
  residue

If a facet is missing, impossible, or intentionally deferred, the action must
record typed residue naming the missing facet, the reason or impossibility, the
owner route, the evidence reference, and the action effect: continue, defer, or
block. If the action later asks to promote something, the same residue must also
state the promotion effect.

### Formal Interpretation

For a governed action `a`, let:

```text
F(a) = (K_a, S_a, H_a, M_a, R_a)
```

where:

- `K_a` is the classification or taxonomy facet
- `S_a` is the schema facet
- `H_a` is the human-continuation view
- `M_a` is the machine-checkable view
- `R_a` is typed residue for any missing, impossible, or deferred facet

The action satisfies the four-facet action method when each of `K_a`, `S_a`,
`H_a`, and `M_a` is either bound to an existing governed surface, created by the
action, or represented in `R_a` with owner route and effect. The method forbids
silent absence; it does not require perfect completion before exploratory work
can begin.

### Operational Interpretation

Use this method before or during any CyberAlchemy v2 action that may matter
later: definition work, constitution work, axiom work, discipline work, Craft
state changes, ontology projections, task execution, workflow design, system
design, validation, or implementation routing.

The method lets the system act without pretending the four facets already
exist. An action may instantiate existing taxonomy, schema, human view, and
machine view; create one or more missing facets; or declare typed residue for
the missing facets. What is forbidden is a silent action that later relies on an
unstated kind, shape, human continuation path, or machine-checkable state.

### Plain-Language Intuition

Before an action is allowed to matter, it must answer four questions: what kind
of thing is this, what shape governs it, how can a human continue it, and how
can a machine check it? If one answer is missing, write down the missing piece,
who owns it, and whether the action can continue.

### Domain-Context Voice

In CyberAlchemy v2, this term corrects the four-facet research finding so it is
not limited to promotion candidates. It is the base action method for work in
definitions, constitutions, axioms, disciplines, tasks, systems, workflows,
Craft, ontology, validation, and implementation routing. Promotion gates remain
stricter downstream uses of the same method, not the method's whole scope.

This method connects `CAV2-D16` typed coupling invariant, `CAV2-D18` residue,
and `CAV2-D20` Craft method. If a schema affects authority, if a classification
affects ontology, if a human view constrains execution, or if a machine view
feeds validation, the coupling must be typed. If any facet cannot be supplied,
the missing facet becomes typed residue with owner and effect.

### Boundary

Four-facet action method is not a promotion gate by itself, not proof of
authority, not a requirement that all exploratory work have perfect schemas
before it starts, and not a single required file format. It allows an action to
create missing facets or carry typed residue.

Generic `schema` semantics are defined locally by `CAV2-D56`; `DEF-ARC-SCHEMA`
remains Arcanum's public surface and this definition's non-normative ancestor. A
classification facet is not ontology membership or promotion. A human-continuation view is not canonical merely
because it is readable. A machine-checkable view is not authority and is not
proof beyond the named checks it can actually run.

### Primary Consumers

- [../../development/research/2026-06-21-schema-taxonomy-view-primitives/ACTION-PRIMITIVE-CORRECTION.md](../../development/research/2026-06-21-schema-taxonomy-view-primitives/ACTION-PRIMITIVE-CORRECTION.md)
- [../../development/research/2026-06-21-schema-taxonomy-view-primitives/findings.md](../../development/research/2026-06-21-schema-taxonomy-view-primitives/findings.md)
- [DEFINITION-TOWERS.md](DEFINITION-TOWERS.md)
- [source-clusters/primordial.md](source-clusters/primordial.md)
- Future `Four-Facet Action Constitution`

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

## CAV2-D23: Authority Lifecycle Axis

Status: active
Term: authority lifecycle axis
Aliases: confidence lifecycle axis, authority axis split, maturity-evidence-commitment split, status-evidence-commitment split

### Normative Definition

Authority lifecycle axis is the CyberAlchemy v2 rule that authority posture must
separate at least these dimensions when they matter to a decision:

- role or kind
- maturity or status
- evidence confidence
- commitment or conviction
- provenance
- owner

No one axis may silently stand in for another. A definition can be mature but
weakly evidenced, an imported source can be well-evidenced but not locally
canonical, an ontology candidate can be useful but unpromoted, and an owner can
be committed to a hypothesis without that hypothesis becoming authority.

### Formal Interpretation

An authority-bearing artifact `a` has lifecycle posture:

```text
L(a) = (kind, status, evidence, commitment, provenance, owner, residue)
```

where each component may be known, unknown, deferred, or source-local. A
governance move is valid only if it changes the intended component and does not
imply changes to the others unless those changes are explicitly recorded.

### Schema

Schema handle: `CAV2-D23-SCHEMA` — tracked in
[DEFINITION-SCHEMAS.md](DEFINITION-SCHEMAS.md).
Status: tracked (documentary).
Bound to: `CAV2-D23` authority lifecycle axis.

Lifecycle posture record:

```text
L(a) = (kind, status, evidence, commitment, provenance, owner, residue)
```

| Field | Meaning | Value posture |
| --- | --- | --- |
| `kind` | role or artifact kind of `a` | known, unknown, deferred, or source-local |
| `status` | maturity or lifecycle state | known, unknown, deferred, or source-local |
| `evidence` | evidence confidence | known, unknown, deferred, or source-local |
| `commitment` | owner conviction or commitment | known, unknown, deferred, or source-local |
| `provenance` | source or origin | known, unknown, deferred, or source-local |
| `owner` | responsible owner route | known, unknown, deferred, or source-local |
| `residue` | unresolved remainder per `CAV2-D18` | typed residue or none |

Schema invariant: a governance move changes the intended field without implying
a change to the others unless an explicit typed coupling (`CAV2-D16`) records the
link. This schema is documentary; a machine-checkable validator is a deferred
follow-up recorded in the registry. Schema changes follow `CAV2-D25` schema
amendment witness.

### Operational Interpretation

Use authority lifecycle axes when evaluating definitions, constitutions, axioms,
ontology nodes, inventory cards, task results, schemas, and implementation
claims. The reviewer should ask which axis is being advanced: source role,
maturity, evidence, owner commitment, provenance, or canonical authority.

### Plain-Language Intuition

"Useful", "trusted", "finished", "owned", and "canonical" are different words.
Do not let one of them impersonate the others.

### Domain-Context Voice

In CyberAlchemy v2, this definition absorbs the imported vault's mature split
between `node_type`, `status`, evidence confidence, and commitment language as a
local lifecycle principle. The source vocabulary is evidence, while CAV2 keeps
the more general axis split so Arcanum, DomainSpec, house_project, ontology,
inventory, Craft, and future implementation artifacts can share one governance
shape without sharing one exact status taxonomy.

### Boundary

Authority lifecycle axis is not a complete status schema and does not make
every artifact an ontology node. It gives the minimum separations that future
schemas, ledgers, and constitutions must preserve.

### Primary Consumers

- [../imports/house_project/docs/vault/ontology-conventions.md](../imports/house_project/docs/vault/ontology-conventions.md)
- [../imports/house_project/docs/vault/premise/ontology-premises.md](../imports/house_project/docs/vault/premise/ontology-premises.md)
- [../imports/house_project/docs/vault/confidence-levels.md](../imports/house_project/docs/vault/confidence-levels.md)
- [../../../.arcanum/inventory/entries/evidence-cards/2026-06-21-authority-node-relationship-taxonomy-cards.md](../../../.arcanum/inventory/entries/evidence-cards/2026-06-21-authority-node-relationship-taxonomy-cards.md)
- [../../../.arcanum/inventory/entries/evidence-cards/2026-06-21-house-project-vault-cards.md](../../../.arcanum/inventory/entries/evidence-cards/2026-06-21-house-project-vault-cards.md)

## CAV2-D24: Provenance-First Navigation

Status: active
Term: provenance-first navigation
Aliases: constitution-first traversal, source-indexed navigation, session-as-provenance navigation, graph-indexed lookup

### Normative Definition

Provenance-first navigation is the CyberAlchemy v2 search method that begins
from governed entrypoints, constitutions, definition indexes, inventory cards,
source manifests, and graph/index surfaces before opening broad conversation,
session, or raw source material.

Sessions and raw exploratory files may explain why a decision emerged, but they
must not be treated as the first or only authority surface when indexed
provenance, canonical sources, or owner-authored read models exist.

### Formal Interpretation

For a query `q`, provenance-first navigation builds a selector ladder:

```text
N(q) = (entrypoint, authority_surface, inventory_or_index, source_manifest,
        primary_source, provenance_session, residue)
```

The search may skip empty layers, but it must preserve the distinction between
canonical authority, read-model evidence, imported source, and provenance
session.

### Operational Interpretation

Use provenance-first navigation when searching CyberAlchemy v2, imported vaults,
ontology material, definitions, constitutions, or prior research. Start with the
nearest index and source manifest, then follow typed source references. Open
sessions or raw conversation logs only after the route needs historical
rationale, conflict evidence, or unreduced residue.

### Plain-Language Intuition

Read the map before walking the whole city. Use sessions for why, not as the
default place to discover what counts.

### Domain-Context Voice

In CyberAlchemy v2, this definition turns the imported vault's agent navigation
and graph-index pattern into a stable repository search rule. It also reinforces
the Inventory boundary: Inventory shortens lookup and supplies evidence cards,
but it does not promote authority by itself.

### Boundary

Provenance-first navigation is not a ban on reading source files. It is a
sequencing rule that protects search cost, provenance, and authority posture.
If indexes are stale or absent, the missing index becomes residue or a route for
Inventory, not permission to blur source authority.

### Primary Consumers

- [../imports/house_project/docs/vault/agent-navigation.md](../imports/house_project/docs/vault/agent-navigation.md)
- [../imports/house_project/docs/vault/graph-edges.md](../imports/house_project/docs/vault/graph-edges.md)
- [../imports/house_project/docs/vault/graph-session-index.md](../imports/house_project/docs/vault/graph-session-index.md)
- [../../../.arcanum/inventory/index.md](../../../.arcanum/inventory/index.md)
- [../../../.arcanum/inventory/entries/evidence-cards/2026-06-21-house-project-vault-cards.md](../../../.arcanum/inventory/entries/evidence-cards/2026-06-21-house-project-vault-cards.md)

## CAV2-D25: Schema Amendment Witness

Status: active
Term: schema amendment witness
Aliases: schema amendment discipline, runtime witness, schema-evolution witness, enforcement witness

### Normative Definition

Schema amendment witness is the CyberAlchemy v2 rule that any schema,
frontmatter, taxonomy, ontology, ledger, event, or machine-view change that
affects validation or authority interpretation must carry both:

- an amendment record naming owner, scope, reason, changed shape, source
  evidence, compatibility effect, and rollout or rollback route
- a witness naming the validator, runtime observation, fixture, review check,
  or typed residue that shows how the changed rule is enforced or why it cannot
  yet be enforced

### Formal Interpretation

For an authority-affecting shape change `s -> s'`, a valid amendment is:

```text
A = (owner, scope, source, delta, compatibility, witness, residue)
```

where `witness` may be deterministic, hybrid, review-based, or absent only when
the absence is typed as residue with owner and effect. The amendment is not
complete if the changed shape can govern downstream work but has no declared
enforcement or residue path.

### Operational Interpretation

Use schema amendment witness before changing frontmatter rules, ontology node
schemas, inventory entry schemas, event catalogs, ledger row identity, machine
envelopes, validation fixtures, or constitution-controlled structure. The
minimum action is to say what changed, who owns it, what evidence justifies it,
what may break, and what witness checks or carries the change.

### Plain-Language Intuition

If the shape changes, leave a receipt and show what will catch mistakes. If
nothing catches them yet, say that out loud and assign the gap.

### Domain-Context Voice

In CyberAlchemy v2, this definition promotes the imported vault's schema
amendment and runtime-witness patterns into a general governance concept. It
binds directly to `CAV2-D21` four-facet action method because schema and
machine-checkable views must either exist, be created, or be recorded as typed
residue.

### Boundary

Schema amendment witness does not redefine generic `schema`; that term is defined
by `CAV2-D56`. This definition governs the *change* of a schema, not its content.
It also does not require a fully automated validator for
every early rule. Review and typed residue are acceptable witnesses when the
artifact is not yet implementation-backed.

### Primary Consumers

- [../imports/house_project/docs/vault/constitution/framework/schema-amendment-discipline-constitution.md](../imports/house_project/docs/vault/constitution/framework/schema-amendment-discipline-constitution.md)
- [../imports/house_project/docs/vault/constitution/framework/frontmatter-ownership-constitution.md](../imports/house_project/docs/vault/constitution/framework/frontmatter-ownership-constitution.md)
- [../imports/house_project/docs/vault/constitution/framework/edge-acyclicity-constitution.md](../imports/house_project/docs/vault/constitution/framework/edge-acyclicity-constitution.md)
- [../../../.arcanum/inventory/entries/evidence-cards/2026-06-21-house-project-vault-cards.md](../../../.arcanum/inventory/entries/evidence-cards/2026-06-21-house-project-vault-cards.md)
- Future schema and machine-view validators

## CAV2-D26: Append-Only Event Ledger

Status: active
Term: append-only event ledger
Aliases: append-only ledger, idempotent event ledger, event-sourced authority ledger, deterministic event ledger

### Normative Definition

Append-only event ledger is a CyberAlchemy v2 ledger pattern for state-changing
or authority-affecting operations where each change is recorded as an additive
event instead of silently rewriting prior state.

An append-only event ledger must preserve:

- registered event kinds or event catalog membership
- deterministic subject or stream identity
- idempotency key or duplicate-guard rule for retryable operations
- event payload or source reference
- actor, owner, or route
- timestamp or ordering handle
- replay, projection, or human-audit interpretation

### Formal Interpretation

For an event stream `E = [e_1, ..., e_n]`, current projected state is:

```text
P(E) = fold(apply, initial_state, E)
```

A new event `e_{n+1}` may be appended when its event kind is admitted, its
subject identity is deterministic, and its idempotency handle prevents a retry
from producing a second semantic change. Corrections are represented by new
events, not untracked mutation of the old event.

### Operational Interpretation

Use append-only event ledger for imports, promotions, schema amendments,
authority movement, idempotent generation, task receipts, validation runs, or
runtime events when replay and audit matter. The ledger may project current
state into indexes or ontology views, but the projection is derivative.

### Plain-Language Intuition

Record what happened as a new line. If the same action is retried, it should
not count twice. If something was wrong, add the correction instead of erasing
the trace.

### Domain-Context Voice

In CyberAlchemy v2, this definition adopts the imported vault's event-system
precedent as a narrow ledger pattern. It supports authority imports, promotion
records, schema amendments, Craft receipts, and future implementation events
without yet declaring generic `ledger` to be a universal primitive.

### Boundary

Append-only event ledger is not the same as `CAV2-D20` Craft method and does
not promote the unresolved generic `ledger` primitive. It is one ledger pattern
for operations where event order, retry behavior, and projection traceability
matter.

### Primary Consumers

- [../imports/house_project/docs/vault/constitution/event-system-constitution.md](../imports/house_project/docs/vault/constitution/event-system-constitution.md)
- [../../../.arcanum/inventory/entries/evidence-cards/2026-06-21-house-project-vault-cards.md](../../../.arcanum/inventory/entries/evidence-cards/2026-06-21-house-project-vault-cards.md)
- [../../../.arcanum/inventory/entries/evidence-cards/2026-06-21-authority-harness-ledger-ontology-cards.md](../../../.arcanum/inventory/entries/evidence-cards/2026-06-21-authority-harness-ledger-ontology-cards.md)
- [reviews/ledger-primitive-review.md](reviews/ledger-primitive-review.md)

## CAV2-D27: Residue Entropy

Status: active
Term: residue entropy
Aliases: entropy observable, typed entropy observable, entropy readout, residue measure, residue measurement

### Normative Definition

Residue entropy is a CyberAlchemy v2 primitive observable for typed residue: it
measures the distinguishability, uncertainty, or information loss exposed by a
transformation, translation, coarse-graining, classification, validation, or
governance operation after the residue type and source operation have been
declared.

Residue entropy may influence authority, routing, validation, ontology, or
implementation only when the entropy claim declares:

- entropy register or mathematical reading
- source operation or transformation
- typed residue source
- measure or observable used
- finite, weighted, retrieval, probabilistic, or categorical scope
- theorem, conjecture, analogy, or review status
- authority effect or non-governing residue treatment

### Formal Interpretation

For a finite probabilistic residue object `R` with finite carrier `F_R` and
probability mass function `rho`, the residue entropy observable is:

```text
H(R) = sum_{x in F_R} negMulLog(rho(x))
```

In the finite microcanonical macrostate bridge, for a coarse-graining
`f : M -> M'`:

```text
S_f(m') = log |fiber_f(m')|
```

and positive entropy marks fully-faithful residue:

```text
S_f(m') > 0  <->  m' in ffNoise(f)
```

This makes finite Boltzmann entropy a readout of `Residue_FF(Macro)`, not a
replacement for the broader `CAV2-D18` residue primitive.

### Operational Interpretation

Use residue entropy when a CyberAlchemy v2 artifact needs to compare, rank,
route, or validate typed residue by a quantitative or categorical observable.
Valid examples include finite Shannon entropy on a `ResidueObject`, Boltzmann
`log |fiber|` in a finite coarse-graining bridge, KL or entropy-gap evidence in
a declared finite-support setting, retrieval entropy as evidence for
classification uniqueness, or an entropy profile over a declared residue chain.

Before using the observable as evidence, the artifact must name what residue is
being measured and which register supplies the measure. If the register cannot
be named, the claim remains analogy, research pressure, or typed residue.

### Plain-Language Intuition

Residue entropy is how much meaningful distinction the current layer collapsed
or left unnamed.

### Domain-Context Voice

In CyberAlchemy v2, residue entropy sits below `CAV2-D18` residue and beside
`CAV2-D22` orthogonal classification. It lets the project reuse Lean-backed
entropy evidence without turning every entropy mention into a global primitive
or treating retrieval entropy, Boltzmann entropy, Gibbs entropy, KL divergence,
and entropy profiles as interchangeable. The matching constitution rule
requires durable entropy claims to declare their register and residue source.

### Boundary

Residue entropy is not generic disorder, not uncertainty by itself, not proof of
novelty, and not automatic promotion. Non-numeric residue may still be valid and
actionable. Weighted, Gibbs, continuous, Markov-category, free-energy, RG, or
physical second-law claims require their own typed bridge before they may govern
CyberAlchemy v2 authority.

### Primary Consumers

- [DEFINITION-TOWERS.md](DEFINITION-TOWERS.md)
- [DEFINITION-DRIFT-AUDIT.md](DEFINITION-DRIFT-AUDIT.md)
- [../constitutions/STABLE-REPOSITORY-CONSTITUTION.md](../constitutions/STABLE-REPOSITORY-CONSTITUTION.md)
- `domainspec-lean-formalization/lean-formalization/Residue.lean` (embedded local source evidence)
- `domainspec-lean-formalization/lean-formalization/EntropyAsFFResidue.lean` (embedded local source evidence)
- `domainspec-lean-formalization/lean-formalization/SecondLawDiscrete.lean` (embedded local source evidence)
- `domainspec-lean-formalization/THERMODYNAMICS.md` (embedded local source evidence)

## CAV2-D28: Value-Cycle Edge Guard

Status: active
Term: value-cycle edge guard
Aliases: edge contextuality guard, value-constraining cycle guard, contextuality tripwire, edge non-contextuality guard

### Normative Definition

A value-cycle edge guard is the CyberAlchemy v2 invariant that no relation,
edge type, or ontology movement may simultaneously:

- constrain the value, label, authority state, schema field, or validation
  outcome of another artifact; and
- be allowed to participate in a cycle without an explicit acyclicity
  constraint.

If a proposed relation needs both properties, it must stop at schema governance
and receive a contextuality-obstruction review before it can influence
authority, ontology, validation, or implementation.

### Formal Interpretation

For any proposed edge type `E`, define two review predicates:

```text
value_constraining(E)
cycle_permitted(E)
```

CyberAlchemy v2 requires:

```text
not (value_constraining(E) and cycle_permitted(E))
```

unless a schema owner records an explicit exception with source evidence,
constraint semantics, satisfiability or obstruction review, validator or review
witness, and typed residue.

The current guard is a watch condition, not a theorem. It is satisfied when
value-constraining edges are acyclic and cycle-permitted edges do not constrain
values. It becomes live only when a proposed edge straddles both classes.

### Operational Interpretation

Use this guard when adding or revising ontology relations, relationship
families, edge catalogs, movement edges, schema links, authority transitions, or
validation-affecting graph rules. If the new edge can force a value or state
and can also form cycles, block the promotion until the review names what
constraints could fail to glue, what validator or reviewer will catch that
failure, and which owner accepts the remaining residue.

### Plain-Language Intuition

An edge can either force a value or freely loop around the graph. If it does
both, stop and prove the loop is safe before it becomes a rule.

### Domain-Context Voice

In CyberAlchemy v2, the TO-VLAD AX-ONT review killed the attempted bridge from
Shannon-style classification orthogonality to Lean Hilbert/projector
orthogonality. The reusable residue is this edge-layer guard: coupling lives in
relations, so the first dangerous place is an edge that both constrains values
and may cycle. CAV2 keeps that condition explicit instead of letting a future
schema change create contextuality-like residue by accident.

### Boundary

Value-cycle edge guard is not a contextuality theorem, not a spectral-presheaf
checker, not a ban on cyclic non-value relations, and not a ban on acyclic
value constraints. It does not promote any live vault edge family. It only says
which edge proposals must be stopped for schema governance and obstruction
review.

### Primary Consumers

- [../constitutions/STABLE-REPOSITORY-CONSTITUTION.md](../constitutions/STABLE-REPOSITORY-CONSTITUTION.md)
- [../../ontology/RELATION-MODEL.md](../../ontology/RELATION-MODEL.md)
- [../../TO-VLAD/TO-VLAD.md](../../TO-VLAD/TO-VLAD.md)
- [../../TO-VLAD/RESOLUTION.md](../../TO-VLAD/RESOLUTION.md)

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

## CAV2-D30: Bounded Recursive Self-Application

Status: active
Term: bounded recursive self-application
Aliases: recursivity, bounded recursivity, recursive self-application, process recursion, altitude-bounded recursion

### Normative Definition

Bounded recursive self-application is the CyberAlchemy v2 invariant that a
governed process may be applied to artifacts produced by that same process only
when each recursive step declares its artifact, altitude or layer, scope, owner,
gate, carried state or residue, recomposition path, and stopping condition.

The recursive move must preserve authority boundaries: the process, the artifact
being processed, the owner route, and the resulting authority posture must remain
distinct unless an explicit promotion or coupling records otherwise.

### Formal Interpretation

Given a governed process `P`, an artifact `a_n` already produced, shaped, or
maintained by `P`, and an altitude marker `h_n`, a valid recursive
self-application step has the form:

```text
P_hn(a_n) -> a_(n+1) at h_(n+1)
```

The step is admissible only if it records:

- source artifact `a_n`
- target artifact `a_(n+1)`
- altitude or layer relation between `h_n` and `h_(n+1)`
- owner route
- gate or validation condition
- residue or state carried forward
- recomposition path back to the lower artifact or parent context
- stopping condition, budget, or explicit next owner

Without those fields, the move is ordinary recursion, self-hosting, looped work,
or open residue, not CyberAlchemy v2 recursivity.

### Operational Interpretation

Use bounded recursive self-application when definitions-governance defines
definition work, Craft records and routes work about Craft, CyberAlchemy applies
its method to CyberAlchemy method artifacts, or a tower creates a higher-layer
artifact that must explain back down to its source.

The action must answer: what artifact is the method operating on, at what
altitude, under which owner and gate, what residue or state is carried, how the
result recomposes with the source, and where the recursion stops or hands off.

### Plain-Language Intuition

The system can use its own method on its own work, but each loop needs a label,
a boundary, a reviewer, and a way back.

### Domain-Context Voice

In CyberAlchemy v2, this definition resolves the earlier `recursivity` candidate
by promoting the bounded form rather than the vague label. It sits beside
`CAV2-D17` reflection tower method and `CAV2-D20` Craft method: reflection tower
names the residue-to-higher-layer move, Craft method names the recursive ledger
discipline, and bounded recursive self-application names the cross-method
invariant that lets a governed method operate on its own artifacts without
collapsing authority surfaces.

This definition partially unblocks the ledger primitive review: `recursivity`
now has a local meaning, but ledger promotion still depends on inheritance
relations and local Craft ledger conformance.

### Boundary

Bounded recursive self-application is not ordinary code recursion, not generic
self-hosting, not endless reflection, not child-folder nesting, not automatic
promotion, and not a license to run agents recursively without a budget. It does
not replace `CAV2-D17` reflection tower method or `CAV2-D20` Craft method; it
governs when process-on-own-artifact moves are admissible across those and
other methods.

### Primary Consumers

- [source-clusters/primordial.md](source-clusters/primordial.md)
- [reviews/ledger-primitive-review.md](reviews/ledger-primitive-review.md)
- [DEFINITION-TOWERS.md](DEFINITION-TOWERS.md)
- [../../CRAFT.md](../../CRAFT.md)
- [../../development/research/2026-06-21-recursivity-promotion-verdict/findings.md](../../development/research/2026-06-21-recursivity-promotion-verdict/findings.md)

## CAV2-D31: Primitive Type

Status: active
Term: primitive type
Aliases: semantic primitive type, primitive semantic type, base semantic object, semantic primitive

### Normative Definition

A primitive type is a CyberAlchemy v2 base semantic kind that lower definitions,
methods, constitutions, disciplines, schemas, ontology records, or execution
artifacts may reference without deriving its meaning from a narrower source
space, implementation layer, project glossary, or generated representation.

To count as a primitive type, the term must declare its stable name, authority
scope, allowed consumers, source-evidence boundary, relation to any external
authority term, and the condition under which lower layers may specialize it.
Lower layers may instantiate, specialize, or compose a primitive type, but they
must not silently redefine it.

### Formal Interpretation

For a CyberAlchemy v2 term `t`, `primitive_type(t)` is admissible only when:

```text
authority_scope(t) = CAV2
owner(t) = definitions-governance
derived_from_narrower_source_space(t) = false
boundary(t) is declared
consumer_surface(t) is declared
specialization_rule(t) is declared
```

If `t` is borrowed from an external authority, the primitive claim applies only
to CyberAlchemy v2's local role for `t`, not to the external authority's whole
meaning.

### Operational Interpretation

Use this term when deciding whether a candidate belongs in the primordial basis
rather than a lower tower. A primitive type should be small enough for multiple
towers to reuse, but strict enough that lower artifacts cannot stretch it by
vibe, proximity, or repeated use.

### Plain-Language Intuition

A primitive type is a base kind the project is allowed to build with before it
builds narrower things.

### Domain-Context Voice

In CyberAlchemy v2, primitive type names the role played by local bases such as
axis orthogonality, bounded recursive self-application, residue, method, and
definition. It also keeps CAV2 local primitives separate from DomainSpec
meta-types, Arcanum schema/contract terms, programming types, and ontology node
types. Those may be evidence or external references, but they become CAV2
primitive types only when this file re-authors the local semantic role.

### Boundary

Primitive type is not a programming-language primitive, not a database field
type, not a schema class, not a DomainSpec `DS-D1` meta-type, not a source
glossary label, and not automatic authority for any term called "primitive" in
another folder.

### Primary Consumers

- [source-clusters/primordial.md](source-clusters/primordial.md)
- [DEFINITION-TOWERS.md](DEFINITION-TOWERS.md)
- [DEFINITION-LOCALIZATION-ROUTE.md](DEFINITION-LOCALIZATION-ROUTE.md)
- [../../CRAFT.md](../../CRAFT.md)

## CAV2-D32: Method

Status: active
Term: method
Aliases: governed method, method primitive, repeatable governance method
Ancestral provenance (non-normative): generic descendant of the CyberAlchemy Method ([`arcanum/framework/CYBERALCHEMY-METHOD.md`](../../../arcanum/framework/CYBERALCHEMY-METHOD.md), 5 anchors). Evidence posture — not deployed. See [DEFINITION-DRIFT-AUDIT.md](DEFINITION-DRIFT-AUDIT.md) § Ancestral Lineage Reconciliation.

### Normative Definition

A method is a governed repeatable way to transform intent, source evidence,
state, or residue into artifacts and continued work under declared roles,
actions or phases, gates, validation conditions, residue handling, provenance,
and recomposition or evolution rules.

A method may be instantiated by a narrower named method, such as `CAV2-D17`
reflection tower method, `CAV2-D20` Craft method, or `CAV2-D21` four-facet
action method. The generic term names the umbrella role; each concrete method
must still declare its own scope, inputs, outputs, gates, and boundaries.

### Formal Interpretation

For a method `M`, an admissible CyberAlchemy v2 method record has at least:

```text
M = (scope, inputs, actions, roles, gates, outputs, evidence,
     residue_rule, validation_rule, recomposition_rule, boundary)
```

The method is repeatable when another execution can identify which fields are
being reused, which are being specialized, and which residue remains open.

### Operational Interpretation

Use this term when deciding whether a repeated CyberAlchemy move is merely a
task habit, an implementation pipeline, a technique, a lifecycle label, or a
governed method. A method can use engines, pipelines, checklists, ledgers,
schemas, agents, or workflows, but it is not identical to any one of them
unless the concrete definition says so.

### Plain-Language Intuition

A method is the repeatable way the project turns intent and evidence into work
that can be checked, carried forward, and improved.

### Domain-Context Voice

In CyberAlchemy v2, method is the umbrella term that lets the project compare
the CyberAlchemy Method source material, Craft method, reflection tower method,
four-facet action method, promotion routes, and later runtime workflows without
collapsing them into one pipeline. This is why `method` belongs in the
primordial basis: lower towers can build their own methods, but their method
claims must remain explicit and reviewable.

### Boundary

Method is not a single technique, not a one-off task, not a mere checklist, not
an engine, not a pipeline, not a lifecycle state, and not authority by itself.
Authority comes from the owner surface and gate that admit a method into a
particular use.

### Primary Consumers

- [source-clusters/primordial.md](source-clusters/primordial.md)
- [DEFINITION-TOWERS.md](DEFINITION-TOWERS.md)
- [../../CRAFT.md](../../CRAFT.md)
- [../../../arcanum/framework/CYBERALCHEMY-METHOD.md](../../../arcanum/framework/CYBERALCHEMY-METHOD.md)

## CAV2-D33: Definition

Status: active
Term: definition
Aliases: governed definition, canonical definition, definition unit, semantic definition unit

### Normative Definition

A definition is a governed semantic unit that assigns a term its normative
meaning inside a declared authority scope, with a stable identifier when the
scope uses identifiers, a status, aliases, colocated definition voices,
boundaries, source or provenance references, primary consumers, index presence,
and a drift route.

In CyberAlchemy v2, a candidate row, glossary note, source quote, research
finding, inventory card, generated index entry, or narrative explanation is not
a definition until definitions-governance promotes or updates it in the
canonical definitions source.

### Formal Interpretation

An admissible CyberAlchemy v2 definition record has the shape:

```text
Definition =
  (id, term, status, aliases, normative_voice, plain_language_voice,
   domain_context_voice, boundary, provenance_or_sources,
   consumers, index_entry, drift_route)
```

The normative voice determines meaning. Plain-language and domain-context
voices explain and locate the term, but they do not override the normative
voice.

### Operational Interpretation

Use this term when deciding whether a piece of wording is allowed to govern
CyberAlchemy v2 semantics. If a term is only represented in a source cluster,
inventory card, tower map, handoff, or discussion, it is still candidate
material. To become a definition, it must enter this file with the required
voices and synchronized lookup surfaces.

### Plain-Language Intuition

A definition is the place where a term is finally allowed to mean something for
this project.

### Domain-Context Voice

In CyberAlchemy v2, definition keeps the v2 authority surface honest while the
project imports scattered vocabulary from Arcanum, DomainSpec, prior
CyberAlchemy work, framework-unification, vaults, research, and validation
evidence. The project may localize all of that material for search and Craft
execution, but only this definitions surface can make a CyberAlchemy v2 term
canonical.

### Boundary

Definition is not a glossary hint, not a candidate source-cluster row, not a
research claim, not an inventory evidence card, not an ontology node by itself,
not a generated lookup row, and not a comment thread. Those surfaces may supply
evidence or navigation, but they cannot silently redefine a canonical term.

### Primary Consumers

- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- [source-clusters/primordial.md](source-clusters/primordial.md)
- [DEFINITION-DRIFT-AUDIT.md](DEFINITION-DRIFT-AUDIT.md)
- [DEFINITION-LOCALIZATION-ROUTE.md](DEFINITION-LOCALIZATION-ROUTE.md)
- [../../CRAFT.md](../../CRAFT.md)

## CAV2-D34: Authority

Status: active
Term: authority
Aliases: normative authority, decision authority, authority primitive
Ancestral provenance (non-normative): re-authors the owner-route principle of the CyberAlchemy Method's "Route" anchor ([`arcanum/framework/CYBERALCHEMY-METHOD.md`](../../../arcanum/framework/CYBERALCHEMY-METHOD.md)). Evidence posture — not deployed. See [DEFINITION-DRIFT-AUDIT.md](DEFINITION-DRIFT-AUDIT.md) § Ancestral Lineage Reconciliation.

### Normative Definition

Authority is the scoped right or responsibility to let a term, rule, status,
artifact, relation, gate result, validation result, or mutation count for a
declared CyberAlchemy v2 purpose.

An authority claim is valid only when it names the scope, owner or owner route,
authority surface, governed object, allowed operation, evidence or decision
basis, effect, and challenge or drift route. Authority may decide what counts
inside its scope, but it does not automatically transfer across scopes,
surfaces, owners, generated mirrors, or source spaces.

### Formal Interpretation

For an authority claim `A` over object `x`, CyberAlchemy v2 requires:

```text
A(x) = (scope, owner, surface, object, operation, basis, effect, challenge_route)
```

The claim is admissible only if `scope`, `owner`, `surface`, `operation`, and
`effect` are explicit. If any field is implicit, the authority claim becomes
candidate evidence or residue, not governing authority.

### Operational Interpretation

Use authority whenever a source, file, owner, process, gate, validator, or
generated view would make something count. Ask: count for what scope, by which
owner, through which surface, with which operation, and with what effect?

### Plain-Language Intuition

Authority is the project's answer to "who or what is allowed to make this
count, and only for which purpose?"

### Domain-Context Voice

In CyberAlchemy v2, authority is the base term under existing local surfaces
such as `CAV2-D3` authority layer, `CAV2-D13` authority promotion queue, and
`CAV2-D23` authority lifecycle axis. It protects the stable repository from
letting file proximity, generated indexes, ontology projections, inventory
cards, source truth, or repeated usage silently become CyberAlchemy v2 canon.

### Boundary

Authority is not truth, confidence, maturity, popularity, file ownership,
repository access, generated status, or implementation success. It may cite
evidence and may be implemented by access controls, but neither evidence nor
access control becomes authority without the scoped owner route.

### Primary Consumers

- [DEFINITION-TOWERS.md](DEFINITION-TOWERS.md)
- [source-clusters/primordial.md](source-clusters/primordial.md)
- [../promotion-policy.md](../promotion-policy.md)
- [../../CRAFT.md](../../CRAFT.md)

## CAV2-D35: Provenance

Status: active
Term: provenance
Aliases: source provenance, origin chain, provenance chain, source chain

### Normative Definition

Provenance is the declared origin and transformation chain for a term, artifact,
claim, rule, decision, relation, validation result, or residue. It records where
the object came from, which sources or prior objects it depends on, which
operations changed it, which owners or processes handled it, and which
authority posture it held at each relevant step.

Provenance must identify source references and relation types with enough
precision that a later reviewer can distinguish source evidence, local
adaptation, promotion, demotion, translation, derivation, validation, and
generated projection.

### Formal Interpretation

For object `x`, provenance is a typed path:

```text
Prov(x) = [(source_i, relation_i, operation_i, owner_i, posture_i)]*
```

The path may be incomplete only if the missing segment is explicitly recorded
as residue with an owner route. Untyped "came from" language is not sufficient
for authority-bearing use.

### Operational Interpretation

Use provenance before promoting, adapting, importing, validating, or publishing
anything. Provenance answers what source material is being used, what happened
to it, and where the current object should be audited if it drifts.

### Plain-Language Intuition

Provenance is the receipt trail for where something came from and how it got
here.

### Domain-Context Voice

In CyberAlchemy v2, provenance is the lower-level basis for
`CAV2-D24` provenance-first navigation, authority imports, source clusters,
inventory evidence cards, Craft links, handoffs, and future extraction review.
It lets v2 import scattered work without flattening source ownership or
pretending that source evidence has already become local authority.

### Boundary

Provenance is not proof, not authority, not trust, not validation, and not
credit assignment by itself. A perfect source trail can still point to a false,
unpromoted, private, or unusable claim. It only tells the project where meaning
and transformations came from.

### Primary Consumers

- [DEFINITION-TOWERS.md](DEFINITION-TOWERS.md)
- [source-clusters/primordial.md](source-clusters/primordial.md)
- [../imports/definitions/MANIFEST.md](../imports/definitions/MANIFEST.md)
- [../../SOURCE-MAP.md](../../SOURCE-MAP.md)
- [../../CRAFT.md](../../CRAFT.md)

## CAV2-D36: Traceability

Status: active
Term: traceability
Aliases: traceable chain, traceable linkage, lifecycle traceability

### Normative Definition

Traceability is the ability to follow explicit, typed links across intent,
source evidence, provenance, definitions, rules, methods, artifacts, gates,
validation, decisions, residue, and next routes so that a later human or agent
can answer why something exists, what it depends on, what it affects, and where
to continue.

Traceability is satisfied only when the relevant chain has enough link targets,
relation types, authority postures, and residue markers to be traversed without
hidden conversation context.

### Formal Interpretation

For a work object `x` and a review question `q`, traceability holds when there
is a declared path:

```text
trace_q(x) = x -> link_1 -> link_2 -> ... -> answer_or_residue
```

Each `link_i` must have a target, relation type, and authority posture. If the
path breaks, the break must be recorded as typed residue or a named gap.

### Operational Interpretation

Use traceability when deciding whether CyberAlchemy v2 is navigable enough to
resume, validate, publish, extract, or hand off. It is the check that source
receipts, definitions, Craft state, decisions, and validation evidence are
connected rather than merely present.

### Plain-Language Intuition

Traceability means you can follow the thread from "why are we doing this?" to
"what changed?" to "what happens next?"

### Domain-Context Voice

In CyberAlchemy v2, traceability turns the stable repository objective into a
navigation requirement. It binds CAV2 definitions, source clusters, import
manifests, Craft contexts, inventory cards, ontology projections, handoffs, and
validation evidence into routes that future work can traverse without replaying
the original conversation.

### Boundary

Traceability is not the same as provenance. Provenance records origin and
transformation history; traceability tests whether the project can navigate the
relevant links for a question. Traceability is also not proof, completeness, or
approval.

### Primary Consumers

- [DEFINITION-TOWERS.md](DEFINITION-TOWERS.md)
- [source-clusters/primordial.md](source-clusters/primordial.md)
- [../../CRAFT.md](../../CRAFT.md)
- [../../TO-VLAD/SESSION-HANDOFF-cav2-primordial-basis.md](../../TO-VLAD/SESSION-HANDOFF-cav2-primordial-basis.md)

## CAV2-D37: Gate

Status: active
Term: gate
Aliases: governance gate, review gate, decision gate, admission gate

### Normative Definition

A gate is an explicit checkpoint that decides or routes whether a candidate
term, rule, artifact, relation, method, claim, mutation, or execution may
continue, must continue with named risk, must stop, or must defer to another
owner.

Every CyberAlchemy v2 gate must declare its owner route, scope, inputs,
criteria, possible verdicts, required evidence, residue handling, record
location, and downstream effect. Unless a narrower gate defines otherwise, the
minimum verdict vocabulary is `pass`, `flag`, `block`, and `defer`.

### Formal Interpretation

A gate `G` is a decision function:

```text
G(scope, input, evidence, criteria) -> verdict
verdict in {pass, flag, block, defer}
```

The verdict is admissible only if it records owner route, evidence basis,
residue or risk when present, and downstream effect.

### Operational Interpretation

Use gate for any controlled transition: promotion, schema amendment,
implementation mutation, validation acceptance, source import, extraction,
public/private boundary movement, or recursive method step. A gate is the place
where ambiguity either receives permission, receives risk, stops, or changes
owner.

### Plain-Language Intuition

A gate is the checkpoint that says "go", "go with this named risk", "stop", or
"send this to the right owner first."

### Domain-Context Voice

In CyberAlchemy v2, gate is the generic primitive under `CAV2-D5` promotion
gate, schema amendment checks, Craft blockers, decision-gate routes, validation
checks, and the pass/flag/block behavior used across research and handoff
surfaces. It keeps consequential movement explicit instead of implied by a file
edit or successful generation.

### Boundary

Gate is not bureaucracy, not a checklist item by itself, not permission without
a record, and not proof of correctness. A gate may use validators or human
decisions, but the gate is the recorded transition logic and effect.

### Primary Consumers

- [DEFINITION-TOWERS.md](DEFINITION-TOWERS.md)
- [source-clusters/primordial.md](source-clusters/primordial.md)
- [../promotion-policy.md](../promotion-policy.md)
- [../../CRAFT.md](../../CRAFT.md)

## CAV2-D38: Claim-Proof Bound

Status: active
Term: claim <= proof
Aliases: claim-proof bound, claim proof invariant, evidence-bounded claim, proof-bounded claim

### Normative Definition

Claim <= proof is the CyberAlchemy v2 epistemic invariant that a claim's
asserted strength, authority effect, validation status, or publication posture
must not exceed the proof, evidence, witness, validation result, owner decision,
or accepted premise cited for it.

If support is absent, partial, private, indirect, disputed, or weaker than the
claim, the claim must be downgraded, marked as hypothesis or candidate,
flagged with residue, routed through a gate, or blocked from governing work.

### Formal Interpretation

For claim `c`, asserted strength `S(c)`, and support package `P(c)`:

```text
S(c) <= strength(P(c))
```

where `strength(P(c))` is interpreted by the relevant domain, validator,
research standard, owner decision, or constitution. If no support package is
declared, `S(c)` defaults to candidate or hypothesis.

### Operational Interpretation

Use claim <= proof when writing research findings, definitions, constitutions,
validation reports, ontology projections, public statements, or implementation
readiness notes. The invariant forces the project to ask: what exactly supports
this claim, and how strong may the wording be?

### Plain-Language Intuition

Do not say more than the evidence can carry.

### Domain-Context Voice

In CyberAlchemy v2, claim <= proof prevents research synthesis, inventory
cards, ontology projections, generated indexes, successful commands, or owner
intuition from hardening into stronger authority than they earned. It is the
epistemic companion to provenance and gates: provenance shows the support
trail, gates decide movement, and claim <= proof bounds what the project is
allowed to say.

### Boundary

Proof does not mean only formal mathematical proof. It can be a source citation,
validation run, witness, owner decision, accepted premise, or formal proof,
depending on the claim type. The invariant does not require maximal certainty;
it requires honest wording relative to declared support.

### Primary Consumers

- [DEFINITION-TOWERS.md](DEFINITION-TOWERS.md)
- [source-clusters/primordial.md](source-clusters/primordial.md)
- [../../CRAFT.md](../../CRAFT.md)
- [../../../projects/framework-unification/CONCEPT-MAP.md](../../../projects/framework-unification/CONCEPT-MAP.md)

## CAV2-D39: Intent

Status: active
Term: intent
Aliases: human intent, work intent, governed intent, source intent

### Normative Definition

Intent is the declared purpose, desired capability, problem pressure, or change
direction that orients a CyberAlchemy v2 method before the exact output shape,
artifact, gate, or implementation path is fully settled.

Intent must be attributable, bounded enough to route, revisable under discovery,
and traceable to the artifacts, decisions, residue, or next routes that claim to
satisfy it. An intent may be refined, split, renamed, or rejected, but it must
not be silently replaced by an artifact or implementation convenience.

### Formal Interpretation

An admissible intent record has at least:

```text
Intent = (source, purpose, scope, constraints, target_pressure,
          current_output_hypothesis, revision_route)
```

The `current_output_hypothesis` may change as discovery proceeds. The intent
remains traceable only if the revision route records why the output changed.

### Operational Interpretation

Use intent at the start of definition, design, research, planning,
implementation, validation, or handoff work. Intent keeps the work oriented
while discovery decides whether the right output is a definition, constitution,
method, work-pack, validation report, code change, or deferred question.

### Plain-Language Intuition

Intent is what the work is trying to make possible before we know the final
shape.

### Domain-Context Voice

In CyberAlchemy v2, intent is the first input to the method stack: user
corrections, stable repository objectives, definition-promotion requests,
research questions, and handoff prompts all become governable when their intent
is named and traceable. This lets the project preserve why a definition or
route exists without treating the initial wording as immutable.

### Boundary

Intent is not a requirement, not an artifact, not proof, not a command to
mutate, and not automatic scope approval. It orients work; gates, authority,
evidence, and later artifact definitions decide what can count.

### Primary Consumers

- [DEFINITION-TOWERS.md](DEFINITION-TOWERS.md)
- [source-clusters/primordial.md](source-clusters/primordial.md)
- [../../CRAFT.md](../../CRAFT.md)
- [../../../arcanum/framework/CYBERALCHEMY-METHOD.md](../../../arcanum/framework/CYBERALCHEMY-METHOD.md)

## CAV2-D40: Challenge Contract

Status: active
Term: challenge contract
Aliases: challenge_contract, challenge response contract, contestability contract, contradiction review contract

### Normative Definition

A challenge contract is the explicit review surface attached to a
CyberAlchemy v2 node, candidate, claim, or authority artifact that states how
the object may be challenged, contradicted, validated, blocked, or routed for
owner review without silently changing its meaning or confidence.

A challenge contract must declare the valid challenge response, admissible
challenge modes, contradiction and validation links when present, owner route,
resolution gate, blocking questions, and challenge residue route. It does not
contain the object's own confidence or residue and does not introduce a third
confidence axis. Object confidence remains a sibling posture using the
`evidence_confidence` and `commitment_confidence` split governed by `CAV2-D23`.

### Formal Interpretation

An admissible challenge contract has at least:

```text
ChallengeContract =
  (challenge_response, valid_challenge_modes, contradiction_edges,
   validation_edges, owner_route, resolution_gate, blocking_questions,
   challenge_residue_route)
```

where `challenge_residue_route` says where unresolved challenge residue is
handled. The object's own confidence and residue are not part of the challenge
contract. When an object records confidence, active CyberAlchemy v2 uses
`evidence_confidence` for evidence support and `commitment_confidence` for
commitment posture.

### Operational Interpretation

Use challenge contract when a candidate ontology node, projection, definition
proposal, constitution proposal, research claim, or authority artifact needs to
say what kind of objection is valid and what happens next. A contradiction
edge may block promotion; a validation edge may increase evidence support; a
blocking question may defer the node; and unresolved challenge residue must
remain attached until an owner route closes, waives, or demotes it.

### Plain-Language Intuition

It is the object's "how to disagree with me correctly" field.

### Domain-Context Voice

In CyberAlchemy v2, challenge contract belongs on the ontology candidate node
shape before candidate concepts become load-bearing. It lets the project reuse
challenge responses, `contradicts` and `validates` edges, owner routes, gates,
and residue routing while node confidence remains outside the contract as
`evidence_confidence` and `commitment_confidence`. It is the schema-level answer
to the question: if this node is challenged, who reviews it, with which
evidence, and where does the challenge residue go?

### Boundary

Challenge contract is not a verdict, not a confidence score, not proof of
truth, not a promotion decision, and not an ontology-owned override of the
relevant owner route. It names the challenge path; owner routes and gates still
decide movement.

### Primary Consumers

- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- [../../ontology/NODE-MODEL.md](../../ontology/NODE-MODEL.md)
- [../../ontology/PACKAGE-MODEL.md](../../ontology/PACKAGE-MODEL.md)
- [../../ontology/LIFECYCLE-MODEL.md](../../ontology/LIFECYCLE-MODEL.md)
- [../imports/house_project/docs/vault/ontology-conventions.md](../imports/house_project/docs/vault/ontology-conventions.md)
- [../imports/house_project/docs/vault/premise/ontology-premises.md](../imports/house_project/docs/vault/premise/ontology-premises.md)

## CAV2-D41: Authority Model

Status: active
Term: authority model
Aliases: CAV2 authority model, project authority model, owner-route model, authority routing model
Ancestral provenance (non-normative): the owner-route traffic map re-authors the CyberAlchemy Method's "Route" anchor ([`arcanum/framework/CYBERALCHEMY-METHOD.md`](../../../arcanum/framework/CYBERALCHEMY-METHOD.md)). Evidence posture — not deployed. See [DEFINITION-DRIFT-AUDIT.md](DEFINITION-DRIFT-AUDIT.md) § Ancestral Lineage Reconciliation.

### Normative Definition

An authority model is the governed structure that classifies candidate material by
authority kind, reliance posture, owner route, admissible movement, gate
vocabulary, validation surface, and non-collapse rule so CyberAlchemy v2 can
decide what may count for which purpose without letting evidence, ontology,
research, generated projections, implementation success, or narrative repetition
silently become authority.

An authority model must name the authority surfaces it coordinates, the route
that owns each kind of promotion, the states or postures a candidate may occupy,
the gates that control movement between states, and the boundary conditions that
prevent one authority layer from overriding another.

### Formal Interpretation

For a candidate object `x`, a CyberAlchemy v2 authority model provides a routing
function:

```text
A(x) =
  (kind, posture, owner_route, allowed_use, blocked_use,
   gate, validation_surface, non_collapse_rules)
```

Movement is admissible only when the responsible `owner_route` records a gate
verdict and the candidate's `allowed_use` covers the intended downstream effect.
If a candidate crosses from evidence or model into local authority, the model
requires a promotion gate rather than implied authority by proximity.

### Operational Interpretation

Use authority model when deciding whether a source fragment, definition
candidate, ontology node, research finding, discipline, constitution rule,
decision, spec, runtime contract, generated projection, validation result, or
implementation artifact is allowed to influence CyberAlchemy v2 work.

The authority model answers: what kind of thing is this, what may we rely on it
for, who owns the next move, which gate must run, and what must not be collapsed
into what?

### Plain-Language Intuition

The authority model is the traffic map for what is allowed to count, who can make
it count, and what it must not be confused with.

### Domain-Context Voice

In CyberAlchemy v2, the authority model is authored in
[../AUTHORITY-MODEL.md](../AUTHORITY-MODEL.md). It coordinates definitions,
constitutions, disciplines, decisions, promotion policy, boundaries, ontology
candidate views, inventory evidence, validation traces, and future implementation
work. It turns the stable-repository objective into an owner-routed contract:
ontology can model authority, inventory can preserve evidence, disciplines can
name recurring practices, and constitutions can enforce scoped rules, but each
promotion still needs the responsible owner route.

### Boundary

Authority model is not ontology by itself, not a schema by itself, not a
decision, not access control, not proof, not a universal constitution, and not a
license to promote all modeled material. It coordinates authority movement; the
responsible owner routes still make the actual promotion decisions.

### Primary Consumers

- [../AUTHORITY-MODEL.md](../AUTHORITY-MODEL.md)
- [../README.md](../README.md)
- [../promotion-policy.md](../promotion-policy.md)
- [../../ontology/AUTHORITY-KINDS.md](../../ontology/AUTHORITY-KINDS.md)
- [../../ontology/AUTHORITY-POSTURES.md](../../ontology/AUTHORITY-POSTURES.md)
- [../constitutions/STABLE-REPOSITORY-CONSTITUTION.md](../constitutions/STABLE-REPOSITORY-CONSTITUTION.md)

## CAV2-D42: Governed Artifact Tree

Status: active
Term: governed artifact tree
Aliases: artifact tree governance interface, governed tree interface, load-bearing artifact tree

### Normative Definition

A governed artifact tree is a load-bearing artifact tree that exposes the
governance interface required before its contents can promote knowledge,
constrain future work, or become a reusable authority surface.

At minimum, the tree must declare:

- owner route
- canonical source or source boundary
- view roles
- evidence inputs
- promotion path
- validation surface
- challenge contract
- drift route
- allowed uses and blocked uses

The tree makes a concept inspectable. It does not make the concept
authoritative by itself. Authority still requires the relevant owner route,
gate, evidence, and promotion decision.

### Formal Interpretation

For artifact tree `T`, a CyberAlchemy v2 governed artifact tree is admissible
only when:

```text
GAT(T) =
  (tree_id, scope, owner_route, canonical_source, view_roles,
   evidence_inputs, promotion_path, validation_surface,
   challenge_contract, drift_route, allowed_use, blocked_use)
```

If any field is absent, `T` may still be useful context or a draft view, but it
cannot promote knowledge, constrain downstream work, or act as a reusable
authority surface without typed residue and owner review.

### Operational Interpretation

Use governed artifact tree when a folder, package, view, pattern library,
ontology branch, architecture tree, validation tree, or other artifact set is
becoming load-bearing. Before downstream work relies on the tree, ask: who owns
it, what does it cite, what view does it provide, what evidence feeds it, how
can it be promoted, how can it be checked, how can it be challenged, and who
handles drift?

### Plain-Language Intuition

A tree is allowed to organize serious work only after it shows who owns it,
what it can prove, and how to disagree with it.

### Domain-Context Voice

In CyberAlchemy v2, `architecture-pattern-inventory` is the architecture-facing
producer of governed artifact trees for architecture knowledge. It can produce
concept cards, relationship cards, dependency rules, testing alignment,
observability alignment, and pattern candidates. It is not the authority owner
by itself; it hands pattern candidates and evidence packages to the
CyberAlchemy authority model, definitions-governance, constitution-governance,
or the relevant owner route.

### Boundary

Governed artifact tree is not a primitive object type, not an ontology node
type, not a promotion event, not an owner decision, and not authority by file
proximity. It is an inspectable interface obligation on a load-bearing tree.

### Primary Consumers

- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- [DEFINITION-TOWERS.md](DEFINITION-TOWERS.md)
- [DEFINITION-DRIFT-AUDIT.md](DEFINITION-DRIFT-AUDIT.md)
- [../constitutions/STABLE-REPOSITORY-CONSTITUTION.md](../constitutions/STABLE-REPOSITORY-CONSTITUTION.md)
- [../../architecture/ARCHITECTURE-KNOWLEDGE-GOVERNANCE.md](../../architecture/ARCHITECTURE-KNOWLEDGE-GOVERNANCE.md)
- [../../../arcanum/arcana/architecture-pattern-inventory/SKILL.md](../../../arcanum/arcana/architecture-pattern-inventory/SKILL.md)

## CAV2-D43: Pattern Promotion Lifecycle

Status: active
Term: pattern promotion lifecycle
Aliases: architecture pattern promotion lifecycle, pattern authority lifecycle, reusable pattern promotion path
Ancestral provenance (non-normative): shares the promotion shape of the Arcanum Discipline Growth Rule ([`arcanum/disciplines/DISCIPLINES.md`](../../../arcanum/disciplines/DISCIPLINES.md)) but governs architecture patterns, NOT disciplines. Evidence posture — not deployed. See [DEFINITION-DRIFT-AUDIT.md](DEFINITION-DRIFT-AUDIT.md) § Ancestral Lineage Reconciliation.

### Normative Definition

Pattern promotion lifecycle is the CyberAlchemy v2 lifecycle by which an
operational, code, design, or specification hypothesis becomes a reusable
architecture pattern authority only after evidence, generalization,
cross-context exercise, challenge, and owner promotion.

The normal path is:

```text
operational/code/spec hypothesis
  -> exercised in domain
  -> evidence set
  -> localized concept
  -> generalized abstraction
  -> pattern candidate
  -> exercised in another context
  -> challenge and residue review
  -> owner promotion
  -> architecture pattern authority
  -> invariant or constitution pressure when justified
```

A pattern is not born authoritative. Evidence can raise confidence; only the
responsible owner route can promote the pattern's authority effect.

### Formal Interpretation

For candidate concept `c`, pattern promotion lifecycle tracks:

```text
PPL(c) =
  (hypothesis, domain_exercise, evidence_set, local_concept,
   abstraction, pattern_candidate, cross_context_exercise,
   challenge_contract, owner_decision, authority_effect, residue)
```

Movement from `pattern_candidate` to `architecture pattern authority` is valid
only when the owner decision declares the authority effect and the claim strength
does not exceed the evidence set.

### Operational Interpretation

Use pattern promotion lifecycle when architecture knowledge emerges from
operations, code, specs, tests, observability, UX lessons, or repeated domain
work. It turns operations into an evidence engine for knowledge promotion
without treating successful execution as promotion by itself.

### Plain-Language Intuition

A pattern earns authority by working, being generalized, being challenged, and
being accepted by the owner route.

### Domain-Context Voice

In CyberAlchemy v2, architecture-pattern-inventory should capture the early and
middle stages of this lifecycle: evidence, localized concepts, generalized
abstractions, pattern candidates, relationship cards, dependency rules, testing
alignment, and observability alignment. CyberAlchemy authority then decides
whether the candidate becomes a reusable pattern authority or creates invariant
or constitution pressure.

### Boundary

Pattern promotion lifecycle is not automatic generalization, not popularity,
not code reuse alone, not an architecture decision record by itself, and not a
shortcut around `CAV2-D21`, `CAV2-D23`, `CAV2-D34`, `CAV2-D38`, or `CAV2-D40`.
When a pattern is promoted for CAV2-wide reuse, it also inherits `CAV2-D48`'s
separation between CAV2 promotion and each domain's version-exact adoption.

### Primary Consumers

- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- [DEFINITION-TOWERS.md](DEFINITION-TOWERS.md)
- [DEFINITION-DRIFT-AUDIT.md](DEFINITION-DRIFT-AUDIT.md)
- [../constitutions/STABLE-REPOSITORY-CONSTITUTION.md](../constitutions/STABLE-REPOSITORY-CONSTITUTION.md)
- [../../architecture/ARCHITECTURE-KNOWLEDGE-GOVERNANCE.md](../../architecture/ARCHITECTURE-KNOWLEDGE-GOVERNANCE.md)
- [../../../arcanum/arcana/architecture-pattern-inventory/SKILL.md](../../../arcanum/arcana/architecture-pattern-inventory/SKILL.md)

## CAV2-D44: View-Bearing Concept

Status: active
Term: view-bearing concept
Aliases: load-bearing view concept, concept with governed view, view-bearing authority candidate

### Normative Definition

A view-bearing concept is a load-bearing concept that needs its own governed
view or tree because it has distinct evidence, lifecycle posture, owner route,
reuse surface, and challenge/drift behavior that cannot be safely handled as
ordinary narrative vocabulary.

Not every term deserves a view. A concept may become view-bearing only when the
view helps preserve evidence, relations, lifecycle, owner route, reuse, or
challenge behavior without pretending to decide authority by itself.

### Formal Interpretation

For concept `c`, `view_bearing(c)` is admissible when:

```text
view_bearing(c) =
  distinct_evidence(c)
  and lifecycle_posture_needed(c)
  and owner_route(c)
  and reuse_surface(c)
  and challenge_or_drift_route(c)
```

The view attached to `c` must declare allowed readings and forbidden authority
moves. If those fields are absent, `c` remains a term, candidate, or local
concept rather than a view-bearing concept.

### Operational Interpretation

Use view-bearing concept when a concept starts carrying enough work that future
agents need a dedicated lens over its meaning, system structure, run evidence,
residue, or promotion status. The view should make the concept inspectable and
usable without loading the whole repository.

### Plain-Language Intuition

Some ideas become important enough to need their own dashboard, but the
dashboard still does not get to make the decision.

### Domain-Context Voice

In CyberAlchemy v2, ontology is becoming a set of governed views over
knowledge. A view-bearing concept can support meaning views, architecture
views, run views, residue/challenge views, and promotion views. For
architecture specifically, architecture-pattern-inventory is the architecture
view interface that turns architecture evidence into reusable candidates before
CyberAlchemy authority decides promotion.

### Boundary

View-bearing concept is not a vault node type, not an ontology branch by
itself, not a lifecycle state, not a promotion state, and not a reason to create
a new tree for every term. It names the threshold where a concept needs a
governed view because ordinary prose is no longer safe enough.

### Primary Consumers

- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- [DEFINITION-TOWERS.md](DEFINITION-TOWERS.md)
- [DEFINITION-DRIFT-AUDIT.md](DEFINITION-DRIFT-AUDIT.md)
- [../../ontology/BRANCH-AS-VIEW.md](../../ontology/BRANCH-AS-VIEW.md)
- [../../ontology/views/ontology-view.md](../../ontology/views/ontology-view.md)
- [../../ontology/views/system-view.md](../../ontology/views/system-view.md)
- [../../ontology/views/bridge-view.md](../../ontology/views/bridge-view.md)
- [../../architecture/ARCHITECTURE-KNOWLEDGE-GOVERNANCE.md](../../architecture/ARCHITECTURE-KNOWLEDGE-GOVERNANCE.md)

## CAV2-D45: UX/UI Knowledge Governance

Status: active
Term: UX/UI knowledge governance
Aliases: experience knowledge governance, interface knowledge governance, UX/UI governance interface

### Normative Definition

UX/UI knowledge governance is the CyberAlchemy v2 lens-specific governance
interface that turns interface iteration, browser evidence, accessibility
evidence, visual evidence, interaction traces, user-study residue, and reusable
experience lessons into governed candidates without treating subjective
experience quality as automatic authority.

It must separate at least these lanes:

- captured interface lesson
- reusable UX/UI pattern candidate
- browser-observable evidence
- accessibility and semantic evidence
- layout and interaction evidence
- cognitive or attention risk proxy
- domain-practice heuristic
- human-study or expert-review residue
- promotion request and owner decision

UX/UI knowledge governance can produce candidate lessons, patterns, claim maps,
validator specs, fixture plans, studio annotation intents, evidence reports, and
promotion requests. It does not promote UX/UI authority by itself.

### Formal Interpretation

For interface knowledge object `u`, CyberAlchemy v2 tracks:

```text
UXG(u) =
  (lesson_ref, pattern_candidate, browser_evidence, accessibility_evidence,
   layout_interaction_evidence, cognitive_attention_proxy,
   domain_practice_claim, human_study_residue,
   owner_route, promotion_path, challenge_contract)
```

The object is authority-bearing only when the relevant owner route records the
promotion effect and the claim strength remains bounded by available evidence.

### Operational Interpretation

Use UX/UI knowledge governance when UI work produces reusable lessons, design
patterns, validation claims, accessibility claims, layout evidence, interaction
evidence, or subjective experience claims. Route lesson capture through
`ux-lessons`, validator-safe evidence through `ux-evidence-validator`, studio
mutation intents through `ui-prototyping-studio`, and promotion through the
CyberAlchemy authority model.

### Plain-Language Intuition

UX/UI governance is how the project remembers interface learning without
pretending that a nice-looking screen, a screenshot, or a passing browser test
is automatically truth.

### Domain-Context Voice

In CyberAlchemy v2, `ux-lessons` is the thin producer for lessons and
`ux-pattern` cards, `ux-evidence-validator` is the validator-safe evidence
interface, and `ui-prototyping-studio` is a governed mutation/prototyping
consumer. Together they form the UX/UI knowledge view. CyberAlchemy authority
still decides whether a pattern, rule, or validator becomes load-bearing.

### Boundary

UX/UI knowledge governance is not a universal UX score, not an accessibility
certificate, not a design-system authority, not a human-study substitute, not a
studio mutation approval, and not a promotion event.

### Primary Consumers

- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- [DEFINITION-TOWERS.md](DEFINITION-TOWERS.md)
- [DEFINITION-DRIFT-AUDIT.md](DEFINITION-DRIFT-AUDIT.md)
- [../constitutions/STABLE-REPOSITORY-CONSTITUTION.md](../constitutions/STABLE-REPOSITORY-CONSTITUTION.md)
- [../../ux-ui/UX-UI-KNOWLEDGE-GOVERNANCE.md](../../ux-ui/UX-UI-KNOWLEDGE-GOVERNANCE.md)
- [../../../arcanum/arcana/ux-lessons/SKILL.md](../../../arcanum/arcana/ux-lessons/SKILL.md)
- [../../../arcanum/arcana/ux-evidence-validator/SKILL.md](../../../arcanum/arcana/ux-evidence-validator/SKILL.md)

## CAV2-D46: Experience Evidence Lifecycle

Status: active
Term: experience evidence lifecycle
Aliases: UX evidence lifecycle, UI learning lifecycle, interface evidence lifecycle

### Normative Definition

Experience evidence lifecycle is the CyberAlchemy v2 lifecycle by which an
interface observation or UI iteration becomes reusable UX/UI knowledge only
after evidence capture, lesson formation, pattern distillation, validator or
studio handoff, cross-session exercise, challenge, and owner promotion.

The normal path is:

```text
interface observation or UI hypothesis
  -> browser/user/session evidence
  -> lesson
  -> ux-pattern candidate
  -> validator claim map or studio annotation intent
  -> fixture, browser, or cross-session exercise
  -> challenge and residue review
  -> owner promotion
  -> UX/UI pattern, validator rule, or interface constraint authority
```

An interface pattern is not authoritative because it looked better once. It must
carry evidence and survive the claim class appropriate to its evidence.

### Formal Interpretation

For experience candidate `e`, the lifecycle is:

```text
EEL(e) =
  (observation, evidence, lesson, pattern_candidate,
   consumer_handoff, exercise, challenge, owner_decision,
   authority_effect, residue)
```

Movement to authority is admissible only when the owner decision names the
authority effect and the claim class is valid for the supporting evidence.

### Operational Interpretation

Use experience evidence lifecycle when harvesting a UI session, distilling a UX
pattern, producing a validator claim map, preparing a studio mutation intent, or
deciding whether repeated interface evidence should become a reusable rule.

### Plain-Language Intuition

A UI lesson becomes a rule only after it earns its way through evidence,
repeat-use, challenge, and owner review.

### Domain-Context Voice

In CyberAlchemy v2, `ux-lessons` owns the early lifecycle from session to
lesson/pattern, while `ux-evidence-validator` owns validator-safe claims and
fixture calibration. `ui-prototyping-studio` can consume pattern intents, but it
does not decide pattern authority.

### Boundary

Experience evidence lifecycle is not a usability study by itself, not a browser
test result by itself, not a studio approval path, and not a guarantee that a
subjective UX claim can become deterministic.

### Primary Consumers

- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- [DEFINITION-TOWERS.md](DEFINITION-TOWERS.md)
- [DEFINITION-DRIFT-AUDIT.md](DEFINITION-DRIFT-AUDIT.md)
- [../../ux-ui/UX-UI-KNOWLEDGE-GOVERNANCE.md](../../ux-ui/UX-UI-KNOWLEDGE-GOVERNANCE.md)
- [../../../arcanum/arcana/ux-lessons/SKILL.md](../../../arcanum/arcana/ux-lessons/SKILL.md)
- [../../../arcanum/arcana/ux-evidence-validator/development/UX-EVIDENCE-CLAIM-MAP.md](../../../arcanum/arcana/ux-evidence-validator/development/UX-EVIDENCE-CLAIM-MAP.md)

## CAV2-D47: Interface Evidence Boundary

Status: active
Term: interface evidence boundary
Aliases: UX evidence boundary, browser-evidence boundary, UX/UI claim class boundary

### Normative Definition

Interface evidence boundary is the CyberAlchemy v2 rule that UX/UI claims must
state which kind of evidence can support them and what that evidence cannot
prove.

At minimum, UX/UI claims must be classified as one of:

- hard gate
- soft flag
- screenshot review
- human study
- not automatable

Browser automation may directly support page-load, accessibility-tree,
keyboard, layout, interaction, screenshot, trace, console/network, and DOM
measurement claims. It may prepare evidence for cognitive, attention,
perception, trust, comprehension, delight, and real-user success claims, but it
must not turn them into deterministic authority without calibrated fixtures and
owner approval.

### Formal Interpretation

For UX/UI claim `c`, let:

```text
IEB(c) = (claim_class, evidence_kind, proxy_limit, owner_route, residue)
```

The claim is valid only when `claim_class` matches `evidence_kind` and the
`proxy_limit` states what remains unproven. If the evidence class is weaker than
the claim, `CAV2-D38` requires downgrading, routing, or blocking the claim.

### Operational Interpretation

Use interface evidence boundary when writing validator specs, Playwright
reports, UI review findings, UX pattern cards, screenshot reviews, or studio
mutation handoffs. Ask whether the claim is deterministic, a risk proxy, a
visual review prompt, a human-study need, or not automatable.

### Plain-Language Intuition

A browser can show what happened on the page. It cannot by itself prove what a
human understood, trusted, felt, or preferred.

### Domain-Context Voice

In CyberAlchemy v2, this definition imports the evidence honesty model from
`ux-evidence-validator`: hard gates, soft flags, screenshot review, human
study, and not-automatable residue. It keeps UI validation useful without
collapsing browser evidence, accessibility, UX heuristics, and user research
into one false certainty.

### Boundary

Interface evidence boundary is not a validator implementation, not a complete
accessibility audit, not user research, not a universal UX score, and not a
license to block dense expert interfaces without false-positive calibration.

### Primary Consumers

- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- [DEFINITION-TOWERS.md](DEFINITION-TOWERS.md)
- [DEFINITION-DRIFT-AUDIT.md](DEFINITION-DRIFT-AUDIT.md)
- [../constitutions/STABLE-REPOSITORY-CONSTITUTION.md](../constitutions/STABLE-REPOSITORY-CONSTITUTION.md)
- [../../ux-ui/UX-UI-KNOWLEDGE-GOVERNANCE.md](../../ux-ui/UX-UI-KNOWLEDGE-GOVERNANCE.md)
- [../../../arcanum/arcana/ux-evidence-validator/development/UX-EVIDENCE-CLAIM-MAP.md](../../../arcanum/arcana/ux-evidence-validator/development/UX-EVIDENCE-CLAIM-MAP.md)
- [../../../arcanum/arcana/ux-evidence-validator/development/UX-PLAYWRIGHT-VALIDATOR-SPEC.md](../../../arcanum/arcana/ux-evidence-validator/development/UX-PLAYWRIGHT-VALIDATOR-SPEC.md)

## CAV2-D48: Authority Promotion Lifecycle

Status: active
Term: authority promotion lifecycle
Aliases: scientific authority lifecycle, promotion lifecycle
Promoted: 2026-06-23 from `source-clusters/authority-lifecycle.md` `CAV2-CAND-LIFECYCLE-001` (per review CR-2; build-from-owned generalization inference)

### Normative Definition

Authority promotion lifecycle is the single staged path by which any
authority-bearing candidate may acquire authority — `source evidence -> candidate
-> owner-routed review -> promoted authority -> (optional) invariant/constitution
pressure` — with per-stage gates, an owner route, and a stopping/demotion rule. It
is the generalization that `../promotion-policy.md`'s ladder instantiates and that
`CAV2-D43` (patterns), `CAV2-D46` (experience), and the Arcanum Discipline Growth
Rule (disciplines) are instances of.

When an authority-bearing candidate originates in a domain and is proposed as
reusable CAV2 authority, the minimum generalization path is:

```text
domain-owned source or candidate
  -> originating-domain exercise and evidence
  -> CAV2 import candidate
  -> generalized proposal with changes and residue stated
  -> exercise in another independently owned domain or materially distinct context
  -> challenge and contrary-evidence review
  -> CAV2 owner decision
  -> promoted, versioned CAV2 authority
  -> separate adoption by each domain that chooses to use that version
```

This branch applies to domain-originated definitions, rules, methods,
specifications, knowledge structures, validators, and patterns proposed for
CAV2-wide reuse only through an existing authority kind and its owner route.
Proof objects, Lean results, Cedar or Datalog results, tests, observations, and
receipts may support such a candidate as evidence; they do not self-promote.

### Formal Interpretation

```text
APL = (stages, per_stage_gates, owner_route, stop_rule)
instances = { CAV2-D43, CAV2-D46, Discipline Growth Rule }
promotion-policy ladder = the cross-kind default

generalized_for_CAV2(c, d0)
  => origin_owner(c) = d0
  and exercised_in(c, d0)
  and exists d1: independently_owned(d1)
                 and materially_distinct(d1, d0)
                 and exercised_in(c, d1)
  and challenge_reviewed(c)
  and CAV2_owner_promoted(c)

promoted_in_CAV2(c, version) =/=> adopted_by_domain(c, version, d)
```

A kind's lifecycle is valid only when it names its stages, gates, owner route, and
stop/demotion rule; `CAV2-D38` bounds any claim of completed promotion to the
evidence.

### Operational Interpretation

Use when a new authority-bearing kind needs a promotion path: reuse a named
instance (`D43`/`D46`/Growth Rule) or justify a new lifecycle. It turns "how does
this earn authority?" into a declared, owner-routed path.

For a domain-originated proposal, keep four decisions separate: the originating
domain owns its local meaning and submission posture; the exercising domain owns
its bounded result; the CAV2 owner decides CAV2 promotion; and each consuming
domain decides whether to adopt the promoted version. A failed cross-context
exercise narrows, revises, or rejects the CAV2 proposal and leaves visible
residue; it does not erase the original domain object.

### Plain-Language Intuition

Domains can teach the base, but one local success cannot rewrite the base or
another domain. The idea must survive evidence, a materially different context,
challenge, CAV2 owner review, and separate adoption.

### Domain-Context Voice

In CyberAlchemy v2 this is the parent of the per-kind lifecycles already promoted
(`D43` patterns, `D46` experience) and the disciplines ladder. Naming it is
**build-from-owned**: the shape is visible across owned sources but the unifying
object is named in none of them, so this is a generalization inference — owner-gated,
not a mechanical lift (review CR-4).

Candidate Mint/Foundry experiment evidence illustrates the autonomy boundary:
domains may inherit CAV2's organizing machinery while owning and improving
their local content. DomainSpec, Lean, Cedar, Datalog, and other formal or
operational work may therefore propose reusable methods or knowledge without
transferring their source semantics or treating a checker result as a CAV2
promotion decision.

### Boundary

Not "everything has a lifecycle" — scoped to **authority-bearing kinds**. Evidence
(`CAV2-D34` / non-collapse rule 1), residue (`CAV2-D18`), ledger events, one-off
logs, and generated projections are inputs or terminal artifacts, not
lifecycle-bearing. The originating domain retains authority over its local
object. CAV2 promotion creates CAV2 authority for one named version; it neither
rewrites the originating domain nor activates that version in another domain.
Each domain owner makes a separate, version-exact adoption decision.

The exact upstream provenance record and any later adoption record are separate
events with separate owners. They do not create a permanent semantic adapter,
synchronized crosswalk, mapping owner, or live coupling between CAV2 and a
domain.

Naming this lifecycle does **not** enact deterministic enforcement. Closure is
enacted in review mode by `CAV2-D49` plus the
[AUTHORITY-MODEL catch-all row](../AUTHORITY-MODEL.md#authority-kinds); its
deterministic kind-enumeration scan remains pending.

### Primary Consumers

- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- [DEFINITION-DRIFT-AUDIT.md](DEFINITION-DRIFT-AUDIT.md)
- [../promotion-policy.md](../promotion-policy.md)
- [source-clusters/authority-lifecycle.md](source-clusters/authority-lifecycle.md)

## CAV2-D49: Closed Authority-Kind Enumeration

Status: active
Term: closed authority-kind enumeration
Aliases: authority-kind closure, default-deny for unenumerated kinds
Promoted: 2026-06-23 from `source-clusters/authority-lifecycle.md` `CAV2-CAND-LIFECYCLE-002` (re-scoped per review CR-1 from "no authority without a lifecycle", which re-skinned the Authority Rule)

### Normative Definition

Closed authority-kind enumeration is the invariant that the set of authority
**kinds** is a closed enumeration (the `../AUTHORITY-MODEL.md` Authority Kinds
table). An artifact whose kind is **not** in that enumeration may not acquire or
exercise authority — it defaults to **blocked** pending an owner decision that adds
the kind to the enumeration with its declared lifecycle (`CAV2-D48`) and owner
route. Adding a kind is itself owner-gated.

### Formal Interpretation

```text
CAKE: Kinds is closed; for an artifact of kind k,
  k in Kinds      -> governed by k's own ladder/owner
  k not in Kinds  -> default-deny (blocked) until an owner amends Kinds
```

This **extends** `CAV2-D41` (which assumes a kind/owner exists and says "route to
it") to the case it assumes away — a kind with no enumerated owner/ladder yet.

### Operational Interpretation

Use when a new *type* of authority appears (a new **kind**, not a new artifact of
an existing kind). Live open instance: `AUTHORITY-MODEL` OQ-2 — `invariant` and
`axiom` govern (`CAV2-D16`/`D29`/`D38`) yet sit outside the kind table.

### Plain-Language Intuition

A new *type* of authority can't start governing just because it appeared. Until it
is on the official list of kinds — with its lifecycle and owner — anything of that
kind is blocked.

### Domain-Context Voice

This definition **names** the closure invariant. As of 2026-06-23 it is **enacted
in review mode**: a **default-deny catch-all row** was added to the
[AUTHORITY-MODEL Authority Kinds table](../AUTHORITY-MODEL.md#authority-kinds) by
decision-gate ([decision record](../decisions/2026-06-23-authority-kind-closure-catchall-row.md)),
so an unenumerated kind defaults to blocked. The **deterministic** enforcement (the
automated kind-enumeration scan, the former `CAV2-C16` validator) is still pending
(OQ-1). Per the OQ-2 recommendation, the kind-table amendment for `invariant`/`axiom`
as their own kinds stays a future decision-gate call (they currently govern as the
`Definition` kind).

### Boundary

Scoped to authority **kinds** (the enumeration), not individual artifacts (that is
the Authority Rule, `CAV2-D41`) and not the per-artifact promotion path (`CAV2-D48`
+ the promotion-policy ladder). Promoting this definition did not by itself enact
the kind table as closed-with-default-deny. Review-mode enactment now lives in
the [AUTHORITY-MODEL catch-all row](../AUTHORITY-MODEL.md#authority-kinds);
deterministic enforcement remains pending.

### Primary Consumers

- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- [DEFINITION-DRIFT-AUDIT.md](DEFINITION-DRIFT-AUDIT.md)
- [../AUTHORITY-MODEL.md](../AUTHORITY-MODEL.md)
- [source-clusters/authority-lifecycle.md](source-clusters/authority-lifecycle.md)
- [../constitutions/STABLE-REPOSITORY-CONSTITUTION.md](../constitutions/STABLE-REPOSITORY-CONSTITUTION.md)

## CAV2-D50: Discipline

Status: active
Term: discipline
Aliases: governed discipline, recurring-practice discipline, discipline kind
Promoted: 2026-06-23 (build-from-owned: AUTHORITY-MODEL Authority Kinds row + `concept.discipline` + Arcanum discipline model). Prerequisite for the governance stack (tracking discipline, non-collapse validator, validating constitution).

### Normative Definition

A discipline is a **recurring, cross-capability practice** promoted to authority via
**discipline-governance** — cataloged in `../../disciplines/` with a steward/owner,
evidence that it already recurs, a maturity status (`candidate -> active-pattern ->
canonical`), and a named hardening route. Evidence of recurrence alone does **not**
self-promote a discipline; the owner route does.

### Formal Interpretation

```text
Discipline = (practice, steward/owner, recurrence_evidence, maturity_status, hardening_move)
maturity_status in { candidate, active-pattern, canonical }
promotion: discipline-governance over the maturity ladder (never auto)
```

A discipline is valid only when it names its steward, recurrence evidence, maturity,
and hardening move; `CAV2-D38` bounds any claim of "canonical" to the evidence.

### Operational Interpretation

Use when a recurring practice spans capabilities and needs a steward + hardening path
(AUTHORITY-MODEL narrowest-owner rule: *"a recurring practice needs a steward and
hardening path → discipline-governance"*). It turns a habit into a governed, hardenable
practice rather than ad-hoc repetition.

### Plain-Language Intuition

A habit the project does across many capabilities — named and hardened so it's done
consistently. It earns authority by recurring and being stewarded, not by being declared.

### Domain-Context Voice

In CyberAlchemy v2, disciplines live as cards under `../../disciplines/` owned by
discipline-governance (e.g. `stable-repository-stewardship`, `provisional-model-stewardship`).
`CAV2-D20` Craft method is itself **a** discipline (an instance), not the genus. The
Arcanum discipline model (maturity ladder / growth rule) is the ancestral source
(Evidence posture).

### Boundary

A discipline is **not** a canonical term (definitions-governance owns terms), **not** a
sigil, **not** a spell, **not** an implementation task (AUTHORITY-MODEL Authority Kinds
"must not collapse into"), and **not** Craft method specifically (`CAV2-D20` is one
discipline). Per AUTHORITY-MODEL non-collapse rule 4: *a discipline can recommend a
route, but it cannot define a term or author a constitution.* It is **not** operational
work (`CAV2-D20` Craft work-state) — authoring a discipline may be work, but the
discipline-as-authority-kind is governance.

### Primary Consumers

- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- [DEFINITION-DRIFT-AUDIT.md](DEFINITION-DRIFT-AUDIT.md)
- [../../disciplines/DISCIPLINES.md](../../disciplines/DISCIPLINES.md)
- [../AUTHORITY-MODEL.md](../AUTHORITY-MODEL.md) (Authority Kinds)
- [../../ontology/NODE-MODEL.md](../../ontology/NODE-MODEL.md) (`concept.discipline`)

## CAV2-D51: Canonical Artifact

Status: active
Term: canonical artifact
Aliases: typed artifact, governed artifact instance, process-origin-declared artifact, process-born artifact, non-canonical artifact (negation)
Promoted: 2026-07-07 (design session: the instance predicate over the canonical-kind enumeration — typed + declared process origin, decoupled from authority)
Origin assurance resolved: 2026-08-22 by accepted `GATE-06`

### Normative Definition

A canonical artifact is an artifact instance whose **kind is a member of the
canonical-kind enumeration** ([../../ontology/canonical-kinds/CANONICAL-KINDS.md](../../ontology/canonical-kinds/CANONICAL-KINDS.md))
and whose responsible owner has admitted an exact `process_origin` declaration
that names one allowed producer and process for that kind. It therefore carries
a defined type (a `CAV2-D21` classification/schema facet that is bound, not left
as residue) and an owner-declared process origin.

The strength of support for the origin declaration is recorded separately as
`origin_assurance`:

- `declared` means an owner or source made the exact origin statement;
- `integrity-bound` means a verifier confirmed that the statement and bound
  artifact-state bytes match an L1 integrity mechanism; and
- `actor-attested` means an identified actor attested the exact tuple under a
  bound L2 identity policy and external signature.

`actor-attested` is a defined future level, not a currently available result.
No assurance level proves that the named process actually executed, that the
statement is true, or that the artifact is correct or authoritative.

Canonical-ness is therefore the property of *being typed and carrying an
owner-admitted, allowed process-origin declaration with an honest assurance
level*. It is **decoupled from authority** — a canonical artifact may be
non-authoritative and still canonical. An artifact whose kind is not in the
enumeration, or whose exact origin does not resolve to an owner-approved producer
for that kind, is non-canonical or remains blocked as typed residue.

### Formal Interpretation

```text
OriginAssurance = { declared, integrity-bound, actor-attested }

allowed_origin(a)
  <-> (producer_ref(a), process_ref(a), process_version_ref(a))
      in allowed_origins(canonical_kind(a))

canonical(a)
  <-> canonical_kind(a) in CanonicalKinds
      and owner_admitted(a)
      and allowed_origin(a)
      and origin_assurance(a) in OriginAssurance

CanonicalKinds  superset-of  AuthorityKinds   (every authority-kind is a canonical-kind;
                                               not every canonical-kind bears authority)
canonical(a)   independent-of   authoritative(a)   (authority is earned via CAV2-D48)
```

Each canonical artifact declares exactly one `canonical_kind` and one exact
`process_origin` record, and inherits from its kind the `authority_kind` it rolls
up to and its `CAV2-D52` durability. The inherited fields are derived, not
asserted: an artifact cannot choose its `authority_kind`.

`allowed_origins(kind)` is intentionally set-valued because one kind may have
more than one allowed producer. The artifact still binds one exact producer,
process, version, and origin statement. The allowed set must come from a current
owner-approved source; the candidate canonical-kind table does not become
authority through this definition. An unresolved or candidate-only producer
cannot establish canonical origin.

### Schema

Schema handle: `CAV2-D51-SCHEMA` — tracked in [DEFINITION-SCHEMAS.md](DEFINITION-SCHEMAS.md).
Status: tracked (documentary).
Bound to: `CAV2-D51` canonical artifact.

Canonical artifact record:

```text
CA(a) = (artifact_id, canonical_kind, authority_kind, process_origin, durability, authority_state)

ProcessOrigin = (
  producer_ref,
  process_ref,
  process_version_ref,
  origin_statement_ref,
  origin_assurance,
  mechanism_ref?,
  verifier_receipt_ref?,
  claim_limit
)
```

| Field | Meaning | Value posture |
| --- | --- | --- |
| `artifact_id` | identifier of the instance | known |
| `canonical_kind` | the canonical-kind it instantiates | member of `CANONICAL-KINDS` |
| `authority_kind` | the authority-kind it rolls up to | a `CAV2-D49` kind (typed coupling `CAV2-D16`) |
| `process_origin` | exact origin declaration and its assurance | `ProcessOrigin`; owner-qualified, version-exact, and digest-bound references |
| `durability` | intended lifespan | `CAV2-D52` ephemeral \| perennial |
| `authority_state` | how much authority it has earned | none \| candidate \| promoted \| demoted (`CAV2-D48`) |

`ProcessOrigin` field meanings:

| Field | Meaning | Requirement |
| --- | --- | --- |
| `producer_ref` | owner-qualified producer identity | required; exact and digest-bound |
| `process_ref` | owner-qualified process identity | required; exact and digest-bound |
| `process_version_ref` | exact process version | required; version- and digest-bound |
| `origin_statement_ref` | exact statement that declares the origin | required; version- and digest-bound |
| `origin_assurance` | strength of support for the statement | declared \| integrity-bound \| actor-attested |
| `mechanism_ref` | integrity or signature mechanism metadata | required for integrity-bound and actor-attested |
| `verifier_receipt_ref` | exact verifier result | required for integrity-bound and actor-attested |
| `claim_limit` | explicit statement of what the level does not prove | required |

Schema invariant: `canonical_kind in CanonicalKinds`; `authority_kind = rollup(canonical_kind)`
is a typed coupling (`CAV2-D16`); `durability` is orthogonal to `authority_kind`
(`CAV2-D29`); `authority_state` does **not** follow from `canonical` — a canonical
artifact defaults to `authority_state = none`, and walks the `CAV2-D48` path
`none -> candidate -> promoted`, with `demoted` for withdrawn or superseded
authority.

Origin-assurance invariants:

```text
declared =/=> integrity-bound
integrity-bound =/=> actor-attested
actor-attested =/=> statement truth
any origin assurance =/=> actual process execution
any origin assurance =/=> authority, discharge, promotion, or publication
```

An assurance upgrade appends or references new evidence; it does not rewrite the
prior origin statement or verifier receipt. Documentary; validator deferred.
Activation requires positive, tampered, wrong-level, missing-reference, and
unsupported-L2 fixtures plus a separate owner decision.

### Operational Interpretation

Use when deciding whether a document is a first-class typed artifact or an
ungoverned working note. Ask: does it instantiate an enumerated canonical kind,
does its owner admit one exact allowed origin, and does the record state how
strongly that origin statement is supported? Under the current review-mode
posture, `declared` is sufficient for owner admission, but the artifact must be
described as owner-declared rather than mechanically verified process output.

Use `integrity-bound` only when the exact statement and artifact-state bytes have
a valid L1 verifier receipt. Reserve `actor-attested` for a real L2 external
signature and identity-policy receipt; no current artifact may claim it merely
because the level is defined.

### Plain-Language Intuition

A canonical artifact is a recognized kind of thing with an exact, allowed origin
statement. The record also says whether that statement was merely declared,
sealed against later byte changes, or signed by an identified actor. None of
those labels says the statement is true or the artifact is authoritative.

### Domain-Context Voice

In CyberAlchemy v2 this names the genus that sits above the
[AUTHORITY-MODEL Authority Kinds table](../AUTHORITY-MODEL.md#authority-kinds):
the fine artifact-types (discovery, research, axiom, ledger, spec, ...) enumerated
in [../../ontology/canonical-kinds/CANONICAL-KINDS.md](../../ontology/canonical-kinds/CANONICAL-KINDS.md), each
rolling up to a coarse `CAV2-D49` authority-kind and carrying a `CAV2-D52`
durability. It is the positive pole opposite `CAV2-D8` import candidate and
non-canonical working material: it lets the project say "this is a typed artifact
with an owner-declared origin" without claiming execution, correctness, or
authority. `CAV2-D35` remains the provenance trail; origin assurance only states
how the exact declaration is supported.

### Boundary

Canonical artifact is **not** authority and **not** "canonical source": the store's
existing *canonical source*, *canonical section*, and *canonical definition*
(alias of `CAV2-D33`) use *canonical = the authoritative version*; this term uses
*canonical = has a canonical form + owner-admitted process-origin declaration*
and is explicitly decoupled from authority. The legacy alias `process-born`
must not be used to imply observed execution unless a separately governed
execution witness supports that claim.

It is **not** the enumeration itself — that is the set of kinds in
`CANONICAL-KINDS.md`; a canonical artifact is a member instance. It does not
promote anything: earning authority is `CAV2-D48`, being a recognized kind is
`CAV2-D49`. Origin assurance is not proof, trust, validation, truth, discharge,
promotion, adoption, or publication. Prior 2026-06-21 review prose that used
"canonical artifact" to mean
"target-owned / deployed authority" is the *authoritative-version* sense and
predates this term (recorded in [DEFINITION-DRIFT-AUDIT.md](DEFINITION-DRIFT-AUDIT.md)).

### Resolved Origin Questions

- `CA-OQ-1` is resolved as set-valued admissibility with exact instance binding:
  a kind may allow multiple producers, while each artifact names one exact origin.
- `CA-OQ-2` is resolved by tiered assurance. `declared` supports current
  owner-admitted canonical status; `integrity-bound` supports exact byte integrity;
  `actor-attested` is future L2 identity assurance. None proves execution or truth.
- The candidate canonical-kind table remains a view, not an authority source.
  Producer-set ratification and deterministic validation remain separate work.

### Primary Consumers

- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- [DEFINITION-DRIFT-AUDIT.md](DEFINITION-DRIFT-AUDIT.md)
- [DEFINITION-SCHEMAS.md](DEFINITION-SCHEMAS.md)
- [../../ontology/canonical-kinds/CANONICAL-KINDS.md](../../ontology/canonical-kinds/CANONICAL-KINDS.md)
- [../AUTHORITY-MODEL.md](../AUTHORITY-MODEL.md) (Authority Kinds)

## CAV2-D52: Artifact Durability

Status: active
Term: artifact durability
Aliases: durability axis, ephemeral artifact, perennial artifact
Promoted: 2026-07-07 (design session: lifespan axis orthogonal to authority-kind and to maturity; carries the contradiction-tolerance coupling)

### Normative Definition

Artifact durability is the axis that classifies a `CAV2-D51` canonical artifact by
**intended lifespan** — `ephemeral` (a work-product meant to be produced,
consumed, and retired) or `perennial` (a standing reference meant to endure and be
maintained). Durability is **orthogonal** to the `authority_kind` (`CAV2-D49`)
and to maturity/status (`CAV2-D23`): two artifacts of the same kind may differ in
durability — a discovery and an inventory index are both `Evidence`, yet the
discovery is ephemeral and the index is perennial.

Durability carries one **contradiction-tolerance** obligation (typed coupling,
`CAV2-D16`):

- an **ephemeral** artifact **may hold live contradictions** — competing
  hypotheses and unresolved tensions are expected and preserved;
- a **perennial** artifact **must not hold live simultaneous contradictions**.
  *Temporal supersession* — a later entry overriding an earlier one in an
  append-only record (`CAV2-D26` ledger), or a decision record narrating the
  contradiction it resolved (`CAV2-D36`) — is **not** a live contradiction and is
  permitted.

### Formal Interpretation

```text
durability(a) in { ephemeral, perennial }
durability(a)  orthogonal-to  authority_kind(a)   (CAV2-D29: independent of authority-kind)
durability(a)  orthogonal-to  status(a)         (CAV2-D23: independent of maturity)
perennial(a)   ->  not ( a holds live  P and not-P simultaneously )
ephemeral(a)   ->  a may hold live  P and not-P
temporal supersession ( E_t overrides E_{t-1} ) is not a live contradiction
```

### Operational Interpretation

Assign durability per canonical-kind as a default (spec / definition /
constitution / decision / axiom / ledger -> perennial; discovery / research /
session -> ephemeral), overridable per instance with an owner note. When reviewing
a perennial artifact, treat a live contradiction as a defect to resolve; when
reviewing an ephemeral one, treat contradictions as legitimate exploration to
preserve.

### Plain-Language Intuition

Some documents are meant to be used and then set aside once they have done their
job (a discovery); others are meant to stand and be kept true (a spec). The
first kind is allowed to argue with itself; the second is not — though a logbook
is still allowed to record that things changed over time.

### Domain-Context Voice

In CyberAlchemy v2, durability is a column on
[../../ontology/canonical-kinds/CANONICAL-KINDS.md](../../ontology/canonical-kinds/CANONICAL-KINDS.md). It answers
"how long is this meant to stand, and can it hold contradictions" — a question
neither `CAV2-D49` (what kind) nor `CAV2-D23` (how mature) asks. It is why a
discovery can freely explore contradictions while a spec cannot, and why a ledger
can record superseding events without violating consistency.

### Boundary

Artifact durability is **not** maturity/status (`CAV2-D23`): a mature discovery is
still ephemeral, a draft spec is still perennial. It is **not** authority:
perennial does not mean authoritative (a perennial spec may still be a candidate).
It is **not** regenerability: a projection is derived and regenerable, which is a
separate property, not "ephemeral" — durability is about intended lifespan, not
whether the artifact can be rebuilt. The two-value set may later gain an
append-only/monotonic third value if the ledger case proves the live-vs-temporal
refinement insufficient; that is an owner-gated extension.

### Primary Consumers

- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- [DEFINITION-DRIFT-AUDIT.md](DEFINITION-DRIFT-AUDIT.md)
- [../../ontology/canonical-kinds/CANONICAL-KINDS.md](../../ontology/canonical-kinds/CANONICAL-KINDS.md)
- [#cav2-d51-canonical-artifact](#cav2-d51-canonical-artifact)
- [#cav2-d26-append-only-event-ledger](#cav2-d26-append-only-event-ledger)

## CAV2-D53: Axiom

Status: active
Term: axiom
Aliases: foundational truth, admitted principle, bedrock commitment
Promoted: 2026-07-08 (design session; axiom/invariant/constitution/premise ladder, stress-tested against ZefraHub and maestro-trama axiom corpora; subject-test boundary against invariant)

### Normative Definition

An axiom is a **foundational proposition taken as given** — bedrock the system does
not derive further within itself and holds as true (high commitment/veracity) —
**from which a family of premises, invariants, and constitution rules derives**,
such that revising it forces rethinking everything built on it. Its defining
subject is the **world or domain** the system operates in: an axiom states *why*
the system is shaped as it is, and the system is **built around** it rather than
made to satisfy it. It is **not** a constraint on the system's own behavior — that
is an invariant (`CAV2-D54`).

### Formal Interpretation

```text
axiom A:  taken-as-given(A) ∧ ¬derives-within-system(A) ∧ veracity(A) = high
          ∧ fan_out(A) = { premises, invariants, constitution-rules derived from A }
subject(A) = world/domain          (not the system's own behavior)
system can violate A?  No — if A is false, the premise was wrong, not the code buggy
genesis:       invariant → "why must this hold?" → A     (discovery order)
justification: A → invariant → constitution rule          (top-down order)
```

The **fan-out** is the axiom's signature: a proposition that grounds only one
downstream item, and nothing else, is not an axiom but the restatement of a single
invariant.

### Operational Interpretation

Use "axiom" for the load-bearing truths a project stands on and reasons *from* —
the ones that justify why a whole area, method, or rule family exists. Three tests:
(1) can the system make it false? If yes, it is an invariant, not an axiom. (2) Is
it actually believed true, or is it a bet? A bet (`veracidade: low`) is a
**premise**, not an axiom. (3) Does a family derive from it? If nothing does, it is
inert.

### Plain-Language Intuition

A truth you build on, not a rule you obey. "Creatives are fat-tailed" is true about
the world; you design around it. If it turned out false, your plan was wrong — not
your code.

### Domain-Context Voice

In CyberAlchemy v2, axiom is the top of the `axiom → invariant → constitution →
validator` justification chain and the *why* reached by asking backward from an
invariant in the `invariant → axiom` discovery direction. It is distinct from
the specific invariant-definitions
already promoted (`CAV2-D16`/`D29`/`D38`/`D49`), which are invariants, not axioms.
Evidence corpora: maestro-trama `creative-axioms` (clean descriptive axioms);
ZefraHub / maestro-trama `system-axioms` (mostly invariants mislabeled as axioms;
`AX-SYS-3` and `AX-ONT-7` are premises).

### Boundary

An axiom is **not** an invariant (`CAV2-D54`): the invariant is a must-hold on the
*system*; the axiom is a given truth about the *world* the system is built around.
It is **not** a premise: a premise is a working bet held at low veracity
(`veracidade: low`), an axiom is held true. It is **not** a constitution
(`CAV2-D58`): the constitution is the authoritative scoped rulebook; the axiom
is the reason behind it. It is **not** a definition (`CAV2-D33`): a definition assigns meaning to
a term, an axiom asserts a foundational truth. An axiom and the invariants it
grounds enforce nothing by themselves. A constitution authorizes and scopes
constraints; a selected validator or gate checks or performs enforcement.

### CAV2-D83: Operational Resilience

Status: active
Term: Operational Resilience
Reconciled: 2026-09-06 from the recorded ORODI promotion selection and immutable source voices; admitted for Craft ORODI by explicit owner direction.

### Normative Definition

Operational Resilience is the evidenced ability of a bounded system to preserve or restore declared critical outcomes under declared stressors, within declared degradation and recovery limits.

### Formal Expression

Resilient(S,K,F,W,P,E) holds only when exact system S, critical outcomes K, stressors F, evaluation window W, policy P, and fresh evidence E are bound and E proves preserve(K) or recover(K) within P; missing(E) yields not_evaluable, never true.

### Plain-Language Intuition

A system is resilient only when we can show what mattered kept working or was restored within the promised limits when something went wrong.

### Domain-Context Voice

ORODI evaluates resilience through finite evidence sets, canary observations, rollback restoration, and explicit degraded or terminal outcomes.

### Boundary

Operational Resilience is not generic uptime, the absence of alerts, static configuration validity, an unbounded aspiration, or proof from one successful test.

### Source and Admission

Selected source: `CAV2-CAND-ORODI-001`.
See [ORODI source cluster](source-clusters/orodi-operational-evidence.md) and
[Craft ORODI reconciliation](../../product/craft/capabilities/orodi/definition-reconciliation/README.md).


## CAV2-D84: Operational Evidence

Status: active
Term: Operational Evidence
Reconciled: 2026-09-06 from the recorded ORODI promotion selection and immutable source voices; admitted for Craft ORODI by explicit owner direction.

### Normative Definition

Operational Evidence is an immutable, provenance-bound set of observations and evaluations about one exact operational subject, environment, time window, policy, and evidence state.

### Formal Expression

OperationalEvidence = (subject, environment, observations, evaluator, policy, created_at, expiry, invalidation_keys, provenance, state, receipt_digest); authority_effect = none.

### Plain-Language Intuition

It is the exact record of what we observed, how we judged it, when it was valid, and what would make it stale.

### Domain-Context Voice

ORODI uses operational evidence for replay, runtime projection, canary comparison, infrastructure-plan evaluation, deployment observation, and rollback verification.

### Boundary

Operational Evidence is not authority, an effect, a live fact without source admission, or a guarantee beyond its bound subject, environment, time, and denominator.

### Source and Admission

Selected source: `CAV2-CAND-ORODI-002`.
See [ORODI source cluster](source-clusters/orodi-operational-evidence.md) and
[Craft ORODI reconciliation](../../product/craft/capabilities/orodi/definition-reconciliation/README.md).


## CAV2-D85: Evaluation Binding

Status: active
Term: Evaluation Binding
Reconciled: 2026-09-06 from the recorded ORODI promotion selection and immutable source voices; admitted for Craft ORODI by explicit owner direction.

### Normative Definition

An Evaluation Binding is the immutable identity-and-state set for every dependency that one evaluation profile declares applicable, together with the complete declared denominator that makes omitted, inapplicable, missing, invalid, and bound dependencies distinguishable.

### Formal Expression

EvaluationBinding = (profile_ref, denominator, dependency_bindings, dependency_states, created_at, expires_at, invalidation_keys, supersedes_ref), where for every d in denominator, state(d) is one of {bound, inapplicable, missing, invalid}; evaluable only if every required applicable d is bound, current, and valid.

### Plain-Language Intuition

Freeze the full checklist for this kind of evaluation, mark what applies, and bind every required item. Do not force irrelevant fields, and do not let an omitted field look inapplicable.

### Domain-Context Voice

An ORODI deployment evaluation can require artifact, environment, authorization, observer, and pre/post-state bindings without inventing a topology or fixture dependency when its selected profile declares those inapplicable.

### Boundary

A complete Evaluation Binding proves denominator and identity completeness only; it does not prove source authenticity, evidence truth, policy correctness, owner acceptance, or effect authority.

### Source and Admission

Selected source: `CAV2-CAND-ORODI-003-R1`.
See [ORODI source cluster](source-clusters/orodi-operational-evidence.md) and
[Craft ORODI reconciliation](../../product/craft/capabilities/orodi/definition-reconciliation/README.md).


## CAV2-D86: Operational Evidence Evaluation State

Status: active
Term: Operational Evidence Evaluation State
Reconciled: 2026-09-06 from the recorded ORODI promotion selection and immutable source voices; admitted for Craft ORODI by explicit owner direction.

### Normative Definition

Operational Evidence Evaluation State is the disjoint typed condition assigned to one evaluated operational obligation: passed, failed, missing, invalid, inconclusive, stale, or not-run.

### Formal Expression

OperationalEvidenceEvaluationState is one of {passed, failed, missing, invalid, inconclusive, stale, not-run}; the set is pairwise disjoint, and an aggregate may be passed only when every required denominator member is present, valid, fresh, executed, and passed.

### Plain-Language Intuition

For one operational check, success, failure, no data, bad data, old data, uncertainty, and never run are different answers. Other questions, such as model coverage, may use their own states.

### Domain-Context Voice

ORODI uses this state only for evaluated operational obligations; model coverage, evidence availability, validator result, lifecycle state, and owner decision remain separate owner-defined facets.

### Boundary

This vocabulary must not flatten model coverage, evidence availability, validation result, lifecycle state, or owner decision into one state machine; absence of failure is never passed.

### Source and Admission

Selected source: `CAV2-CAND-ORODI-004-R1`.
See [ORODI source cluster](source-clusters/orodi-operational-evidence.md) and
[Craft ORODI reconciliation](../../product/craft/capabilities/orodi/definition-reconciliation/README.md).


## CAV2-D87: Failure Meaning Separation

Status: active
Term: Failure Meaning Separation
Reconciled: 2026-09-06 from the recorded ORODI promotion selection and immutable source voices; admitted for Craft ORODI by explicit owner direction.

### Normative Definition

Failure Meaning Separation is the invariant that subject-level failure meaning, boundary or integration outcome, and runtime exception remain distinct owner-defined roles throughout evaluation and recovery.

### Formal Expression

SubjectFailureRole != BoundaryOutcomeRole != RuntimeExceptionRole; map(RuntimeExceptionRole, profile_owner) -> BoundaryOutcomeRole and interpret(BoundaryOutcomeRole, subject_owner) -> optional SubjectFailureRole; each owner controls its vocabulary and neither mapping redefines the target role.

### Plain-Language Intuition

What failed for the business, what the boundary reported, and what the runtime threw may be connected, but they are not interchangeable and need not share universal type names.

### Domain-Context Voice

ORODI profiles map tool and runtime exceptions into boundary outcomes while the owning domain decides whether those outcomes establish a subject-level failure and who may continue or recover.

### Boundary

A runtime exception cannot create subject meaning, a boundary outcome cannot silently become an owner decision, and a subject failure does not prescribe one exception, retry, or integration vocabulary.

### Source and Admission

Selected source: `CAV2-CAND-ORODI-005-R1`.
See [ORODI source cluster](source-clusters/orodi-operational-evidence.md) and
[Craft ORODI reconciliation](../../product/craft/capabilities/orodi/definition-reconciliation/README.md).


## CAV2-D88: Product Observability

Status: active
Term: Product Observability
Reconciled: 2026-09-06 from the recorded ORODI promotion selection and immutable source voices; admitted for Craft ORODI by explicit owner direction.

### Normative Definition

Product Observability is the bounded ability to derive evidence about a product subject from admitted traces, metrics, logs, exemplars, health facts, and their complete accounting, without granting the observer actuation authority.

### Formal Expression

Observe(subject, environment, window) -> ObservationSet; observer_effects subset_of {append_evidence}; observer_effects intersection {deploy, shift_traffic, inject_fault, rollback, admit, promote, release} = empty.

### Plain-Language Intuition

Observability lets us understand what the product did; it does not let the observer change what the product is doing.

### Domain-Context Voice

ORODI keeps product telemetry separate from Arcanum workflow telemetry and uses it only through bound evidence contracts.

### Boundary

Workflow or agent telemetry is not product-runtime evidence, and the presence of a dashboard or signal does not prove coverage or correctness.

### Source and Admission

Selected source: `CAV2-CAND-ORODI-006`.
See [ORODI source cluster](source-clusters/orodi-operational-evidence.md) and
[Craft ORODI reconciliation](../../product/craft/capabilities/orodi/definition-reconciliation/README.md).


## CAV2-D89: Telemetry Conservation

Status: active
Term: Telemetry Conservation
Reconciled: 2026-09-06 from the recorded ORODI promotion selection and immutable source voices; admitted for Craft ORODI by explicit owner direction.

### Normative Definition

Telemetry Conservation is the accounting invariant that every offered observation is queued or rejected, and every queued observation is exported, dropped, or pending, with partial success and loss explicit.

### Formal Expression

offered = queued + rejected; queued = exported + dropped + pending; all quantities are nonnegative and scope-identical; closure false => evidence completeness is inconclusive or invalid.

### Plain-Language Intuition

Every signal must have a known fate; if some disappeared and we cannot account for them, we cannot call the evidence complete.

### Domain-Context Voice

ORODI requires telemetry accounting before stable/candidate comparisons or operational claims can pass.

### Boundary

Telemetry Conservation proves accounting closure, not semantic correctness, representativeness, privacy compliance, or that the observed system behaved well.

### Source and Admission

Selected source: `CAV2-CAND-ORODI-007`.
See [ORODI source cluster](source-clusters/orodi-operational-evidence.md) and
[Craft ORODI reconciliation](../../product/craft/capabilities/orodi/definition-reconciliation/README.md).


## CAV2-D90: Runtime Evidence

Status: active
Term: Runtime Evidence
Reconciled: 2026-09-06 from the recorded ORODI promotion selection and immutable source voices; admitted for Craft ORODI by explicit owner direction.

### Normative Definition

Runtime Evidence is operational evidence produced by an admitted observer during an authorized execution in the exact bound environment and accepted only for its declared subject, window, denominator, freshness, and invalidation keys.

### Formal Expression

RuntimeEvidence subset OperationalEvidence where execution_ref != null, execution_authorization_ref != null, observer_admitted = true, environment_observed = bound_environment, and simulated = false.

### Plain-Language Intuition

Runtime evidence comes from watching the real authorized run in the exact place we claim, not from a schema, replay, plan, or simulation.

### Domain-Context Voice

ORODI requires runtime evidence for commissioning and environment-behavior claims while keeping offline and projected evidence explicitly denied.

### Boundary

Static tests, decoded receipts, generated projections, configuration, simulation, plans, and not-run packages are not Runtime Evidence.

### Source and Admission

Selected source: `CAV2-CAND-ORODI-008`.
See [ORODI source cluster](source-clusters/orodi-operational-evidence.md) and
[Craft ORODI reconciliation](../../product/craft/capabilities/orodi/definition-reconciliation/README.md).


## CAV2-D91: Deployment Evidence

Status: active
Term: Deployment Evidence
Reconciled: 2026-09-06 from the recorded ORODI promotion selection and immutable source voices; admitted for Craft ORODI by explicit owner direction.

### Normative Definition

Deployment Evidence is independent Runtime Evidence that an explicitly authorized environment transition occurred and that binds the observed pre-state, requested transition, resulting state, time, actor or controller, and exact stable and candidate identities.

### Formal Expression

DeploymentEvidence = RuntimeEvidence + (authorization_ref, pre_state, requested_transition, observed_post_state, actor_ref, stable_digest, candidate_digest); observed_effect = true; authority_effect = none.

### Plain-Language Intuition

It proves that an authorized change really happened and records what state the environment reached; it does not grant permission for the change.

### Domain-Context Voice

ORODI keeps simulated deployment separate from independently observed environment effects and uses deployment evidence as input to rollback and terminal-state evaluation.

### Boundary

A deployment plan, command invocation, simulation, canary verdict, static configuration, or controller acknowledgement alone is not Deployment Evidence.

### Source and Admission

Selected source: `CAV2-CAND-ORODI-009`.
See [ORODI source cluster](source-clusters/orodi-operational-evidence.md) and
[Craft ORODI reconciliation](../../product/craft/capabilities/orodi/definition-reconciliation/README.md).


## CAV2-D92: Rollback Restoration Evidence

Status: active
Term: Rollback Restoration Evidence
Reconciled: 2026-09-06 from the recorded ORODI promotion selection and immutable source voices; admitted for Craft ORODI by explicit owner direction.

### Normative Definition

Rollback Restoration Evidence is independent Runtime Evidence that, before the bound deadline, every resource in the complete rollback inventory has zero candidate reference and the declared stable identity and required critical outcomes are restored.

### Formal Expression

Restored(inventory, deadline) iff complete(inventory) and forall r in inventory: candidate_refs(r, observed_at<=deadline)=0 and stable_digest(r)=expected_stable_digest and critical_outcomes_restored; invocation(rollback) alone is insufficient.

### Plain-Language Intuition

Rollback is complete only when an independent check shows the candidate is gone everywhere it should be and the stable system is actually back.

### Domain-Context Voice

ORODI uses a recovery ledger, ordered rollback, complete resource inventory, deadline, and independent observer to establish restoration.

### Boundary

Calling a rollback function, stopping one component, receiving a controller acknowledgement, or passing a tabletop test is not Rollback Restoration Evidence.

### Source and Admission

Selected source: `CAV2-CAND-ORODI-010`.
See [ORODI source cluster](source-clusters/orodi-operational-evidence.md) and
[Craft ORODI reconciliation](../../product/craft/capabilities/orodi/definition-reconciliation/README.md).


## Open Questions

#### AX-OQ-1. Descriptive-only, or a prescriptive species too?

Is `axiom` descriptive-only (a world/domain truth), with all must-satisfy content
routed to `CAV2-D54` invariant, or is there a distinct prescriptive-axiom species?
Current lean: descriptive-primary — must-satisfy content is invariant-shaped, and
the subject-test (world vs system) is the discriminator. Status: OPEN.

#### AX-OQ-2. Own authority-kind, or governs as `Definition`?

Should `axiom` be a first-class authority kind, or continue governing as the
`Definition` kind? Mirrors [AUTHORITY-MODEL OQ-2](../AUTHORITY-MODEL.md) and
[CANONICAL-KINDS OQ-2](../../ontology/canonical-kinds/CANONICAL-KINDS.md). Status: OPEN (tracked
upstream).

#### AX-OQ-3. The axiom-vs-premise threshold, and defeasibility.

How is the line between an axiom (held true) and a premise (a bet, `veracidade:
low`) operationalized — an owner judgment, or a labeled/measured cutoff on the
`CAV2-D23` evidence/commitment axes? And can a **defeasible** axiom that carries a
stated boundary condition (e.g. maestro-trama `AX-CRT-4`, which "fails under
bidding bugs, adversarial network") remain an axiom, or does defeasibility push it
toward premise? Status: OPEN.

### Primary Consumers

- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- [DEFINITION-DRIFT-AUDIT.md](DEFINITION-DRIFT-AUDIT.md)
- [#cav2-d54-invariant](#cav2-d54-invariant)
- [#cav2-d58-constitution](#cav2-d58-constitution)
- [../AUTHORITY-MODEL.md](../AUTHORITY-MODEL.md) (Invariant, Axiom, Constitution)
- [../../ontology/canonical-kinds/CANONICAL-KINDS.md](../../ontology/canonical-kinds/CANONICAL-KINDS.md) (`axiom` canonical-kind)

## CAV2-D54: Invariant

Status: active
Term: invariant
Aliases: must-hold constraint, system invariant
Promoted: 2026-07-08 (design session; generic parent of CAV2-D16/D29/D38/D49; subject-test boundary against axiom)

### Normative Definition

An invariant is a **condition on the system's own behavior or artifacts that must
remain true** across a declared scope of decisions, transformations, or states —
such that a violation is **drift or a defect**. Its defining subject is the
**system**: unlike an axiom (`CAV2-D53`), which the system is built around, an
invariant is something the system **must satisfy** and can fail to. An invariant is
the checkable *what-must-stay-true* that a constitution rule (`CAV2-D58`)
operationalizes and a validator or gate (`CAV2-D37`) enforces.

### Formal Interpretation

```text
invariant I:  ∀ state/transition s in scope(I):  must-hold(I, s)
subject(I) = the system            (its behavior / artifacts)
system can violate I?  Yes — a violation is drift/defect (a bug)
grounded-by:        an axiom (CAV2-D53) answering "why must I hold?"
operationalized-by: constitution rule (CAV2-D58)
enforced-by:        validator / gate (CAV2-D37)
```

CyberAlchemy v2 already carries specific invariants — `CAV2-D16` typed coupling,
`CAV2-D29` axis orthogonality, `CAV2-D38` claim ≤ proof, `CAV2-D49` closed
authority-kind enumeration; this definition is their generic parent.

### Operational Interpretation

Use "invariant" for a single must-hold truth about the system that is, in
principle, checkable and whose breach is a defect. Two tests: (1) can the system
violate it (is a breach a bug)? If yes, it is an invariant; if the system cannot
make it false, it is an axiom. (2) Is it one condition (invariant) or a bundle of
authoritative rules with selectors and modes (a constitution, `CAV2-D58`)? Each
invariant should trace *up* to an axiom (its "why") and *down* to a validation
mode.

### Plain-Language Intuition

A condition the system must keep true — "same input, same output." Break it and
you have a bug. It is the *what must stay true*, sitting below the axiom that
says *why* and above the rulebook that says *how*.

### Domain-Context Voice

In CyberAlchemy v2, invariant is the middle of the `axiom → invariant →
constitution → validator` chain: the checkable anchor that a constitution may
operationalize and a selected validator or gate may enforce, and the parent
genus of the already-promoted invariant instances
(`CAV2-D16`/`D29`/`D38`/`D49`). An invariant with no axiom under it is unjustified;
an invariant with no validation mode is un-enforceable (`none-yet`, per
constitution-governance).

### Boundary

An invariant is **not** an axiom (`CAV2-D53`): same-input-same-output is a system
must-hold; "unreproducible results cannot be trusted" is the world-truth behind it.
It is **not** a constitution (`CAV2-D58`): the invariant is one must-hold
proposition, the constitution is the scoped, composable rulebook that
operationalizes many invariants with selectors, examples, validation modes, and
precedence. It is **not** a validator or gate (`CAV2-D37`): the invariant states
what must be true, the validator is the check that enforces it. It is **not**
automatically authority — an invariant governs only through its owner route.

### Open Questions

#### IN-OQ-1. Generic parent vs. the specific instances.

Does a generic `invariant` parent add a real distinction over the specific
instances (`CAV2-D16`/`D29`/`D38`/`D49`), or risk over-abstraction? Promoted as the
parent genus; watch that it does not absorb or blur their specific boundaries.
Status: OPEN (monitor).

#### IN-OQ-2. Own authority-kind, or governs as `Definition`?

Should `invariant` be a first-class authority kind, or continue governing as the
`Definition` kind (as `CAV2-D16`/`D29`/`D38`/`D49` currently do)? Mirrors
[AUTHORITY-MODEL OQ-2](../AUTHORITY-MODEL.md). Status: OPEN (tracked upstream).

#### IN-OQ-3. Is the trace obligation a constitution rule or a soft expectation?

Should the expectation that every invariant traces *up* to an axiom (`CAV2-D53`)
and *down* to a validation mode (`deterministic`/`review`/`hybrid`/`none-yet`) be a
**constitution rule** (authoritatively adopted and scoped), or a soft documentary
expectation? Ties to the
enforcement thread and [AUTHORITY-MODEL OQ-1](../AUTHORITY-MODEL.md). Status: OPEN.

### Primary Consumers

- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- [DEFINITION-DRIFT-AUDIT.md](DEFINITION-DRIFT-AUDIT.md)
- [#cav2-d53-axiom](#cav2-d53-axiom)
- [#cav2-d58-constitution](#cav2-d58-constitution)
- [#cav2-d37-gate](#cav2-d37-gate)
- [../AUTHORITY-MODEL.md](../AUTHORITY-MODEL.md) (Invariant, Axiom, Constitution)
- [../../ontology/governance/README.md](../../ontology/governance/README.md)

## CAV2-D55: Premise

Status: active
Term: premise
Aliases: working premise, working hypothesis, hypothesis, conviction bet
Promoted: 2026-07-08 (design session; the `veracidade: low`/`convicção: high` bet layer completing the axiom/invariant/premise trio)

### Normative Definition

A premise is a **working proposition the project adopts in order to proceed
without having established it as true** — a defeasible bet or commitment,
characteristically held at **low veracity but often high conviction**
(`veracidade: low`, `convicção: high`) — that is expected to be revised, promoted,
or retired as evidence accumulates. A premise may complement axioms (a working
elaboration built on the bedrock) or stand alone as a conjecture the project is
betting on. It can provisionally ground invariants and rules, but it does **not**
carry the settled truth of an axiom (`CAV2-D53`).

### Formal Interpretation

```text
premise P:  adopted-to-proceed(P) ∧ ¬established-true(P) ∧ defeasible(P)
            typically veracity(P) = low, conviction(P) = high   (CAV2-D23: the two axes diverge)
lifecycle:  P --evidence--> { promote → axiom (CAV2-D48) | revise | retire }
distinguished-from:
  axiom (CAV2-D53):      veracity high, held true     → a premise is a bet
  invariant (CAV2-D54):  a must-hold on the system    → a premise is a proposition to reason from
```

The premise is exactly the case where **veracity and conviction diverge**
(`CAV2-D23`): the project may be highly committed to acting on `P` while `P`
remains unproven.

### Operational Interpretation

Use "premise" for the load-bearing bets a project stands on *provisionally* — the
things it commits to acting on before they are proven, and expects to test. The
marker is a hedge: if a candidate axiom says "hypothesis", "we conjecture — not
prove", or carries `veracidade: low`, it is a premise. A premise earns its way to
axiom only through the evidence/promotion path (`CAV2-D48`), never by conviction
alone.

### Plain-Language Intuition

A bet you are willing to build on for now. You act as if it is true, but you know
it is not proven — and you are watching for the evidence that confirms it, revises
it, or kills it.

### Domain-Context Voice

In the vault corpora, premises live beside axioms (`business-premises`,
`ontology-premises`, `system-premises`) and "sit on top of" them; `veracidade: low
/ convicção: high` is the premise signature. ZefraHub `AX-ONT-7` ("we conjecture —
not prove") and `AX-SYS-3` ("the folder structure is a hypothesis") are premises
mislabeled as axioms. Demotion is normal and healthy: a vault moved an
"adaptive-system axiom" to the `P-ONT-9` premise because it was "an engineering
commitment about maintenance, not a foundational truth."

### Boundary

A premise is **not** an axiom (`CAV2-D53`): the axiom is held true (high veracity),
the premise is a bet (low veracity) even when conviction is high — `CAV2-D23` keeps
veracity and commitment separate, and the premise is exactly where they diverge. It
is **not** an invariant (`CAV2-D54`): the invariant is a must-hold on the system, a
premise is a proposition to reason from. It is **not** a disposable hypothesis: a
premise is *load-bearing* (things are built on it) while still unproven — which is
what makes its defeasibility worth tracking rather than ignoring. Promotion premise
→ axiom is an evidence-gated lifecycle move (`CAV2-D48`), never automatic.

### Open Questions

#### PR-OQ-1. Premise vs. hypothesis — one term or two?

Do we need both `premise` and `hypothesis`, or is `premise` the CAV2 term and
`hypothesis` a source-local alias (the vaults use "hypothesis" in `AX-SYS-3`)?
Current lean: one term, `premise`, with `hypothesis` an alias. Status: OPEN.

#### PR-OQ-2. Where is the premise → axiom threshold?

Where exactly does a premise become an axiom (veracity crosses a line) or get
retired? Ties to `AX-OQ-3` and the `CAV2-D23` evidence/commitment axes; the
promotion move itself is `CAV2-D48`. Status: OPEN.

#### PR-OQ-3. May a premise ground an invariant or constitution rule?

If a rule is built on a premise (a bet) rather than an axiom (a truth), how is that
provisional footing marked so the rule is visibly a bet — a residue flag, a
validation-mode caveat, or a blocked promotion? Status: OPEN.

### Primary Consumers

- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- [DEFINITION-DRIFT-AUDIT.md](DEFINITION-DRIFT-AUDIT.md)
- [#cav2-d53-axiom](#cav2-d53-axiom)
- [#cav2-d23-authority-lifecycle-axis](#cav2-d23-authority-lifecycle-axis)
- [#cav2-d48-authority-promotion-lifecycle](#cav2-d48-authority-promotion-lifecycle)

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

## CAV2-D57: Exact Publication Authorization

Status: active
Term: exact publication authorization
Aliases: two-step publication authorization, source-owner release authorization, exact-output publication approval, private-by-default release
Promoted: 2026-08-22 from accepted `GATE-08`; definition only, with no present publication effect

### Normative Definition

Exact publication authorization is the CyberAlchemy v2 rule that private
material may cross a publication boundary only after two separate decisions:

1. every source owner authorizes an exact candidate slice, its allowed claims,
   audience, channel, privacy policies, and requested publishing principal; and
2. after private generation and privacy validation, that publishing principal
   approves the exact final output bytes, digest, audience, channel, and claim
   ceiling.

The first decision permits creation and review of a private publication
candidate. It does not permit unknown future bytes to be published. The second
decision applies only to the exact output it binds. Any change to the sources,
claims, policies, generator, output bytes, audience, channel, or publishing
principal requires the applicable decisions to be repeated.

All material is private by default when no valid exact authorization exists.
Generation, validation, proof, obligation discharge, CAV2 promotion, or domain
adoption does not grant publication permission.

### Formal Interpretation

```text
PublicationAuthorization =
  (release_authorizations, exact_output_approval, publication_receipt?)

publishable(output, audience, channel)
  <-> every contributing source has a valid exact release authorization
      and privacy_validation(output) = pass
      and exact_output_approval binds
          (output bytes, output digest, audience, channel, claim ceiling)

generated(output) =/=> publishable(output, audience, channel)
validated(output) =/=> publishable(output, audience, channel)
promoted(output)  =/=> publishable(output, audience, channel)
```

Source owners and the publishing principal are separate authority roles. A
generator or validator may check that bindings exist and match; it cannot act as
either owner unless a separate authority decision explicitly assigns that role.

### Schema

Schema handle: `CAV2-D57-SCHEMA` — tracked in [DEFINITION-SCHEMAS.md](DEFINITION-SCHEMAS.md).
Status: tracked (documentary).
Bound to: `CAV2-D57` exact publication authorization.

```text
ReleaseAuthorization =
  (source_owner, owning_system, source_refs, source_classifications,
   allowed_surface, forbidden_surface, claim_ceiling, audience,
   channel, policy_refs, publishing_principal, authorization_ref,
   validity_conditions, revocation_route)

ExactOutputApproval =
  (release_authorization_refs, generator_ref, generation_input_refs,
   policy_refs, privacy_validation_receipt_ref, output_ref,
   output_byte_length, output_digest, audience, channel, target,
   claim_ceiling, limitation_notice, publishing_principal,
   decision, decision_ref, validity_conditions, revocation_route)

PublicationReceipt =
  (output_digest, audience, channel, target_locator,
   publishing_principal, published_at, authorization_refs,
   observed_result)
```

All identities, versions, policies, decisions, source objects, inputs, outputs,
and receipts are owner-qualified, version-exact, and digest-bound where bytes
exist. `decision` is `approve | refuse`. A publication receipt records an
observed boundary crossing; it does not supply missing permission or make a
claim true.

### Operational Interpretation

Use this definition when someone wants to turn private DomainSpec, CAV2,
proof-substrate, Mint, Cedar, Datalog, Lean, research, evidence, or generated
material into a public-safe output. First ask each source owner exactly what may
be used and said. Generate and check the candidate privately. Then ask the named
publishing principal about the final bytes, not a template or promise. If any
bound input or output changes, return to the relevant decision.

### Plain-Language Intuition

Permission to prepare a public draft is not permission to publish it. Owners
first approve the ingredients and limits; a publisher later approves the exact
finished file and destination.

### Domain-Context Voice

In CyberAlchemy v2 this definition keeps the private authority spine and its
domain evidence private while still allowing a later, deliberately bounded
public explanation or result. A generated documentation page remains a private
projection until both decisions exist. Public Arcanum receives no private prose,
proof internals, engine mechanisms, research, or validation material merely
because a generator or checker succeeded.

### Boundary

Exact publication authorization is not classification authority, adoption,
promotion, proof, truth, freshness, privacy validation, deployment, or release by
itself. It does not create a universal classification vocabulary: each source
owner retains its own meanings, and a projection carries exact owner-qualified
references without reinterpreting them. It authorizes no present public output;
every actual publication still needs exact permissions and a boundary-crossing
receipt.

### Primary Consumers

- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- [DEFINITION-SCHEMAS.md](DEFINITION-SCHEMAS.md)
- [DEFINITION-DRIFT-AUDIT.md](DEFINITION-DRIFT-AUDIT.md)
- [../../SOURCE-MAP.md](../../SOURCE-MAP.md)
- [../boundaries.md](../boundaries.md)
- [../../../research/2026-08-20-domainspec-v2-cav2-proof-obligation-substrate/development/refinement-runs/20260821T145409Z-proof-substrate-next-steps/stages/10-gate-01-top03-refresh/apply-corrected/owner-decisions/GATE-08-DECISION.md](../../../research/2026-08-20-domainspec-v2-cav2-proof-obligation-substrate/development/refinement-runs/20260821T145409Z-proof-substrate-next-steps/stages/10-gate-01-top03-refresh/apply-corrected/owner-decisions/GATE-08-DECISION.md)

## CAV2-D58: Constitution

Status: active
Term: constitution
Aliases: governed constitution, modular constitution, structure constitution, constitution artifact
Promoted: 2026-08-29 by owner-requested definitions defect repair; definition authority only, with no constitution, rule, policy, validator, or gate activation

### Normative Definition

A constitution is an **owner-scoped, selector-bound, composable authority
artifact** that turns axioms and invariants into reusable governance rules and
policies for named kinds of governed subject. Those subjects may be artifacts,
tasks or workflows, repository-owned agent actions, system operations or state
transitions, validation surfaces, or authority movements.

A constitution must declare its scope, subject kinds, selectors, owner route,
authority level, rules and policies, precedence and composition behavior,
validation modes or bindings, downstream effect, challenge route, and retirement
or split conditions. It constrains a subject only after an owner decision adopts
the exact constitution version and scope and the subject matches its selectors.
A candidate, selected, or context-loaded constitution does not govern by those
facts alone.

### Formal Interpretation

```text
Constitution C =
  (id, version, scope, subject_kinds, selectors, rules, policies,
   precedence, composition, owner_route, authority_level,
   validation_bindings, downstream_effect, challenge_route,
   retirement_or_split_rule)

subject_kinds(C) subset-of
  { artifact, task_or_workflow, repository_owned_agent_action,
    system_operation_or_state_transition, validation_surface,
    authority_movement }

applies(C, subject) <->
  promoted(C) and version_exact_owner_adoption(C) and
  subject in scope(C) and selector_matches(C, subject)

validation_mode(rule) in { deterministic, review, hybrid, none-yet }
candidate(C) or selected(C) or context_loaded(C) =/=> applies(C, subject)
```

Schema handle: `CAV2-D58-SCHEMA` — tracked in
[DEFINITION-SCHEMAS.md](DEFINITION-SCHEMAS.md). Status: tracked (documentary);
no machine validator is activated by this definition.

### Operational Interpretation

Use a constitution when a recurring class of future subjects needs the same
authoritative constraints, ownership, precedence, examples, and validation
expectations. Keep one-off advice, observations, and owner decisions outside it.
A discipline may gather evidence and route a constitution proposal, but cannot
author or adopt the constitution. A validator may check an adopted rule, but
cannot supply the authority that the constitution and owner decision provide.

### Plain-Language Intuition

A constitution is a named rulebook for named things. It says which rules apply,
to what, under whose authority, and how conflicts and checks work. It is not a
universal prompt for every person, agent, repository, or external system.

### Domain-Context Voice

In CyberAlchemy v2, Constitution is one closed authority kind in
[AUTHORITY-MODEL.md](../AUTHORITY-MODEL.md). The candidate
[Stable Repository Constitution](../constitutions/STABLE-REPOSITORY-CONSTITUTION.md)
is an instance candidate; this definition does not promote or activate it. A
repository constitution cannot override system, developer, host, external-owner,
or other higher-precedence authority outside its declared scope.

### Boundary

A constitution is **not** an axiom (`CAV2-D53`), invariant (`CAV2-D54`),
discipline (`CAV2-D50`), decision, validator, gate (`CAV2-D37`), evidence, or
proof. Axiom grounds; invariant states what must remain true; governance rule or
policy operationalizes; discipline stewards a recurring practice; owner decision
adopts; constitution carries the adopted constraints; validator or gate checks or
performs enforcement. Authority (`CAV2-D34`) scopes every part of that graph.

Promoting this term creates Definition authority for the meaning of
`constitution`. It does not promote any constitution artifact, adopt a rule or
policy, activate a validation binding, or authorize an effect.

### Primary Consumers

- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- [DEFINITION-SCHEMAS.md](DEFINITION-SCHEMAS.md)
- [DEFINITION-DRIFT-AUDIT.md](DEFINITION-DRIFT-AUDIT.md)
- [../AUTHORITY-MODEL.md](../AUTHORITY-MODEL.md)
- [../constitutions/](../constitutions/)
- [../../../.agents/skills/constitution-governance/SKILL.md](../../../.agents/skills/constitution-governance/SKILL.md)

## CAV2-D59: Goal

Status: active
Term: goal
Aliases: governed goal, project goal, outcome goal
Promoted: 2026-08-29 by owner-requested product-foundation modeling; definition authority only

### Normative Definition

A goal is a durable, attributable statement of a desired future outcome for one
project. It says what should become true, why that outcome matters, what is in
and out of scope, who owns the goal, how success will be judged, which evidence
is required, how it connects to a product thesis or other purpose, and how it
can be revised, challenged, achieved, abandoned, or superseded.

A goal may stay active without a deadline. It becomes achieved only when its
declared success conditions have adequate evidence and the goal owner records
the lifecycle change. Activity, progress, a passing sub-check, or an agent claim
does not achieve it automatically.

### Formal Interpretation

```text
Goal =
  (id, project_ref, outcome, rationale, thesis_refs, scope, exclusions,
   owner_route, success_conditions, evidence_requirements, evidence_refs,
   lifecycle_state, target_horizon?, revision_history, challenge_route)

lifecycle_state in { draft, active, achieved, abandoned, superseded }

achieved(Goal) only if
  all_required_success_conditions_have_adequate_evidence
  and owner_records_achievement
```

### Schema

Schema handle: `CAV2-D59-SCHEMA` — tracked in
[DEFINITION-SCHEMAS.md](DEFINITION-SCHEMAS.md). Status: tracked (documentary).
The machine-checkable candidate instance contract is owned by
[../../goals/schemas/goal-package.schema.json](../../goals/schemas/goal-package.schema.json).

### Operational Interpretation

Use a goal when a project needs to preserve an eventual result across sessions,
plans, tasks, experiments, and implementation changes. Let plans choose a path
and tasks perform bounded work, but keep checking both against the goal's result
and success evidence.

### Plain-Language Intuition

A goal says which future result the project is trying to reach and what evidence
will let us honestly say it was reached.

### Domain-Context Voice

In CyberAlchemy v2, a goal connects product meaning to project work. For
example, the PythonConstraint goal connects the CyberAlchemy product thesis to a
bounded CyberAlchemy-v2 and DomainSpec-v2 experiment. Its plans and runs may
change, but the desired result, owner, evidence requirements, and current
achievement claim remain visible.

### Boundary

A goal is not intent (`CAV2-D39`), a project (`CAV2-D60`), a plan, a task, a
work pack, evidence, a deadline, or authority to execute. Intent can orient work
before its final result is clear. A goal states the result clearly enough to be
tested. A plan chooses how to pursue it. Evidence supports an achievement
decision. The goal itself grants no implementation, publication, deployment, or
external-effect authority.

### Primary Consumers

- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- [DEFINITION-SCHEMAS.md](DEFINITION-SCHEMAS.md)
- [../../goals/README.md](../../goals/README.md)
- [../../goals/GOAL-DOCUMENT-TYPE.md](../../goals/GOAL-DOCUMENT-TYPE.md)
- [../../product/PRODUCT-THESIS.md](../../product/PRODUCT-THESIS.md)

## CAV2-D60: Project

Status: active
Term: project
Aliases: governed project, project identity, work project
Promoted: 2026-08-29 by owner-requested product-foundation modeling; definition authority only

### Normative Definition

A project is a durable, identity-bearing coordination boundary that groups
related goals, owners, evidence, decisions, artifacts, work, and lifecycle state
toward a declared purpose.

A project must name its purpose, scope, exclusions, owners, current Goal references,
evidence index, lifecycle state, purpose or product-thesis connections,
instance-binding references, and challenge route. Its identity remains stable
when a plan, task, folder, tool, or implementation changes.

### Formal Interpretation

```text
Project =
  (id, name, purpose, scope, exclusions, owner_routes, goal_refs,
   research_refs, experiment_refs, evidence_index, thesis_refs,
   instance_binding_refs, lifecycle_state, challenge_route)

lifecycle_state in { proposed, active, completed, cancelled, superseded }
|goal_refs| >= 1
proposed(Project) => exists g in goal_refs: lifecycle(g) in { draft, active }
active(Project) => exists g in goal_refs: lifecycle(g) = active
```

### Schema

Schema handle: `CAV2-D60-SCHEMA` — tracked in
[DEFINITION-SCHEMAS.md](DEFINITION-SCHEMAS.md). Status: tracked (documentary).
The machine-checkable candidate project record is owned by
[../../goals/schemas/goal-package.schema.json](../../goals/schemas/goal-package.schema.json).
Its v2 shape adds `instance_binding_refs`; the referenced records are owned by
the Project binding registry rather than embedded as untyped Project metadata.

### Operational Interpretation

Use a project to keep several sessions and kinds of work connected to the same
purpose. A project can have several goals, and each goal in the current contract
belongs to exactly one project. A proposed Project may begin with a draft Goal;
an active Project must retain at least one active Goal. Project evidence may come from many spaces, but
it stays indexed under the project identity. When the Project coordinates a
locally owned instance of a parent model, `instance_binding_refs` names the
exact `CAV2-D64-SCHEMA` records that preserve that relationship. An empty list
means that the Project currently asserts no recursive instance binding.

### Plain-Language Intuition

A project is the named piece of work that keeps its goals, owners, evidence, and
history together even when the files and plans move.

### Domain-Context Voice

In CyberAlchemy v2, the PythonConstraint experiment is a project shared by the
CyberAlchemy-v2 product lane and the DomainSpec-v2 implementation/research lane.
It may use `product/`, `goals/`, `projects/domainspec-v2/`, validation, and
temporary runtime spaces without becoming identical to any one of those places.

### Boundary

A project is not a project space (`CAV2-D15`), goal (`CAV2-D59`), product,
repository, plan, work pack, session, team, or authority envelope. A project
space is a place where work lives; a project is the identity and coordination
boundary of the work. Creating a project does not authorize its goals or tasks.
Project membership, a folder named `project`, or a DomainSpec minted-project
manifest does not create a `CAV2-D60` Project or a recursive instance binding.

### Primary Consumers

- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- [DEFINITION-SCHEMAS.md](DEFINITION-SCHEMAS.md)
- [../../goals/README.md](../../goals/README.md)
- [../../goals/GOAL-DOCUMENT-TYPE.md](../../goals/GOAL-DOCUMENT-TYPE.md)
- [../../goals/bindings/recursive-instance-bindings.json](../../goals/bindings/recursive-instance-bindings.json)

## CAV2-D61: Research

Status: active
Term: research
Aliases: governed research, project research, research aggregate
Promoted: 2026-08-29 by owner-requested product-foundation modeling; definition authority only

### Normative Definition

Research is a bounded, attributable investigation that gathers and organizes
source material and observations to answer one declared question for a Project
and one or more Goals.

A Research artifact must preserve its question, scope, sources, method,
evidence aggregate, counterevidence, limitations, owner route, Goal and Project
links, and references to any separate findings. Research records what was
investigated and gathered. It does not silently turn its evidence aggregate
into a conclusion, decision, definition, specification, or product claim.

### Formal Interpretation

```text
Research =
  (id, project_ref, goal_refs, question, scope, sources, method,
   evidence_aggregate, counterevidence, findings_refs, limitations,
   created, last_updated, owner_route, challenge_route)

Research.outcome is absent
Findings.question = Research.question
Findings derives_from Research
```

### Schema

Schema handle: `CAV2-D61-SCHEMA` — tracked in
[DEFINITION-SCHEMAS.md](DEFINITION-SCHEMAS.md). Status: tracked (documentary).
The machine-checkable private record and Markdown carrier checks live under
[../../research/](../../research/README.md).

### Operational Interpretation

Use Research when a Project must inspect literature, repositories, benchmarks,
past evidence, observations, or competing explanations before deciding what to
believe or do. Keep the aggregate separate from findings so a later reader can
see the source material without inheriting the synthesis as fact.

### Plain-Language Intuition

Research is the evidence-gathering investigation behind an answer. It shows the
question, what was examined, how it was examined, and what remains uncertain.

### Domain-Context Voice

In CyberAlchemy v2, the PythonConstraint Research record explains why that
benchmark was selected, which exact sources support the selection, and which
questions about DomainSpec-v2 fit remain open. It informs the Project and Goal
without claiming that the experiment has run.

### Boundary

Research is not a Goal (`CAV2-D59`), Project (`CAV2-D60`), experiment
(`CAV2-D62`), findings, owner decision, canonical definition, proof, or
execution authority. It is an ephemeral canonical Evidence artifact: it records
an investigation at a time and cannot become authority by promotion.

### Primary Consumers

- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- [DEFINITION-SCHEMAS.md](DEFINITION-SCHEMAS.md)
- [../../research/README.md](../../research/README.md)
- [../../research/RESEARCH-DOCUMENT-TYPE.md](../../research/RESEARCH-DOCUMENT-TYPE.md)
- [../../goals/README.md](../../goals/README.md)

## CAV2-D62: Experiment

Status: active
Term: experiment
Aliases: governed experiment, project experiment, controlled experiment
Promoted: 2026-08-29 by owner-requested product-foundation modeling; definition authority only

### Normative Definition

An experiment is a bounded, attributable empirical test that produces
observations by applying a declared protocol to a defined subject under named
conditions in order to test a question, hypothesis, Goal condition, or Research
question.

An Experiment artifact must preserve its Project and Goal links, Research
links when present, question or hypothesis, subject, protocol, conditions,
variables or interventions, measures, environment, prerequisites, stop rules,
run references, evidence references, findings references, limitations, owner
route, and challenge route. Missing run evidence means the experiment was not
shown to have run.

### Formal Interpretation

```text
Experiment =
  (id, project_ref, goal_refs, research_refs, question_or_hypothesis,
   subject, protocol_ref, conditions, variables_or_interventions,
   measures, environment, prerequisites, stop_rules, run_refs,
   evidence_refs, findings_refs, limitations, created, last_updated,
   owner_route, challenge_route)

ran(Experiment) only if valid_run_refs_exist
concluded(Experiment) only through separate Findings or owner decision
```

### Schema

Schema handle: `CAV2-D62-SCHEMA` — tracked in
[DEFINITION-SCHEMAS.md](DEFINITION-SCHEMAS.md). Status: tracked (documentary).
The machine-checkable private record and Markdown carrier checks live under
[../../experiments/](../../experiments/README.md).

### Operational Interpretation

Use an Experiment when a Project needs observations created by a repeatable
test rather than only existing sources or argument. Freeze the protocol inputs
and claim limits before treating run output as comparable evidence. Keep design,
run evidence, analysis, and owner decisions distinct.

### Plain-Language Intuition

An experiment is a fair, recorded test. It says what was tested, under which
conditions, what was measured, what happened, and what the test cannot prove.

### Domain-Context Voice

In CyberAlchemy v2, the PythonConstraint Experiment record narrows the prepared
Define downstream-utility protocol to the owner-selected benchmark. Until exact
run receipts exist, it remains a documented experiment design and cannot
support a claim that Define or DomainSpec improves engineering outcomes.

### Boundary

An experiment is not Research (`CAV2-D61`), a Goal (`CAV2-D59`), a plan, a
runtime, a test suite, one command, findings, causal proof, or authority to run.
It is an ephemeral canonical Evidence artifact. A successful validator can show
that its record is well formed; it cannot show that the experiment ran or that
its hypothesis is true.

### Primary Consumers

- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- [DEFINITION-SCHEMAS.md](DEFINITION-SCHEMAS.md)
- [../../experiments/README.md](../../experiments/README.md)
- [../../experiments/EXPERIMENT-DOCUMENT-TYPE.md](../../experiments/EXPERIMENT-DOCUMENT-TYPE.md)
- [../../goals/README.md](../../goals/README.md)

## CAV2-D63: Product Thesis

Status: active
Term: product thesis
Aliases: governed product thesis, product commitment thesis, product meaning thesis
Promoted: 2026-08-29 by owner-requested product-foundation correction; definition authority only

### Normative Definition

A product thesis is an owner-held, durable proposition that explains which
product should exist, for whom, which problem it addresses, how it intends to
create value, which first-order principles constrain it, which outcomes it
seeks, which claims remain hypotheses, what evidence tests particular
realizations, and what evidence or counterevidence requires revision.

A Product Thesis must preserve the product identity, participants, problem,
value proposition, value mechanism, first-order principles, intended outcomes,
boundaries, hypotheses, evidence and counterevidence routes, revision criteria,
owner route, commitment state, revision history, and challenge route. Its
principles may be committed before a complete product realization exists, but
outcome, market, causal, and effectiveness claims remain bounded by evidence.

### Formal Interpretation

```text
ProductThesis =
  (id, product_ref, participants, problem, value_proposition,
   value_mechanism, first_order_principles, intended_outcomes,
   boundaries, hypotheses, evidence_routes, counterevidence_routes,
   revision_criteria, owner_route, commitment_state,
   revision_history, challenge_route)

commitment_state in { draft, committed, revised, retired, superseded }

committed(ProductThesis) =/=> realized(Product)
evidence_for_one_realization =/=> proves(ProductThesis)
```

### Schema

Schema handle: `CAV2-D63-SCHEMA` — tracked in
[DEFINITION-SCHEMAS.md](DEFINITION-SCHEMAS.md). Status: tracked (documentary).
The private machine record and document validator live under
[../../product/](../../product/README.md).

### Operational Interpretation

Use a Product Thesis to keep product direction stable while Projects, Goals,
Research, Experiments, designs, interfaces, and implementations change. Trace
each Project and Goal to the part of the thesis it is trying to realize or test.
Use evidence to judge realizations and bounded outcome claims, and use the
declared revision criteria when evidence challenges the thesis itself.

### Plain-Language Intuition

A product thesis says why a product should exist, what we believe it must do and
protect, how it should create value, and what evidence could make us change our
mind.

### Domain-Context Voice

In CyberAlchemy v2, the Product Thesis commits to an ergonomic, governed
human-machine work loop that preserves human agency, shared meaning, evidence,
ownership, bounded authority, and honest incompleteness. The PythonConstraint
Project tests one bounded realization of that thesis. It cannot prove the whole
thesis or redefine it from one experiment.

### Boundary

A Product Thesis is not the product, product vision, strategy, roadmap,
business plan, Goal (`CAV2-D59`), Project (`CAV2-D60`), premise (`CAV2-D55`),
hypothesis, specification, evidence, market claim, or implementation. It can
contain hypotheses and guide specifications without becoming either one. A
committed thesis does not prove that the product exists, works, creates value,
has customers, or has product-market fit.

Promoting this term creates Definition authority for the meaning of `product
thesis`. It does not promote the CyberAlchemy thesis artifact, approve a product
strategy, achieve a Goal, authorize an Experiment, or validate product value.

### Primary Consumers

- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- [DEFINITION-SCHEMAS.md](DEFINITION-SCHEMAS.md)
- [../../product/PRODUCT-THESIS.md](../../product/PRODUCT-THESIS.md)
- [../../product/PRODUCT-THESIS-DOCUMENT-TYPE.md](../../product/PRODUCT-THESIS-DOCUMENT-TYPE.md)
- [../../ontology/product/README.md](../../ontology/product/README.md)
- [../../goals/README.md](../../goals/README.md)

## CAV2-D64: Recursive Instance Ownership Invariant

Status: active
Term: recursive instance ownership invariant
Aliases: instance ownership invariant, recursive ownership invariant, parent-instance ownership invariant, model-instance ownership invariant, capability instance ownership
Promoted: 2026-08-29 by owner-requested product-instance ownership modeling; definition authority only

### Normative Definition

The recursive instance ownership invariant is the must-hold CyberAlchemy v2
condition that a governed parent model and a locally owned instance remain
connected without collapsing their semantic authority, coordination boundary,
or lifecycle.

The parent-model owner holds scoped semantic authority for the shared contract
and the conditions under which it may be instantiated, specialized, or
composed. The named instance owner holds a separate scoped semantic authority
for the instance's local meaning, state, evidence, and lifecycle. Here,
`ownership` is shorthand for these explicit `CAV2-D34` authority claims; it is
not inferred from a folder, label, repository permission, or generic
responsibility. A Project carries the typed binding, goals, owners, evidence,
and challenge route that keep the instance connected to its purpose, but
Project membership or file placement does not itself create semantic,
adoption, or execution authority.

The parent and instance must be joined by an explicit `CAV2-D16` typed relation
bound to an exact parent version or state. The instance may narrow or realize
the parent contract only inside its declared specialization scope. It must not
silently redefine the parent. The parent must not absorb, overwrite, or treat
instance-local meaning as shared authority without the instance owner's route
and the applicable `CAV2-D48` promotion or adoption path.

### Invariant Statement

For a parent model `M`, owned instance `I`, coordinating Project `P`, and typed
binding `B`, the relationship is admissible only when:

```text
RecursiveInstanceBinding =
  (binding_id, project_ref, model_ref, model_version_ref,
   model_authority_claim, instance_ref, instance_kind,
   instance_authority_claim, relation_kind, inherited_contract_ref,
   extension_scope, adoption_decision_ref, adoption_owner_route,
   adoption_posture, conformance_ref, lifecycle_state, altitude,
   evidence_refs, challenge_route, drift_owner_route, drift_route,
   recomposition_route, recursion_budget_or_stop,
   terminal_owner_or_handoff, authority_effect)

valid(B) only if
  B.project_ref = P
  and B.model_ref = M
  and B.instance_ref = I
  and exact(B.model_version_ref)
  and typed_relation(B.relation_kind, I, M)
  and scoped_authority(B.model_authority_claim, M)
  and scoped_authority(B.instance_authority_claim, I)
  and exact(B.inherited_contract_ref)
  and within_scope(I, B.extension_scope)
  and owner_decided(B.adoption_decision_ref,
                    B.adoption_owner_route,
                    B.adoption_posture,
                    B.model_version_ref)
  and preserves_parent_meaning(I, M)
  and B.authority_effect = none

change(M) =/=> adopted_by(I)
change(I) =/=> promoted_into(M)
conforms(I, M) =/=> authority(I) or authority(M)
member_of(I, P) =/=> authority(I)

conflicts_with(I, B.inherited_contract_ref) => drift(I, M)
within(I, B.extension_scope) =/=> drift(I, M)

becomes_parent(I)
  => exists B_next:
       complete_recursive_binding(B_next)
       and altitude(B_next) > altitude(B)
       and bounded(B_next.recursion_budget_or_stop,
                   B_next.terminal_owner_or_handoff)
```

The model-authority lane and instance-authority lane remain distinct roles even
when the same actor currently fills both. Variation inside the declared
extension scope is local specialization, not drift. Conflict with the exact
adopted mandatory contract is drift and is routed to the named drift owner. If
the parent version, either authority claim, inherited contract, extension scope,
adoption decision, conformance relation, challenge route, drift route,
recomposition path, or recursive stop is missing or disputed, the binding is
residue or a blocker rather than an implicit ownership or authority transfer.

### Schema

Schema handle: `CAV2-D64-SCHEMA` — tracked in
[DEFINITION-SCHEMAS.md](DEFINITION-SCHEMAS.md). Status: tracked (documentary).
The Project package owns the first machine-checkable binding registry because
Project carries the durable coordination identity. `CAV2-PROJECT-SCHEMA-AMEND-D64-001`
adds binding references to the Project record and a closed registry shape, but
the registry currently contains no concrete binding.
`CAV2-GOAL-PACKAGE-SCHEMA-AMEND-D64-PREREQ-001` adds separate Project-owned
candidate registries for complete `CAV2-D34` claim tuples and exact inherited
contracts. These prerequisite records remain source-declared candidates: they
do not activate authority, admit a relation, record adoption, prove
conformance, or satisfy this invariant. The Governance ontology
registers this definition as `GOV-INV-CAV2-D64` and links it to the candidate
review rule `GOV-RULE-D64-BINDING-COMPLETE`; those records remain ontology
instances with no authority, adoption, enforcement, implementation, or Project
conformance effect.

`CAV2-GOAL-PACKAGE-SCHEMA-AMEND-D64-ADOPTION-CANDIDATE-001` first added one
Project-owned adoption-decision candidate envelope bound to the exact Define
model-version ref and inherited-contract digest.
`CAV2-GOAL-PACKAGE-SCHEMA-AMEND-D64-RELATION-CANDIDATE-001` then records the
user's `REL-INSTANCE-OF` choice as one directed, Project-owned semantic
relation candidate and binds that candidate into the envelope by ID and digest.
`CAV2-GOAL-PACKAGE-SCHEMA-AMEND-D64-RELATION-ADMISSION-001` preserves that
candidate and its digest, records the protected joint-owner `ADMIT-INSTANCE-OF`
decision, and adds a separately digested admitted-relation record. That exact
record supplies the `typed_relation(...)` conjunct for the named source, target,
versions, direction, kind, and inherited contract only. The envelope's selected
D48 adoption posture and owner decision remain null. Admission is not the
`owner_decided(...)` witness, conformance, authority activation, or a concrete
binding's `adoption_decision_ref`.

Field meanings:

- `binding_id` identifies the binding; `project_ref` identifies its coordinating
  Project; `model_ref` and `model_version_ref` identify the exact parent state.
- `model_authority_claim` and `instance_authority_claim` each carry the
  `CAV2-D34` scope, owner, surface, object, operation, basis, effect, and
  challenge route for their separate semantic lanes.
- `instance_ref` and `instance_kind` identify the local object;
  `relation_kind` types its directed connection to the parent.
- `inherited_contract_ref` identifies the mandatory adopted parent contract;
  `extension_scope` states where local specialization is allowed.
- `adoption_decision_ref`, `adoption_owner_route`, and `adoption_posture` bind
  adoption of the exact parent version to an owner decision rather than
  proximity or conformance.
- `conformance_ref`, `lifecycle_state`, `altitude`, and `evidence_refs` record
  checked relationship state without granting authority.
- `challenge_route`, `drift_owner_route`, and `drift_route` distinguish a
  challenge from contract drift and name who routes resolution.
- `recomposition_route` returns instance learning upstream only as a typed
  candidate; `recursion_budget_or_stop` and `terminal_owner_or_handoff` bound
  any instance that becomes a parent.
- `authority_effect` is `none` for the binding itself.

The current Define prerequisite candidate uses `cav2.define` as the parent and
`cav2.define.system-runtime.v1` as the local instance. It binds both to exact
profile states and selects `instance_of` only as an unadmitted semantic
candidate. The protected joint-owner decision now admits one separately digested
exact relation as the `typed_relation(...)` witness. `child-package` remains
separate topology evidence; authority-claim promotion, D48 adoption, conformance,
complete recursion termination, and terminal handoff remain unresolved. The exact
D48 adopt/reject/defer/stop gate is now presented to the `CyberAlchemy v2 Define
runtime owner`, but no option is selected; gate preparation is not the
`owner_decided(...)` witness. This is
typed-relation evidence only, not a `RecursiveInstanceBinding` or D64 satisfaction.

### Axiom And Invariant Basis

The authority basis is `CAV2-D34` and `CAV2-D41`: authority moves only through
an explicit scoped owner route and does not transfer through proximity,
membership, generation, validation, or repeated use. `CAV2-D30` supplies the
bounded recursive separation of artifact, layer, owner, recomposition, and stop
condition. `CAV2-D16` requires the parent-instance wire to be typed and visible.

This definition specializes those existing principles for parent-model and
owned-instance relationships. It does not create a new authority kind.

### Validation Mode

Current validation mode: `review-only`.

The Governance ontology registration makes the invariant and its candidate
operational rule discoverable. The Project package can now validate the admitted
typed-relation witness plus the closed shape and reference closure of any registered
binding, but it has no concrete binding to evaluate. D48 owner adoption, conformance,
complete recursion termination, and terminal handoff remain absent, so CAV2-D64 is
not satisfied. This does not supply the unresolved source-owned semantic
version, exact grounding Governance Axiom, adopted Constitution membership,
enforcement binding, complete Define Project binding, kernel program, or runtime
integration.

A review checks that every load-bearing parent-instance relationship has the
complete `CAV2-D64-SCHEMA` binding, that both owner lanes resolve, that the
Project is not treated as an authority envelope, that parent and instance
changes do not propagate implicitly, that adoption binds an exact parent
version and owner decision, that inherited contract and extension scope are
separate, that drift and recomposition follow their named routes, and that
conformance claims remain inside their evidence. A later Project-package
validator may make these checks deterministic only after a separately reviewed
schema amendment witness.

### Operational Interpretation

Use this invariant when CyberAlchemy defines a reusable product, capability,
method, ontology, or other parent model and a Project creates or evolves a
locally owned instance. Register the exact parent version, instance package,
both authority claims, inherited contract, extension scope, adoption decision,
specialization relation, conformance evidence, challenge and drift routes,
recomposition path, and recursive stop in the Project. Route shared-model
changes to the parent owner and instance-local changes to the instance owner.

### Plain-Language Intuition

The parent owns the blueprint. The local capability owns its built instance.
The Project keeps the labeled connection between them. Neither side may quietly
rewrite the other.

### Domain-Context Voice

In CyberAlchemy v2, the product ontology is the intended owner surface for the
shared CyberAlchemy product model. A Define Project can coordinate the goals,
owners, evidence, and lifecycle for a Define product instance, while a
separately established Define instance owner would own that instance's business
meaning. The product ontology may register and constrain an adopted instance;
the Define instance may specialize the adopted product contract inside its
extension scope. Neither relationship lets the Project, ontology projection,
validation result, or runtime claim semantic authority it was not granted.

The current candidate profiles do not yet prove this binding: they do not carry
the complete version-exact adoption record and separately scoped instance-owner
claim required here. They are candidate evidence for the first application of
the invariant, not a conforming instance by declaration.

### Boundary

This invariant is not authority, ownership by file location, Project authority,
repository access, inheritance by naming, schema conformance, implementation
success, automatic adoption, or promotion. It does not require every artifact
to have a parent model, make every capability a Project, or make every instance
canonical. It governs only relationships where downstream work relies on a
parent model and an independently scoped owned instance remaining connected.

It is not a Discipline (`CAV2-D50`). A later Discipline may steward recurring
binding audits and hardening, and a Constitution may enforce selected bindings,
but neither is created or adopted by this definition.

### Primary Consumers

- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- [DEFINITION-SCHEMAS.md](DEFINITION-SCHEMAS.md)
- [../../goals/README.md](../../goals/README.md)
- [../../ontology/product/README.md](../../ontology/product/README.md)
- [../../ontology/governance/invariants.json](../../ontology/governance/invariants.json)
- [../../ontology/governance/rules.json](../../ontology/governance/rules.json)
- [../../goals/ontology/project-instance-bindings.json](../../goals/ontology/project-instance-bindings.json)
- [../../goals/ontology/project-binding-schema-amendment.json](../../goals/ontology/project-binding-schema-amendment.json)
- [../../define/business-ontology/README.md](../../define/business-ontology/README.md)

## CAV2-D65: DomainSpec-Governed Construction Invariant

Status: active
Term: prototype-first DomainSpec construction invariant
Aliases: DomainSpec-governed construction invariant, DomainSpec v2 construction invariant, definitions-to-implementation construction invariant, DomainSpec-first construction path, CyberAlchemy construction pipeline
Promoted: 2026-08-30 by explicit owner direction to make DomainSpec v2 the construction path inside CyberAlchemy v2; definition authority only
Revised: 2026-09-03 by explicit owner direction to make product construction prototype-first and defer every authority request until after tested-product approval

### Normative Definition

The prototype-first DomainSpec construction invariant is the must-hold
CyberAlchemy v2 condition that every new or materially revised
implementation-bearing system or capability advances through one inspectable,
version-exact learning and construction chain:

```text
prototype definitions
  -> agent-facing ontology scaffolds
  -> product-capability and capability-local business prototypes
  -> DomainSpec v2 authored prototype source
  -> deterministic compiled graph and system-ontology scaffolds
  -> implementation prototypes iterated with tests
  -> one exact testable product candidate
  -> current product-test evidence
  -> product approval
  -> only then requests for authority, admission, activation, cutover,
     publication, release, or deployment decisions
```

Definitions begin explicitly as prototypes. They may be reused, split,
specialized, contradicted, or revised as construction teaches the product what
its terms must mean. Ontology records are scaffolded early to help agents find
concepts, relationships, constraints, questions, and evidence. An ontology
scaffold is provisional navigation and coordination material: it is not
canonical truth, admission, permission, implementation authority, or a reason
to stop prototype learning.

Product, business, DomainSpec, compiled-system, and implementation artifacts
remain prototypes while they are being iterated. DomainSpec is the authored
technical source for each compiled prototype epoch. Its graph and system
ontology must be deterministic projections of that exact source, not
independently authored competitors. The implementation and scaffolds may be
revised together through bounded prototype loops, but every testable product
candidate freezes their exact identities and digests for testing.

Product approval may be requested only for an exact testable candidate whose
required product tests pass with current evidence. Product approval accepts the
candidate as worth considering for governed use; it grants no operational
authority. No request for authorization, ontology or system admission,
activation, cutover, publication, release, deployment, or other authority
decision is eligible before that exact tested candidate receives product
approval. Each post-approval effect remains a separate owner decision.

Every candidate boundary preserves predecessor identities, versions, digests,
test outcomes, residue, and challenge routes. Missing or changing prototype
material causes another prototype epoch; it does not require an authority
decision. Missing, stale, unsupported, ambiguous, or non-reproducible bytes in
a frozen test candidate invalidate that candidate's test or approval
eligibility; they never become an implicit PASS.

### Invariant Statement

For one construction subject `S`, let:

```text
PrototypeConstructionStage =
  {definition_prototype, ontology_scaffold, product_capability_prototype,
   business_prototype, domainspec_prototype, compiled_system_prototype,
   implementation_prototype, testable_product_candidate,
   product_test_evidence, product_approval,
   post_approval_authority_decisions}

PrototypeState =
  {absent, scaffolded, prototyped, blocked, not_evaluable, testable,
   test_failed, tested, product_approved, stale, superseded}

ConstructionBinding =
  (construction_id, project_ref, subject_ref,
   definition_prototype_refs, definition_prototype_digests,
   ontology_scaffold_refs, ontology_scaffold_digests,
   product_capability_prototype_refs, product_capability_prototype_digests,
   business_prototype_refs, business_prototype_digests,
   domainspec_project_ref, domainspec_profile_ref,
   domainspec_language_refs, domainspec_language_digests,
   source_set_ref, source_set_digest,
   compiler_ref, compiler_version_ref, compiler_digest,
   compiled_graph_ref, compiled_graph_digest,
   system_ontology_ref, system_ontology_digest,
   implementation_prototype_ref?, implementation_prototype_digest?,
   testable_product_candidate_ref?, testable_product_candidate_digest?,
   product_test_contract_ref?, product_test_evidence_refs,
   product_approval_ref?, product_approval_candidate_digest?,
   post_approval_decision_refs,
   contributor_routes, stage_states, evidence_refs,
   challenge_route, drift_route, authority_effect)

ontology_scaffold(S) => authority_effect(S) = none
ontology_scaffold(S) =/=> canonical_truth(S)
ontology_scaffold(S) =/=> admission(S)

eligible(product_approval_request) only if
  exact(testable_product_candidate_ref,
        testable_product_candidate_digest)
  and testable(testable_product_candidate_ref)
  and required_product_tests_pass(product_test_contract_ref,
                                  product_test_evidence_refs)
  and current(product_test_evidence_refs)

before(product_approval) =>
  authority_effect(ConstructionBinding) = none
  and eligible(authority_request) = false

eligible(authority_request) only if
  product_approved(product_approval_ref,
                   product_approval_candidate_digest)
  and exact(product_approval_candidate_digest,
            testable_product_candidate_digest)

product_approved(S) =/=> authorized(S)
product_approved(S) =/=> admitted(S)
product_approved(S) =/=> activated(S)
product_approved(S) =/=> cut_over(S)
test_pass(S) =/=> product_approved(S)
```

The prototype portion is intentionally iterative rather than monotonic. Agents
may move backward, replace scaffolds, and create new epochs without requesting
authority. The chain becomes digest-monotonic only when one testable product
candidate is frozen. Any change to that candidate invalidates its dependent
tests and product approval. Product approval opens only the right to prepare and
request separately scoped authority decisions; it performs none of them.

### Schema

Schema handle: `CAV2-D65-SCHEMA` — tracked in
[DEFINITION-SCHEMAS.md](DEFINITION-SCHEMAS.md). Status: tracked (documentary).
The Governance package now owns the first parallel revision-2 prototype
`ConstructionBinding` registry, ontology-scaffold registry, deterministic
freezer/evaluator, and hostile test surface. Its current exact candidate has
passing product-test evidence and is eligible for a product-approval request;
it has no product approval or authority-request eligibility. The earlier
Governance and Goals stage-completion registries implement the superseded
pre-prototype interpretation and remain quarantined diagnostic evidence until
migrated. No current CyberAlchemy package may claim D65 conformance, product
approval, admission, or authority merely from this definition, a registry row,
a deterministic compile, or a passing prototype test.

Field meanings:

- `construction_id`, `project_ref`, and `subject_ref` identify one bounded
  construction chain and its coordinating Project.
- Prototype-definition, ontology-scaffold, product-capability, and business
  refs preserve the exact learning epoch without promoting prototypes.
- DomainSpec project, profile, language, source-set, and compiler bindings name
  the exact authored model and deterministic construction mechanism.
- Compiled-graph and system-ontology refs bind derived scaffolds without
  turning those projections into independent authority.
- Product-test contracts and evidence say whether the exact frozen candidate is
  testable and tested; they do not approve the product.
- `product_approval_ref` binds one exact tested candidate and grants no
  operational authority.
- Post-approval decision refs are absent before product approval and remain
  separately scoped afterward.
- `contributor_routes`, `stage_states`, `evidence_refs`, `challenge_route`, and
  `drift_route` keep decisions, support, dispute, and invalidation explicit.
- `authority_effect` is `none` for the binding itself.

### Ownership And Decision Order

- Before product approval, definitions, ontology, product, business,
  DomainSpec, compiler, implementation, and test owners contribute prototype
  artifacts and evidence. Their validations are learning checkpoints, not
  authorization or authority gates.
- An independent product-test route evaluates the exact frozen candidate.
- The product owner may approve that exact candidate only after the required
  tests pass with current evidence.
- Only after product approval may the applicable authority owners be asked to
  decide admission, authorization, activation, cutover, publication, release,
  deployment, or other effects.

The same actor may occupy more than one route, but product testing, product
approval, and each later authority decision remain distinct. No prototype,
ontology scaffold, compiler receipt, test PASS, or product approval may
substitute for a later authority decision.

### Axiom And Invariant Basis

`CAV2-D16` requires every load-bearing transition to be a visible typed
coupling. `CAV2-D25` requires schema and construction-shape changes to preserve
their amendment witnesses. `CAV2-D34` and `CAV2-D41` prevent validation,
generation, repository location, or implementation success from becoming
authority. `CAV2-D38` bounds every stage claim to its proof. `CAV2-D48` governs
promotion and version-exact adoption. `CAV2-D64` keeps parent DomainSpec models
and locally owned CyberAlchemy instances connected without collapsing their
semantic ownership.

This definition composes those rules into the mandatory CyberAlchemy
construction order. It does not create a new authority kind.

### Validation Mode

Current validation mode: `prototype-review-only`.

The definition and documentary schema are active definition authority. The
current Governance registration and revision-2 machine contract remain
candidate, prototype-only, and non-effectful. Legacy validators built for the
superseded stage-admission sequence remain diagnostic until migrated.

The revision-2 deterministic validator permits bounded prototype iteration,
requires ontology scaffolds to declare their non-authoritative posture, freezes
exact bytes at the testable-candidate boundary, rejects stale or contradictory
product-test evidence, rejects a product-approval record before the required
tests pass, and rejects every authority request before exact product approval.
Its PASS makes a product-approval request eligible; it cannot approve the
product or infer authority from scaffolding, compilation, validation, testing,
or product approval.

### Operational Interpretation

Start with prototype words and an ontology scaffold that helps agents navigate
the product. Build product, business, DomainSpec, compiled-system, and
implementation prototypes together. Iterate until one candidate can be frozen
and tested as a product. After its required tests pass, ask for product approval.
Only after that approval may anyone prepare or ask for the separate authority
decisions needed for governed use or external effect.

Legacy or imported implementation may seed a prototype and its tests. It does
not become approved or authorized by proximity, and it does not force premature
canonicalization of the definitions or ontology scaffolds around it.

### Plain-Language Intuition

Sketch the words and the map so agents can build and learn. Keep revising the
prototypes until the product can really be tested. Approve that exact tested
product first. Only then ask whether it may be admitted, activated, cut over,
published, released, or deployed.

### Domain-Context Voice

Inside CyberAlchemy v2, package-local DomainSpec projects, generated
`NODES.json` and `RELATIONS.json`, product ontologies, and system ontologies may
all help agents construct the next prototype. They remain scaffolds until an
exact implementation-bearing product candidate is frozen and tested. Even a
deterministic projection or complete conformance suite does not create product
approval or authorize governed use.

### Boundary

This invariant does not make prototypes disposable or untraceable, move
CyberAlchemy meaning into DomainSpec, make an ontology scaffold canonical truth,
approve a product, or authorize implementation use, admission, activation,
cutover, publication, release, deployment, or external effect. It does not
require implementation when work legitimately stops at exploratory definitions
or ontology. It governs advancement when CyberAlchemy work moves toward a
product-realizing implementation-bearing system.

### Primary Consumers

- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- [DEFINITION-SCHEMAS.md](DEFINITION-SCHEMAS.md)
- [../../ontology/product/README.md](../../ontology/product/README.md)
- [../../ontology/governance/README.md](../../ontology/governance/README.md)
- [../../define/business-ontology/README.md](../../define/business-ontology/README.md)
- [../../define/system-ontology/README.md](../../define/system-ontology/README.md)
- [../../../projects/domainspec-v2/ARCHITECTURE.md](../../../projects/domainspec-v2/ARCHITECTURE.md)

## CAV2-D66: Context

Status: active
Term: context
Aliases: governed context, work context, product-work context
Promoted: 2026-08-30 by explicit owner direction to make Context a first-class CyberAlchemy v2 concept before Registry Context migration and implementation; definition authority only

### Normative Definition

A Context is a durable, identity-bearing, owner-qualified boundary of relevance
and interpretation for one declared purpose. It names the Product, optional
Project, optional Goal, intended consumers and uses, subject scope, and source
policies that frame what information and meaning may be assembled for the work.

Every CyberAlchemy Context belongs to exactly one Product. A project Context
belongs to exactly one Project. A goal Context belongs to exactly one Project
and focuses on exactly one Goal that already belongs to that Project. The first
contract intentionally allows only one primary Goal per Context; cross-goal
work requires separate Contexts or a later explicitly defined composite model.

A Context identity remains stable across new source epochs, resolution
requests, immutable views, interface presentations, session pauses, and
refreshes that preserve its Product, Project, Goal, and purpose. A material
change to any of those anchors creates a successor Context and supersedes the
earlier one instead of silently changing what the earlier identity meant.

### Formal Interpretation

```text
Context =
  (id, kind, product_ref, project_ref?, goal_ref?, purpose,
   bounded_context_refs, consumer_refs, intended_uses, subject_scope,
   source_policy_refs,
   owner_route, lifecycle_state, revision_history, challenge_route)

kind in { product, project, goal }
lifecycle_state in { draft, active, superseded, retired }
|product_ref| = 1
|project_ref| <= 1
|goal_ref| <= 1
|bounded_context_refs| >= 0
|consumer_refs| >= 1

kind = product => project_ref = null and goal_ref = null
kind = project => project_ref != null and goal_ref = null
kind = goal =>
  project_ref != null
  and goal_ref != null
  and belongs_to(goal_ref, project_ref)

material_change(product_ref, project_ref, goal_ref, purpose) =>
  successor_context_required

current(ContextView) =/=> current(Context)
active(Context) =/=> sources_true_or_authoritative
Context =/= BoundedContext
```

### Schema

Schema handle: `CAV2-D66-SCHEMA` — tracked in
[DEFINITION-SCHEMAS.md](DEFINITION-SCHEMAS.md). Status: tracked (documentary).
The first closed machine-checkable candidate contract is owned by
[../../context/schemas/context.schema.json](../../context/schemas/context.schema.json).
The Context package, its example instances, and its validation receipts remain
separate from canonical definition authority.

### Operational Interpretation

Create a Context before assembling a reusable context view for a Product,
Project, or Goal. Keep the Context identity and purpose stable, then let a
resolver create immutable Views bound to exact requests and source epochs.
Consumers may reuse the Context identity across CLI, chat, and session
continuations, but they must not silently reuse a stale View.

Use a Context to answer: which Product frames this work, which Project and Goal
apply, why context is needed, who will use it, which subjects are in scope, and
which DDD Bounded Context meanings must remain intact, and which source policies
govern resolution. Put selected records, digests,
bindings, and residue in a Context View or Snapshot, not in the Context
identity itself.

### Plain-Language Intuition

Context is the named frame that says what this work is about, why information
is needed, and what belongs in the conversation.

### Domain-Context Voice

Inside CyberAlchemy v2, the first Context connects the CyberAlchemy Product,
the Define Project, the Define first-class ownership Goal, and the Define
shared-meaning consumer. Registry Context can resolve exact Product, Project,
Goal, Language, and Definition selections into one immutable View for that
Context without taking ownership of any source.

The Language package already uses a DDD-style Bounded Context to say where a
Language and model have consistent meaning. A Context may reference zero or
more of those Bounded Contexts. Such a reference preserves each domain model,
Language, conflict, and owner boundary; it does not merge them. A Bounded
Context is not an alias for this definition and is not promoted or redefined
by `CAV2-D66`.

### Boundary

A Context is not a Product, Product Thesis, Project (`CAV2-D60`), Goal
(`CAV2-D59`), Project Space (`CAV2-D15`), DDD Bounded Context, Language,
Registry, source selection, request, immutable View, Snapshot, Context Pack,
Session, prompt, event ledger, authority envelope, owner decision, or execution
permission.

Declaring a source relevant does not make it true, current, authoritative,
accepted, or executable. Activating a Context does not activate its Project or
Goal. A passing Context validator does not prove that a consumer understood or
used the Context correctly. Canonical admission of this definition does not
admit a Context instance, accept a resolver contract, or authorize runtime,
publication, release, deployment, or external effects.

### Primary Consumers

- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- [DEFINITION-SCHEMAS.md](DEFINITION-SCHEMAS.md)
- [../../context/README.md](../../context/README.md)
- [../../ontology/product/README.md](../../ontology/product/README.md)
- [../../goals/README.md](../../goals/README.md)
- [../../language/README.md](../../language/README.md)

## CAV2-D67: Product Capability

Status: active
Term: product capability
Aliases: governed product capability, product behavior capability
Promoted: 2026-08-30 by explicit owner direction to make Capability Ontology canonical; definition authority only

### Normative Definition

A Product Capability is a stable, owner-qualified statement of an outcome that
one Product must enable for named participants or consumers while preserving
explicit scope, contracts, context policies, evidence routes, and authority
limits. It states what the Product must make possible and why that behavior
belongs to the Product. It does not select the agent, component, command,
interface, workflow, or implementation that realizes the outcome.

Every Product Capability belongs to exactly one Product. Its identity remains
stable while realizations, interfaces, evidence, and implementation technology
change, provided the outcome, Product anchor, scope, and owner boundary remain
the same. A material change to any of those anchors requires a successor
Product Capability rather than a silent rewrite.

### Formal Interpretation

```text
ProductCapability =
  (id, product_ref, outcome, scope, exclusions, participant_refs,
   consumer_refs, input_contract_refs, output_contract_refs,
   context_policy_refs, owner_routes, lifecycle_posture,
   realization_refs, evidence_refs, revision_history,
   challenge_route, authority_effect)

|product_ref| = 1
|owner_routes| >= 1
|consumer_refs| >= 1

lifecycle_posture =
  (kind, status, status_vocabulary_ref, evidence, commitment,
   provenance, owner, residue_refs)

lifecycle_posture.kind = product-capability
status_vocabulary_ref != null

valid(c) only if
  stable(c.id)
  and bounded(c.outcome, c.scope, c.exclusions)
  and contracts_resolve(c.input_contract_refs, c.output_contract_refs)
  and context_policies_resolve(c.context_policy_refs)
  and c.authority_effect = none

material_change(product_ref, outcome, scope, owner_routes) =>
  successor_product_capability_required

adopted(c) =/=> realized(c)
realized(c) =/=> conformant(c)
conformant(c) =/=> valuable(c)
observed(c) =/=> adopted(c)
permission_for(c) =/=> product_capability(c)
```

`lifecycle_posture` applies the `CAV2-D23` axis split. `status` is meaningful
only with its owning `status_vocabulary_ref`; this definition does not impose
one lifecycle enum on every capability. Evidence, owner commitment,
provenance, and residue remain separate posture fields. Realization,
conformance, and operational availability are separate axes owned by their
respective artifacts and evidence. None may be inferred from another or
collapsed into one `status` field.

### Schema

Schema handle: `CAV2-D67-SCHEMA` — tracked in
[DEFINITION-SCHEMAS.md](DEFINITION-SCHEMAS.md). Status: tracked (documentary).
The first closed machine-checkable candidate contract and business-system
bridge are owned by
[../../capability/schemas/capability.schema.json](../../capability/schemas/capability.schema.json).
The package references this definition and public `DEF-ARC-CAPABILITY`; it does
not replace either definition authority.

### Operational Interpretation

Define a Product Capability after the Product Thesis identifies an outcome the
Product must repeatedly enable. Name its consumers, scope, inputs, outputs,
context policies, owners, and exclusions before selecting a realization.
Later, bridge it to one or more Agent Capabilities or system realizations and
test that bridge with separate conformance and runtime evidence.

Keep capability instances with the module that owns their local meaning and
lifecycle. A central Capability Ontology may index or project those instances,
but it must not copy their authority or turn one registry into their owner.

### Plain-Language Intuition

A Product Capability says what useful thing the product must make possible. It
does not yet say which tool or implementation will do it.

### Domain-Context Voice

Inside CyberAlchemy v2, Define Shared Meaning, Resolve Bounded Language
Context, Resolve Registry Context, Governed Work Loop, and Governance
Enforcement are Product Capability candidates or projections owned by their
respective product and module surfaces. Public Arcanum Agent Capabilities such
as Invoke Define may realize part of a Product Capability, but the public
agent contract and the private product meaning remain separate authorities.

### Boundary

A Product Capability is not the Product, Product Thesis, Project (`CAV2-D60`),
Goal (`CAV2-D59`), Context (`CAV2-D66`), Agent Capability
(`DEF-ARC-CAPABILITY`), Bounded Context, business rule, implementation,
component, command, interface, workflow, service, permission, role, authority
grant, runtime process, test, metric, evidence receipt, or release state.

An adopted Product Capability is not proof of implementation. An implemented
realization is not proof of conformance. A passing conformance check is not
proof of customer value, product-market fit, authority transfer, publication,
release, deployment, or permission to execute.

### Primary Consumers

- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- [DEFINITION-SCHEMAS.md](DEFINITION-SCHEMAS.md)
- [../../capability/README.md](../../capability/README.md)
- [../../ontology/product/README.md](../../ontology/product/README.md)
- [../../context/README.md](../../context/README.md)
- [../../define/README.md](../../define/README.md)
- [../../language/README.md](../../language/README.md)
- [../../registry-context/README.md](../../registry-context/README.md)

## CAV2-D68: Person

Status: active
Term: person
Aliases: human individual
Promoted: 2026-08-31 by explicit owner direction to make Person a first-class CyberAlchemy v2 concept; definition authority only

### Normative Definition

A Person is one human individual whose identity may be referenced by
CyberAlchemy products, Projects, Contexts, Teams, responsibilities, decisions,
and evidence without reducing that human to an account, role, permission,
session, or machine-readable record.

Person identity remains distinct from every participation relationship. A
Person may join or leave Teams, hold different roles, own different work, use
multiple accounts, or have no digital account while remaining the same Person.
Any stored record is a bounded reference or projection of the Person, not the
Person itself. CyberAlchemy must minimize personal data and must not infer
private attributes merely because a Person is referenced.

### Formal Interpretation

```text
Person(p) => HumanIndividual(p)

represents(account, p) =/=> account = p
holds(p, role) =/=> p = role
member_of(p, team) requires exists membership
owns(p, artifact_or_decision) =/=> authorized_for(p, action)
observed(record_about_p) =/=> record_about_p = p

change(team_memberships(p), roles(p), accounts(p))
  =/=> successor_person_identity_required
```

Here `p` is a human individual. `represents`, `holds`, `member_of`, and `owns`
are relationships whose records and lifecycle remain independently owned. The
non-implications prevent identity, participation, ownership, and authority from
collapsing into one another.

### Operational Interpretation

Use Person when CyberAlchemy must refer to the same human across a Product,
Project, Goal, Context, Team, decision, or handoff. Keep accounts, interface
identities, memberships, roles, responsibilities, owner routes, and authority
grants as separate records linked to the Person reference. Collect only the
minimum attributes required by the named use and preserve the applicable
privacy, correction, challenge, and retirement routes.

### Plain-Language Intuition

A Person is the human, not their login, job title, permission, or database row.

### Domain-Context Voice

Inside CyberAlchemy v2, a Person may be a Human Participant, Work Owner,
reviewer, researcher, or member of one or more Teams. Those are ways the Person
participates. They do not replace the Person's identity and do not silently
grant authority. The People and Teams product owns the first business model
that connects these meanings while keeping sensitive personal data outside the
initial ontology.

### Boundary

A Person is not a user account, authentication subject, credential, contact,
employee record, customer record, legal identity assertion, profile, role,
permission, authority envelope, owner route, agent, model, session, or Team.
This definition does not establish identity verification, employment status,
consent, access rights, organizational hierarchy, or a right to process
personal data. A reference to a Person creates no authority effect.

### Primary Consumers

- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- [../../people-and-teams/README.md](../../people-and-teams/README.md)
- [../../people-and-teams/definitions.json](../../people-and-teams/definitions.json)
- [../../people-and-teams/nodes.json](../../people-and-teams/nodes.json)

## CAV2-D69: Team

Status: active
Term: team
Aliases: purpose-bound team
Promoted: 2026-08-31 by explicit owner direction to make Team a first-class CyberAlchemy v2 concept; definition authority only

### Normative Definition

A Team is a durable, owner-qualified collective identity through which Persons
coordinate toward one declared purpose and scope. Its identity, lifecycle,
membership, roles, responsibilities, and authority relationships are explicit
and remain separate.

A Team is not merely the current set of its members. Membership changes do not
silently create a different Team while its identity, purpose, scope, and owner
boundary remain stable. An active Team has at least one current Person
membership. A proposed Team may exist before its first membership so its
purpose and owner can be reviewed without inventing members.

### Formal Interpretation

```text
Team(t) => CollectiveIdentity(t)
purpose(t) != empty
owner_route(t) != empty

active(t) => exists p, m:
  Person(p)
  and TeamMembership(m)
  and binds(m, p, t)
  and current(m)

members(t, time_1) != members(t, time_2) =/=> t_at_time_1 != t_at_time_2
holds(team_or_person, role) =/=> authorized_for(team_or_person, action)
owns_responsibility(team_or_person, r) =/=> authority_grant(r)
```

Here `t` is the Team identity, `p` is a Person, and `m` is an independently
lifecycle-managed membership relation. Team membership, role assignment,
responsibility ownership, and authority are related but non-equivalent facts.

### Operational Interpretation

Create a Team with a stable identity, purpose, scope, owner route, lifecycle
state, and challenge route. Add Persons through explicit Team Membership
records. Attach Team Roles and Responsibilities through separately owned
assignments so that membership alone never implies a role, responsibility, or
permission. Preserve membership history rather than rewriting the current
member list as if earlier participation never existed.

### Plain-Language Intuition

A Team is a named group working toward a purpose. The group stays recognizable
even when its members change.

### Domain-Context Voice

Inside CyberAlchemy v2, a Team can coordinate Projects, Goals, definitions,
research, reviews, or product responsibilities. A Team may be named as an owner
route only when the corresponding ownership record says so. Team membership
alone does not make every member an owner or decision authority. The People and
Teams product owns the first candidate business ontology for these relations.

### Boundary

A Team is not a Product, Project, Goal, organization, company, department,
mailing list, chat channel, access group, permission group, role, owner route,
authority envelope, workflow, or an unqualified collection of accounts. This
definition does not create employment, reporting lines, permissions,
organizational authority, or an implementation. A passing Team validator does
not prove that the Team exists outside the modeled context.

### Primary Consumers

- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- [../../people-and-teams/README.md](../../people-and-teams/README.md)
- [../../people-and-teams/definitions.json](../../people-and-teams/definitions.json)
- [../../people-and-teams/nodes.json](../../people-and-teams/nodes.json)

## Withdrawn Definition IDs

The following IDs were assigned to product-local Knowledge Exchange Protocol
terms and withdrawn from CyberAlchemy-v2 shared authority on 2026-08-31 before
ontology admission. They are reserved permanently and must not be reused.
Their successor definitions are owned by the product-local
[Knowledge Exchange Protocol definitions](../../product/knowledge-exchange-protocol/authority/definitions/DEFINITIONS.md).

| Withdrawn ID | Product-local successor |
| --- | --- |
| CAV2-D70 | KEP-D1 |
| CAV2-D71 | KEP-D2 |
| CAV2-D72 | KEP-D3 |
| CAV2-D73 | KEP-D4 |
| CAV2-D74 | KEP-D5 |
| CAV2-D75 | KEP-D6 |
| CAV2-D76 | KEP-D7 |
| CAV2-D77 | KEP-D8 |
| CAV2-D78 | KEP-D9 |
| CAV2-D79 | KEP-D10 |
| CAV2-D80 | KEP-D11 |
| CAV2-D81 | KEP-D12 |

## Open Questions

### OQ-1. Which imported definitions should be promoted first?

Context: the top-anchor queue is now promoted as `CAV2-D9` through `CAV2-D15`.
The import manifest still contains 149 definition-like candidates, including
`AgenticSystem`, `ContextSolution`, and `TranslationResidue` source material.
`OperationalOntology` source material has been demoted into D19/D23 language.
Recommendation: classify and deduplicate the remaining import candidates before
promoting terms into this file. Status: OPEN.
