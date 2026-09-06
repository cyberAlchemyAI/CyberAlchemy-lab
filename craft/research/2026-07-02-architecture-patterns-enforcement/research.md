---
node_type: research
role: collected-returns
subject: v2 architecture-pattern enforcement — layering, composability, uniformity (start-now)
dispatch_id: 2026-07-02-v2-architecture-patterns-enforcement
schema_version: "0.6.0"
status: collected
agents:
  - "van Lamsweerde, Axel — explorer (E1 authority/formal, cav2 spine)"
  - "Alexander, Christopher — explorer (E2 empirical/precedent, impl trees)"
  - "Goldratt, Eliyahu — explorer (E3 adversarial/pragmatic, temporal)"
anti_bias_global: "authority-mandate vs owned-substrate vs enforce-now-safely"
note: >
  Verbatim collected explorer returns (Principle 9). The cited synthesis is in findings.md;
  every load-bearing claim there cites one of the three returns below.
---

# Collected returns — architecture-pattern enforcement in domainspec-v2

## E1 — van Lamsweerde (AUTHORITY / FORMAL, cav2 spine)

### 0. Status of the authority itself (claim-bound first)
The governance interface reported on is **not yet full authority** — it is self-labeled `Status: candidate architecture interface` (`cyberAlchemy-v2/architecture/ARCHITECTURE-KNOWLEDGE-GOVERNANCE.md:3`) and its folder is `Status: placeholder with boundary` (`cyberAlchemy-v2/architecture/README.md:3`). The piece that IS active, stable-repository authority is `CAV2-C14 Governed Artifact Tree Interface` (`cyberAlchemy-v2/authority/constitutions/STABLE-REPOSITORY-CONSTITUTION.md:283-328`, validation mode: hybrid) plus definitions `CAV2-D42/D43/D44` (`Status: active`, `authority/definitions/DEFINITIONS.md:2709,2792,2875`). So: the rules governing how patterns must be shaped and promoted are active authority; the architecture-pattern-inventory package/tree itself is candidate-only, empty except for the boundary doc (`architecture/README.md:6-13`).

### 1. What the interface REQUIRES of any v2 architecture pattern
**Mandatory governance-interface fields** (stated three times — governance doc, CAV2-D42, CAV2-C14 — a converged requirement): `owner_route`, `canonical_source` (or explicit "no canonical source yet" boundary), `view_roles`, `evidence_inputs`, `promotion_path`, `validation_surface`, `challenge_contract`, `drift_route`, `allowed_use`, `blocked_use`. Source: `ARCHITECTURE-KNOWLEDGE-GOVERNANCE.md:81-97`; formalized `GAT(T) = (tree_id, scope, owner_route, canonical_source, view_roles, evidence_inputs, promotion_path, validation_surface, challenge_contract, drift_route, allowed_use, blocked_use)` in CAV2-D42 (`DEFINITIONS.md:2739-2747`); restated in CAV2-C14 (`STABLE-REPOSITORY-CONSTITUTION.md:292-302`). Missing field ⇒ the tree "cannot promote knowledge, constrain downstream work, or act as a reusable authority surface without typed residue and owner review" (`DEFINITIONS.md:2749-2751`).

**Candidate shape** — every `pattern_candidate_id` must carry (`ARCHITECTURE-KNOWLEDGE-GOVERNANCE.md:99-122`): `pattern_candidate_id, label, source_hypothesis, domain_exercise, evidence_set, localized_concept, generalized_abstraction, concept_cards, relationship_cards, dependency_rules, testing_alignment, observability_alignment, known_counterexamples, challenge_contract, owner_route, promotion_request, current_authority_posture, allowed_use, blocked_use, residue`. Caveat: "an interface shape, not a live schema. A future schema amendment witness is required before this becomes machine-enforced" (`:124-125`) — review-checked prose today, not a validator.

**Promotion lifecycle** (governance doc + CAV2-D43): hypothesis → exercised in domain → evidence set → localized concept → generalized abstraction → pattern candidate → exercised in another context → challenge review → owner promotion → architecture pattern authority → invariant/constitution pressure when justified (`ARCHITECTURE-KNOWLEDGE-GOVERNANCE.md:62-74`; formal tuple `PPL(c)` in `DEFINITIONS.md:2828-2833`). Gate rule: movement candidate→authority "is valid only when the owner decision declares the authority effect and the claim strength does not exceed the evidence set" (`DEFINITIONS.md:2835-2837`) — tied to claim-proof bound CAV2-D38 (`:2428`). CAV2-D44 gates whether a concept deserves a view/tree at all: only when distinct_evidence ∧ lifecycle_posture_needed ∧ owner_route ∧ reuse_surface ∧ challenge_or_drift_route (`DEFINITIONS.md:2894-2903`) — not every recurring code shape earns a governed tree.

### 2. AUTHORIZED vs BLOCKED
Core guardrail `has a tree != has authority` (`ARCHITECTURE-KNOWLEDGE-GOVERNANCE.md:26-33`), constitutionally: a tree "may not become authority by having a folder, branch view, inventory row, concept card, architecture package, or projection. Authority requires the relevant owner route and promotion gate" (CAV2-C14, `STABLE-REPOSITORY-CONSTITUTION.md:304-307`).

**AUTHORIZED today:** build inventory packages (concept cards, relationship cards, **dependency rules**, testing/observability alignment, pattern candidates) as inspectable non-authoritative artifacts (`:19-24`; C14 Example 1 `:311-314`); name a dependency rule as an observation; route candidates to owners; label lifecycle posture (CAV2-D23) + attach challenge contracts (CAV2-D40).

**BLOCKED (Non-Authority Rules, verbatim, `:153-163`):** storing a card; naming a candidate; **adding a dependency rule as observation** (writing "layer X must not depend on Y" does NOT make it enforceable); reusing code successfully once; showing a concept in an ontology view; adding a concept to a tree; passing tests that don't name the pattern claim they support. Reinforced by AUTHORITY-MODEL Non-Collapse Rules (`AUTHORITY-MODEL.md:122-133`): evidence/inventory/successful-run never promote by themselves. The Authority Kinds table is closed/default-deny (CAV2-D49, `AUTHORITY-MODEL.md:61-72`): "architecture pattern" is not one of the nine kinds — it must be promoted INTO Constitution or Definition to bind anything.

**Reads on the task:** standing up layering/composability/uniformity *enforcement* in v2 now is authorized as inventory-building but **blocked as binding enforcement** — a dependency rule in the tree cannot function as a gate; it stays an observation until owner-promoted.

### 3. Promotion path (owner routing)
Architecture-specific (`ARCHITECTURE-KNOWLEDGE-GOVERNANCE.md:140-152`): evidence→candidate = architecture-pattern-inventory; candidate→architecture authority = CyberAlchemy authority model + architecture owner; candidate→definition = definitions-governance; candidate→constitution/invariant pressure = constitution-governance; candidate→discipline = discipline-governance; candidate→implementation = invoke/task-session after gates; schema change = schema governance + amendment witness; challenge = route named by challenge contract. Narrowest-owner rule confirms (`AUTHORITY-MODEL.md:90-103`). Execution sequence (`:165-180`): capture hypothesis → record refs/exercise → build concept+relationship cards → attach dependency/testing/observability alignment → label lifecycle (D23) → apply claim-proof bound (D38) → add challenge contract (D40) → route to owner. Only after the owner gate clears does it become authority and may exert constitution/invariant pressure (via constitution-governance, not self-declared).

**Open-work caveat (`:182-190`):** first CAV2 architecture-pattern-inventory package NOT yet built; no cross-context promotion example run; machine-checkable schema undecided. `architecture/README.md` OQ-1 (`:27-32`): repository architecture map still open (PARTIAL). No v2 pattern has completed the path to authority — any layering/composability/uniformity rule enforced in v2 today is at most a *pattern candidate under construction*, not authority, and cannot exert binding pressure without owner promotion.

---

## E2 — Alexander (EMPIRICAL / PRECEDENT-SWEEP, impl trees)

Repo root `/home/vrondelli/projects/domainspec-core`. Confirmed by direct diff except where noted.

### LAYERING
| mechanism | owner (exact path) | what it does | status | runnable / docs-only |
|---|---|---|---|---|
| Layer model (Domain/Application/Infrastructure/Interface) + folder blueprint | v1 `implementation/domainspec/architecture/pattern-library/LAYERING-REFERENCE.md` | per-layer responsibilities, module-boundary guidelines, suggested `src/` layout | **pending** — not in IMPORT-MANIFEST at all (no v2 dest row for `architecture/` tree) | docs-only |
| Dependency direction rules | v1 `.../architecture/pattern-library/DEPENDENCY-RULES.md` | Domain/App/Infra/Interface import-boundary constraints; "violation heuristic" = block merge on inward-import breach | **pending** — untriaged | docs-only (recommends ESLint/tsconfig/arch-tests, ships none) |
| Architecture navigation index | v1 `.../architecture/ARCHITECTURE.md` | index-only pointer into pattern-library | **pending** | docs-only |
| Foundational principles + layer-model baseline | v1 `.../architecture/pattern-library/ARCHITECTURE-FOUNDATIONS.md` | 39-line principles doc | **pending** | docs-only |
| Layer↔test / layer↔observability obligation maps | v1 `.../pattern-library/TESTING-ALIGNMENT.md`, `OBSERVABILITY-ALIGNMENT.md` | point each layer at its test/metric obligation source | **pending** | docs-only (thin, <30 lines) |
| **C6 — Forbidden Edges Are Unconstructible** | v2 `authority/constitutions/domainspec-v2-CONSTITUTION.md` (`domainspec-v2-C6`) | THE v2 layering **law**: forbidden relation typed unconstructible, not flagged post-hoc; no dependency crosses adapter line (cites AXIOMS A2) | net-new formulation, **OPEN/reformulation-pending** — split target `constitutions/layering-governance-CONSTITUTION.md` named but does **not exist yet** | docs-only (no typed-edge catalog implementing it) |
| Axiom A2 — Decisions Belong To The Domain, Not Adapters | v1 `AXIOMS.md` → v2 `impl/spec/AXIOMS.md` | the cited authority behind C6 | **imported-verbatim**, overall REFORMULATE/reformulation-pending (Batch 1) | docs-only |
| `domainspec-audit-layering` skill | v1 `.claude/skills/domainspec-audit-layering/SKILL.md` | layering-drift audit → dependency-ordered migration plan keyed to SPEC concept IDs | **pending** (Batch 3, rows 25,26) — zero SKILL.md under v2 | runnable **only in v1 shape** (hardcoded `docs/features`, `backend/src/domain`, `backend/src/use-cases` — none exist in v2) |
| `domainspec-audit-alignment` skill | v1 `.claude/skills/domainspec-audit-alignment/SKILL.md` | implementation-fidelity audit (compliant/partial/missing/extra) | **pending** (Batch 3, row 18) | v1-shape-only |
| `ADLC-ALIGNMENT.md` | v1 `implementation/domainspec/ADLC-ALIGNMENT.md` (644 lines) | meta-track/ADLC layer mapping, feedback dynamics, gap roadmap | **pending** (Batch 3, row 27, dest `impl/spec/`) | docs-only |
| Write-path containment guard | v2 `impl/test-derivation-engine/src/paths/containment.ts` + test | pure fn refusing writes outside allowed root / into public `arcanum/` — working instance of an "unconstructible boundary" (adjacent precedent for C6) | net-new | **runnable today** (unit-tested, used by `derive --out`/`emit-tests`) |
| `validate-relationships.ts` (edge-law **check** half) | v1 `tools/validate-relationships.ts` → v2 `impl/tools/validate-relationships.ts` | confirms declared relations conform to RELATIONSHIPS typed-edge vocabulary | imported + **partially reformulated** (3 path args retargeted, diff-confirmed) | **runnable today** `npm run validate:rels` (but `spec/features/` has no real packs, only `__fixtures__/`) |

### COMPOSABILITY
| mechanism | owner | what it does | status | runnable |
|---|---|---|---|---|
| Composability pattern matrix | v1 `governance/tags/CODE-TAG-COMPOSABILITY-PATTERNS.md` → v2 `impl/governance/tags/…` | edge matrix (`enforces/calculates/applies/exposes/orchestrates/mutates/fetches/produces/transitions/contracts/consumes`) → required code composition, w/ "Enforced by Tool" column | **imported-verbatim** | docs-only, paired with runnable checker |
| `check-code-tag-composability.ts` | v1 `.../tools/…` → v2 same | encodes `ComposabilityRule[]` (edge/fromType/toType/direction/severity, codes CT-COMP-001..004+), validates tag call graphs | **imported-verbatim** | **runnable today** `npm run tags:composability` |
| `extract/compare-drift/validate-code-tags.ts`, `lib/*`, adapters `{js,js-like,py,ts}` | v1 `.../tools/` → v2 `impl/governance/tags/tools/` | full tag toolchain (extract, schema-validate, drift compare) across TS/JS/Py | **imported-verbatim** except `validate-code-tags.ts` (3-line path retarget) — reformulation-pending (Batch 2) | **runnable today** `tags:extract/validate/drift` |
| `CODE-TAG-SCHEMA.md`/`.json` | v1 → v2 `impl/governance/tags/…` | canonical tag shape `domainspec.concept.{id,type,concern,spec_ref}` + `domainspec.edges[]` | **imported-verbatim** | machine-checkable JSON schema + docs |
| `CODE-TAG-REMEDIATION.md` | v1 → v2 | failure-code remediation catalog paired to validator error codes | **imported-verbatim** | docs-only |
| Composability example snippets (8 files) | v1 `.../examples/composability/*.ts` → v2 | minimal working code per pattern | **imported-verbatim** (`diff -rq` clean) | code samples, not tests |
| `CODE-TAG-WAIVERS.md` / `code-tag-waivers.yaml` | v1 → v2 `impl/governance/tags/` | waiver policy + registry | **imported-verbatim but STALE** — v2 still holds v1's 3 AEO entries; manifest said "reset to empty", **not done** | data file consumed by validator |
| C9 (Link & Import Integrity) / C11 (Relationship/Edge-Law Conformance) | v2 `authority/constitutions/domainspec-v2-CONSTITUTION.md` | rules labeled `⟵ validation governance (build-from-owned)`, cite `validate-doc-links.ts`/`validate-relationships.ts` | net-new rule text wired to imported tools | docs-only rule + runnable tool pair |
| `validate-doc-links.ts` | v1 `tools/validate-doc-links.ts` → v2 `impl/tools/…` | broken-link/dangling-import blocker across feature packs | imported + 1-line retarget | **runnable today** `npm run validate:docs` |

### UNIFORMITY
| mechanism | owner | what it does | status | runnable |
|---|---|---|---|---|
| Per-meta-type schema criteria | v2 `impl/spec/meta-types/{structural,behavioral,connective,lifecycle}/*.schema.yml` (14 files, one per backend meta-type) + matching `.md` | decidable per-type "SCHEMA-CONSTITUTION" criterion each instance must satisfy — operational def of uniform shape | **net-new** (no v1 equiv), built against v1 TAXONOMY groupings | docs+schema; consumed by runnable checker |
| `validate-content.ts` | v2 `impl/tools/validate-content.ts` | walks `spec/features/**/SPEC.md`, checks each concept vs its meta-type schema (SHAPE only). Header: "Build-from-owned: markdown-table parsing modeled on `tools/validate-relationships.ts`" | net-new logic, build-from-owned parsing | **runnable today** `npm run validate:content`; 151-line test + 28 ok/bad fixtures at `impl/spec/__fixtures__/mt/*` |
| `instances.ts` | v2 `impl/tools/instances.ts` | `generate`: emits canonical example instance YAML per schema (14 files present); `validate`: checks structured YAML instances vs criterion | net-new | **runnable today** `instances:generate`/`validate`; 50-line test; 14 generated files on disk |
| Taxonomy baseline (24 meta-types, 4+4 groupings) | v1 `TAXONOMY.md` → v2 `impl/spec/TAXONOMY.md` | conceptual uniformity contract the schema layer operationalizes | **imported-verbatim**, reformulation-pending (Batch 1) | docs-only |
| `CODE-TAG-SCHEMA` | (see composability) | one canonical annotation shape across every tagged symbol, any language | imported-verbatim | machine-checkable |
| **Gap** — UI meta-types have no schema | n/a | `spec/meta-types/` covers only 14 backend types; 11 UI meta-types (Page/Layout/Component/View Model/Hook/Form/Action/Guard/Binding/Adapter/State Indicator) have **no `.schema.yml`** | confirmed absent | — |

### Cross-cutting
- No `architecture/`/`pattern-library/` tree exists anywhere under `projects/domainspec-v2/` (confirmed by find). All layering-pattern-library content is cited only as harvested evidence in v2 research docs, never imported — **the single largest build-from-owned opportunity not yet triaged.**
- `CODE-TAG-DRIFT-REPORT*.md` + `code-tags*.json` (v1 runtime **data**) correctly DROP, absent from v2.

---

## E3 — Goldratt (ADVERSARIAL / PRAGMATIC, temporal)

### THE SINGLE SHARED CONSTRAINT (the actual bottleneck)
Every Batch-2 validator and the engine CLI import **only `node:*` builtins + local relative files — zero external npm deps** (verified across `impl/tools/*.ts`, `impl/governance/tags/tools/**`). So "make C9/C10/C11 runnable" reduces to **one missing thing: a `tsx` loader**. There is no `package.json` anywhere under `impl/` except the engine, and even the engine's `node_modules/.bin/tsx` is **ABSENT**. So constitution OQ-1 ("`pnpm install && pnpm test && pnpm run lint:docs` green") is genuinely OPEN — nothing in v2 can execute a `.ts` today. **The minimum enforceable discipline is gated on one ~10-line `package.json` (tsx devDep) at `impl/`, mirroring `impl/test-derivation-engine/package.json`.** Rank everything below *after* that unlock. Second shared fact: the defaults are inconsistently half-migrated `docs/features`→`spec/features`; each tool needs the same tiny retarget but they disagree on where they already point.

### 1. START-NOW-MINIMAL (ranked value/cost)
**S1 — Engine `lint` = C10 Spec Completeness. HIGHEST.** Handle `impl/test-derivation-engine/src/cli.ts` `runLint` (403–428); script `lint:docs`. Reports non-canonical tables + `needs-formal` cells, exit 4 — exactly C10's declared method (constitution 107–114). Wiring: just tsx; accepts a **path arg** via `resolveTarget` (cli.ts 173–177) so it runs against a fixture today. Do NOT rely on bare-feature-name default — `featureDirFor` (cli.ts 69–76) hardcodes the **v1** poker-team path; pass explicit path. Data-path-clean, strongest start-now item.

**S2 — `instances.ts validate` + `validate-content.ts` = meta-type SHAPE conformance. HIGH.** Both **data-driven off `spec/meta-types/**/*.schema.yml`**, so resilient to meta-type churn by construction — moving parts live in `.schema.yml`, not code. Wiring: tsx + cwd=`impl/` or `--schema-dir impl/spec/meta-types`. `instances validate` covers 14 committed instances; `validate-content` covers SPEC aspect files (only `sample` exists). Caveat: the `.schema.yml` **format binding (SCHEMA-CONSTITUTION import, delta D2) is still pending** per `development/meta-type-formalization/REFRESH-2026-07-02.md` — tools are safe; a schema-format churn is a data migration, not a code rewrite.

**S3 — `validate-code-tags.ts` = the endpoint-signature half of C11. HIGH value, MEDIUM cost, one defect to clear.** Loads edge-law **dynamically** from `RELATIONSHIPS.md` via `parseRelationshipRules` (lib/code-tag-rules.ts 67–117), checks source/target types (CT-004 line 396, CT-006 line 424) + concept.type ∈ TAXONOMY (CT-010 line 226). Both source docs exist. Wiring: tsx + retarget `--relationships/--taxonomy/--features-root`; needs `code-tags.json` from `extract-code-tags.ts` — **v2 has no tagged impl code yet, so this runs but is vacuous today.** **MUST-FIX-BEFORE-TRUST:** `code-tag-waivers.yaml` **still carries live v1 AEO waivers** (`AEO-CT-004-…`, `expiresAt: 2026-12-31`); manifest Batch-2 ordered "reset to empty for v2" — **not done**. Any v2 run silently suppresses CT-004/CT-006 for nonexistent paths — pre-laundered violations. Reset to `waivers: []` first. Second remnant: `normalizeSpecPath` (749–758) anchors on literal `"docs/features/"`; under v2 the anchor never matches and CT-017/018 degrade to full-path compare (silent behavior change).

**S4 — `validate-doc-links.ts` = C9 Link & Import Integrity. MEDIUM.** Pure structural (frontmatter deps resolve, includes/links/anchors resolve). **Zero meta-type coupling → safest to hard-wire.** Wiring: tsx + cwd=`impl/`. Defect: `--only-changed` path (`getChangedMarkdownFiles` line 228) still filters `docs/features/`; use full-scan or fix prefix. Low value today (only `spec/features/sample`) but correct.

**S5 — `validate-relationships.ts` = the LABEL half of C11 ONLY. LOW-MEDIUM — do NOT badge as "C11 done."** Checks edge label ∈ canonical set (72, 98) and **nothing else — never checks endpoint signatures.** C11 (constitution 122–129) demands "typed-edge vocabulary **+ endpoint signatures**." This covers vocabulary; the signature half lives in S3 but only over *code tags*, not feature-pack *declared relations*. **Net: no tool today checks feature-pack declared-relation endpoint signatures against the edge-law.** Wiring C11 as "satisfied by validate-relationships.ts" overclaims — `pass` on labels, silent on signatures.

### 2. WAIT LIST (hard-wiring now = rework; dependency named)
**W1 — C6 "Forbidden Edges Are Unconstructible."** Not runnable and cannot be made runnable by wiring an existing tool. Every validator FLAGS post-hoc; C6 (constitution 77–82) rejects exactly that. "Unconstructible" needs a typed catalog-construction layer that doesn't exist. **Dependency:** the meta-type formalism, *actively moving today* (`development/meta-type-formalization/research/2026-07-02-formalism-and-primitives/` holds competing `formalism-minimal/-lean/-solver` + `verify-decidability.md`). Declaring C6 enforced now is premature by definition.

**W2 — `check-code-tag-composability.ts` hard-coded edge-law. The premature-enforcement trap E2 will wave through.** Lines 27–109 bake a **frozen 9-rule TS array** duplicating a subset of RELATIONSHIPS's 29 edges. Its sibling `validate-code-tags.ts` reads the same law **dynamically** — so v2 has **two disagreeing sources of edge truth**. **Dependency:** DS-D2 edge verbs + endpoint signatures, still moving (MT3 node types just landed, `git 22bf33b1`). Fix is cheap/known: refactor to consume `parseRelationshipRules`; until then WAIT.

**W3 — `compare-code-tag-drift.ts` = C7 Convergence-as-Trend.** C7 (constitution 84–90) is "a **trend over time**, never a single passing check" — needs a drift baseline/series that doesn't exist in v2; tool still defaults `--features-root` to `docs/features`. **Dependency:** stable edge-law + committed v2 baseline. Measuring convergence against a moving target is noise.

**W4 — Any `binding`-touching enforcement** (composability CT-COMP-006/007; cross-layer `fetches/mutates/contracts/mirrors`). `binding` is load-bearing in cross-layer edges + TAXONOMY (UI Connective) **but has NO `.schema.yml`**. **Dependency:** binding's formalization; endpoint signature can change when it lands.

**W5 — Binding validators to specific C-numbers / the governance-file split.** OQ-2 (constitution 173–177) defers per-rule C1–C11 reformulation + the split into `validation-/layering-/drift-governance-CONSTITUTION.md` to "at reformulation." **Dependency:** OQ-2. Don't hard-code "validator X === Cn" or the C6↔C11 cross-binding into CI until the split lands, or you rewire twice.

**W6 — Engine `roundtrip`/`self-check` (L0 falsification gate) in v2.** `featureDirFor` (cli.ts 69–76) hardcodes the **v1** poker-team path, and `roundtrip`/`self-check` always use it (unlike lint/derive/check which accept a path). Engine README (23–25): parser + δ-rules were **typed stubs** at import. **Dependency:** a real v2 feature pack + confirmation δ-rules are no longer stubs. Treat engine as **lint-only** until a v2 feature yields a green roundtrip (this is OQ-1's build-proof, OPEN). `instances.ts generate` is a **write/authoring path**, not enforcement — don't count as a gate.

### Bottom line
- Cheapest real win: one `package.json` (tsx) at `impl/` unlocks S1–S5 simultaneously — the constraint is a runtime, not the tools.
- Start now, low rework: S1 (engine lint/C10) and S2 (validate-content/instances validate) — data-driven, edge-independent.
- Start now but clean the defect first: S3 — reset `code-tag-waivers.yaml` to empty and fix the `docs/features` anchor before trusting it.
- The trap to catch E2 on: `check-code-tag-composability.ts` (W2) and any "C11-satisfied" claim on label-only `validate-relationships.ts` (S5) — both look reusable, both silently under-/mis-enforce the edge-law while meta-types move (as of 2026-07-02).
