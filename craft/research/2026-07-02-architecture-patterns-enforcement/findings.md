---
node_type: research
role: findings
subject: v2 architecture-pattern enforcement — layering, composability, uniformity (start-now)
dispatch_id: 2026-07-02-v2-architecture-patterns-enforcement
schema_version: "0.6.0"
status: synthesized-revised (loop-1 feedback incorporated)
agent: "Spivak, David — synthesizer"
reviewers:
  - "Kuhn, Thomas — skeptic (precedent): relabel v1-imported engine; waivers=4 not 3"
  - "Popper, Karl — skeptic (non-vacuity): FALSIFIED the tsx-blocker premise on disk (HEAD 22bf33b1)"
  - "Quine, Willard Van Orman — skeptic (definitional): demote C6 soundness — edge-law re-skins RELATIONSHIPS"
anti_bias_global: "authority-mandate vs owned-substrate vs enforce-now-safely"
guardrail: >
  E1's core invariant governs this whole document: "has a tree != has authority"
  (E1 §2 → ARCHITECTURE-KNOWLEDGE-GOVERNANCE.md:26-33; CAV2-C14
  STABLE-REPOSITORY-CONSTITUTION.md:304-307). No v2 pattern has completed the
  promotion path (E1 §3 open-work caveat :182-190), so every mechanism below is a
  *pattern candidate under construction* — a handle that produces evidence, never
  architecture authority — until owner-promoted. "architecture pattern" is not one
  of the nine authority kinds (E1 §2 → CAV2-D49, AUTHORITY-MODEL.md:61-72); it must
  promote INTO a Constitution or Definition to bind anything.
---

# Findings — architecture-pattern enforcement in domainspec-v2

Reading rule for the matrix: a **found owner is never a KILL** — it relabels to
`build-from-owned`. KILL is reserved for **no-witness** (nothing runnable/constructible)
and **tautological** (definitional collapse: observation ≠ authority). Ownership is a
label, not a verdict.

> **Loop-1 skeptic corrections applied (verified on disk at HEAD `22bf33b1`):**
> 1. **The tsx blocker is FALSIFIED (S2).** `impl/package.json` (with `tsx`) already exists and is committed; tsx@4.22.4 is installed; the P0/P1 scripts are wired. Phase 0 is **runnable NOW**, not "after a tsx unlock" — the remaining constraint is **inputs (real feature packs / tagged code), not runtime.**
> 2. **The `test-derivation-engine` is a byte-identical v1 import (S1)**, not v2-native — `containment.ts`, `cli.ts`, engine `lint`/`roundtrip` relabel `net-new → build-from-owned`, owner `implementation/domainspec/tools/test-derivation-engine/`. (No verdict moves — all were GO already.)
> 3. **C6/LAYERING soundness demoted (S3):** its edge-law content **re-skins RELATIONSHIPS** (= the spec-ontology typed-node+typed-edge formalism); only the *unconstructibility modality* is net-new, and it is **no-witness**. Owner of the edge-law content is RELATIONSHIPS/spec-ontology, not `containment.ts`.
> 4. **`validate-relationships.ts` / `validate-code-tags.ts` are byte-identical to v1 (S1)** — the "diff-confirmed retarget" did **not** happen; the `docs/features` anchors are still owed (strengthens G2). Waiver count is **4, not 3** (S1/S2).

## (A) RESEARCH VERDICT MATRIX

### LAYERING

| candidate | owner (precedent) | witnessed? (runs today?) | sound? (not a re-skin) | verdict | use-mode |
|---|---|---|---|---|---|
| **C6 Forbidden-Edges-Unconstructible** — general layering law | edge-law content owned by **RELATIONSHIPS / spec-ontology typed graph** (S3 demotion); layer-direction by TAXONOMY Layer Dependency Rule + AXIOMS A2; modality net-new in `domainspec-v2-C6` (E2; E3 W1; S3) | **No** for the general catalog — "a typed catalog-construction layer that doesn't exist" (E3 W1); `containment.ts` is an **analogy, not an edge-law instance** (S3) | **Partial (S3)** — edge-law/admissibility content **re-skins RELATIONSHIPS**; only the *unconstructibility modality* is net-new, and it is **no-witness** | **GO** | build-from-owned (owner = **RELATIONSHIPS/spec-ontology** for edge-law; `containment.ts` only an adjacent write-path analogy) — **deploy deferred, Phase 2** |
| **`containment.ts`** write-path unconstructible boundary | **v1-imported byte-identical** (S1), owner `implementation/domainspec/tools/test-derivation-engine/` → v2 `impl/test-derivation-engine/src/paths/containment.ts` + test (E2; S1) | **Yes** — unit-tested, used by `derive --out`/`emit-tests` (E2) | Yes — working instance of an "unconstructible *write-path*" boundary; adjacent analogy for C6, **not** the edge-law (E2; S3) | **GO** | build-from-owned (owner v1) — already-wired for public/private write containment only |
| **`validate-relationships.ts`** — edge-law **label** half of C11 | v1 `tools/…` → v2 `impl/tools/validate-relationships.ts`, **imported byte-identical — the claimed 3-arg retarget was NOT applied** (S1 diff); still carries v1 `docs/features` anchors → strengthens G2 | **Yes** `npm run validate:rels` (runtime present); vacuous — `spec/features/` holds only `sample/` (E2; E3 S5; S2) | **Partial** — checks label ∈ canonical set (72,98) **only, never endpoint signatures** (E3 S5) | **GO** (scope-demoted) | already-deployed (label half of C11 **only**) |
| **`domainspec-audit-layering`** skill | v1 `.claude/skills/domainspec-audit-layering/SKILL.md` (E2) | **No in v2** — runs only in v1 shape (hardcoded `docs/features`, `backend/src/domain`, `backend/src/use-cases` — none exist in v2) (E2) | Yes — real drift-audit → migration plan keyed to SPEC IDs (E2) | **GO** | build-from-owned (owner v1; retarget owed) — **Phase 2** |
| v1 **pattern-library** (LAYERING-REFERENCE, DEPENDENCY-RULES, FOUNDATIONS, TESTING/OBSERVABILITY-ALIGNMENT) | v1 `implementation/domainspec/architecture/pattern-library/*` (E2) | **No** — docs-only, not in IMPORT-MANIFEST, no v2 dest row (E2) | Yes — real v1 content; DEPENDENCY-RULES ships no tool (recommends ESLint/arch-tests) (E2) | **GO** | build-from-owned — "single largest build-from-owned opportunity not yet triaged" (E2 cross-cutting) — **Phase 2** |
| **Dependency rule written as a tree observation** treated as a binding gate | (v2 tree; E1 blocked list) | n/a | **No** — "adding a dependency rule as observation" does NOT make it enforceable (E1 §2 :153-163) | **KILL** | tautological — observation ≠ authority (C14 :304-307). *The underlying DEPENDENCY-RULES.md doc is build-from-owned above; only the observation-as-gate collapses.* |

### COMPOSABILITY

| candidate | owner (precedent) | witnessed? | sound? | verdict | use-mode |
|---|---|---|---|---|---|
| **`validate-code-tags.ts`** — endpoint-signature half of C11 | v1 → v2 `impl/governance/tags/tools/…`, **imported byte-identical — retarget NOT applied** (S1 diff); anchors owed (G2) | **Yes** `tags:validate` (runtime present), but **vacuous** — no tagged v2 impl code → empty `code-tags.json` (E3 S3; S2) | Yes — reads edge-law **dynamically** via `parseRelationshipRules` (lib/code-tag-rules.ts:67-117); CT-004:396, CT-006:424, CT-010:226. **Two defects gate trust** (waivers stale; `docs/features` anchor) (E3 S3) | **GO** (after defect-clear) | already-deployed |
| **`check-code-tag-composability.ts`** | v1 → v2 same, imported-verbatim (E2) | **Yes** `tags:composability` NOW (runtime present) (E2) | **No as-is** — frozen 9-rule TS array (lines 27-109) duplicates a subset of RELATIONSHIPS's 29 edges; **disagrees with the dynamic sibling** → two edge-truth sources (E3 W2) | **GO** (owner exists) | build-from-owned — **refactor to `parseRelationshipRules` (Phase 1)**; full trust Phase 2 (dep DS-D2) |
| tag toolchain **extract / validate / drift** + lib + adapters {js,js-like,py,ts} | v1 → v2 `impl/governance/tags/tools/`, imported-verbatim (E2) | **Yes** `tags:extract/validate/drift` NOW (runtime present) (E2) | Yes (drift caveat → C7 row below) | **GO** | already-deployed |
| **`validate-doc-links.ts`** — C9 Link & Import Integrity | v1 → v2 `impl/tools/…`, imported + 1-line retarget (E2; E3 S4) | **Yes** `validate:docs` NOW (runtime present); low value (only `spec/features/sample`) (E3 S4) | Yes — **zero meta-type coupling → safest to hard-wire**; one defect (`--only-changed` still filters `docs/features`, line 228) (E3 S4) | **GO** | already-deployed |
| **`compare-code-tag-drift.ts`** — C7 Convergence-as-Trend | v1 → v2, imported-verbatim (E2); **as-authority the concept is owned by `impl/spec/DRIFT-CONVERGENCE.md`** (S3) | Runs, but **no baseline** — C7 is "a trend over time, never a single passing check"; tool defaults `--features-root` to `docs/features` (E3 W3, constitution:84-90) | Runs; cannot measure a trend against a moving target = noise (E3 W3); C7-as-authority collapses into DRIFT-CONVERGENCE (S3) — honestly routed as WAIT | **GO** | build-from-owned — **Phase 2** (dep: stable edge-law + committed v2 baseline) |
| CODE-TAG-COMPOSABILITY-PATTERNS.md matrix + CODE-TAG-SCHEMA.md/.json + REMEDIATION | v1 → v2 `impl/governance/tags/…`, imported-verbatim (E2) | **Yes** — machine-checkable JSON schema; docs paired to the runnable checkers (E2) | Yes | **GO** | already-deployed (candidate docs / observation, not authority) |
| **Badge "C11 done / satisfied" via `validate-relationships.ts` alone** | (overclaim) | n/a | **No witness** — "no tool today checks feature-pack **declared-relation** endpoint signatures against the edge-law" (E3 S5, constitution:122-129) | **KILL** | no-witness for the signature half — the demotion E3 mandates: label-pass, silent on signatures |

### UNIFORMITY

| candidate | owner (precedent) | witnessed? | sound? | verdict | use-mode |
|---|---|---|---|---|---|
| **`validate-content.ts`** — meta-type SHAPE conformance | v2 net-new `impl/tools/validate-content.ts` (parsing modeled on `validate-relationships.ts`) (E2; E3 S2) | **Yes** `validate:content` NOW (runtime present); 151-line test + 28 ok/bad fixtures `impl/spec/__fixtures__/mt/*` (E2) | Yes — **data-driven off `spec/meta-types/**/*.schema.yml`**, resilient to churn by construction (E3 S2) | **GO** | already-deployed |
| **`instances.ts validate`** — structured-instance conformance | v2 net-new `impl/tools/instances.ts` (E2; E3 S2) | **Yes** `instances:validate` NOW (runtime present); 14 generated files on disk, 50-line test (E2) | Yes — data-driven. (`instances generate` is a **write/authoring path, NOT a gate** — E3 W6) | **GO** | already-deployed (`validate` only) |
| **Engine `lint` / `runLint`** — C10 Spec Completeness | **v1-imported engine** (S1), owner `implementation/domainspec/tools/test-derivation-engine/` → v2 `impl/test-derivation-engine/src/cli.ts:403-428`, script `lint:docs`; `engine:lint` already wired with explicit path (S2) | **Yes, NOW** — runtime present, explicit-path wiring committed (`… lint spec/features/sample`) (E3 S1; S2) | Yes — reports non-canonical tables + `needs-formal` cells, exit 4 = exactly C10's method (constitution:107-114). **Do NOT use bare-name default** (`featureDirFor` cli.ts:69-76 = v1 poker path) (E3 S1) | **GO** | build-from-owned (owner v1; runnable now, vacuous until real feature pack) |
| Per-meta-type **schema criteria** (14 `.schema.yml` + `.md`) | v2 net-new `impl/spec/meta-types/{structural,behavioral,connective,lifecycle}/*` (E2) | **Yes** — 14 files on disk, consumed by the checkers above (E2) | Yes — net-new against v1 TAXONOMY groupings. Caveat: **SCHEMA-CONSTITUTION format binding (delta D2) still pending** (REFRESH-2026-07-02.md) — format churn = data migration, not code rewrite (E3 S2) | **GO** | already-deployed (data layer) |
| **TAXONOMY** baseline (24 meta-types) + CODE-TAG-SCHEMA (cross-language uniform annotation) | v1 → v2 `impl/spec/TAXONOMY.md`, imported-verbatim, reformulation-pending Batch 1 (E2) | **Yes** as the contract; docs-only (E2) | Yes | **GO** | already-deployed (candidate contract / observation) |
| **Engine `roundtrip` / `self-check`** — L0 falsification gate | **v1-imported engine** (S1), owner `implementation/domainspec/tools/test-derivation-engine/`; v2 `cli.ts` (E3 W6) | **No** — `featureDirFor` (cli.ts:69-76) hardcodes v1 poker path; roundtrip/self-check always use it; parser + δ-rules were **typed stubs** at import (README:23-25) (E3 W6) | Yes (v1-imported engine — S1) | **GO** | build-from-owned (owner v1) — **Phase 2** (dep: real v2 feature pack + non-stub δ-rules = OQ-1 build-proof, OPEN) |
| **UI-meta-type / `binding` uniformity** enforcement | (gap — no owner artifact) | **No** — 11 UI meta-types (Page…State Indicator) have **no `.schema.yml`**; `binding` is load-bearing in cross-layer edges + TAXONOMY (UI Connective) but unschematized (E2 uniformity gap; E3 W4) | n/a — nothing to be sound about | **KILL** (as a now-mechanism) | no-witness — no schema exists to check against; blocks W4 below. Building the schemas is a future build-from-owned once `binding` formalizes |

## (B) PHASED START-NOW / ADJUST-LATER ENFORCEMENT PLAN

**Correction (S2 disk-verify, loop-1): the runtime is ALREADY in place — the plan does NOT
sit behind a tsx unlock.** `impl/package.json` exists and is committed (HEAD `22bf33b1`),
declaring `tsx ^4.7.0` + all P0/P1 scripts (lines 16–28); `impl/node_modules/.bin/tsx` →
tsx@4.22.4 is installed; `engine:lint` is already wired with an explicit path
(`… lint spec/features/sample`). E3's premise ("nothing in v2 can execute a `.ts` today; the
only blocker is a missing tsx loader") is **falsified**. So **Phase 0 is runnable NOW** — the
remaining constraint is **inputs (real feature packs / tagged code), not runtime**. The
checkers execute today but are **vacuous until real inputs exist** (only `spec/features/sample`
+ the meta-type fixtures are present).

### Phase 0 — runnable NOW (gated only by the two must-fix defects + real inputs)

**Gating pre-conditions (do FIRST; nothing in Phase 0 is trustworthy before these):**
- **G0 — DONE (S2).** The tsx `package.json` at `impl/` is committed (HEAD `22bf33b1`) and
  installed (tsx@4.22.4); the P0/P1 scripts are wired. **No action needed.** What remains
  OPEN in constitution OQ-1 is a *green build-proof on a real feature pack*, not the runtime.
- **G1 — reset `code-tag-waivers.yaml` to `waivers: []`.** v2 still carries v1's **4** live
  AEO entries (2×CT-004, 2×CT-006, `expiresAt: 2026-12-31`; S1/S2 counted 4, not the 3 E2
  stated); manifest Batch-2 ordered the reset, **not done**. Any v2 run silently suppresses
  CT-004/CT-006 for nonexistent paths = pre-laundered violations (E3 S3; E2 STALE note; S1/S2).
  **Gating** — do before trusting S3/P0-3.
- **G2 — fix the `docs/features`→`spec/features` anchors.** `normalizeSpecPath`
  (`validate-code-tags.ts:749-758`), `getChangedMarkdownFiles` (`validate-doc-links.ts:228`),
  and `compare-code-tag-drift.ts --features-root` default all anchor on the v1 literal;
  under v2 they degrade silently (CT-017/018 → full-path compare) (E3 S3/S4/W3).

**Phase-0 handles** *(each: what it enforces · cav2 promotion step it satisfies ·
owner-promotion still owed).* E1 guardrail applies to all: these are candidate handles
that **produce evidence**, not authority.

- **P0-1 (E3-S1, HIGHEST) — engine `lint`/`runLint`** (cli.ts:403-428, `lint:docs`).
  *Enforces:* C10 spec completeness (non-canonical tables + `needs-formal` cells, exit 4;
  constitution:107-114) (E3 S1). Run with an **explicit path arg**, never the bare-name
  default. *cav2 step (E1 lifecycle ARCHITECTURE-KNOWLEDGE-GOVERNANCE:62-74):* "exercised
  in domain → evidence set." *Owes:* owner-promotion via constitution-governance before
  C10 binds — candidate handle, not authority (E1 :304-307).
- **P0-2 (E3-S2, HIGH) — `validate-content.ts` + `instances.ts validate`.** *Enforces:*
  meta-type SHAPE/uniformity, **data-driven off `spec/meta-types/**/*.schema.yml`** so
  edge-independent and churn-resilient (E3 S2). *cav2 step:* exercises the uniformity
  candidate + produces its evidence set. *Owes:* SCHEMA-CONSTITUTION format binding
  (delta D2) still pending (E3 S2); owner-promotion.
- **P0-3 (E3-S3, HIGH — only after G1+G2) — `validate-code-tags.ts`.** *Enforces:* the
  endpoint-signature half of C11, edge-law read **dynamically** (E3 S3). Runs but
  **vacuous** until v2 impl code is tagged. *cav2 step:* candidate exercised on fixtures.
  *Owes:* real tagged code + owner-promotion.
- **P0-4 (E3-S4, MEDIUM) — `validate-doc-links.ts`** (C9). *Enforces:* frontmatter deps /
  includes / links / anchors resolve; **zero meta-type coupling → safest hard-wire**
  (E3 S4). *cav2 step:* exercises the C9 candidate. *Owes:* owner-promotion.
- **P0-5 — tag `extract`/`validate` toolchain** (X3), supporting P0-3 (E2).
- **Demotion (mandated):** `validate-relationships.ts` (E3-S5) may run in Phase 0 as the
  **label half of C11 ONLY**. Do **not** badge "C11 done" — no tool checks feature-pack
  declared-relation endpoint signatures (E3 S5, constitution:122-129).

### Phase 1 — small wiring

- **P1-1 — per-tool default retargets** for the tools *not* on the G2 gate: the defaults
  are inconsistently half-migrated and "disagree on where they already point" (E3
  constraint section). Mechanical, low-risk.
- **P1-2 — refactor `check-code-tag-composability.ts` to read the edge-law
  dynamically** — replace the frozen 9-rule TS array (lines 27-109) with
  `parseRelationshipRules`, collapsing v2's **two disagreeing edge-truth sources** into
  one (E3 W2). Fix is cheap/known. *Owes:* DS-D2 edge verbs still moving (MT3 landed,
  `git 22bf33b1`) — the refactor removes the trap but composability enforcement still
  owes the **settled** edge-law before it can promote.
- (Skill retargets `domainspec-audit-layering`/`-alignment` are named here but their v2
  target dirs don't exist yet → they fall to Phase 2.)

### Phase 2 — WAIT list (after meta-types/edges settle) — each with its named dependency

- **W1 — C6 general unconstructible catalog.** *Dep:* meta-type formalism, actively moving
  today (`development/meta-type-formalization/research/2026-07-02-formalism-and-primitives/`:
  competing `formalism-minimal/-lean/-solver` + `verify-decidability.md`) (E3 W1).
  *Owes:* typed catalog-construction layer generalizing `containment.ts`, then
  owner-promotion. Declaring C6 enforced now is premature by definition (E3 W1).
- **W2 — full-trust composability binding-edges.** *Dep:* DS-D2 edge verbs + endpoint
  signatures (E3 W2). (Phase-1 refactor removes the disagreement; trust waits on DS-D2.)
- **W3 — `compare-code-tag-drift.ts` → C7 convergence-as-trend.** *Dep:* stable edge-law +
  committed v2 baseline series (E3 W3, constitution:84-90).
- **W4 — any `binding`-touching enforcement** (CT-COMP-006/007; cross-layer
  `fetches/mutates/contracts/mirrors`). *Dep:* `binding`'s formalization — load-bearing but
  has **no `.schema.yml`** (E3 W4; E2 uniformity gap). Endpoint signature can change when
  it lands.
- **W5 — binding validators to specific C-numbers + the governance-file split**
  (`validation-/layering-/drift-governance-CONSTITUTION.md`). *Dep:* OQ-2
  (constitution:173-177) (E3 W5). Don't hard-code "validator X === Cn" or the C6↔C11
  cross-binding into CI until the split lands or you rewire twice. Note:
  `layering-governance-CONSTITUTION.md` is named as C6's split target but **does not exist
  yet** (E2).
- **W6 — engine `roundtrip`/`self-check` (L0 falsification gate).** *Dep:* a real v2
  feature pack + confirmation δ-rules are no longer typed stubs (README:23-25); this is
  OQ-1's build-proof, OPEN (E3 W6). `instances.ts generate` is authoring, **not** a gate.
- **W7 — import + triage the v1 pattern-library** into v2. *Dep:* IMPORT-MANIFEST triage —
  no v2 dest row exists (E2 cross-cutting). May begin as **inventory** anytime (E1
  authorizes inventory-building), but stays observation, never a gate, until owner-promoted.

**Guardrail restated for every phase item (E1 §3 → ARCHITECTURE-KNOWLEDGE-GOVERNANCE:140-152):**
each handle owes promotion through its named owner route — candidate→definition =
definitions-governance; candidate→constitution/invariant = constitution-governance;
candidate→architecture authority = CyberAlchemy authority model + architecture owner.
"architecture pattern" is not one of the nine authority kinds (E1 §2 → AUTHORITY-MODEL:61-72);
nothing in v2 has completed the path (E1 :182-190).

## (C) THE ONE-LINE ANSWER

The runtime is already in place (S2), so reset the stale waivers/anchors and **run the
data-driven, edge-independent checkers today** — engine `lint` (C10), `validate-content` +
`instances validate` (meta-type uniformity), `validate-doc-links` (C9) — against a first
real feature pack as **pattern-candidate handles that produce evidence, not authority**,
while deferring C6-unconstructibility, the composability edge-law, and C7-drift until the
meta-types and edges settle and each candidate is owner-promoted; the binding gain is not a
missing tool or runtime but **authoring a real v2 feature pack + tagged code** to make the
already-runnable checkers non-vacuous.
