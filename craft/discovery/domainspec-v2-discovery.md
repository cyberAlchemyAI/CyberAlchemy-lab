<!--
  DISCOVERY (system-explanatory) for the `domainspec-v2` project.
  INTERNAL / private — never publish to arcanum/. This is a discovery in the
  problem-space / core-concepts / flows / open-questions sense (per the
  discovery-writing convention), adapted to EXPLAIN an existing system rather than
  scope a single change. It is the load-bearing upstream doc for later views
  (ontology-view / system-view / engineer-view) — if a view needs a fact this doc
  does not carry, that is a gap HERE, not license for the view to invent.
  Claim discipline: every "exists" claim is grounded in a file; every ambition is
  labelled as ambition (designed / L0 / not-yet-executed). No claim exceeds its proof.
-->

# DomainSpec v2 — Discovery

Status: draft (v0.2.1) — system-explanatory discovery; repo-fidelity review
(review-2026-07-06) + adversarial meta-type/carving soundness review
(review-2026-07-07) applied
Owner: DomainSpec v2 owner
Last updated: 2026-07-07

## Objective

Capture what DomainSpec v2 **is**, the problem it attacks, its core concepts, and
its end-to-end flow — separating cleanly what **exists and runs today** from what
is **designed but not yet executed**. This document is an orientation baseline for
anyone (human or agent) who needs to reason about v2 without re-deriving it from
the source tree.

## 1. Business Context

### Why now

DomainSpec v2 is, as of 2026-06-29, becoming the **implementation home** of the
DomainSpec discipline: v1 (`implementation/domainspec/`) is frozen as a read-only
evidence source, and its capabilities are being imported and re-authored into
`projects/domainspec-v2/impl/` (see [README.md](../README.md),
[IMPORT-MANIFEST.md](../IMPORT-MANIFEST.md)). v2 exists to hold one mandate cleanly:
**govern and enforce the DomainSpec language (Ontology A) on evidence** — type
intent into spec concepts, derive their obligations, validate them, rule on their
architectural layer, and measure drift toward convergence.

The umbrella goal behind it: *build a system that builds other systems.* DomainSpec
is the **what** (typed intent), Arcanum the **how** (the spells agents run), Saturn
the **loop** that keeps intent and reality coupled with evidence.

### What's broken (the problems v2 attacks)

Each is a concrete failure the design targets, grounded in the source:

- **Implementation agents are expensive and drift-prone.** An LLM asked to
  implement a feature must hold the whole system in context and makes global
  choices that diverge from intent over time. (Motivating the
  `spec-ontology-unification` tower — [README.md](../README.md) active-towers table.)
- **The spec→code mapping is implicit.** Nothing mechanically checks whether code
  still does what the spec said. "Spec and code are really two forms of the same
  domain taxonomy" but are not treated as such. (Same tower.)
- **Drift is invisible and accumulates.** Divergence between intended and observed
  behavior has no measurable home across its surfaces
  ([impl/spec/DRIFT-CONVERGENCE.md](../impl/spec/DRIFT-CONVERGENCE.md)).
- **Authority leakage on mint.** A domain repo cast from the cav2 template could
  silently treat cav2 as its method authority, collapsing its independence. This one
  is *guarded, not open*: the **Obs-B** invariant already holds at emit time (it needs
  no later decision to become true) and is the design's standing guard against
  mint-time authority leakage ([authority/AUTHORITY-MODEL.md](../authority/AUTHORITY-MODEL.md)).

### What stays the same (scope boundary of THIS doc)

- This discovery does **not** re-derive the authority model, the drift/convergence
  semantics, or the recursive-governance math — those are owned by
  [authority/AUTHORITY-MODEL.md](../authority/AUTHORITY-MODEL.md) and cited here, not
  restated.
- It does **not** cover the research-tower program mechanics (Two-Lane Discipline,
  individual tower seeds) beyond naming the towers that bear on the core flow.
- It does **not** touch the public `arcanum/` surface, submodule discipline, or v1's
  frozen internals except as provenance.
- The engine's private moat (`impl/test-derivation-engine/src/rules/`) is described
  at the level of *what it does*, never disclosing the withheld algorithm.

## 2. Core Concepts

Five concepts carry the whole system. Each is named, defined in one line, and
tied to where it lives.

- **Meta-type (the typed node).** One of the 13 active backend concept types — Entity, Operation,
  Rule, Calculation, State Machine, … — that classify a *domain concept* (a noun or
  verb of the business), **not** a language type. The node vocabulary is defined by
  `domainspec-v2-D6` / DS-D1 ([definitions/DEFINITIONS.md](../definitions/DEFINITIONS.md),
  [meta-types/meta-types.md](../definitions/meta-types/meta-types.md)). The set is
  closed for active backend concepts; every such concept must be exactly one.
  **Caveat on machine backing:** the staged vocabulary is 13 active backend types
  plus 11 formation-deferred UI labels ([impl/spec/TAXONOMY.md](../impl/spec/TAXONOMY.md)),
  and only the **13 backend** types carry a decidable *meta-type criterion* today —
  the registry [definitions/meta-types/meta-types.yml](../definitions/meta-types/meta-types.yml)
  enumerates 13 members with 13 criterion schemas under
  `impl/spec/meta-types/{structural,behavioral,connective,lifecycle}/`.
  The 11 UI types have **no meta-type criterion schema** (they are not machine-decidable
  as *node* classifications) — but they are **not** prose-only: relationships.yml
  registers them as active typed *edge endpoints* (Page, Component, Hook, Form, …,
  `feature_scope: ui`/`ui-backend` — State Indicator and Binding appear only under
  `ui-backend`). So the current staged view is 13 active backend types plus 11
  deferred UI labels; the UI labels are machine-present as edge endpoints without
  gaining DS-D1 formation authority.
  *Why this design:* a closed, decidable alphabet is what lets the core stay dumb
  (a table-walk, no solver) while remaining auditable.

- **Formal cell.** A small machine-evaluable expression an author writes in a table
  cell (`retryCount <= maxRetries`, `limit >= NL100 ? 0.5 : 0.4`, `count(...) <= 1`).
  It is the single bridge from prose to a derived test *with a known expected value*
  — the value is parsed out of the string, never obtained by running code.
  Classifier: [impl/test-derivation-engine/src/rules/index.ts](../impl/test-derivation-engine/src/rules/index.ts);
  parser: [.../src/formal/ast.ts](../impl/test-derivation-engine/src/formal/ast.ts).
  *Why this design:* it is the mechanical reason for the rule "expected values come
  from the spec, never from running the implementation."

- **Typed graph + the engine IR.** The spec, parsed. Two granularities: the
  *authored concept graph* (nodes = domain concepts, edges = one of 31 legal
  relationship signatures) and the engine's *Intermediate Representation*
  (`ConceptGraph`), which flattens each concept into finer addressable nodes —
  Transition, Invariant, Response, … — so tests can be derived per row and traced
  back to a `source_anchor`. Types: [.../src/ir/types.ts](../impl/test-derivation-engine/src/ir/types.ts);
  edge law: [definitions/relationships/relationships.yml](../definitions/relationships/relationships.yml).
  **Why exactly 31:** the signature set is not arbitrary — the *admissibility criterion*
  is `domainspec-v2-D3` (Edge-Law Admissibility, active): an edge type earns its own slot
  **iff it composes into different code** (a non-redundant distinction over
  {concept-type, relation-kind, composition-shape, feature-boundary}); widening *who* an
  edge connects is clean, overloading *what it points at* is rejected. The signature
  authority is DS-D8 and the verb set DS-D2
  ([definitions/DEFINITIONS.md](../definitions/DEFINITIONS.md)). This is what admits or
  refuses a 32nd signature — it is the reason `enforces`/`enforces-cross` collapsed to one
  edge + a flag while `enforces`≠`applies` stayed two.
  *Why this design:* human-friendly source → uniform, addressable IR is the classic
  compiler split; you derive and trace from rows, not from whole concepts.

- **The three-actor division of labor.** Fuzzy semantic work (modeling,
  classifying, drafting, coding) is pushed to **LLM agents** at the edges; crisp
  decidable work (check shape, derive obligations, check drift) is done by the
  **deterministic engine**; **authority** (ratify a classification, decide
  promotion, own the contract) is held by the **human owner**. The engine never
  guesses; the human never types characters by hand as the point; the agent never
  holds authority.
  *Why this design:* isolating determinism means the trustworthy core can be
  audited while the untrustworthy LLM is fenced by shape gates.

- **Governance triad (what / how / when).** Layering = the LAW (admissible typed
  structure), validation = the CHECK (does a typed spec conform), drift = the TREND
  (does conformance hold over time), with Saturn as the return edge closing the loop.
  Owned by [authority/AUTHORITY-MODEL.md](../authority/AUTHORITY-MODEL.md); cited, not
  redefined here.

## 3. The Authoring & Derivation Flow (what runs today)

The path from intent to a checkable test, with the actor for each step:

1. **Author the spec** — an *agent* (front door: the Arcanum `invoke define` spell)
   or a person writes a feature `SPEC.md`: a Concept Registry (`concept | type`), a
   field table per concept, a Formal cell per rule/invariant/calculation, and an
   edge list. A terse `concise` syntax can desugar into the canonical markdown
   ([.../src/concise/desugar.ts](../impl/test-derivation-engine/src/concise/desugar.ts)).
2. **Parse → IR** — the engine's Stage A parser reads the markdown headings + tables
   and builds the typed `ConceptGraph`; non-canonical tables raise a violation,
   never a guess ([.../src/grammar/index.ts](../impl/test-derivation-engine/src/grammar/index.ts)).
3. **Validate shape** — each concept's field table is checked against its meta-type
   criterion (a decidable table-walk; e.g. an Entity must have ≥1 identity field);
   each edge must match a legal signature — an edge outside the signature set is
   *unconstructible* (raised as an `unconstructible-edge` violation), not a well-formed
   edge flagged after the fact (DS-D8; D16, [DEFINITIONS.md](../definitions/DEFINITIONS.md))
   ([impl/tools/validate-content.ts](../impl/tools/validate-content.ts),
   [impl/tools/validate-relationships.ts](../impl/tools/validate-relationships.ts)).
4. **Derive obligations** — the pure, total `derive(graph)` function emits the exact
   set of test obligations: one per transition row, the full invalid-transition
   cross-product, one Formal cell → an exact count by class (RANGE→4, COUNT_CAP→2,
   …), prose Formal → a surfaced `needs_formal` (never a guessed test)
   ([.../src/rules/index.ts](../impl/test-derivation-engine/src/rules/index.ts)).
5. **Emit** — obligations render to a deterministic TEST-SPEC
   ([.../src/emit/](../impl/test-derivation-engine/src/emit/)).
6. **(Optional) tag code** — a `domainspec:` YAML block in a `/** … */` comment over
   an exported symbol declares which concept + type that code implements; an
   extractor collects the tags and a drift tool compares them to the spec graph
   ([impl/governance/tags/tools/](../impl/governance/tags/tools/)). *State: the
   extractor + drift tooling exist, but no v2 source is actually tagged yet — this
   step is wired, not exercised.*

Determinism is by construction: no LLM, no network, no clock — same spec in →
byte-identical obligations out (no-LLM/no-network:
[.../src/index.ts](../impl/test-derivation-engine/src/index.ts); no-clock:
[.../src/rules/index.ts:37](../impl/test-derivation-engine/src/rules/index.ts#L37)).

## 4. The Target Loop (designed, not yet executed)

The larger ambition, owned by the `spec-ontology-unification` research tower, which
[README.md](../README.md) lists as a **"hypothesis under test"** (the tower's *dispatch
route* — the plan to investigate — is the thing marked "designed and validated, not
yet executed"; the loop itself has not been proven):

- Treat spec and code as **one typed graph** (this is *Lane Z* — fuse spec == ontology;
  see OQ-5). Each meta-type schema carries a `code_pattern` (e.g. Entity → "a persisted
  row with a primary key"); each edge type carries a composition rule (e.g. `enforces` →
  "Rule gates the Operation").
- Feed **one node + its edges** to an *ephemeral, cheap* implementation agent that
  only needs `type → code_pattern` and `edge → composition` — so it fills a mold
  instead of holding the system (this "spec generates code, kept separate" reading is
  *Lane A*). Whether the two planes fuse (Lane Z) or stay separate with a generated
  mapping (Lane A) is the open bet OQ-5 — not settled here.
- The same typed graph that the agent implements from is the one the engine derives
  tests from, so code ↔ test ↔ intent share one addressing scheme, and Saturn can
  measure drift → correct → converge.

Today the `code_pattern` / composition entries are **prose descriptions**, not
machine-actionable templates, and nothing consumes them to emit code. The hooks
exist; the automation on top does not.

## 5. What Exists vs. What Is Still a Bet

| Piece | State | Evidence |
| --- | --- | --- |
| Deterministic engine (parse → derive → emit; shape + edge validators) | **Exists and runs** | `impl/test-derivation-engine/`, `impl/tools/` |
| Meta-type registry + machine criteria | **Exists**, all members `status: candidate` | [meta-types.yml](../definitions/meta-types/meta-types.yml) |
| One real feature pack as witness | **Exists** (non-vacuous validators) | [impl/spec/features/financial-settlement/SPEC.md](../impl/spec/features/financial-settlement/SPEC.md) |
| Authority model + promotion gates + Obs-B | **Authored** (kinds ratified 2026-06-29; L2 seal pending) | [AUTHORITY-MODEL.md](../authority/AUTHORITY-MODEL.md) |
| Spec authoring by agent (`invoke define`) | **Exists, L0** (baseline, not hardened) | invoke spell, mode `define` |
| Drift measurement beyond build-time | **Doc map, not engine** (`Stream<CheckResult>` + guardedness absent — residue R-trend-type) | [DRIFT-CONVERGENCE.md](../impl/spec/DRIFT-CONVERGENCE.md), AUTHORITY-MODEL §Governance Chain |
| Saturn (the convergence loop) | **Spec/private, not code that runs here** | root CLAUDE.md pillar note |
| Typed spec → ephemeral agents generate code | **Hypothesis under test, not executed** | [README.md](../README.md) towers table |

The honest asymmetry: the rigor of the **authority** (gates, Obs-B, non-collapse
rules) is well ahead of the **evidence that the end-to-end loop works**. The
central bet — that a real domain fits the staged vocabulary + fixed edges *and* that this makes
implementation cheaper and less drift-prone — has not been run end to end.
The adversarial review-2026-07-07 supplies the first concrete counter-signal to the
first half of that bet: the alphabet carried one structurally undistinguished kind
(Saga — collapsed into scoped Workflow by the 2026-07-11 owner decision, resolving OQ-7), one
unconstructible genre (time, OQ-7), and the "any domain" claim (TAXONOMY.md) is
over-stated — the 24 staged labels are visibly of the DDD/web genre. The non-collapse rigor that
is well ahead on **edges** has a matching **node** gap (OQ-6), so the "authority is
ahead of evidence" asymmetry is itself uneven across the two planes.

## 6. Open Questions

Each carries a recommendation, not just a question.

- **OQ-1 — Semantic mistyping is invisible.** The engine checks *shape*, not
  meaning: an Operation mislabelled with `state_change: no` validates as a Query
  and silently derives the wrong obligations. (This is structural, not a bug: by
  convention D15, the discriminator is read from a declared attribute value (e.g.
  `state_change`), never parsed from the Formal cell — so a mistype propagates unchecked.) *Recommendation:* treat the
  human/agent classification as the load-bearing risk; invest the owner-gate and any
  future cross-check budget there before hardening downstream tooling.
  *Sharpened (review-2026-07-07, [findings.md](../development/meta-type-formalization/research/2026-07-07-method-carving-soundness-review/findings.md)):*
  of the 13 active backend distinguishers, **10 are checked by string-compare over a declared
  attribute** (`attribute-equals`/`attribute-present` — validation at *author-attestation*
  strength, not structural); only Entity/Value Object/Enum read real structure. The pos/neg
  discrimination test is tautological for those 11 (the negative fixture is the positive with the
  tag flipped), so passing proves "the validator reads the declaration," not "a mistyped concept
  is caught" — confirmed empirically on disk. This sits **inside** the conceded moat (it is *not*
  a defect — the earlier "structurally broken" framing was refuted at verification), but the
  method should **declare the attestation-strength limitation in prose** rather than leave it
  implicit. The `formal_return_type` trio (Rule/Policy/Calculation) is the limit case: return-sort
  is semantic and D15 forbids parsing the Formal cell, so there a structural criterion is
  permanently non-constructible — a **declared exception** the method must own, not a failure.
- **OQ-2 — `code_pattern` is prose.** The target loop needs `type → code_pattern`
  to become machine-actionable. *Recommendation:* prove it on ONE meta-type end to
  end (spec node → generated code → derived tests pass) before generalizing — a
  witness, not a framework.
- **OQ-3 — Two edge vocabularies.** The engine IR defines 7 structural EdgeTypes;
  the authored/layering law has 31 signatures (governed by DS-D8 and the `domainspec-v2-D3`
  edge-law). *Note:* `derive()` itself reads nodes-by-type (`byType(graph, NodeType)`),
  never `graph.edges` — so the 7 EdgeTypes describe IR *structure*, they are not a
  derivation input. *Recommendation:* document the mapping explicitly so "edge" is never
  ambiguous across the two planes.
- **OQ-4 — Which bet to attack first.** Prove the loop on a real feature
  (spec→code→drift) vs. harden authoring (`invoke define` L0 → reliable).
  *Recommendation:* the loop witness (OQ-2) yields more information per unit effort;
  authoring hardening pays off only once there is a loop worth authoring into.
- **OQ-5 — Fuse or generate (the one open architectural bet).** `DEC-DSV2-LANE-ZA`
  (open, default: defer): **Lane Z** fuses spec and ontology into one typed graph;
  **Lane A** keeps them separate with a generated bidirectional mapping. The toy proved
  the *mapping* is viable — which both lanes need — so it does not decide between them;
  the decider is the unmeasured "cheaper agents" claim → an agent-cost experiment.
  *Recommendation:* hold the default-defer until the OQ-2 witness produces a cost signal;
  do not let §4's loop read as if the fuse-vs-generate choice were already made.
- **OQ-6 — Node formation has no non-collapse test (the structural root).** The edge law has a
  rigorous admissibility gate (`domainspec-v2-D3`), but **node/meta-type formation is exempt from
  the only non-collapse discipline the method operates**: D18's promotion boundary reads "governs
  relationship promotion, **not DS-D1 meta-type formation**," and D6/D7 carry only *coverage*
  challenges (fits-no-type / fits-two), never a *collapse* test asking whether two types reduce to
  one (confirmed, review-2026-07-07
  [findings.md](../development/meta-type-formalization/research/2026-07-07-method-carving-soundness-review/findings.md)).
  Consequence: a self-declared attribute can mint a type it never structurally earned — this one
  asymmetry produced both the orchestration over-cut (resolved OQ-7) and the 11 attestation-strength distinguishers
  (OQ-1). *Recommendation:* install a **node non-collapse gate** — every node type must exhibit
  EITHER a structural-table witness OR distinct edge-participation that reads structure; a
  self-declared tag alone is inadmissible. This is the single highest-leverage change: it forces
  the orchestration split to prove structure or merge, forces a new time node to ship subgraph structure, and turns
  the semantic trio into an explicit declared exception instead of a hidden one.
- **OQ-7 — Resolved over-cut; the opposite-sign genre gap remains.**
  The 2026-07-11 owner decision collapsed Saga into Workflow plus the declared `scope` tag. The earlier
  schemas had identical `edge_participation`, and `compensates` was not exclusive, so the split had no
  admitted structural witness. Symmetrically, the **time genre** remains missing: there is no Schedule/Timer
  and a `billing_date`/cron trigger is unconstructible (a clock has no Operation/Entity producer that
  Event requires). *Recommendation:* preserve the completed orchestration collapse and separately adjudicate
  Schedule with a structural witness; the remaining gap cannot reopen the retired split by implication. Fine-grained edge decisions
  the review surfaced (`constrains`, `compensates`, `contains`-source-widen, and the Projection
  node-vs-View-Model fork) are engineer-view / DEFINE open-decision material, routed there, not here.

## Connections

- Derives-from / stands-on: [authority/AUTHORITY-MODEL.md](../authority/AUTHORITY-MODEL.md),
  [authority/promotion-policy.md](../authority/promotion-policy.md),
  [impl/spec/DRIFT-CONVERGENCE.md](../impl/spec/DRIFT-CONVERGENCE.md),
  [impl/spec/TEST-PIPELINE.md](../impl/spec/TEST-PIPELINE.md),
  [README.md](../README.md).
- Downstream (derive-only, on demand once stabilized): `ontology-view` (typed
  nodes/edges), `system-view` (stakes), `engineer-view` (verdicts).

## Provenance

Authored from a 2026-07-06 working session that traced the system from the authority
model down into the engine source (`meta-types.yml`, `rules/index.ts`,
`formal/ast.ts`, `grammar/index.ts`, `ir/types.ts`, the code-tag tools, the invoke
spell, and the v2 README). No `domainspec-findings.md` fan-out preceded it; claims
are grounded in the cited files directly. The adversarial assessment the draft was
pending has now run for the meta-type/carving axis — review dispatch
`2026-07-07-metatype-method-carving-soundness` (a 3-attacker red-team with two
independent verifiers; see
[findings.md](../development/meta-type-formalization/research/2026-07-07-method-carving-soundness-review/findings.md)
and its companion research.md), which resolved into OQ-1 (sharpened), OQ-6, and OQ-7.
Broader adversarial assessment (authority model, drift semantics, the end-to-end loop)
remains pending before promotion past draft.
