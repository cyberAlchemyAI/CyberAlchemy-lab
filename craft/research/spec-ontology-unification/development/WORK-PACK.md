---
node_type: work-pack
is_session: false
status: candidate
boundary: LOCAL RESEARCH ONLY — no spec/code/schema mutation (SEED.md:56-58); engine black-box; v1 read-only
created: 2026-07-01
authored_by: invoke (mode: plan)
define: ../DEFINE.md
design: ../DESIGN.md
layering: ./implementation-layering.md
target_artifact: spec-ontology-unification toy (Lane Z falsification)
complexity: medium
---

# Spec–Ontology Unification Toy — Work-Pack

Runs the DESIGN's measurement harness over the financial-settlement corpus to decide DEFINE's frozen
four-part criterion (Lane Z substrate viability), then weighs Lane A. **Output is a verdict + evidence,
never a spec/code change** (promotion boundary). Corpus:
`impl/test-derivation-engine/__fixtures__/financial-settlement/` (v1 read-only; the fixture is the v2 copy).

## SWU manifest
| SWU | Layer | Title | Acceptance (reviewable) |
| --- | --- | --- | --- |
| **T1** ✅ | L0 | Extract the spec-graph | **DONE 2026-07-01** → [toy/graph.md](../toy/graph.md): 23 owned nodes (12/14 backend types), 25 edges (10 edge types), 4 categories → **NOT INVALID**. 5 anomalies noted for T3 (dual-typed node, latent Entity, 2 edge-law gaps, cross-feature context). Backend-scoped; UI-SPEC deferred. |
| **T2** ✅ | L1 | Author the two mapping tables | **DONE 2026-07-01** → [toy/mapping.md](../toy/mapping.md): 11/12 node-types map 1:1 (1 exception A1 dual-typed; 1 composite Event); 10/10 edge-types mapped (2 gaps A3a untyped-read / A3b missing op-returns-VO). 23 nodes + 25 edges all covered, no silent drops. |
| **T2b** ✅ | L1 | Catalog coverage — author ALL 29 edge rules + M0 | **DONE 2026-07-01** → [toy/catalog.md](../toy/catalog.md): M0-node **25/25**, M0-edge-entry **29/29** (19 new rules, 0 forced), but **M0-coverage INCOMPLETE** — catalog misses ≥2 real edge types → 3 R3 proposals (R3-P1/P2/P3). |
| **T3** ✅ | L2 | Run the toy + attack (the falsification) | **DONE 2026-07-01** → [toy/run.md](../toy/run.md): M1 100% · M2 ~96% · M3 ~96% · M4 bounded — **all bars PASS**; every exception traced to a v1-spec-doc gap, not the hypothesis; 3 attack lenses run; determinism ✓. |
| **T4** ✅ | L3 | Lane A compare + verdict | **DONE 2026-07-01** → [toy/verdict.md](../toy/verdict.md): **SURVIVED (narrow+conditional)** — substrate viable on the tested feature; failures = v1-spec-doc gaps → R3; Lane Z-vs-A still OPEN (proxy gap → agent-cost experiment); two-plane boundary = interim. |

---

## T1 — Extract the spec-graph  (L0)
- **Write scope:** `research/spec-ontology-unification/toy/graph.md` (new).
- **Steps:** read the corpus `domain.md` (+ any aspect files present); list every concept as a node with its TAXONOMY type; list every relation as an edge with its RELATIONSHIPS type + endpoints.
- **Impl detail:** node row = `{id, TAXONOMY-type}`; edge row = `{from, edge-type, to}`. A concept that fits no type is recorded as `unclassifiable` (a live M1 signal, not an error to hide).
- **Validation:** every domain.md concept appears exactly once; counts noted (feeds M1). **Edge case:** if the corpus exercises <3 TAXONOMY categories → stop, mark **INVALID**, escalate to agent-execution-orchestrator (DEF-D1).
- **Verification:** reviewer confirms the inventory matches domain.md (no concept missing/invented).

## T2 — Author the two mapping tables  (L1)
- **Write scope:** `research/spec-ontology-unification/toy/mapping.md` (new).
- **Steps:** for each node-type in T1, copy its pattern from `impl/spec/TAXONOMY.md` "Architecture Mapping Appendix"; for each edge-type in T1, write its composition rule (DESIGN §2 table is the seed).
- **Impl detail:** a node-type with 0 appendix patterns or >1 candidate pattern is recorded as an exception (feeds M2). An edge with no composition rule is a gap (feeds M3). Do NOT invent a pattern to force 1:1 — an honest gap is the finding.
- **Validation:** every T1 node/edge has a row (mapped or explicitly gap). No silent drops.
- **Verification:** reviewer confirms each mapping traces to the TAXONOMY appendix or a stated rule.

## T2b — Catalog coverage: author all 29 edge rules + M0  (L1)  ← added 2026-07-01 (refresh)
- **Write scope:** `research/spec-ontology-unification/toy/catalog.md` (new). Research only — **do NOT edit `impl/spec/RELATIONSHIPS.md`**; gaps are proposed to batch-1 R3.
- **Depends:** T1 (edge inventory) + T2 (the 10 authored rules).
- **Steps:** (1) enumerate all **25 TAXONOMY types** → confirm each has exactly one appendix pattern (0 or >1 = catalog gap); (2) enumerate all **29 RELATIONSHIPS edges** → author a composition rule for each — T2 did 10, so write the remaining **19**; (3) record **M0** = (types-with-one-pattern)/25 and (edges-with-a-rule)/29.
- **Impl detail:** an edge whose rule can't be written without inventing structure is a **catalog gap**, not a forced rule (same honesty rule as T2) → it becomes an R3 input. This is the feature-independent completeness check the single-corpus toy cannot give.
- **Validation:** all 25 types + all 29 edges have a row (rule or gap); the 19 previously-missing edge rules are present or explicitly gap-flagged; every gap names its R3 follow-up.
- **Verification:** M0 is recomputable from `catalog.md`.

## T3 — Run the toy + attack  (L2)  ← the falsification
- **Write scope:** `research/spec-ontology-unification/toy/run.md` (new).
- **PRE-STEP (gate):** FREEZE the criterion — copy DEFINE's four bars + thresholds into `run.md` header, dated, **before** computing anything. No post-hoc threshold edits (experiment discipline).
- **Steps:** apply the T2 mapping to the T1 graph → write the resulting pattern skeleton **on paper** (pattern names + how edges compose them; no real code). Compute M1–M4 with their exception lists. Re-run the computation once from the same inputs and confirm identical metrics (determinism). Then ATTACK (DESIGN §4): 1:1-break, cross-cutting-context, taxonomy-closure-under-stress — each lens gets a paragraph + any break added to the exception lists.
- **Impl detail — inputs/outputs/edge cases/failure modes:**
  - inputs: `graph.md`, `mapping.md`, frozen criterion.
  - outputs: **M0 (catalog coverage from T2b)** + M1–M4 numbers + per-metric exception list + **exercise-coverage** (types/edges the corpus tested) + attack findings.
  - edge cases: shared Value Object (Money) reached only via `contains` → classify as named-carrier (M4-b, not unbounded); cross-feature edge → M4-c candidate (unbounded) unless a carrier is named.
  - failure mode: if determinism re-run differs, the mapping is under-specified → record as an M2/M3 finding, do not paper over.
- **Validation:** the frozen criterion is present and dated before metrics; **M0 +** all 4 metrics + **exercise-coverage** + all 3 attack lenses present.
- **Verification:** an independent reader can recompute M1–M4 from `graph.md`+`mapping.md` and get the same numbers.
- **Execution route:** run T3 as an **`experiment` dispatch** (pre-registered criterion freeze → run → SURVIVED/FALSIFIED/INVALID) — the experiment skill owns the criterion-freeze + verdict vocabulary; this SWU supplies its design.

## T4 — Lane A compare + verdict  (L3)
- **Write scope:** `research/spec-ontology-unification/toy/verdict.md` (new).
- **Steps:** sketch Lane A for the same feature (generated bidirectional node→pattern map + drift check — the v1 direction); compare whether Lane A gives bounded-agent context without fusion. Render the verdict against the frozen bars: SURVIVED / FALSIFIED / INVALID. Write the promotion recommendation.
- **Impl detail:** the recommendation MUST respect the promotion boundary — it recommends the *next* approved task-session (or "do not pursue Lane Z"), never a spec-schema change here.
- **Validation:** verdict cites M1–M4 vs the frozen thresholds; Lane A explicitly weighed; recommendation names an owner + honors the boundary.
- **Verification:** the verdict is entailed by the metrics (a reader agrees SURVIVED/FALSIFIED follows from the numbers).

---

## Dispatch technique trace
`sequence` (T1→T4 strict) · `owner_boundary_check` (v1 read-only; engine black-box; promotion boundary — output is verdict-only) · `validation_loop` (each SWU acceptance = a reviewable artifact; T3 adds a determinism re-run) · `concrete_path_evidence` (corpus + TAXONOMY appendix + toy/ files named) · `scu_swu_reduction` (5 SWUs: T1/T2/T2b/T3/T4, one artifact each) · `recomposition_proof` (→ closes the SEED Lane Z-vs-A decision) · `residue_ledger` (below). **No full dispatch JSON** for the plan itself (single-owner). **T3 execution IS a dispatch** — route it through `experiment` (criterion pre-registration), registered via `register-dispatch`.

## Distill validation — flag
- **Smallest coherent units:** ✅ one artifact per SWU (graph / mapping / catalog / run / verdict).
- **Recomposition proof:** ✅ the four artifacts are exactly the evidence the SEED tower needs to decide Lane Z vs A.
- **Gaps named (repair path):** (1) **proxy gap** — the toy measures *substrate viability* (M1–M4), NOT actual agent cost/drift savings; a positive verdict authorizes only a *follow-up agent-run experiment*, not the SEED's full claim → owner: a later experiment tower. (2) **single-corpus** — one feature can falsify but not fully confirm; SURVIVED on financial-settlement → repeat on a richer feature before any promotion.
- **Verdict:** flag (routable; both gaps carried below).

## Residue
- Single corpus (financial-settlement); a SURVIVED verdict is necessary, not sufficient — needs a second feature.
- Proxy: substrate metrics stand in for "cheaper agents"; the agent-cost claim stays unproven until a runtime experiment.
- The node→pattern appendix is v1-authored; its own completeness is under test (M2/M3), so a FALSIFIED result may indict the appendix rather than the hypothesis — the verdict must distinguish these.
- **Catalog vs corpus (added 2026-07-01, refresh):** M0/T2b now check catalog completeness (all 25 types × 29 edges) feature-independently — but only a second, UI-heavy corpus would *exercise* the 13 untested types in practice (optional T5, not scheduled).

## Next route
`experiment` dispatch for **T3** (freeze criterion → run → verdict), with T1/T2 as its inputs and T4 as
its synthesis; or `task-session` per SWU if run solo. Result feeds back to `SEED.md` (close its Lane
assignment) and, only via a later approved task-session, to any spec decision.
