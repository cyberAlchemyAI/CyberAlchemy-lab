---
title: DCB Saga Correctness Review — Attacks (verbatim returns)
dispatch_id: 2026-06-17-dcb-saga-correctness-review
dispatch_type: review
status: attacks
date: 2026-06-17
---

# Attacks — verbatim attacker + confrontation returns

Review of the completed `dcb-saga-correctness` research package. Three attackers
swept distinct lenses (mechanics/correctness, fidelity/governance,
abuse-gaming/overclaim) over the whole corpus read-only, robot_talks. Below are
each attacker's **initial** position and **final** (post-confrontation) position
— both preserved for collapse detection (constitution P14).

Note on robot_talks: this was NOT a collapse. Tarski materially revised his
overall verdict under Spekkens's attack (no-law-breach → breached-on-claim);
Wisnesky independently re-derived Spekkens's central claim from source and
sharpened his own; Spekkens conceded the comparator is sound but held the
overclaim. Convergence by argument, not by deference.

---

## Attacker 1 — Wisnesky, Ryan (mechanics / correctness)

### Initial position

Reproducibility: PASS. With native `node --experimental-strip-types run-toy.ts`
(Node 22.12; `npx tsx` was broken in this env), the harness runs clean and
regenerates `toy-run-result.json` and `toy-run-result.md` **byte-for-byte
identical** to the checked-in files. All seven read-set markers, the rejection
reason text, trace, and assertion table match. Hashing (sha256 over
`stableStringify`) and freshness-rejection control flow are real and execute as
documented.

- **F1 — MAJOR — assertion 2 is circular (tests a value against itself).**
  `saga-spec.ts:325-335`. `expectedCompensations` is the *identical* filter
  expression `enumerateRuns` uses to populate `run.compensationsRun`; the
  assertion compares the same computation to itself — cannot fail by
  construction. A run with `trace: []` still passes. Fix: assert the *trace*
  contains a `kind:"compensation"` event for each expected op in reverse order.
- **F2 — MAJOR — `enumerateRuns` is a hand-scripted transcript, not a saga
  executor.** `saga-spec.ts:254-318`. `acceptedSuccess: false` and
  `terminalState: "compensatedFailure"` are author-set literals, not derived
  from `CreateShipment` failing. Assertion 1
  (`success-not-accepted-after-shipment-failure`) tests `!run.acceptedSuccess`
  against a constant hardcoded to `false`. Fix: derive
  `acceptedSuccess`/`terminalState` from trace outcomes.
- **F3 — MINOR — assertion 3 mislabels what it detects.** `saga-spec.ts:336-363`.
  The error fires from the `!compensationOperation && !terminalFailurePolicy`
  rule (line 213); removing the compensation but adding a `terminalFailurePolicy`
  yields 0 errors. It is a genuine negative witness but the claim overstates its
  specificity. Fix: reword to "step left with neither compensation nor
  terminal-failure policy."
- **F4 — MINOR — freshness rejection is driven by any fact field, incl `id`.**
  `saga-spec.ts:199-201,379-385`; `order-fulfillment.fixture.ts:239-252`;
  `toy-run-result.md:56`. `hashFact` hashes the whole `Fact`; changing only the
  waiver `id` (`-v1`→`-v2`) with identical decision content still yields
  `rejected`. Correct-as-freshness but weaker-than-narrated. Fix: hash only
  `content`, or state the marker covers fact identity not just decision
  semantics.

No CRITICAL. Survived: deterministic stable hash; the `key` vs `id` split works;
doc-vs-code numbers all match the regenerated output; `graph_witness:"flag"`
residue path reproduces. Net: freshness/hashing layer sound and reproducible;
the **behavioral witness is largely tautological** (assertions 1, 2 test
literals / self-equal computations).

### Final position (post-confrontation)

**(1) Spekkens's central claim — CONFIRMED, from the code.** The detection branch
(saga-spec.ts:426) `current.marker !== entry.marker` is applied to **every**
entry regardless of `mechanism`. `entry.mechanism` is consumed nowhere except
line 427 to choose the reason **string** (433-435); both branches return an
identical `{status:"rejected",...}`. Markers are `sha256(stableStringify(fact))`
in both `buildReadSet` and the acceptor — acceptance is byte-for-byte a
content-hash equality check. Re-tagging `dcb`→`hash` changes only a string. He
is right; no input flips the verdict on `mechanism`.

**(2) This revises my net.** I keep "SOUND" (correct content-hash freshness
gate, total over the read-set, byte-identical reproduction) but retract the
implicature that it witnesses anything DCB. Corrected: **sound-as-content-hash,
null-as-DCB.** Per g03 ("if all facts are deterministic, downgrade to content
hash") and the fact that every marker IS a deterministic hash, the toy meets its
own downgrade trigger; "DCB freshness win" is mechanically unsupported. **I
uphold Spekkens's CRITICAL.**

**(3) F1/F2 reinforce "can only succeed."** Two of three behavioral assertions
cannot fail on this fixture: assertion 1 reads a literal, assertion 2 is
reflexive; only assertion 3 runs live code, and per F3 it over-claims
specificity. Same structural pathology as the freshness side.

Findings kept: F1 (MAJOR), F2 (MAJOR), F3 (MINOR), F4 (MINOR). Cross-lens:
uphold Spekkens CRITICAL + MAJOR; push back on reading Tarski's "borrow-carefully
appropriate" as sufficient — the verdict is justified by a DCB demonstration
that does not exist in the code.

---

## Attacker 2 — Tarski, Alfred (fidelity / governance)

### Initial position

Read all docs, harness, results, dispatch JSON gates. Grepped every
prove/proof/correctness occurrence; checked submodule state for taxonomy/
relationship/template/validator/registry mutation. **Corpus strongly conformant**
— proof/freshness split explicitly defended, witness-not-proof repeated, g05
honored by recording `orchestrates` strain as residue.

- **F1 — MAJOR — `*-proof-*` identifier in the freshness claim contradicts the
  g02/naming verdict.** `run-toy.ts:93` → `toy-run-result.json` `claimId`,
  `toy-run-result.md:14`. `buildFreshnessClaim("order-fulfillment-saga-proof-c1",
  ...)` — the claim id for an `AcceptSagaProofFreshnessClaim` is literally named
  `...-saga-proof-c1`, reintroducing the "proves saga behavior" connotation the
  verdict ("the name matters") forbids. Fix: rename to
  `...-saga-proof-freshness-c1` or `...-acceptance-c1`.
- **F2 — MINOR — SYNTHESIS verdict header front-loads the conflated phrase.**
  `SYNTHESIS.md:9-13`: "DCB is feasible for saga correctness only as..." binds
  DCB to "saga correctness" before the qualifier. Fix: lead with the object DCB
  acts on.
- **F3 — MINOR — research-question artifacts retain pre-split "prove" framing.**
  `LANES.md:9`, `PROOF-OBLIGATIONS.md` title, `dispatch.json:6`. Fix: one-line
  note that "prove" = the model/harness proves; DCB only guards freshness.
- **F4 — MINOR — `ProofVerdictIssued` + `mechanism: DCB` risks reading as "DCB
  issues the proof verdict."** `PROOF-OBLIGATIONS.md:78`. Fix: relabel to
  "receipt of externally-issued verdict + DCB freshness."

Clean: g05 honored (submodules clean, strain is residue); witness-not-proof
asserted in every doc + the harness; P10 — verdict capped at `borrow-carefully`,
formal proof deferred. **0 CRITICAL, 1 MAJOR, 3 MINOR; no law breach.**

### Final position (post-confrontation)

**Spekkens is right, and I was checking the wrong thing.** I verified the corpus
*says* the disciplined words; I did not verify the verdict's *load-bearing claim
is carried by the code*. It is not.

Mechanism gate confirmed: `acceptSagaProofFreshnessClaim` rejects on
`current.marker !== entry.marker` (a content-hash mismatch); `mechanism` only
selects the reason string. Re-tag the waiver `hash` → still REJECTS, byte
identical.

Governance reading: g03 (dispatch.json:497) and TOY-RUN-PLAN's stop condition
(line 397) say downgrade to content-hash if a content hash suffices. The toy's
detection layer **is** a content hash; the waiver is detected identically to the
five `hash` facts. The trigger fired on the realized mechanism; the toy did not
downgrade — it kept the `borrow-carefully` DCB framing. That is a g03
spirit-violation, and because SYNTHESIS.md's verdict rests on a demonstration
indistinguishable from a hash, the claim exceeds the evidence — a **P10
claim-≤-proof breach** I missed.

**Disclosure does not cure it.** Disclosure cures *omission*, not
*contradiction*. Stating the downgrade rule then not applying it when its trigger
fires is documenting the breach, not transparency. P10 is satisfied when claim ≤
proof, not when the gap is narrated.

**FINAL:** uphold Spekkens's CRITICAL as a joint **P10 + g03** finding; revise
overall conclusion from "STRONGLY CONFORMANT — NO LAW BREACH" to
**CONFORMANT-ON-PROCESS / BREACHED-ON-CLAIM** (taxonomy + disclosure law clean,
but the `borrow-carefully` DCB justification at SYNTHESIS.md:9 is unsupported and
must be downgraded). Keep F1 (MAJOR) — same disease as the CRITICAL: a name
asserting "proof" over a freshness surface. The 3 MINOR items stand.

---

## Attacker 3 — Spekkens, Robert (abuse-gaming / overclaim)

### Initial position

- **F1 — CRITICAL — the "DCB freshness win" is mechanically identical to a plain
  content-hash; mechanism never changes detection, only the prose.**
  `saga-spec.ts:402-445`. Detection is `if (current.marker !== entry.marker)`
  where `marker = hashFact(fact)` for *every* entry; `mechanism` is consulted
  only at line 427 to select between two reason strings. The toy rejects the
  stale waiver via the same sha256 content-hash diff it applies to the five
  `hash` facts — per the corpus's own g03 (`HANDOFF.md:61`,
  `TOY-SAGA-SCENARIO.md:116`) it demonstrates nothing DCB-specific. Fix: make
  `dcb` facts exercise a capability content-hash cannot (concurrent-acceptance
  race, version/append-position, re-derivation differs); else downgrade per g03.
- **F2 — MAJOR — the single `HumanWaiverApplied` fact manufactures a DCB
  necessity the harness never relies on.** `order-fulfillment.fixture.ts:215-252`;
  `saga-spec.ts:465`. Re-tagging the waiver `dcb`→`hash` produces byte-identical
  behavioral + freshness verdicts; the "non-rerunnable" framing is decoration.
  Inflates the `borrow-carefully` DCB justification. Fix: add a genuinely
  non-content-hashable property, or a concurrent second claim.
- **F3 — MAJOR — the harness is constructed so it can only succeed.**
  `run-toy.ts:110-115`; `saga-spec.ts:40`. `run-toy.ts` throws unless
  `behavioral_witness==="pass" && freshness_claim==="rejected" &&
  command==="AcceptSagaProofFreshnessClaim"`. The rejection is guaranteed because
  `currentFactsAfterStaleWaiver` is the same array with one entry's content
  mutated; the negative witness hand-removes `ReleaseInventory`. No input reports
  failure/accepted. Fix: drive freshness from an independently produced snapshot
  or two competing claims; include a control where a `dcb` fact is stale but
  content-identical.

Verified against code: every read-set entry is content-hashed regardless of
`mechanism`. `acceptSagaProofFreshnessClaim` has no concurrency path;
`PROOF-OBLIGATIONS.md:59` lists the concurrent-acceptance-race obligation as a
requirement the harness does not implement. The corpus is internally honest about
the gate but the toy and its verdict ignore that the toy itself meets the
downgrade condition.

### Final position (post-confrontation)

**On Wisnesky's "sound" — conceded, sharpened.** The freshness layer is sound *as
a content-hash comparator*. But "sound" and "demonstrates DCB value" are
different claims; only the second is shipped (`recommendation:"borrow-carefully"`,
`notes:"DCB guards acceptance freshness"`, the `non_rerunnable_fact` field, the
dcb reason branch). Soundness of the comparator does not transfer to the DCB
attribution. Wisnesky's tautological-assertion findings strengthen this: a
tautological behavioral witness + a decorative DCB layer = a harness that can
only pass.

**On Tarski's "discloses g03, therefore conformant" — disclosure aggravates.**
The corpus states the downgrade rule (`PROOF-OBLIGATIONS.md:94` — deterministic
facts must be hash/rerun, not wrapped in DCB unnecessarily) then ships a
`borrow-carefully` DCB verdict whose sole "non-rerunnable" win is a content-hash
result. Disclosure converts an innocent gap into known-trigger-shipped-anyway.

**Honest-exit re-examination (does any path let `dcb` catch what hash cannot?):**
content change → caught regardless of mechanism; re-tag dcb→hash → only the
reason flips; concurrency/acceptance-race → obligation at PROOF-OBLIGATIONS.md:59
**not implemented**, no version/append-position field; re-derivation → never
occurs. **No path.** Claim exceeds proof.

**FINAL:** F1 CRITICAL held; F2 MAJOR held; F3 MAJOR held (reinforced by
Wisnesky). Remedy: implement the concurrent-acceptance-race path so `dcb` does
work content-hash cannot, or downgrade the verdict to "content-hash freshness;
DCB not yet demonstrated."
