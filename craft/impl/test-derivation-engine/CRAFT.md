---
node_type: craft-view
title: CRAFT — Deterministic Test-Derivation Engine
status: active
updatedAt: 2026-08-24
---

# CRAFT — Deterministic Test-Derivation Engine

> Human view of [`.craft/ledger.yml`](.craft/ledger.yml), the source of truth. This scoped ledger covers the original deterministic derivation engine; newer BTE/EVF work in the same package remains owned by the parent DomainSpec-v2 Craft contexts.

## Current frontier

The original deterministic engine core is complete through P1-P4: the falsifiable/injective gate, dialect bridging, corpus generalization and runnable-body emitter are recorded complete. E1a passes and E3 ran over 160 mutants with no harness errors; the main quality lever is a value-asserting makeup oracle. Remaining: run E2 with at least three non-author testers, resolve the accepted progression-prose and postcondition-ID gaps, and recompose the SMT/FOL decidability map without claiming a completed bridge. Later BTE and EVF additions in this package are tracked by the parent DomainSpec-v2 Craft contexts and are not closed by this legacy engine ledger. No Git action is selected by this refresh.

- Open decisions: none
- Active blockers: none
- Active gaps: `GAP-TDE-PROGRESSION-PROSE-001`, `GAP-TDE-POSTCONDITION-IDS-001`, `GAP-TDE-E2-NONAUTHOR-USABILITY-001`, `GAP-TDE-SMTFOL-RECOMPOSITION-001`

## Contexts

### `CTX-TDE-ROOT` — Deterministic Test-Derivation Engine

Stage/gate: `validate` / `flag`

Build a fully deterministic, no-LLM engine that compiles a feature's canonical Markdown docs into byte-stable test obligations (parse -> typed graph G -> pure delta -> content-addressed obligation_key -> emit), making DomainSpec paper claim C2 (determinism) true by construction and yielding a shippable product that replaces the LLM-backed domainspec-generate-tests.

Next: The original deterministic engine core is complete through P1-P4: the falsifiable/injective gate, dialect bridging, corpus generalization and runnable-body emitter are recorded complete. E1a passes and E3 ran over 160 mutants with no harness errors; the main quality lever is a value-asserting makeup oracle. Remaining: run E2 with at least three non-author testers, resolve the accepted progression-prose and postcondition-ID gaps, and recompose the SMT/FOL decidability map without claiming a completed bridge. Later BTE and EVF additions in this package are tracked by the parent DomainSpec-v2 Craft contexts and are not closed by this legacy engine ledger. No Git action is selected by this refresh.

### `CTX-TDE-SMTFOL` — SMT/FOL research tower (engine formal foundation)

Stage/gate: `review-audit` / `flag`

Preserve the historical research into how SMT solvers + first-order logic ground the engine's Formal-cell classes and `needs_formal` boundary. Its TDE recomposition informs δ classification only; operational solver integration belongs to EVF.

Next: Recompose only the decidability map into the engine as the formal justification for the `needs_formal` boundary (P1/P4). Preserve the opt-in SMT verify/witness proposal as source evidence for the parent DomainSpec-v2 EVF provider-integration gap; do not implement or close that operational frontier in this legacy engine ledger.

## Decisions

- `DEC-TDE-HOME-001` — `closed` → `tools/test-derivation-engine/`: Where should the TypeScript engine live?
- `DEC-TDE-LANG-001` — `closed` → `TypeScript`: Engine implementation language?
- `DEC-TDE-INPUT-SCOPE-001` — `closed` → `Extend to all 7 docs`: Should the engine parse 4 aspect docs or all 7 source docs?
- `DEC-TDE-SEMANTIC-RIGOR-001` — `closed` → `SPLIT — accept op-bucketing for postconditions; reject concept-bucketing for WF/QT/MT`: Should the round-trip gate verify per-row obligation identity, or is owning-concept-bucket bridging acceptable for PC/WF/QT/MT rows?
- `DEC-TDE-DOMAINSPEC-FEATURE-001` — `closed` → `operations+interfaces scope (honest fit; skip forced states/events) under implementation/domainspec/docs/features/test-derivation-engine/`: Should the engine be defined/designed as a DomainSpec feature (its own states/operations/interfaces/events), and at what scope/location?

## Gates, blockers, and enablers

- `ENA-TDE-L0-PASS-001` — `enabler` / `active`: The passing L0 gate over the full 7-doc input is the load-bearing evidence the engine works.
- `BLK-TDE-AUTH-CONVENTION-001` — `blocker` / `resolved`: refine 2026-06-21: the failing `column-typed` dialect is the corpus MAJORITY (5/7); the passing `rv-ct` dialect is the minority (2/7). Of auth's 30 misses ~16 are convention drift (fix via a doc-derived dialect descriptor, no feature-name branches) but ~12+ are GENUINE δ gaps — error-obligations and consumer-side events the engine derives nothing for. So closing this needs general bridging AND new δ rules, not just identity recovery. Delete the hardcoded MAKEUP_CALC_IDS overfit as part of this.
- `GATE-TDE-CORPUS-GENERALIZATION-001` — `gate` / `resolved`: One passing feature proves feasibility; the C2 claim needs corpus-level evidence (ties to experiments E1a/E2/E3).
- `BLK-TDE-COMMIT-DISCIPLINE-001` — `blocker` / `resolved`: Multiple turns of work are uncommitted; submodule discipline requires push-before-parent-bump, an operator-gated outward action.
- `BLK-TDE-GATE-HONESTY-001` — `blocker` / `resolved`: The current financial PASS partly depends on non-injective folds; a δ regression dropping workflow steps 2–5 would still PASS. Honesty before generalization — this lands first (P1) or every later PASS is suspect.

## Gaps

- `GAP-TDE-EMITTESTS-BODIES-001` — `resolved` / `low`: emit_tests renders one runnable `it.todo`/failing case per obligation_key but the test BODIES are stubs (expect.fail). Real assertion bodies are needed before the emitted suite can drive E3 mutation testing. RESOLVED 2026-06-21 (P4) for the deterministically-evaluable subset: hybrid emitter (Formal-AST → assertion-from-Formal + seeded property fallback) + bindings.json (declares WHICH pure fn, not the answer) emits 11 real bodies (10 assertions + 1 property) for financial-settlement, all PASS vs real domain code, byte-stable; the remaining 56 are honest `it.skip` + coverage_gap (exists/aggregate/makeup-math/ transitions/contracts/events — need a human oracle, never faked).
- `GAP-TDE-PROGRESSION-PROSE-001` — `active` / `low`: player-progression round-trip has 5 genuine misses: 5 per-assertion calc-scenario prose rows over 4 source calcs (makeup-policy-math class, R-C2-5) — prose outside the decidable fragment (needs_formal/oracle per the SMT-FOL tower). Honest untuned holdout.
- `GAP-TDE-POSTCONDITION-IDS-001` — `active` / `medium`: Committed TEST-SPEC PC/WF/QT/MT rows carry no surviving source id, so the round-trip bridges them at owning-concept-bucket level, not per-row. Gate verifies "covered this operation/workflow" not "covered each specific row". Per-row rigor needs the oracle to embed P-/WF-/QT-/MT-ids (upstream authoring fix). Bumped low->medium by refine 2026-06-21: WF/QT/MT bucketing is non-injective and the financial PASS depends on it (see BLK-TDE-GATE-HONESTY-001 / DEC-TDE-SEMANTIC-RIGOR-001).
- `GAP-TDE-E2-NONAUTHOR-USABILITY-001` — `active` / `medium`: E2 requires at least three non-author testers; local author-driven evidence cannot satisfy that usability and comprehension boundary.
- `GAP-TDE-SMTFOL-RECOMPOSITION-001` — `active` / `medium`: The research tower has a declared TDE recomposition target, but no receipt proves that its decidability map has been incorporated into the engine contract. Optional SMT verify/witness integration is excluded from this gap and tracked by the parent DomainSpec-v2 EVF context.

## Pending recomposition

- `CTX-TDE-SMTFOL → CTX-TDE-ROOT` remains pending only for the engine's decidability map. Optional SMT verify/witness integration is EVF-owned and does not gate this TDE recomposition; see `GAP-TDE-SMTFOL-RECOMPOSITION-001` and the parent `GAP-DSV2-EVF-SMT-PROVIDER`.

## Artifacts

- [`ART-TDE-PACKAGE`](.) — `active` · Original TypeScript engine package plus later parent-owned BTE/EVF additions; historical pre-P1 test count superseded.
- [`ART-TDE-SPEC`](../../../../development/deterministic-test-derivation-engine/SPEC.md) — `active` · Define-mode historical source spec at the umbrella repository root.
- [`ART-TDE-ARCH`](../../../../development/deterministic-test-derivation-engine/ARCHITECTURE.md) — `active` · Design-mode historical six-view architecture and decision log.
- [`ART-TDE-GLOSSARY`](../../../../development/deterministic-test-derivation-engine/GLOSSARY.md) — `active` · Historical 13-term glossary; determinism-vs-completeness distinction.
- [`ART-TDE-WORKPACK`](../../../../development/deterministic-test-derivation-engine/WORK-PACK.md) — `active` · Original engine work-pack; later ledger evidence records P1-P4, E1a and E3 beyond its L0 snapshot.
- [`ART-TDE-L0-REPORT`](../../../../development/deterministic-test-derivation-engine/L0-ROUNDTRIP-REPORT.md) — `pass` · Historical L0 round-trip evidence; the auth convention blocker was later resolved.
- [`ART-TDE-REFINE-RESULT`](../../../../implementation/domainspec/development/refinement-runs/2026-06-12-test-derivation-c2-cluster/RESULT.md) — `pass` · Refine result that produced the engine pivot + two-track plan. Committed (89ae887).
- [`ART-TDE-CRAFT-LEDGER`](.craft/ledger.yml) — `active` · Craft source of truth for the engine project.
- [`ART-TDE-CRAFT-VIEW`](CRAFT.md) — `active` · Human-readable view of the ledger; not source of truth.
- [`ART-TDE-DSFEATURE`](../../../../implementation/domainspec/docs/features/test-derivation-engine/) — `active` · Historical DomainSpec feature definition that enables the self-derivation fixpoint.
- [`ART-TDE-SMTFOL-TOWER`](../../../../research/smt-fol-test-derivation/) — `active` · SMT/FOL research provenance; TDE still owes decidability-map recomposition, while optional solver integration is tracked by EVF.

## Definitions

- `DEF-TDE-ENGINE-001` — **deterministic test-derivation engine**: A pure, no-LLM, no-network pipeline (parse -> G -> delta -> obligation_key -> emit) that compiles canonical feature docs into byte-stable test obligations, so determinism is true by construction rather than measured on a stochastic generator.
- `DEF-TDE-OBLIGATION-KEY-001` — **obligation_key**: sha1(source_anchor | rule_type | canonical_params) — a content-addressed, order-invariant, byte-stable identifier for a derived obligation. Gives cross-run determinism structurally and dissolves the original E1 "Jaccard over hand-numbered IDs" problem.
- `DEF-TDE-SEMANTIC-ROUNDTRIP-001` — **semantic round-trip identity**: A normalized identity (`normRuleType:tokens`) that BOTH the engine output and the committed TEST-SPEC map into, since their raw ID schemes differ. The L0 gate asks "did the engine cover every source obligation the human catalogued?" (engine-set superset of committed-set) at this level, not per-micro-case.
- `DEF-TDE-NEEDS-FORMAL-001` — **needs_formal**: The deterministic escape hatch: a Formal cell that is prose the sub-grammar cannot classify is flagged needs_formal (counted, surfaced by the linter), never guessed. Keeps the engine deterministic about what it cannot formalize.

## Export receipt

- Refresh date: `2026-08-24`
- Index pointer and path-map repair included
- No Git, product, admission, authority, publication, release, or deployment effect
