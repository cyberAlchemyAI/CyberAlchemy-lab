---
node_type: define
is_session: false
status: candidate
created: 2026-07-01
authored_by: invoke (mode: define)
build_from: ./SEED.md (2026-06-11 — Lane Z anchor + promotion boundary)
informed_by: ../2026-07-01-spec-as-ontology/findings.md (two-plane boundary; Lane Z-vs-A left open for this tower)
target_artifact: spec-ontology-unification toy (Lane Z falsification)
promotion_boundary: LOCAL RESEARCH ONLY — no change to spec schema, code-pattern catalog, agent constitutions, or runtime until a later approved task-session (SEED.md:56-58)
---

# Define — Spec–Ontology Unification Toy (Lane Z falsification)

## Intent

Decide, with evidence, whether DomainSpec's typed spec-graph is a viable **substrate** for the
node→code-pattern / edge→composition model the SEED hypothesizes — i.e. whether "spec == ontology"
(Lane Z) earns a real decision, or whether Lane A (keep separate + generated mapping) is the honest
answer. The 2026-07-01 spec-as-ontology research explicitly **deferred** Lane Z-vs-A to this tower
(its toy was unrun); this define makes the toy runnable and its verdict decidable.

## The falsifiable claim (pre-registered — FREEZE before the run)

> For a real feature, DomainSpec's typed graph (25 TAXONOMY node-types + 29 RELATIONSHIPS edge-types)
> maps to code deterministically and near-1:1, with cross-cutting context bounded by the node's own
> subgraph — making it a sound substrate for bounded/ephemeral implementation agents.

**Toy corpus:** `impl/test-derivation-engine/__fixtures__/financial-settlement/` (small, engine-parseable;
spans Structural + Behavioral + Connective + Lifecycle — Entity, Value Object (Money), Enum
(PaymentMethod/PaymentErrorCode), Operation (ProcessPayment), Rule (MaxAmountRule), Event
(PaymentInitiated), State Machine (PaymentStatus)).

**SURVIVED iff ALL four hold on the corpus:**
1. **Taxonomy closure** — 100% of the feature's concepts classify to exactly one of the 25 types (0 unclassifiable).
2. **Node→pattern near-1:1** — ≥90% of nodes map to exactly one code pattern (TAXONOMY "Architecture Mapping Appendix"); the 0-pattern / >1-pattern exceptions are ≤10% and each documented.
3. **Edge→composition coverage** — ≥90% of the feature's edges map to a named composition rule; gaps ≤10%, each documented.
4. **Bounded cross-cutting context** — every pattern's required inputs are carried by the node + its direct edges (the "spec subgraph"), OR the leak is a NAMED, enumerable carrier (e.g. shared Value Objects via `contains`). 

**FALSIFIED** if any of 1–4 fails materially (taxonomy not closed / node↔pattern materially many-to-many
/ edges uncomposable / patterns routinely need context outside the subgraph → bounded agents can't work).
**INVALID** if the corpus is too trivial to exercise ≥3 TAXONOMY categories (pick a richer feature).

Passing the toy is **substrate viability**, NOT proof of agent cost savings (that needs a later,
separate agent-run experiment) and NOT authority to fuse spec and code — see promotion boundary.

**Coverage vs completeness (added 2026-07-01, from T1/T2 evidence).** A pass on one feature exercises
only the *subset* of the catalog that feature uses (financial-settlement: **12/25 node-types, 10/29
edge-types**). So distinguish THREE things, not one: **corpus closure** (M1 — do the corpus's concepts
fit a type), **catalog coverage** (M0 — do ALL 25 types + 29 edges each have a pattern/rule,
feature-independent), and **exercise coverage** (how much of the catalog a corpus actually tests). A
SURVIVED verdict MUST state its exercise coverage; single-feature is necessary, not sufficient.

## Glossary

- **spec-graph** — the feature's concepts as typed nodes + typed edges (TAXONOMY × RELATIONSHIPS).
- **node→code-pattern** — the map from a concept-type to an implementation pattern (the TAXONOMY
  functional-style appendix, e.g. Rule → pure predicate, Operation → use-case factory).
- **edge→composition rule** — how two patterns compose across an edge (e.g. `enforces`: the Rule
  predicate is called inside the Operation use-case).
- **near-1:1** — a node maps to exactly one pattern (the failure modes are 0 patterns or >1).
- **taxonomy closure** — every concept fits exactly one of the 25 types; nothing falls outside.
- **cross-cutting context leak** — a pattern needs data not carried by its node's own subgraph.
- **Lane Z / Lane A** — unify (spec==ontology) vs keep-separate-with-generated-mapping (SEED.md:43-53).

## Non-goals (from SEED.md:60-64)

- Committing to "spec == code/ontology" as canonical before the toy proves gains.
- Designing the ephemeral-agent runtime (this decides whether the typed graph is the right substrate,
  not how to ship agents).
- Any spec-schema, engine, or code mutation (promotion boundary).

## Open decisions (surfaced, not decided)

- **DEF-D1 — corpus choice.** financial-settlement (recommended: small, engine-known) vs
  agent-execution-orchestrator (richer, has rules.md). If financial-settlement fails INVALID
  (too trivial), escalate to AEO.
- **DEF-D2 — criterion thresholds.** The 90%/≤10% bars are proposed; the owner FREEZES them at the
  experiment step before the run (experiment discipline — no post-hoc adjustment).
- **DEF-D3 — catalog coverage (added 2026-07-01).** T1/T2 tested only 12/25 types + 10/29 edges. Add a
  feature-independent **catalog-coverage instrument (M0)**: does every one of the 25 types have exactly
  one appendix pattern, and every one of the 29 edges a composition rule? (Only **10/29** edge rules are
  authored today — SWU-T2b writes the other 19.) Optionally add a second, UI-heavy corpus so the 13
  untested types get exercised. The 19 authored edge rules feed the batch-1 **R3** (RELATIONSHIPS).
