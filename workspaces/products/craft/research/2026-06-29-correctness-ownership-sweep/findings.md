# findings.md — owned-vs-net-new map (cited synthesis)

Dispatch: `2026-06-29-correctness-ownership-sweep` (research) · final_approver: parent (accepted)
Every load-bearing claim cites the collected return in `research.md` (A=Explorer-A, B=Explorer-B,
S=Skeptic) and, where re-verified, the on-disk artifact. claim ≤ proof throughout.

## One-line answer (to the dispatch goal)

**The repo genuinely OWNS the honest-labeling *discipline* (claim-register vocabulary, the
necessary-not-sufficient scope fence, misuse-warned definition cards) plus a thin layer of
decidable/toy *structural* witnesses — and that discipline IS the Kodamai wedge. It does NOT yet
own any *behavioral-correctness* or *concurrency/attestation* guarantee that survives scrutiny:
those collapse today to content-hashing or a hand-scripted transcript, or are net-new for everyone
(Kodamai included).**

## Verdict matrix

| candidate | owner (cite) | witnessed? | sound? | verdict | use-mode |
|---|---|---|---|---|---|
| A1 σ-edge graph/compensation check | `dcb-saga-correctness/toy-harness/saga-spec.ts:203` (S) | yes — toy, fires on inputs | yes | GO | build-from-owned |
| A2 behavioral saga witness | `…/saga-spec.ts:254,321` (S) | **partial** — 1/3 assertions a real negative witness; 2 tautological (empty-trace lying run passed) | no | GO (partial) | build-from-owned (negative-witness leg is the seed) |
| A3 DCB freshness guard | `…/saga-spec.ts:402` (S + parent P8 re-read) | yes **as content-hash only** — `dcb→hash` flip verdict-invariant; mechanism read only for a reason string (L427/433-435) | no (DCB claim) | GO as content-hash / net-new for DCB edge | build-from-owned (hash wiring) |
| A4 non-rerunnable fact-class | `…/saga-spec.ts:27` + fixture (S) | no — relabel | no | prose-only | (subsumed by A3) |
| A5 edge-signature validation | `…/saga-spec.ts:165` (S) | yes — clean | yes | GO | build-from-owned |
| A6 AcceptSpecCodeCorrectnessClaim | `dcb-correctness/SYNTHESIS.md, HANDOFF.md` (S) | no — designed | — | designed-not-wired | build-from-owned (design) / net-new code |
| A7 spec→test engine | `test-engine/HANDOFF.md` (S: only file; "not executed") | no | — | designed-not-wired | net-new code |
| A8 formal model-check (TLA+/Alloy/Lean) of saga | precedent-clean; `alloy-tla CLAIM-LEDGER R1/R2` unvalidated (S) | no | — | prose-only | novel-attempt / precedent-clean |
| B1 five-label proof vocabulary | `alloy-tla/CLAIM-LEDGER.md C3/C8` + `DISTILL.md` (B,S) | yes — applied per-row | yes | GO | **build-from-owned (the wedge)** |
| B2 P8 necessary-not-sufficient fence | `domainspec-language/…/DEPENDENCY-MAP.md H-3` + `CONVERGENCE-MODEL-DECISION DEC-CONV-01` (B,S) | yes — defined-governed | yes | GO | build-from-owned |
| B3 M6 representability detector | `CATEGORICAL-FORMALIZATIONS.md` / `Richness.lean:85` (S ran `lake env lean --run`: 16-elt list, `native_decide`) | **yes — executed** (detector); fullness-tie open | detector sound; verdict net-new | GO (detector) | build-from-owned (detector) + net-new (grading) |
| B4 Definition Cards w/ misuse warning | `alloy-tla/DEFINITIONS.md` (B,S) | yes | yes | GO | build-from-owned |
| B5 DCB validator-vs-freshness split | `dcb-correctness/SYNTHESIS.md` (B,S) | yes (definitional) | yes | GO | build-from-owned |
| B6 claim≤validation auto-verdict gate | `…/02-claim-proof-gate.md` (B,S) | no — no verdict-computing predicate | — | prose-only | net-new |
| B7 subset-rule Pass/Flag/Block gate | `…/02-claim-proof-gate.md` (named open) | no | — | aspirational | net-new |
| B8 "model-checked ≠ verified" predicate | `CLAIM-LEDGER C9` operator-reading (B,S) | no gate | — | prose-only | net-new (cheap) |
| B9 contract/schema separation predicate | `DEPENDENCY-MAP D1-3` ("nothing in Report.lean checks this") | no — MISSING | — | designed-not-wired | net-new |

## The owned-vs-net-new split (the deliverable)

**OWNED & genuinely witnessed (build-from-owned, at honest register):**
1. **Honest-labeling discipline** — five-label proof vocabulary (B1), the P8 necessary-not-sufficient
   scope fence (B2), misuse-warned Definition Cards (B4), the DCB validator-vs-claim-freshness split
   (B5). *This is the competitive wedge and it is real and self-consistent.*
2. **Decidable/toy structural witnesses** — the M6 representability **detector** executed under Lean
   (B3), σ-edge graph + edge-signature validation (A1/A5), and the negative-witness leg of the saga
   harness (A2-partial). Honestly bounded; no proof claim.
3. **Content-hash freshness wiring** (A3, *as a content hash* — not as DCB).

**NET-NEW (precedent-clean, or collapses-today → genuine build surface):**
1. **Concurrency/TOCTOU acceptance discrimination** — the DCB edge a content-hash cannot do
   (`PROOF-OBLIGATIONS.md:59`). Repo owns **zero**; A3/A4 prove the toy never touches it.
2. **Auto-computed claim≤proof verdict** — a predicate that *computes* Pass/Flag/Block from
   claim-vs-evidence (B6/B7). Only prose + an existence-gate rename exist.
3. **M6 ⇒ not-full grading** — wire the STUB `gradeP4Ambiguity` to the already-executable
   `m6Witnesses` + the representability theorem (B3: detector owned, verdict net-new).
4. **Trace-derived behavioral witness** — replace A2's two tautological literal-driven assertions
   with trace-derived outcomes (seed: A2's genuine negative-witness leg).
5. **Spec→test engine + AcceptSpecCodeCorrectnessClaim** — designed-not-wired, no code (A6/A7).
6. **Contract/schema separation validator predicate** — MISSING (B9); the adequacy predicate.

## P8 trust-but-verify (parent)

Re-read `saga-spec.ts:402-445` directly: confirms S's A3 verdict — `current.marker !== entry.marker`
over `hashFact`; `entry.mechanism` consumed only to pick a reason string; both branches return
`rejected`. `dcb→hash` is verdict-invariant. **A3 collapse-to-content-hash accepted.** S's other
hand-runs (A2 empty-trace, B3 Lean execution) taken as reported (P8 spot-check scoped to the single
most consequential claim).

## Connection to the Kodamai competitive read

This **confirms** `[[kodamai-smithe-correctness-layer-synthesis]]`: neither we nor Kodamai own a
behavioral/concurrency verifier. Our genuine differentiator is **owned honest-labeling discipline +
executed (bounded) witnesses + a self-caught-overclaim trail** (the 2026-06-17 red-team demotion, A) —
artifacts Kodamai's corpus does not show. "Provably constrained" we can honestly claim = the decidable
σ-edge/graph checks + content-hash freshness, *labeled at their true register*. "Provably correct"
(behavioral/concurrency) is net-new for everyone. The wedge is **honesty + demonstration**, not a
verifier we possess — exactly the prior synthesis's verdict, now backed by an executed sweep.

## Close

`exit_reason: resolved` — parent accepted after the P9 citation check + P8 spot-verify. A found owner
is a WIN: most "owned" candidates are build-from-owned; the typed negatives (A3 DCB-edge, A2 two
assertions, B6 gate) are demotions, not kills — they name the exact net-new surface.
