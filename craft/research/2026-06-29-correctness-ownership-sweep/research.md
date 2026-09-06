# research.md — collected returns (verbatim)

Dispatch: `2026-06-29-correctness-ownership-sweep` (research) · schema v0.6.0
Goal: map what the unswept domainspec-v2 research program + adjacent assets already OWN
toward {cross-record/saga consistency, honest proof-claim labeling, freshness/attestation,
deterministic engine}, and isolate the genuine net-new surface vs the Kodamai read.

Pipeline: G1 explorers (formal-behavioral A + definitional B) →seq→ G2 skeptic (non-vacuity).
Anti-bias gate (infrastructure, unregistered): checker PASS + reviewer PASS.
final_approver: parent (P8 spot-verify on A3 done — confirmed).

---

## Explorer A — formal-behavioral / executed-artifact lens (verbatim)

Corpus: dcb-saga-correctness/ (tower + executed toy harness + review), dcb-correctness/
(tower, no toy), dcb-for-correctness-pack/ (distillation prose), test-engine/ (handoff only).

Capability table:
- Cross-saga compensation ordering enforcement — toy-harness/saga-spec.ts validateGraph() L203-252;
  assertBehavioralObligations() L321-377; order-fulfillment.fixture.ts L1-163 — EXECUTED-WIRED
  (toy-run-result.json; review confirmed byte-identical reproduction, Node 22.12).
- Bounded behavioral witness (saga failure+compensation) — enumerateRuns() L254-318 +
  assertBehavioralObligations() L321-377 — EXECUTED-WIRED with MAJOR caveat: red-team 2026-06-17
  found acceptedSuccess/terminalState hard-coded literals (M3), compensation assertion compares a
  filter to itself (M2), negative-witness uses !comp && !terminal (m1). Trace scripted; assertions
  partially tautological.
- Freshness / DCB acceptance guard (acceptSagaProofFreshnessClaim L402-445; buildReadSet L379-386;
  buildFreshnessClaim L388-400) — EXECUTED-WIRED with MAJOR caveat C1: mechanism "dcb" vs "hash"
  gates only a reason string; detection path identical sha256(stableStringify(fact)); concurrent-
  acceptance race (PROOF-OBLIGATIONS.md L59) unimplemented.
- Non-rerunnable fact-class identification (FactMechanism L27; fixture L165-237; PROOF-OBLIGATIONS
  L63-83) — EXECUTED-WIRED with MAJOR caveat M1: discrimination asserted-not-shown.
- Cross-context edge validation (EDGE_SIGNATURES L165-184; validateGraph L203-252) — EXECUTED-WIRED
  clean; Saga `orchestrates` flagged as residue, not error (g05-clean).
- AcceptSpecCodeCorrectnessClaim (dcb-correctness/SYNTHESIS.md, HANDOFF.md, LANE-RECEIPTS.md) —
  DESIGNED-ONLY (no toy execution).
- Spec-to-test engine (test-engine/HANDOFF.md) — DESIGNED-ONLY (handoff only; rule tables live in
  implementation/domainspec/TEST-PIPELINE.md, out of corpus).
- Model-checking TLA+/Alloy/Lean for the saga — PROSE-CLAIM (selection rationale only; Lean deferred).

Class verdicts: (1) saga consistency OWNED+partially-executed, concurrency/TOCTOU asserted-not-shown;
(2) model-checking: TS witness executed, formal lanes precedent-clean; (3) deterministic engine: weak
signal, executor DESIGNED-ONLY; (4) freshness: content-hash freshness executed, DCB discrimination open.

---

## Explorer B — definitional / claim-discipline / ontology lens (verbatim)

Corpus: spec-ontology-unification/, target-state/, domainspec-language claims-ladder
(2026-06-08-language-validator-convergence, categorical-language-critique-lane.md), definitions.

Class 1 — claim-register / proof-label discipline:
- Five-label proof-kind vocabulary (CLAIM-LEDGER C3/C8 + DISTILL Operator Reminder) — DEFINED-GOVERNED.
- Source-kind taxonomy (6 kinds, operator-reading quarantine) — DEFINED-GOVERNED.
- DCB label split (validator vs claim-freshness, dcb-correctness/SYNTHESIS) — DEFINED-GOVERNED.
- claim ≤ validation-report gate (cyber-alchemy-lean-fusion .../02-claim-proof-gate.md) — PROSE-ONLY
  (label-deep; magnitude check OPEN).
- Computable subset-rule gate — ASPIRATIONAL (named open).
- "model-checked ≠ implementation verified" predicate — none as gate (C9 operator-reading only).

Class 2 — proof scope labeling:
- P8 owner-approval sufficient / Lean pass only necessary (DEPENDENCY-MAP H-3 + CONVERGENCE-MODEL-
  DECISION DEC-CONV-01) — DEFINED-GOVERNED.
- Saga proof obligations scoped by class (PROOF-OBLIGATIONS §Obligation Classes) — DEFINED-GOVERNED.
- bounded-witness-not-proof label rule (SYNTHESIS Tension 3) — DEFINED-GOVERNED.
- "validator passed ≠ promoted" — PROSE-ONLY (documented confusion, no gate).

Class 3 — representability / adequacy:
- Lan-faithful-not-full residue + m6Witnesses computable detector (CATEGORICAL-FORMALIZATIONS
  Framing 3) — DEFINED-GOVERNED.
- staged-claim discipline (MVP proves operational presheaf; Lan-unit iso stays open) — DEFINED-GOVERNED.
- orchestrates semantic mismatch (CLAIM-LEDGER C13) — PROSE-ONLY.
- anti-collapse contract/schema separation predicate (DEPENDENCY-MAP D1-3) — ASPIRATIONAL (MISSING).
- DomainSpec-as-extraction-vocabulary-not-proof-language (SYNTHESIS Tension 1) — DEFINED-GOVERNED.

Class 4 — vocabulary governance:
- Definition Cards w/ Misuse Warning + promotion boundary (DEFINITIONS.md) — DEFINED-GOVERNED.
- promotion-candidate status (local-research-only) — DEFINED-GOVERNED.
- categorical-term-must-map-to-artifact-path (critique-lane §Scope) — DEFINED-GOVERNED.
- "composition ≠ proof of semantic success" (critique-lane) — DEFINED-GOVERNED.
- minimal named-relation vocabulary (implements/validates/projects_to/...) — ASPIRATIONAL.
- NON-CANONICAL ANALOGY tag on external categorical lit — DEFINED-GOVERNED.

---

## Skeptic — non-vacuity gate, hand-verified (verbatim)

All cited artifacts opened; two ★ A-claims hand-run (empty-trace lying run + dcb→hash flip);
★B3 executed via `lake env lean --run`.

- A1 validateGraph — witnessed-bounded (toy); L213/L239 errors fire on real inputs. build-from-owned.
- A2 behavioral witness — collapses-to-prescripted-transcript: forged run with trace:[] but author-set
  acceptedSuccess:false/terminalState returned status:"pass". 1 of 3 assertions a genuine negative
  witness (re-validates mutated brokenSpec); 2 tautological self-comparisons. build-from-owned (the
  negative-witness leg is the salvageable seed).
- A3 freshness guard — collapses-to-plain-content-hashing: dcb→hash flip left verdict byte-identical
  ("VERDICT INVARIANT: true"); mechanism read only for a reason string (L427/L433-435). No TOCTOU
  discrimination owned. build-from-owned only as content-hash wiring; concurrency guard is net-new.
- A4 fact-class — prose-only / relabel (same root as A3).
- A5 edge-signature — witnessed-bounded (clean). build-from-owned.
- A6 AcceptSpecCodeCorrectnessClaim — designed-not-wired.
- A7 spec→test engine — designed-not-wired (test-engine/ has only HANDOFF.md; "not executed").
- A8 formal model-checking saga — prose-only / precedent-clean (R1/R2 flag .alloy/.tla unvalidated).
- B1 five-label vocabulary — defined-governed (honest).
- B2 P8-necessary-not-sufficient — defined-governed (concedes "designed, not wired").
- B3 M6 detector — witnessed-bounded (executed: lake env lean --run printed 16-element m6Witnesses,
  native_decide cardinality m6_residue_count = 16). BUT fullness tie prose-only (gradeP4Ambiguity is a
  STUB; "⇒ Δ not full" is open conjecture). Detector build-from-owned; fullness verdict net-new.
- B4 Definition Cards — defined-governed.
- B5 DCB two-sentence split — defined-governed (holds independent of A3's impl collapse).
- B6 claim≤validation gate — prose-only (View 02 STATUS "PARTLY OWNED"; no verdict-computing predicate;
  owned half is a rename of an existence-gate).
- B7 subset-rule gate — designed-not-wired / aspirational.
- B8 "model-checked ≠ verified" predicate — prose-only (operator-reading, no predicate).
- B9 contract/schema separation predicate — designed-not-wired (MISSING; "nothing in Report.lean checks this").

Roll-up: genuinely witnessed at toy/decidable register = m6Witnesses (B3 detector), validateGraph +
EDGE_SIGNATURES (A1/A5), A2's negative-witness leg. Collapses to weaker = A2 (scripted transcript),
A3/A4 (content-hash), B6 (prose), B3-fullness (open conjecture). Definitional governance (B1/B2/B4/B5)
genuinely owned and honest.
