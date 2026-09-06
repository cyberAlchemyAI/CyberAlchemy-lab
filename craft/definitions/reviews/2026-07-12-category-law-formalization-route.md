---
artifact_role: pre-canonical-category-law-route
status: research-routed
current_claim: typed-composable-graph-fragment
next_route: research-tower
owner: definitions-governance
source_task: SWU-R3C-008
created: 2026-07-12
---

# Category-Law Formalization Route

## Current boundary

DomainSpec v2 currently governs a **typed composable graph fragment**, not a
formal category. Active [DS-D8 signatures](../relationships/relationships.yml)
provide finite typed edges and endpoint checks. The earlier
[category-boundary findings](../../research/2026-07-02-first-class-category-boundary/findings.md#plain-language-category-theory-answer)
explicitly reserve “category” for a future package that formalizes objects,
morphisms, identities, composition, closure, and associativity.

This packet routes that future work. It defines no canonical law and does not
amend R3A completion.

## Candidate-law matrix

| Candidate law | Candidate statement | Positive example | Non-example / falsifier | Current validation status | Needed proof or experiment | Owner route |
|---|---|---|---|---|---|---|
| Object closure | Every graph object belongs to the admitted DS-D1 type set for the selected profile. | Entity, Operation, and Event nodes resolve to current schemas in a valid feature pack. | A node uses an unknown or formation-deferred type as if active. | Partly enforceable now by content/schema validation for the active profile. | Define profile-relative object universe and prove/fixture closure across at least two real packs. | definitions-governance after research-tower fixes the formal statement. |
| Morphism typing | Every authored edge is an active DS-D8 signature whose source/target types satisfy its endpoint union and scope. | `Operation --produces--> Event`; `Binding --mutates--> Operation`. | `State Machine --enforces--> Operation`; generated/deprecated/deferred label authored as active. | Enforceable now by relationship/content validators and focused negative fixtures. | Consolidate the finite rule as a candidate law and prove status handling remains subordinate to root authority. | definitions-governance + validator owner. |
| Identity | Each admitted object has a neutral identity morphism for composition, without inventing an authored relationship label. | A formal path may compose with `id_Entity` while the stored DomainSpec graph remains unchanged. | Adding a canonical `identity` edge or self-loop merely to satisfy category terminology. | Not represented or validator-enforceable today. | Choose notation/semantics for formal identities and prove they are meta-level operators, generated views, or explicit authored data. | research-tower first; decision-gate only if storage authority is contested. |
| Typed composition | If `f: A→B` and `g: B→C` are composable, `g∘f` has a declared operational meaning and preserves type/scope obligations. | `Entity --performs--> Operation --produces--> Event` yields an actor-to-success-event execution path. | Two individually valid edges are called composed although the intermediate type, feature scope, or operational meaning does not align. | Only local endpoint compatibility is enforced; composed-path semantics are not. | Enumerate admissible two-edge path families, counterexamples, and observable obligation changes; test on real packs. | research-tower, then definitions-governance for finite accepted laws. |
| Closure under composition | Every admitted composed path stays inside the selected object/morphism universe or is explicitly rejected. | `Binding --mutates--> Operation --produces--> Event` remains within admitted types/signatures. | Composition requires a deferred relationship or produces an untyped endpoint. | Not enforced as a general law. | Build a finite composition table/model and falsify closure against active, generated, deprecated, and deferred states. | research-tower with formal-model experiment handoff. |
| Associativity | For composable `f,g,h`, `(h∘g)∘f` and `h∘(g∘f)` yield the same typed path obligations and observable projection. | `Binding -> Operation -> Event -> State Machine` has grouping-invariant endpoint/scope obligations. | Different grouping changes required validation, ordering, failure semantics, or generated output. | Not represented or enforced. | Define the composition operator first, then test associativity on at least one three-edge real-pack path and one countermodel. | research-tower; formalism owner after notation bridge. |
| Projection preservation | Generated/human views preserve root relationship meaning and cannot create new authored authority. | `owned-by` is generated from `owns` while `owns` remains canonical. | A projection, card, or generated inverse is counted as an active authored signature. | Partly enforceable through current status guards and retired-reference/relationship tests. | Specify a projection functor/read-model contract and test authority/status preservation under generation. | definitions-governance after research-tower establishes the mapping. |
| Obligation preservation | Translating a valid authored graph into validator, code-tag, or generated views preserves the public obligation set. | A valid active edge remains accepted by relationship and content validation; an invalid endpoint remains rejected. | A projection passes while the root edge fails, or drops a required obligation. | Bounded checks exist; no general preservation theorem. | Compare root, feature-pack, code-tag, and generated projections on shared fixtures; state the public invariant without exposing private derivation rules. | research-tower plus research-evidence-harness; definitions-governance owns any promoted law. |

## Validation layers

| Layer | What can be claimed now | What cannot yet be claimed |
|---|---|---|
| Finite DS-D8 | Active endpoint signatures, scope/status checks, examples/non-examples, and selected projection rules are executable. | A general composition algebra or category theorem. |
| Real-pack evidence | Multiple nodes/edges and focused invalid endpoints exercise parts of the graph fragment. | Closure or associativity over all admissible paths. |
| Formal candidate | Identity, composition, closure, associativity, projection preservation, and obligation preservation can be researched as explicit candidates. | Canonical status before notation, counterexamples, and owner review. |

## Selected next route

**Next: `research-tower`.** The question is source-first and formal: what is the
smallest category-like law package that matches DomainSpec’s finite typed graph
without importing ornamental terminology or overstating current validators?

The tower should deliver:

1. source corpus and related-work map for typed categories/graphs and
   specification composition;
2. notation bridge from DS-D1/DS-D8 into objects, morphisms, identities, and
   composition;
3. candidate law set with countermodels and operational interpretations;
4. finite path/fixture plan tied to real DomainSpec packs;
5. residue separating definitions-governance candidates from formal-model or
   validator work.

After the tower:

- route law definitions to definitions-governance only when their three voices,
  counterexamples, and owner boundary are ready;
- route executable models/fixtures to a formalism or research-evidence harness;
- invoke decision-gate only if competing storage/authority models remain.

No law may become canonical or part of R3A completion through this route packet.
