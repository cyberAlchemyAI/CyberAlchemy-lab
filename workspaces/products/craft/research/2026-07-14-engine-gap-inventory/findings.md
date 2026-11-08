# Goal

Turn the engine audit into an authority-safe inventory of witnessed implementation residue, existing owners, dependency order, and smallest executable slices for the DomainSpec v2 first-production-release path.

# TL;DR

**The semantic engine is the first major implementation capability, but the next safe execution is authority preparation: `FPR-01 → FPR-02 → FPR-03` must fix the baseline, supported profile, source disposition, and precedence contract before `FPR-04` creates the graph an implementer can traverse.** This is the shared conclusion of the executable audit and governance analysis ([Agent 1](./research.md#agent-1--shannon-claude), `development/first-production-release/ROADMAP.md:58-67,94-104`; [Agent 2](./research.md#agent-2--senge-peter), `.craft/ledger.yml:284-312`, `ROADMAP.md:54-104`).

The 21 `EGI-*` rows below are evidence identifiers in a non-authority read model, not new gap identities. Eight packages route them into existing owners. Only `EGI-005`, `EGI-010`, and `EGI-020` are newly witnessed residue, and even those belong inside existing work. Exact-owner aliases `EGI-003`, `004`, `009`, `018`, and `019` must merge into their named owner nodes rather than create competing lifecycle authority.

# Context

The repository already contains a roadmap, Craft continuation state, definitions authority, gap/frontier IDs, manifests, validators, an imported test-derivation engine, and historical receipts. The audit found real false-greens and missing products, but a flat “gap list” would duplicate existing ownership and confuse release severity with safe execution order. The right artifact is therefore an ownership and live-witness crosswalk: it preserves the evidence while refusing to supersede the Craft ledger, FPR roadmap or manifest, definitions authority, owner decisions, or work-packs ([Agent 2](./research.md#agent-2--senge-peter), `.craft/ledger.yml:1-14`, `authority/AUTHORITY-MODEL.md:40-64`; [Agent 3](./research.md#agent-3--turing-alan), “Existing owner if any”).

# Authority boundary

This findings file has no independent gap, lifecycle, gate, status, or continuation semantics. Package labels are routing conveniences; evidence IDs identify observations. Existing owners decide disposition, promotion, execution, and closure. In particular, machine evidence currently favors `13` backend types, `24` staged labels, and `30` relationships, but only `FPR-01` can ratify a release baseline ([Agent 2](./research.md#agent-2--senge-peter), `definitions/meta-types/meta-types.yml:9-23`, `impl/spec/TAXONOMY.md:1-25`, `definitions/relationships/relationships.yml:17-18`, `definitions/DEFINITIONS.md:358-359,1030-1065,1137-1139`).

# Authority-safe dependency chain

```text
FPR-00
  → FPR-01 authority baseline
      → FPR-02 supported profile and denominators
          → FPR-03 governed B → Spec precedence and mapping
              → FPR-04 Spec → Sg and bounded Sg → G → Sg_canonical
                  ├─→ FPR-05 admitted patterns/compositions
                  ├─→ FPR-06 bounded formal profile
                  ├─→ FPR-07 independent obligations and execution evidence
                  └─→ FPR-08 code → I_struct
                              ↓
                         FPR-09 directional conformance
```

Before `FPR-01`, safe work is limited to restoring failing guards, evidence census, deterministic stale-reference detection, red fixtures, and proposed source dispositions. It must not mint a competing vocabulary, graph schema, or obligation denominator ([Agent 2](./research.md#agent-2--senge-peter), `ROADMAP.md:77-104`, `.craft/ledger.yml:77-82`, `development/first-production-release/craft/expected-node-edge-manifest.yml:49-66`).

# Eight existing-owner packages

1. `PKG-1 — FPR-01 authority preflight`
2. `PKG-2 — FPR-02/FPR-04 fail-closed profile and input`
3. `PKG-3 — FPR-03 existing precedence gate`
4. `PKG-4 — FPR-04 compiler and retraction`
5. `PKG-5 — FPR-05 admitted implementation semantics`
6. `PKG-6 — FPR-07 independent obligations and executable coverage`
7. `PKG-7 — validation integration and existing FPR-08/FPR-09 loop closure`
8. `PKG-8 — package/read-model maintenance`

# Ownership and live-witness crosswalk

| Evidence | Package | Bounded live witness | Existing owner routing | Execution use / release severity |
|---|---|---|---|---|
| `EGI-001` | PKG-1 | Surfaces disagree on 13/14 backend types, 24/25 labels, 30/31 relationships, and maturity wording. `13/24/30` is favored, not ratified ([A2](./research.md#agent-2--senge-peter), `meta-types.yml:9-23`, `TAXONOMY.md:1-25`, `relationships.yml:17-18`, `DEFINITIONS.md:358-359,1030-1065,1137-1139`). | `FPR-01`; definitions, validation, layering. | Baseline census, dispositions, receipt, mutants. Blocks every downstream denominator and release. |
| `EGI-002` | PKG-1/4 | Authority prose, local validators, and imported CLI resolve feature sources from different homes. No authoritative `Sg` exists, so divergent compiled graphs are not demonstrated ([A2](./research.md#agent-2--senge-peter), `authority/AUTHORITY-MODEL.md:23-31`, `ontology/README.md:17-25`, `impl/tools/validate-content.ts:56-71`, `impl/test-derivation-engine/src/cli.ts:68-82`). | `DEC-DSV2-SPEC-HOMING`, reformulation, `FPR-01`; executable manifest in `FPR-04`. | Source dispositions. Blocks reproducible compiler input. |
| `EGI-003` | PKG-2 | Exact alias `GAP-SH-UI11-MIGRATE`: UI types are formation-deferred while signatures use UI endpoints. This is a profile/status contract, not logical contradiction; backend-only may defer it ([A2](./research.md#agent-2--senge-peter), `meta-types.yml:18-23`, `relationships.md:65-87`). | Existing gap, batch-1 R2/MT5, `FPR-01/02`. | Separate formation/signature/profile admission. Blocks full-language, not necessarily backend profile. |
| `EGI-004` | PKG-3 | Exact alias `FR-FPR-ONTOLOGY-DIRECTION`: contract→authoring is stated; business/ontology/spec precedence, supersession, provenance, and contradiction handling remain unresolved ([A2](./research.md#agent-2--senge-peter), `.craft/ledger.yml:894-904,606-619`, `research/2026-07-01-spec-as-ontology/findings.md:54-73`; [A3](./research.md#agent-3--turing-alan), `definitions/DEFINITIONS.md:183-216`). | Existing frontier; semantic owner, definitions governance. | Close FPR-03; keep ontology/learning generated-only. Blocks FPR-04. |
| `EGI-005` | PKG-1 | Manual drift audit says pass while retaining stale count 31 and explicitly leaves deterministic scanning unfinished ([A2](./research.md#agent-2--senge-peter), `definitions/DEFINITION-DRIFT-AUDIT.md:5-12,38-57`, `relationships.yml:17-18`). | New control residue inside definitions governance / `FPR-01`. | Deterministic count/reference/status scan and red fixtures. Blocks trustworthy baseline evidence. |
| `EGI-006` | PKG-1 | The explorer’s pre-output retired-orchestration audit found 210 matching files, 1,765 matches, and 2 violations while the historical Saga receipt was green. After `research.md` and this `findings.md` existed, the parent rerun found 212 files, 1,777 matches, and 4 violations; the two dispatch files are the additional unclassified violations and require classification/allowlist disposition. This is an expired/reopened proof, not proof the historical run was false ([A3](./research.md#agent-3--turing-alan), `development/saga-removal/runs/SWU-SGRM-008/TASK-SESSION-RESULT.md:14-17,55-63` plus pre-output and post-output audit receipts). | Reopen SGRM-006/007 verification; validation governance. | Classify or allowlist the two dispatch artifacts and restore the guard before baseline ratification. Current red validation blocks release evidence. |
| `EGI-007` | PKG-2 | Sample content passes with 0 concepts and 0 edges. Unknown-type rejection is a bounded absent-fixture finding, not a persisted negative result ([A3](./research.md#agent-3--turing-alan), `impl/spec/features/sample/SPEC.md:3-10`, `impl/tools/validate-content.ts:99-119`). | `FPR-02` negatives; `FPR-04` total projection. | Separate empty-content and unknown/absent-schema tests. Empty projection blocks release. |
| `EGI-008` | PKG-2 | Missing feature `derive` exits 0 with empty obligations; `lint` exits 0 with `CLEAN (0)`; optional missing aspects are tested behavior ([A1](./research.md#agent-1--shannon-claude), `grammar/index.ts:934-940`, `index.test.ts:28-38`, `cli.ts:179-206,403-427`). | `FPR-04` missing-source/empty-graph; `FPR-07` zero-obligation. | First engine negative control; release-blocking false-green. |
| `EGI-009` | PKG-4 | Exact alias `FPR-04`: declared graph/compiler/manifest/schema/verifier products are absent from inspected FPR surface; `deriveFeature()` exposes obligations/spec/tests, not authoritative `Sg` ([A1](./research.md#agent-1--shannon-claude), `expected-node-edge-manifest.yml:121-146`, `src/index.ts:22-33`). | Existing `FPR-04`; semantic, validation, engine. | First bounded compiler slice after predecessors. Release-blocking, not yet safe to execute. |
| `EGI-010` | PKG-4 | Audited parser declares seven edge labels but constructs `Consumer --consumes--> Event`; authority defines `Component --consumes--> Hook`, and local `enforces` also conflicts. Financial witness: 62 nodes, 2 edges ([A1](./research.md#agent-1--shannon-claude), `ir/types.ts:5-35`, `grammar/index.ts:486-545`, `relationships.yml:1-18,83-97,323-337`). | New technical residue inside `FPR-04` quotient/projection. | Explicit `Sg→G` mappings/internal renames. Blocks authoritative traversal once FPR-04 starts. |
| `EGI-011` | PKG-4 | Independent `Sg→G→Sg_canonical` comparator is absent; current obligation-catalogue round-trip is narrower and not proven broken ([A1](./research.md#agent-1--shannon-claude), `roundtrip/index.ts:789-865`, `index.test.ts:266-299`, `expected-node-edge-manifest.yml:129-145`). | `FPR-04` proof slice. | Retraction comparator and mutants. Blocks FPR-04 closure. |
| `EGI-012` | PKG-2 | Inspected current packs positively exercise 11/13 backend types and 9/30 active verbs; registry loading is not positive exercise ([A3](./research.md#agent-3--turing-alan), current feature-pack census and `development/r3-closeout-plan/task-sessions/2026-07-12-swu-r3c-001/TASK-SESSION-RESULT.md:14-17,50-66`). | Literal exercise sets in `FPR-02/04`; bounded R3C remains closed. | Select admitted/exercised subsets. Blocking only if broader completeness is claimed. |
| `EGI-013` | PKG-5 | Five backend pattern cards are evidence-ready; others are staged or superseded. They are unadmitted, not necessarily nonexistent ([A2](./research.md#agent-2--senge-peter), `architecture-pattern-enforcement/cards/backend/README.md:10-16,25-43`). | APE/definitions governance under `FPR-05`. | Admit first-witness pattern; otherwise `pattern-unavailable`. Selected unsupported node blocks implementation. |
| `EGI-014` | PKG-5 | Evidence reports nine derived code-call rules and 26 unsupported active call-semantic signatures; the sets are not claimed to partition or sum to 30 ([A2](./research.md#agent-2--senge-peter), `SWU-R3C-001/TASK-SESSION-RESULT.md:19-27,49-58`). | Existing APE breadth under `FPR-05`; do not reopen R3. | Supported/unsupported composition registry. Selected unsupported edge blocks implementation. |
| `EGI-015` | PKG-6 | Generator owns its denominator: `RuleSet` is only a version and ignored; obligation families are hard-coded. Independent `O_spec`, outcomes, and evidence requirements are absent ([A1](./research.md#agent-1--shannon-claude), `rules/index.ts:1-39,51-56,631-655`; [A2](./research.md#agent-2--senge-peter), `IMPORT-MANIFEST.md:22-32`, import-triage `findings.md:29-37`). | Reformulation R4/validation, then `FPR-07`. | Independent profile-scoped obligations. Release-blocking after FPR-04/05/06 inputs. |
| `EGI-016` | PKG-6 | Legacy emits `todo`; Financial hybrid reports 67 gaps/79 obligations and skips unresolved work; hybrid CLI returns 0 and does not fail parser violations ([A1](./research.md#agent-1--shannon-claude), `emit/tests.ts:71-91,330-433`, `cli.ts:353-394`, `emit/tests.test.ts:61-107`). | Existing `FPR-07` coverage controls. | Exact-set, nonempty, zero-skip/todo, binding, execution, mutation gate. Release-blocking false-green. |
| `EGI-017` | PKG-7 | Aggregate `npm run validate` omits engine tests, tag tests, instance validation, and typecheck relative to intended release profile; omitted suites currently pass independently ([A3](./research.md#agent-3--turing-alan), `impl/package.json:17-32` and live receipts). | Validation integration across `FPR-04/07/08`. | Required-check manifest and exhaustive aggregate. Structural release risk, not current suite failure. |
| `EGI-018` | PKG-7 | Exact alias `FPR-08`: candidate-bound `I_struct` artifacts were absent from inspected engine/FPR surface, not proven absent repository-wide ([A1](./research.md#agent-1--shannon-claude), `expected-node-edge-manifest.yml:225-247`). | Existing `FPR-08`; implementation/platform. | Later exact-root AST/symbol/import/call extraction. Release-blocking, later execution. |
| `EGI-019` | PKG-7 | Exact alias `FPR-09`: directional predicate registry and conformance vector were absent from inspected FPR/engine surface ([A1](./research.md#agent-1--shannon-claude), `ROADMAP.md:65-67`, `expected-node-edge-manifest.yml:249-269`). | Existing `FPR-09`. | Later one-predicate `Sg↔I_struct` witness. Last execution slice; release-blocking join. |
| `EGI-020` | PKG-1 | Import manifest promises a missing RESULT section and points to absent `impl/spec/DEFINITIONS.md` ([A3](./research.md#agent-3--turing-alan), `IMPORT-MANIFEST.md:22,93-97`). | New hygiene residue inside import migration/definitions governance; feeds `FPR-01/04`. | Repair/remove destinations and bind imports to owners. P1; blocking if used as authority/input. |
| `EGI-021` | PKG-8 | README calls implemented parser/rules stubs; a rule comment says `TEST-PIPELINE.md` is absent although it exists ([A1](./research.md#agent-1--shannon-claude), `README.md:23-25`; [A3](./research.md#agent-3--turing-alan), `rules/index.ts:2-4,631-663`). | Engine package/read-model maintenance. | Documentation synchronization. Nonblocking; not a program gap. |

# Reviewer verdict matrix

Ownership is positive routing. Only an unwitnessed or tautological evidence item could be `KILL`; none is. The definitional reviewer’s `KILL-ID` means “kill the duplicate identity,” not “discard the evidence.”

| Candidate/evidence ID | Owner (precedent) | Witnessed? | Sound? | Verdict |
|---|---|---|---|---|
| EGI-001 | FPR-01 | Yes | Yes, with unratified 13/24/30 qualification | ROUTE/MERGE |
| EGI-002 | source-homing decision + FPR-01/04 | Yes | Yes, bounded to source conflict | ROUTE/MERGE |
| EGI-003 | `GAP-SH-UI11-MIGRATE` | Yes | Yes as profile contract, not contradiction | ROUTE/MERGE exact alias |
| EGI-004 | `FR-FPR-ONTOLOGY-DIRECTION` | Yes | Yes with stated/unresolved split | ROUTE/MERGE exact alias |
| EGI-005 | definitions governance + FPR-01 | Yes | Yes; missing scan is the residue | MERGE new witness |
| EGI-006 | SGRM-006/007 | Yes | Yes as expired/reopened proof | REOPEN/MERGE |
| EGI-007 | FPR-02/04 | Yes, 0/0; unknown fixture absent | Yes with split claims | MERGE distinct fixtures |
| EGI-008 | FPR-04/07 | Yes | Yes, executable false-green | MERGE negative control |
| EGI-009 | FPR-04 | Yes | Yes as bounded absence | ROUTE/MERGE exact alias |
| EGI-010 | FPR-04 quotient | Yes | Yes, audited-parser scope | MERGE new witness |
| EGI-011 | FPR-04 proof | Yes | Yes; current check not declared broken | MERGE proof slice |
| EGI-012 | FPR-02/04 | Yes | Yes, inspected-pack scope | MERGE exercise set |
| EGI-013 | FPR-05/APE | Yes | Yes, unadmitted not nonexistent | MERGE pattern slice |
| EGI-014 | FPR-05/APE | Yes | Yes, no partition claim | MERGE composition slice |
| EGI-015 | FPR-07 | Yes | Yes, generator-owned denominator | MERGE obligation slice |
| EGI-016 | FPR-07 | Yes | Yes, mode-specific | MERGE coverage slice |
| EGI-017 | validation + FPR-04/07/08 | Yes | Yes, omitted suites currently green | MERGE integration slice |
| EGI-018 | FPR-08 | Yes | Yes, inspected-surface scope | ROUTE/MERGE exact alias |
| EGI-019 | FPR-09 | Yes | Yes, inspected-surface scope | ROUTE/MERGE exact alias |
| EGI-020 | import migration + definitions | Yes | Yes, exact stale paths | MERGE new witness |
| EGI-021 | engine maintenance | Yes | Yes as documentation contradiction | ROUTE maintenance; no gap |

# Execution order versus release severity

Execution order answers **what can safely be worked next**:

1. Restore the live failing retired-reference guard.
2. Close `FPR-01`.
3. Freeze `FPR-02`.
4. Resolve `FPR-03`.
5. Build and prove the first `FPR-04` slice.
6. Add selected `FPR-05` semantics; route `FPR-06` through its owner.
7. Build independent `FPR-07` evidence and `FPR-08` observation.
8. Join at `FPR-09`.

Release severity asks **what must be true before release**; it is not an execution queue. Applicable `FPR-01..09` obligations remain release-blocking even where safe execution is later. Documentation maintenance is not equivalent to those blockers. A backend-only profile may defer UI formation breadth only if `FPR-02` explicitly says so ([Agent 1](./research.md#agent-1--shannon-claude), `ROADMAP.md:56-71`; [Agent 2](./research.md#agent-2--senge-peter), dependency graph and `expected-node-edge-manifest.yml`).

# Typed negatives and non-claims

- `13/24/30` is the strongest machine reading, not ratified authority ([A2](./research.md#agent-2--senge-peter)).
- `97/97` proves the prototype contract, not FPR-04/07/08 completion ([A1](./research.md#agent-1--shannon-claude), `impl/test-derivation-engine/src/index.ts:22-33`).
- The historical Saga receipt is not disproved; live drift expired its present evidentiary force. The explorer’s pre-output audit found 2 violations, while the parent’s post-output audit found 4 because `research.md` and `findings.md` also require classification/allowlist disposition ([A3](./research.md#agent-3--turing-alan), `SWU-SGRM-008/TASK-SESSION-RESULT.md:14-17,55-63` plus pre-output and post-output audit receipts).
- `11/13` and `9/30` apply only to inspected current feature packs ([A3](./research.md#agent-3--turing-alan)).
- `Operation→Value Object`, untyped `depends-on`, and event payload/publisher composites are deferred owner candidates, not edges the dogfood project may invent ([A2](./research.md#agent-2--senge-peter), `definitions/reviews/2026-07-12-deferred-relationship-candidates.md:22-40`).
- Lane Z versus Lane A, general category laws, and agent-cost superiority are unproved and are not prerequisites for a bounded generated-`Sg` walker ([A2](./research.md#agent-2--senge-peter), `spec-ontology-unification/toy/verdict.md:29-40`, `category-law-formalization-route.md:13-23`).
- Corepack friction is only an invocation observation: direct binaries passed; no engine-semantic conclusion follows ([A1](./research.md#agent-1--shannon-claude), command receipts and `impl/test-derivation-engine/package.json:8-19`).
- Whether `candidate` and `active` are distinct maturity dimensions remains ungrounded; the current surfaces use both without a machine baseline that relates them ([A2](./research.md#agent-2--senge-peter), `definitions/meta-types/meta-types.md:8-22`, `impl/spec/TAXONOMY.md:1-7`). Authoritative source homing, UI admission, precedence, quotients, independent obligations, and exact `I_struct` roots remain owner decisions.

# First slices of existing FPR nodes

1. **Restore guard and ratify baseline**
   - `owner_node: FPR-01`
   - Classify or allowlist this dispatch’s `research.md` and `findings.md`, restore SGRM-006/007’s live retired-reference guard against the post-output 4-violation state, then produce authority census, source dispositions, deterministic drift scan, owner receipt, and count/path/status mutations. Preserve the explorer’s 2-violation result as its valid pre-output observation.
   - Evidence: `EGI-001`, `002`, `005`, `006`, `020`.
   - Basis: [Agent 2](./research.md#agent-2--senge-peter), `development/first-production-release/craft/expected-node-edge-manifest.yml:49-66`; [Agent 3](./research.md#agent-3--turing-alan), `development/saga-removal/runs/SWU-SGRM-008/TASK-SESSION-RESULT.md:14-17,55-63`.

2. **Freeze the bounded supported profile**
   - `owner_node: FPR-02`
   - Enumerate literal admitted backend node types, edge signatures, required documents, obligations, and exercised subsets; add empty-content, unknown/absent-schema, formation-deferred, missing-root, and legacy-path negatives.
   - Evidence: `EGI-003`, `007`, `008`, `012`.
   - Basis: [Agent 2](./research.md#agent-2--senge-peter), `meta-types.yml:18-23`, `relationships.md:65-87`; [Agent 3](./research.md#agent-3--turing-alan), `impl/tools/validate-content.ts:99-119`.

3. **Close the existing precedence gate**
   - `owner_node: FPR-03`
   - Resolve business/ontology/spec precedence, supersession, provenance, and contradiction handling. Keep ontology and learning surfaces generated-only unless an owner changes that contract.
   - Evidence: exact-owner alias `EGI-004`.
   - Basis: [Agent 2](./research.md#agent-2--senge-peter), `.craft/ledger.yml:894-904,606-619`, `research/2026-07-01-spec-as-ontology/findings.md:54-73`; [Agent 3](./research.md#agent-3--turing-alan), `definitions/DEFINITIONS.md:183-216`.

4. **Build the tiny authoritative walking skeleton**
   - `owner_node: FPR-04`
   - Compile one required source with two authoritative nodes and one admitted edge into schema-valid `Sg`; establish the source manifest, explicit `Sg→G` quotient, independent retraction, and missing-source/empty-graph/type/field/direction/edge/quotient mutants.
   - Evidence: exact-owner alias `EGI-009`, plus `002`, `008`, `010`, `011`.
   - Basis: [Agent 1](./research.md#agent-1--shannon-claude), `development/first-production-release/craft/expected-node-edge-manifest.yml:121-146`, `impl/test-derivation-engine/src/index.ts:22-33`.

5. **Add only first-witness implementation semantics**
   - `owner_node: FPR-05`
   - Admit one node pattern and one edge-composition rule required by the witness. Unsupported objects emit `pattern-unavailable` or `composition-unsupported`; do not expand FPR-07 in this slice.
   - Evidence: `EGI-013`, `014`.
   - Basis: [Agent 2](./research.md#agent-2--senge-peter), `development/architecture-pattern-enforcement/cards/backend/README.md:10-16,25-43`, `development/r3-closeout-plan/task-sessions/2026-07-12-swu-r3c-001/TASK-SESSION-RESULT.md:19-27,49-58`.

## Interactive ontology implementer dogfood handoff

The interactive ontology project is a **read-only consumer** of the generated `FPR-04` `Sg`. It is never a semantic authority, continuation authority, or new gap owner. Entry is allowed only after `FPR-01` ratifies the authority baseline, `FPR-02` freezes the supported profile, `FPR-03` closes precedence/direction, and `FPR-04` emits the two-node/one-admitted-edge walking skeleton.

Its first scenario traverses that skeleton and exercises the typed negatives behind `EGI-008`, `EGI-010`, and `EGI-011`: missing or empty required input must not yield an empty success; an incompatible or unapproved local edge mapping must remain explicit residue rather than an authoritative relation; and mutated node, field, edge direction, or quotient data must fail the independent `Sg→G→Sg_canonical` retraction. Any observed residue routes to the existing `FPR-04`, `FPR-05`, or `FPR-07` owner. The dogfood application cannot mint relations, evidence authority, lifecycle IDs, or replacement gap identities ([Agent 1](./research.md#agent-1--shannon-claude), `development/first-production-release/ROADMAP.md:58-67,94-104`, `development/first-production-release/craft/expected-node-edge-manifest.yml:121-146,198-223`).

Independent obligations belong to later `FPR-07` work after relevant `FPR-04/05/06` inputs exist. `I_struct` and conformance remain exact-owner work in `FPR-08/09`; their absence must not become new EGI gap identities.

# Evidence boundary and reviewer disposition

Evidence came from the bounded sources and read-only commands recorded by the three explorers. Agent 1 inspected the FPR roadmap/manifest and every executable engine source/test, observing 97/97 tests, successful typecheck, missing-feature false-greens, and a 62-node/2-edge Financial parse. Agent 2 traced continuation and definition authority, dependency order, owner nodes, count conflicts, and deferred language candidates. Agent 3 adversarially ran current validators, bounded the dirty-worktree observations, distinguished expired proof from historical falsehood, and separated omitted-but-green suites from active failures. Agent 3’s retired-orchestration count is a valid pre-output snapshot; the parent’s later count includes the two dispatch outputs and does not retroactively change that observation ([Agent 1 evidence boundary](./research.md#evidence-boundary); [Agent 2 authority sources](./research.md#authority-sources); [Agent 3 evidence boundary](./research.md#evidence-boundary-1)).

Non-vacuity review retained all 21 evidence items after narrowing overclaims. Definitional/precedent review rejected duplicate identities while preserving their evidence and routed the inventory into eight existing-owner packages. No evidence item met the allowed `KILL` condition of being unwitnessed or tautological. The final distinctions—read model not authority, evidence ID not gap ID, execution order not release severity, and exact aliases merged rather than minted—are reviewer-required controls.

Infrastructure residue: the dispatch named output-writing skills that were not exposed under those names as invocable runtime capabilities. Their required output behavior was specified inside the repository-local research dispatch contract and was followed directly, so the artifacts could be produced, but the missing named packages remain dispatch infrastructure residue rather than DomainSpec engine evidence.

Provenance note: the writer received `.synthesis-revised.tmp.md` and `.reviewer-attacks.tmp.md` alongside `research.md`; those temporary staging files are process inputs, not authority sources or continuation artifacts.

## Post-run parent verification

- `engine:test`: **PASS**, 97/97.
- `typecheck`: **PASS**.
- Sample `validate:content`: **PASS** with 0 concepts and 0 edges.
- Missing-feature witness through the correct workspace binary: `derive` exited 0 and emitted only the empty table header; `lint` exited 0 and reported `CLEAN (0)` against the v1 poker-team path.
- `audit:retired-orchestration`: **FAIL**, 212 matching files, 1,777 matches, 4 violations. The increase from the explorer’s pre-output 2 is accounted for by unclassified `research.md` and `findings.md`; both require classification/allowlist disposition.

## Connections

| Target | Relation | Description |
|---|---|---|
| [research.md](./research.md) | `derives-from` | This findings artifact derives from the three verbatim explorer returns and preserves their evidence boundaries. |

# Open Questions

- **OQ-1 (BLOCKER)** — Will `FPR-01` ratify `13/24/30`, or dispose another baseline with explicit reasons? Recommendation: derive the census from named sources, record stale projections, and require the existing owner receipt. Owner: `FPR-01` definitions/validation/layering owners.
- **OQ-2 (BLOCKER)** — Which feature-source home is authoritative? Recommendation: close `DEC-DSV2-SPEC-HOMING`, encode dispositions in the baseline, and make FPR-04’s manifest reject legacy or missing roots. Owner: source-homing decision owner plus `FPR-01/FPR-04`.
- **OQ-3 (BLOCKER)** — What exact backend/UI profile and maturity dimensions does FPR-02 admit? Recommendation: keep formation, signature, and profile admission separate and add red fixtures for every excluded class. Owner: `FPR-02` and `GAP-SH-UI11-MIGRATE` owners.
- **OQ-4 (BLOCKER)** — How are business, ontology, and Spec precedence, supersession, provenance, and contradictions resolved? Recommendation: close the existing direction frontier; do not let generated views write authority backward. Owner: `FR-FPR-ONTOLOGY-DIRECTION` semantic owner via definitions governance.
- **OQ-5** — What quotient from authoritative `Sg` to local compiler `G` is permitted? Recommendation: start with two nodes and one admitted edge, name every mapping, and require independent retraction mutants. Owner: `FPR-04` semantic/validation/engine owners.
- **OQ-6** — Which one pattern and composition rule form the first implementation witness? Recommendation: select only after the FPR-02 profile and FPR-04 graph exist; fail closed for everything else. Owner: `FPR-05` / APE owner.
- **OQ-7** — What independent obligation denominator and evidence requirements close FPR-07? Recommendation: keep `O_spec` separate from generator-owned `O_gen` and require nonempty, no-skip/todo, executed evidence. Owner: `FPR-07` validation/governance owner.
- **OQ-8** — Which exact generated roots and first predicate should witness `I_struct` and directional conformance? Recommendation: bind one FPR-08 extractor slice to one FPR-09 predicate after the first implementation witness. Owner: `FPR-08` implementation/platform owner and `FPR-09` conformance owner.
- **OQ-9** — Who repairs the output-writing capability-registration mismatch? Recommendation: register or rename the runtime skills to match the governed repository contracts before the next dispatch. Owner: dispatch/runtime infrastructure owner.
