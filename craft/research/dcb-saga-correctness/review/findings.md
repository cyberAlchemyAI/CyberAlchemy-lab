---
title: DCB Saga Correctness Review — Findings (verified change requests)
dispatch_id: 2026-06-17-dcb-saga-correctness-review
dispatch_type: review
status: verified
date: 2026-06-17
final_approver: auditor (Lakatos, Imre)
---

# Findings — verified change requests

Red-team of the completed `dcb-saga-correctness` research package. Severity:
**CRITICAL** breaks the system / flatly contradicts governing law; **MAJOR**
load-bearing overclaim, functional gap, or tautological check; **MINOR** wording
/ stale pointer. Verdict per artifact: **FIX** iff ≥1 surviving CRITICAL/MAJOR.
Every finding cites its attack return (`attacks.md`) and quotes the artifact
(claim ≤ proof).

**Verification:** every factual claim was empirically re-confirmed by running the
harness in an isolated copy (Turing, Node 22.12 — byte-identical reproduction;
`mechanism` dcb→hash flip is verdict-invariant; id-only change still rejects) and
deductively scrutinised against the governing gates (Gödel). The deductive pass
**demoted the headline from CRITICAL to MAJOR** and demoted M4/M5 to MINOR —
those demotions are adopted here (claim ≤ proof; the review holds itself to its
own discipline). No CRITICAL survives.

## Headline (verified)

The package's **load-bearing conclusion outran its own evidence — a MAJOR
overclaim, not a law breach.** All three lenses converged and both verifiers
confirmed: the toy's freshness check is a plain content-hash; the declared
`mechanism` (`hash` vs `dcb`) gates only a *reason string*, never detection
(empirically: re-tagging the waiver dcb→hash leaves the verdict byte-identical).
The toy therefore witnesses DCB *wiring*, not DCB *value* — it exercises nothing
a content-hash cannot, and the concurrent-acceptance-race obligation it would
need (`PROOF-OBLIGATIONS.md:59`) is unimplemented. Consequently the `SYNTHESIS`
verdict's "freshness **and concurrency** guard" clause and the `borrow-carefully`
DCB justification assert more than the bounded witness shows (P10 claim ≤ proof).

What the package gets *right* (survived attack): it breaks **no** taxonomy/
process law (g05 honored — `orchestrates` strain recorded as residue, nothing
mutated); the `AcceptSagaProofFreshnessClaim` command name correctly enacts the
g02 proof-vs-freshness split; it is consistently framed as a *bounded witness,
not a proof*; it reproduces byte-for-byte. Its **process honesty is high** — the
defect is that the verdict's prose and the toy's DCB framing overreach the code,
which the package's own Tension 2 ("a DCB toy without non-rerunnable evidence is
over-built") and gate g03 anticipate.

---

## `toy-harness/saga-spec.ts` — verdict: **FIX**

| # | evidence | severity | proposed fix |
|---|---|---|---|
| C1 | `acceptSagaProofFreshnessClaim` (L402-445): the only detection is `current.marker !== entry.marker` (L426) per entry, `marker = sha256(stableStringify(fact))`; `entry.mechanism` is read only at L427 to choose the reason string; both branches return identical `{status:"rejected",...}`. **Empirically confirmed**: dcb→hash flip is verdict-invariant. So `dcb` does no detection work content-hash cannot. | MAJOR | Make `dcb` facts exercise a capability content-hash cannot (concurrent-acceptance race per `PROOF-OBLIGATIONS.md:59`, a version/append-position marker, or a re-derivation-differs check) so flipping `mechanism` changes the verdict — **or** carry the SYNTHESIS S1 downgrade. |
| M2 | Assertion `completed-compensatable-steps-compensated` (L325-335): `expectedCompensations` is the *same* filter expression used to build `run.compensationsRun`; it compares a value to itself. **Empirically confirmed**: a `trace:[]` run still passes. | MAJOR | Assert the *trace* contains a `kind:"compensation"` event per expected op, in reverse order. |
| M3 | `enumerateRuns` (L254-318) is a hand-scripted transcript: `acceptedSuccess:false`, `terminalState:"compensatedFailure"` are author-set literals (L313-314), so assertion `success-not-accepted-after-shipment-failure` tests a hardcoded constant, not executed behavior. | MAJOR | Derive `acceptedSuccess`/`terminalState`/`compensationsRun` from trace outcomes. |
| m1 | Assertion `missing-compensation-detected` (L336-363) fires from the `!compensationOperation && !terminalFailurePolicy` rule (L213) — a step with no compensation but a terminal policy yields 0 errors; it detects "neither," not "missing compensation." | MINOR | Reword the assertion detail, or add a distinct check for a completed step lacking compensation even with a terminal policy. |
| m2 | `hashFact` (L199-201) hashes the whole `Fact` incl `id`. **Empirically confirmed**: changing only the waiver `id` with identical decision content still rejects. | MINOR | Hash only `content`, or document that the marker covers fact identity, not just decision semantics. |

## `toy-harness/order-fulfillment.fixture.ts` — verdict: **FIX**

| # | evidence | severity | proposed fix |
|---|---|---|---|
| M1 | The lone `HumanWaiverApplied` "non-rerunnable" fact (L215-252) differs from the five deterministic facts only by `mechanism:"dcb"`; `currentFactsAfterStaleWaiver` (L239-252) edits its content and is caught by the same hash diff. This fails the package's own standard `PROOF-OBLIGATIONS.md:94` ("deterministic facts handled by hash rather than wrapped in DCB unnecessarily") — the waiver is wrapped in DCB without DCB doing distinguishing work. | MAJOR | Give the waiver a genuinely non-content-hashable freshness property, or a concurrent second claim a snapshot hash cannot adjudicate; otherwise re-tag it `hash` and accept the downgrade. |

## `SYNTHESIS.md` — verdict: **FIX**

| # | evidence | severity | proposed fix |
|---|---|---|---|
| C1↑ | "DCB is feasible for saga correctness only as a freshness **and concurrency** guard around accepted proof evidence" (L9). The toy exercises no concurrency path and no detection content-hash lacks; the "concurrency guard" clause and the DCB-value basis of `borrow-carefully` exceed what the bounded witness demonstrates. | MAJOR | Downgrade to "content-hash freshness *wiring* witnessed; discriminating DCB value (concurrency / non-rerunnable) **asserted-not-shown**, pending the C1/M1 fix," and propagate to `HANDOFF.md` + regenerated toy-run results. |
| m3 | The verdict header (L9-13) front-loads "DCB ... for saga correctness" before the "only as a freshness guard" qualifier. | MINOR | Lead with the object DCB acts on (freshness of accepted saga-correctness evidence). |

## `toy-harness/run-toy.ts` — verdict: **KEEP** (MINOR fixes)

| # | evidence | severity | proposed fix |
|---|---|---|---|
| M4 | Freshness claim id `order-fulfillment-saga-proof-c1` (L93) embeds `-proof-`, in tension with SYNTHESIS's "the name matters." **Demoted to MINOR** (Gödel): the g02-bearing *command* name `AcceptSagaProofFreshnessClaim` is correct; the residual `-proof-` is an internal claim-id wording issue. (Turing: the id lives in `toy-run-result.json` `claimId`, not `toy-run-result.md:14`, which renders the command.) | MINOR | Rename to `order-fulfillment-saga-proof-freshness-c1` (or `...-acceptance-c1`). |
| M5 | The harness can only succeed: it throws unless `behavioral_witness==="pass" && freshness_claim==="rejected" && command==="AcceptSagaProofFreshnessClaim"` (L110-115); `command` is a hard-coded literal (`saga-spec.ts:393`) and the rejection is forced by the fixture's content edit, so no input fails. **Demoted to MINOR** (Gödel): this is the *intended* single bounded witness; its substantive teeth (no DCB-discriminating path, tautological assertions) are already counted in C1/M2/M3 — keep as a noted weakness, not a separate MAJOR. | MINOR | Add a control case that can fail (e.g. an unchanged read-set that must `accept`), so the witness is falsifiable. |

## `toy-run-result.md` / `toy-run-result.json` — verdict: **FIX (derived)**

Generated outputs; carry the `-proof-` `claimId` (M4) and the "DCB guards
acceptance freshness" framing (C1). Regenerate after the upstream fixes; do not
hand-edit.

## `PROOF-OBLIGATIONS.md` — verdict: **KEEP** (note)

Correctly *lists* the concurrent-acceptance-race obligation (L59) and the
"don't wrap deterministic facts in DCB unnecessarily" rule (L94) — the defect is
the harness ignoring these, not the doc. m5: `ProofVerdictIssued | ... DCB`
(L78) risks reading as "DCB issues the verdict" — MINOR relabel to "receipt of
externally-issued verdict + DCB freshness."

## `LANES.md`, `TOY-SAGA-SCENARIO.md`, dispatch JSON — verdict: **KEEP** (note)

m4: research-question artifacts retain pre-split "prove" framing (`LANES.md:9`,
dispatch objective) — MINOR one-line clarifying note. `TOY-SAGA-SCENARIO.md`
states the g03 downgrade rule the toy then ignores — context for C1.

## `HANDOFF.md`, `RESIDUE.md`, `MODEL-CHOICE.md`, `TAXONOMY-EDGE-FRAME.md`, `LANE-RECEIPTS.md` — verdict: **KEEP**

Governance-clean: g05 honored (no taxonomy/relationship/validator mutation;
`orchestrates` strain recorded as residue), witness-not-proof discipline
consistent. `HANDOFF.md` inherits the C1 downgrade once `SYNTHESIS.md` is fixed.

---

## Change-request list (ordered by severity)

**No CRITICAL.** 4 MAJOR, 7 MINOR.

1. **[MAJOR] C1 — Resolve the DCB-vs-content-hash overclaim.** Either (a) make
   the `dcb` mechanism do work content-hash cannot — implement the
   concurrent-acceptance-race obligation (`PROOF-OBLIGATIONS.md:59`) / a
   version/append-position marker / a re-derivation check — so `mechanism`
   gates detection (`saga-spec.ts:402-445`); or (b) downgrade the `SYNTHESIS.md:9`
   verdict to "content-hash freshness wiring witnessed; DCB value
   asserted-not-shown," dropping the unexercised "concurrency guard" clause, and
   propagate to `HANDOFF.md` + regenerated toy-run results.
2. **[MAJOR] M1 — De-decorate the non-rerunnable waiver** (`fixture.ts:215-252`):
   make it genuinely non-content-hashable, or concede hash-equivalence per its
   own `PROOF-OBLIGATIONS.md:94` standard.
3. **[MAJOR] M2 — Make assertion 2 non-circular** (`saga-spec.ts:325-335`).
4. **[MAJOR] M3 — Derive run outcomes from the trace** (`saga-spec.ts:254-318`).
5. **[MINOR] M4, M5, m1–m5** — `-proof-` claim-id rename; add a falsifiable
   control case; assertion-3 label; whole-fact hashing; verdict-header phrasing;
   "prove" framing in question artifacts; `ProofVerdictIssued`+DCB labeling.

Applying these fixes is a separate follow-up act (a future task-session or a
`max_loops` re-run), not part of this review. The substantive next step is C1:
the package should either earn the DCB claim with a concurrency/non-rerunnable
path, or downgrade the verdict to what the content-hash toy actually proves.

---

## Dispatch close

- **dispatch_id:** `2026-06-17-dcb-saga-correctness-review` · **exit_reason:** `resolved`
- **final_approver:** auditor (Lakatos, Imre) — **ACCEPTed** (coverage complete
  across all three lenses; refuted CRITICAL + two refuted MAJORs verified as
  genuinely demoted; citations check against source).
- **agents_spawned:** 9 — explorer 6 (3 attackers + 3 robot_talks confrontation),
  skeptic 2 (verifiers), writer 0 (synthesizer role performed by the parent
  strategist), auditor 1; loops_used 1; plus 2 check-tension gate agents
  (infrastructure). `SendMessage` was unavailable in this harness, so the
  robot_talks final positions were re-grounded as fresh spawns rather than
  in-context continuations.
- **Verification:** all factual findings empirically re-run (Turing, byte-identical
  reproduction + dcb→hash invariance test) and deductively scrutinised (Gödel),
  which demoted the headline CRITICAL to MAJOR and M4/M5 to MINOR — adopted here.
