---
node_type: research
role: synthesizer
subject: DomainSpec v1 → v2 import triage
agent: "Spivak, David — synthesizer / adjudicator"
dispatch_id: 2026-06-29-domainspec-v1-import-triage
dispatch_type: research
date: 2026-06-29
discipline: claim <= proof; one verdict per capability; found owner = build-from-owned, never a kill
persisted_by: parent (synthesizer .md write was harness-blocked; content returned verbatim and P8-verified against the cited inventory)
inputs:
  - offers-scout.md  vs  offers-skeptic.md
  - drift-scout.md   vs  drift-skeptic.md
  - audit-scout.md   vs  audit-skeptic.md
  - layering-scout.md vs layering-skeptic.md
---

# Findings — DomainSpec v1 → v2 import triage

## One-line answer

v2 is overwhelmingly **build-from-owned, not import**: of the de-duplicated capabilities,
**only 3 are genuine IMPORTs** (the deterministic spec→test executor, its `obligation_key`
identity seam, and the DCB concurrency/TOCTOU discrimination edge); everything else is
REFORMULATE over a live v1 owner or DROP on hard-boundary grounds — and the moat is
**attestation + governance-data + vertical**, NOT the engine algorithm and NOT Lean (both
are overclaims the canonical machine-map explicitly inverts).

## Master triage table (32 de-duplicated rows) — count split: **3 IMPORT · 25 REFORMULATE · 4 DROP**

| # | Capability | Area | Verdict | v2 target surface | Existing owner (cite) | Witnessed? | One-line reason |
|---|---|---|:--:|---|---|:--:|---|
| 1 | Deterministic spec→test **executor** (parse→δ→key→emit) | offers | **IMPORT** | v2 engine seed; `src/rules/` private | `tools/test-derivation-engine/` (offers-scout C2; audit-skeptic C4; layering-skeptic C5) | partial (L0 PASS on `financial-settlement`; 2 blockers) | Real net-new code w/ passing L0; carry with blockers. claim≤proof: "wired, not finished." |
| 2 | `obligation_key` stable-identity seam | offers | **IMPORT** | drift/freshness coupling | `src/keys/` (offers-scout C3) | yes (impl+tested) | Drift-checkable identity coupling engine to correctness; carry explicitly. |
| 3 | DCB **concurrency/TOCTOU discrimination edge** | audit | **IMPORT** | net-new correctness edge | none — audit-skeptic C5b ("net-new for everyone, incl. Kodamai") | no | Genuinely absent; collapses to content-hash today. Label separately from freshness. |
| 4 | TEST-PIPELINE rule families (14+6) | offers | **REFORMULATE** | typed obligation-schema | `TEST-PIPELINE.md` (audit-skeptic C3; offers-skeptic T5) | yes (rules defined) | Owner exists; rules are the *spec the engine runs*, not the engine — don't re-import as executor. |
| 5 | Fail-closed `check`/round-trip gate | offers | **REFORMULATE** | PostToolUse hook | `src/roundtrip/` (offers-scout C5) | yes (L0 gate) | Owned + runs; v2 work is *wiring* (ASSIMILATION-TABLE A1), not a new gate. |
| 6 | ENGINE-FIRST split contract | offers | **REFORMULATE** | v2 governance axiom | `domainspec-generate-tests/SKILL.md:26-44` (offers-scout C7) | yes | Boundary owned as process rule; re-author as axiom; skill file is scaffolding. |
| 7 | UI/E2E rules 15–20 (LLM surface) | offers | **REFORMULATE** | free-path taxonomy | `TEST-PIPELINE.md:299-446` (offers-scout C8) | yes | Owned but assumes Playwright/UI-SPEC; reformulate sans app-runtime. |
| 8 | LLM-mediated test generator | offers | **DROP** | — | superseded per engine README (offers-skeptic T2; layering D5) | n/a | Explicitly superseded; re-import = downgrade (ASSIMILATION S3). |
| 9 | Full `domainspec-pipeline` orchestrator | offers | **DROP** | — | `domainspec-pipeline/SKILL.md` (offers-scout C6) | yes (live) | App-builder, not governance; presumes running project = adapter-line violation. |
| 10 | Code-tag extract/annotate | drift | **REFORMULATE** | evidence-ingest sensor | `governance/tags/` + `domainspec-tag-code` (drift-skeptic C1) | yes (`code-tags.json`) | **Scout→IMPORT; owner found→REFORMULATE.** Sharpen: endpoint-type vs 25 types. |
| 11 | Code-tag validate (schema+edge) | drift | **REFORMULATE** | endpoint-pair type gate | `validate-code-tags.ts` ~770L, in CI (drift-skeptic C2) | yes (wired) | Sharpen: endpoint-pair type-check (not string-match). |
| 12 | Drift detect (code→spec) + writeback | drift | **REFORMULATE** | extend owned emitter | `compare-code-tag-drift.ts` ~470L (drift-skeptic C3) | yes (4-error diff) | **Scout→IMPORT extraction/convergence; full owner found→REFORMULATE.** Writeback = ASSIMILATION B1; flag-only, never promotion write. |
| 13 | Composability enforcement | drift | **REFORMULATE** | PostToolUse hook | `check-code-tag-composability.ts` + test (drift-skeptic C4) | yes | Owned+tested; wire into fail-closed hook. |
| 14 | Waiver registry | drift | **REFORMULATE** | time-bound waivers | `CODE-TAG-WAIVERS.md` + `.yaml` (drift-skeptic C5) | yes | Owned; add auto-expiry + reviewed-by. |
| 15 | Convergence tracking (5 surfaces) | drift | **REFORMULATE** | v2 authority doctrine | `DRIFT-CONVERGENCE.md` (drift-scout C3; audit-skeptic C2) | defined (no sensor) | **Scout→IMPORT; doc is owner→REFORMULATE.** Carry doctrine; wire sensor. |
| 16 | Registry sync (spec→catalog) | drift | **REFORMULATE** | Ontology-A catalog sync | `domainspec-sync-registry` (drift-scout C5) | yes (live) | Re-target reader to ontology surface; writes index not status (proviso safe). |
| 17 | Promotion-status auto-write | drift | **DROP** | — | none — correctly absent (drift-skeptic C6) | n/a | HARD reject: violates write-authority proviso (Conant-Ashby re-fusion). |
| 18 | Alignment classify+remediate (4-class) | audit | **REFORMULATE** | feature conformance gate | `domainspec-audit-alignment/SKILL.md` (audit-scout CAP-A1) | yes (skill report) | **Scout→IMPORT; live skill owner→REFORMULATE.** Machine gate (B6) is *separate* net-new. |
| 19 | Lean audit collision method (7-axis) | audit | **REFORMULATE** | v2 collision-audit harness | `VLACHOPULOS/SMITHE-AUDIT.md` (audit-scout CAP-A2) | yes (2 examples) | Method owned; content physics-domain (Ont. B). Re-author for Ont. A. |
| 20 | Conformance triage (witnessed slice) | audit | **REFORMULATE** | v2 conformance baseline | `correctness-ownership-sweep/findings.md` B1/B2/B4/B5/A1/A5/A3 (CAP-A3) | yes (honest register) | **Scout→IMPORT; triage map is the owner→REFORMULATE.** Use as baseline, don't re-derive. |
| 21 | Honest-labeling discipline (5-label + P8) | audit | **REFORMULATE** | v2 claim-labeling authority | `CLAIM-LEDGER.md` + `DISTILL.md` + `DEPENDENCY-MAP` (audit-skeptic C6) | yes (per-row) | Kodamai wedge; carry unchanged. Quarantine "constrained"→"correct" w/o behavioral verifier. |
| 22 | Behavioral saga witnesses | audit | **REFORMULATE** | trace-derived assertions | `saga-spec.ts` A1/A5 (audit-skeptic C8) | partial (A2 2/3 tautological) | Clean legs carry; tautological = demotion not kill; replace w/ trace outcomes. |
| 23 | TAXONOMY.md 25-concept + layer law | layering | **REFORMULATE** | v2 Ontology-A axiom | `TAXONOMY.md` canonical (layering-skeptic C1; audit-skeptic C1; layering-scout C4) | yes (edge-sig runs) | **Scout→IMPORT; canonical owner→REFORMULATE.** Net-new = endpoint-pair predicate. |
| 24 | Edge Law / forbidden-edge guard | layering | **REFORMULATE** | endpoint-typed validator | `RELATIONSHIPS.md` + `validate-relationships.ts` (layering-skeptic C2) | yes (label check) | Net-new = endpoint-pair typing (forbidden = unconstructible). |
| 25 | Layer drift detection | layering | **REFORMULATE** | v2 enforcement detector | `domainspec-audit-layering/SKILL.md` §3 (layering-scout C1) | yes (live skill) | **Scout→IMPORT; live skill→REFORMULATE.** Re-anchor authority to v2 constitution. |
| 26 | Dependency-ordered migration plan | layering | **REFORMULATE** | remediation plan | `domainspec-audit-layering/SKILL.md` §5 (layering-scout C2) | yes (live) | Reference Ontology-A IDs, not feature-local SPEC.md. |
| 27 | ADLC L0–L7 map + gaps G1–G16 | layering | **REFORMULATE** | v2 coverage checklist | `ADLC-ALIGNMENT.md` (layering-scout C3) | yes (doc) | Re-author from v2 view; G-IDs as checklist (esp. G13, G16). |
| 28 | AXIOMS.md A1–A6 (adapter line A2) | layering | **REFORMULATE** | v2 invariant surface | `AXIOMS.md` (layering-skeptic C7; audit-skeptic C2) | yes (doctrine) | Authority all candidates measured against; carry as-is. |
| 29 | Observer / telemetry infra | layering/drift | **REFORMULATE** | sensor-loop upgrade | `run-async-observer.ts`, `OBSERVABILITY.md`, otel skills (layering-skeptic C4; audit-skeptic C9) | built, under-performing | Feedback loop open; finishing it = highest structural leverage (machine-map). |
| 30 | Write-authority proviso | cross | **REFORMULATE** | v2 hard invariant | `ontology-operationalization-...-synthesis` §decision-spine (audit-skeptic C10; drift-skeptic C6) | yes (invariant) | "Absence of the edge, not a relaxable policy." Its loss is a kill. |
| 31 | App-runtime concerns (CQRS, auth, RLS, agent state) | layering | **DROP** | — | none — correctly absent (layering-skeptic C8/D1–D4; ASSIMILATION S4–S10) | n/a | Below adapter line (Axiom A2); would force v2 to presuppose a running app. |
| 32 | "Lean kernel = the moat" framing | offers/layering | **DROP** (as moat) / cite-only | reference from governance spec | `domainspec-lean-formalization/` sorry=0 (offers-skeptic T4) | yes (sorry-free) | Lean owned, but importing *as the moat* inverts machine-map (zero cav2→Lean links). Cite as amplifier only. |

**The 3 genuine IMPORTs:** rows 1 (executor), 2 (obligation_key seam), 3 (DCB concurrency/TOCTOU edge).
**The 4 DROPs:** superseded LLM generator (8), out-of-layer pipeline orchestrator (9), promotion-status auto-writer (17, proviso), app-runtime concerns (31, adapter line) — plus Lean-as-moat (32) dropped *as a moat claim only*, retained cite-only.

## DO-THIS-NOW (ranked by leverage)

1. **Wire the fail-closed PostToolUse hook on `docs/features/**`** (rows 5/11/13) — ASSIMILATION-TABLE A1, the single highest-ROI move, zero capability gap, pure wiring; three memos converge on it.
2. **Finish the read-only observer loop** (row 29) — highest *structural* leverage per machine-map; read-only / propose-only, never observe-and-mutate.
3. **Add endpoint-pair type admissibility to Edge Law / tag validators** (rows 11/24) — forbidden edges from string-rejected to unconstructible; eliminates schema-drift (instance-drift stays net-new — do not overclaim).
4. **Activate the engine on a 2nd feature** (rows 1/4) — clear the two L0 blockers.
5. **Decide the attestation fire-point** (residue) — gated, never auto-applied.

## Free-vs-moat resolution

Adjudicated against the **canonical inventory**, not the memos' paraphrases. `machine-map-and-moat-synthesis`
is definitive: the moat is **"attestation + governance-data + vertical," with provability (cat-theory/Lean)
a conjectural amplifier, not the moat — the inverse of the original framing"** (card
`moat-inversion-attestation-not-provability`). `cav2-authority-and-determinism-synthesis` (lines 93–99,102)
sharpens it: determinism is *an optimization, not a necessity*; "the engine moat" is *defined* there as
**`cite + demonstrate results, never publish the algorithm`** — i.e. the engine's δ-rule algorithm in
`src/rules/` is a **withheld internal advantage, not the defensible wall**.
`attestation-capability-moat-mvp-synthesis` confirms the wall is real and partly built (L1 integrity-seal
BUILT + demonstrated; mechanism private; L2 intended-not-shipped).

**Final boundary (three-object split, not two):**
- **(a) FREE wedge** — the test-derivation METHOD/executor, the doc-schema surface syntax, and the
  drift/layering/validator tooling (no LLM, no moat material; publishable to public `arcanum/` as
  results-and-behavior).
- **(b) MOAT wall** — attestation + governance-data + vertical integration (L1 built, mechanism private,
  internal-only).
- **(c) withheld-but-not-the-wall** — the engine's δ-rule algorithm (`src/rules/`), kept private under
  cite-results-withhold-mechanism as an *optimization edge*, explicitly NOT the moat.
- **(d) AMPLIFIER, conjectural** — the Lean formal-proof lever, citeable on top of the wall, not the wall.

This makes the **offers-scout's "deterministic engine algorithm = moat" an OVERCLAIM** and the
**layering-skeptic's "Lean itself = the moat" an OVERCLAIM**; the offers-skeptic (Gödel) and audit-skeptic
(Russell) are sustained: method/executor = free wedge, attestation + governance-data = moat, Lean = amplifier.

## Residue (with owner)

- **G1/G2 spec→code-test seam + correctness-coupling** — owner: DomainSpec plan + `dcb-correctness`.
- **Attestation fire-point** in v2 promotion lifecycle — owner: commercialization decision-gate + plan owner (gated, never auto).
- **Two-ontologies boundary** — tag validation checks `TAXONOMY.md` (Ontology A) only; cav2-kind checks route to cav2's gate — owner: cav2 authority owner.
- **Provability-as-moat bet** — zero complete cav2→Lean links; live owner-decision — owner: commercialization decision-gate.
- **Schema-drift vs instance-drift scope** — v2 governs schema-level; instance-drift is net-new (B6/B7); do not claim v2 eliminates all drift — owner: DomainSpec plan owner.
