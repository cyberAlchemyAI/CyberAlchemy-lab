# Goal

Estimate the remaining cost of completing DomainSpec FPR-01 through FPR-04 while keeping engineering effort, owner-decision effort, elapsed critical-path time, validation/compute burden, and uncertainty separate. Compare assurance-first completion with the candidate-first posture without treating candidate output as FPR authority.

# TL;DR

The selected modeled FPR-01…04 budget is **26.5 / 48 / 86 engineering person-days (PD)** plus **24 / 52 / 100 narrowly defined owner-review hours**, low/base/high. The separate modeled calendar envelope is **10–16 / 20–32 / 41–68 weeks**; it is not a conversion of PD because serial owner gates and independent verification dominate elapsed time. Assurance-first plus the learning map is modeled at **46 / 84 / 150 PD** and **36 / 76 / 148 owner-review hours**. Candidate-first plus later authority rebind is modeled at **50 / 94 / 174 PD** and **40 / 84 / 164 owner-review hours**, including a modeled **4 / 10 / 24 PD** and **4 / 8 / 16 owner-review-hour** tax. Candidate-first may shorten time to interactive evidence only with a genuinely separate engineering lane, but it closes no FPR gate. These are planning estimates, not measured durations or SLAs. [Agent 1: bottom-up estimate and route comparison](./research.md#agent-1--bottom-up-fpr-and-learning-map-work-breakdown) [Agent 3: latency and tail-risk model](./research.md#agent-3--adversarial-owner-latency-and-tail-risk-model)

# Context

The live route has **13 remaining receipt-serial SWUs** after the completed census. That census identified 21 sources, 12 unresolved disagreements, and five owner queues without selecting an authority baseline. The completed `SWU-FPR01-001` census work is **sunk** and excluded from every remaining-cost band in this document: engineering PD, owner-review hours, E3 aggregate hours, calendar, TSE, and CPU. The work still to be costed moves from owner decisions into validators, negative fixtures, digest-bound replay, business-to-Spec mapping, production projection code, quotient semantics, and an independently implemented comparator. A task-count-only forecast would therefore hide both rework and authority latency. [Agent 1: FPR arithmetic and dependency chain](./research.md#fpr-bottom-up-arithmetic) [Agent 2: reference-class calibration](./research.md#agent-2--empirical-task-session-reference-class-calibration) [Agent 3: why the path is long](./research.md#why-the-path-is-long)

# Selected resource budget

All values in the next table are **modeled, not measured**. A PD is defined as six focused engineering hours and includes bounded context preparation, implementation, tests, deterministic replay, and receipt packaging. Owner-review hours are a narrow, separate allowance for accountable decisions and reviews; they exclude owner waiting and must not be added to PD without first choosing an explicit labor-cost conversion. [Agent 1: estimation basis](./research.md#estimation-basis-and-assumptions)

| FPR | Modeled engineering PD L / B / H | Modeled owner-review h L / B / H | Main burden |
|---|---:|---:|---|
| FPR-01 | **4.5 / 8 / 14** | **8 / 20 / 38** | Five owner dispositions, baseline/schema validator, fixtures, ratification, independent verification |
| FPR-02 | **5.5 / 10 / 18** | **4 / 8 / 16** | Profile decision, multi-artifact contract, ten negative categories executed twice |
| FPR-03 | **7 / 13 / 24** | **8 / 16 / 30** | Direction/precedence decision, three graph/schema families, total-map validation, independent exact-set check |
| FPR-04 | **9.5 / 17 / 30** | **4 / 8 / 16** | Source contract, compiler, quotient semantics, independent comparator and mutants |
| **FPR-01…04 total** | **26.5 / 48 / 86** | **24 / 52 / 100** | Thirteen serial SWUs |

The low case assumes stable sources, prompt decisions, and no material rework; the base case assumes one review/revision cycle; the high case assumes two cycles, contract ambiguity, and limited identity migration. A foundational decision reversal is outside the high band and triggers re-estimation. Confidence is medium on relative burden and low-medium on absolute PD because future validator durations have not been measured. [Agent 1: assumptions and arithmetic](./research.md#estimation-basis-and-assumptions)

# Unit bridge: keep the models non-collapsed

The three explorer models answer different questions and should remain visible as different units:

| View | What it represents | Modeled low / base / high | How to use it |
|---|---|---:|---|
| Engineering PD | Focused engineering resource budget for FPR-01…04 | **26.5 / 48 / 86 PD** | Selected resource-planning denominator |
| PD-to-hours bridge | Arithmetic only at 6 focused h/PD | **159 / 288 / 516 focused engineering h** | Capacity illustration; not elapsed time and not measured duration |
| Owner-review h | Narrow owner decision/review allowance | **24 / 52 / 100 h** | Staff accountable review separately from engineering |
| Task-Session equivalent (TSE) | Receipt-producing session/rework count | **13 / 19–21 / 29–32 TSE** | Reference-class pressure test; not a duration unit |
| E3 aggregate h | Broader accountable-owner, implementer, reviewer, and independent-verifier effort | **165–260 / 350–520 / 780–1,170 h** | Tail-risk envelope; overlaps other labor categories and must not be summed with them |
| Calendar | Serial elapsed envelope including waits | **10–16 / 20–32 / 41–68 weeks** | Schedule risk; not convertible from PD without staffing and latency assumptions |

The empirical TSE study also produced modeled active-engineering ranges of **12–18 / 22–32 / 38–55 hours**, but sparse receipts do not record reliable start/finish effort. Those ranges calibrate likely retry pressure; they do **not** override or convert the selected bottom-up PD budget. Git cadence is likewise unsuitable because large commits batch unrelated work. [Agent 2: cost calibration and reference class](./research.md#cost-calibration) The E3 aggregate-hour model assumes 20–30 focused aggregate hours per week and normal decision turnarounds; it is intentionally broader than narrow owner-review hours. [Agent 3: estimate model](./research.md#estimate-model)

# Critical path and calendar

The reconstructable 13-SWU critical path is:

`FPR01-002 → FPR01-003 → FPR01-004 → FPR02-001 → FPR02-002 → FPR02-003 → FPR03-001 → FPR03-002 → FPR03-003 → FPR04-001 → FPR04-002 → FPR04-003 → FPR04-004`.

The route permits only one successor after the predecessor receipt. Harness sketches can be prepared early, but downstream schemas, fixtures, and acceptance cannot safely finalize before owner decisions. The modeled calendar view remains separate:

| Stage | Modeled E3 aggregate h, low / base / high-tail | Modeled calendar, low / base / high-tail |
|---|---:|---:|
| FPR-01 | 25–40 / 55–80 / 120–180 | 2–3 / 4–6 / 8–12 weeks |
| FPR-02 | 35–55 / 75–110 / 160–240 | 2–4 / 4–7 / 8–14 weeks |
| FPR-03 | 45–70 / 90–140 / 200–300 | 3–4 / 5–8 / 10–17 weeks |
| FPR-04 | 60–95 / 130–190 / 300–450 | 3–5 / 7–11 / 15–25 weeks |
| **Serial total** | **165–260 / 350–520 / 780–1,170** | **10–16 / 20–32 / 41–68 weeks** |

These E3 and calendar numbers are modeled, not measured. They surface authority latency, migration, replay, and verifier staffing; they are not alternative prices to add to the selected PD and owner-review budget. [Agent 1: dependencies and parallelism](./research.md#dependencies-and-parallelism) [Agent 3: estimate model](./research.md#estimate-model)

# Validation and compute burden

The task contracts contain **43 unique negative controls**. Because FPR-02 runs its ten categories twice, the minimum is **at least 53 negative executions**: FPR-01 contributes 6, FPR-02 contributes 20 executions from 10 unique controls, FPR-03 contributes 8, and FPR-04 contributes 19. The prior “roughly 70” figure is retained only as an **approximate, unverified planning bridge** for total acceptance executions after positives, deterministic replays, exact-set checks, schema parsing, typecheck, guard reruns, and receipt verification are included. It is not a verified execution census. [Agent 1: validation inventory](./research.md#validation-and-compute-burden)

For FPR-01…04, final accepted automated evidence is modeled at **1–4 CPU-hours**, with **8–30 CPU-hours** modeled across iterative development. The learning map adds modeled **6–20 CPU-hours** for accepted automated evidence and **20–60 CPU-hours** iteratively. These CPU numbers are not benchmark-derived; the jobs are expected to be small local JSON/YAML/Node/TypeScript workloads, while human diagnosis and the learning map’s accessibility and pilot procedures remain labor, not CPU. [Agent 1: validation and compute](./research.md#validation-and-compute-burden)

# Route comparison

All route values below are modeled and share the same denominator. “Candidate-first plus rebind” includes later binding to owner-issued FPR authority; it is not a shortcut around FPR acceptance.

| Route | Modeled engineering PD L / B / H | Modeled owner-review h L / B / H | Interpretation |
|---|---:|---:|---|
| Assurance-first FPR + learning map | **46 / 84 / 150** | **36 / 76 / 148** | Lowest expected total work and migration exposure |
| Candidate-first + later authority rebind | **50 / 94 / 174** | **40 / 84 / 164** | Earlier product learning only if capacity is independent |
| Candidate-first incremental tax | **4 / 10 / 24** | **4 / 8 / 16** | Provenance guard, candidate seed, equivalence/rebind or identity migration |

The modeled learning-map component is **19.5 / 36 / 64 PD** and **12 / 24 / 48 owner-review hours**. With two genuinely separate engineering lanes, the candidate technical path is modeled at **28.5 / 54 / 102 working days**; that figure excludes owner waits and is not the calendar envelope. With one engineer, candidate-first is modeled as **50 / 94 / 174 sequential working days**. Candidate output closes **no FPR gate**, cannot authorize an FPR claim, and remains exposed to count, maturity, source-home, projection, UI-admission, ontology-direction, quotient, and identity decisions. [Agent 1: route arithmetic](./research.md#assurance-first-versus-candidate-first) [Agent 3: candidate migration exposure](./research.md#candidate-to-authoritative-migration-exposure)

# Research-contract verdict matrix

This matrix records research ownership and review coverage; it is not a release or budget approval. Russell's conditional result establishes only the requested arithmetic/non-vacuity witness after correction. Popper's definitional-soundness review did not occur.

| Candidate | Owner / precedent | Witnessed / non-vacuity | Sound / definitional | Verdict |
|---|---|---|---|---|
| Assurance-first | Abramsky owns the bottom-up task-contract model; Kahneman supplies receipt-based precedent; Baez supplies authority-latency and tail-risk challenge. [Agent 1](./research.md#agent-1--bottom-up-fpr-and-learning-map-work-breakdown) [Agent 2](./research.md#agent-2--empirical-task-session-reference-class-calibration) [Agent 3](./research.md#agent-3--adversarial-owner-latency-and-tail-risk-model) | **Russell: conditional non-vacuity PASS**, contingent on the reconstructable 13-SWU schedule and corrected validation counts now present. | **Popper: NOT REVIEWED** because the reviewer failed to launch at the runtime thread ceiling. | **PROVISIONAL** — not an approved budget baseline pending independent definitional review. |
| Candidate-first plus rebind | Abramsky owns the modeled route and rebind tax; Kahneman supplies the disposable-spike precedent; Baez challenges migration and high-tail exposure. [Agent 1](./research.md#assurance-first-versus-candidate-first) [Agent 2](./research.md#sequencing-implications) [Agent 3](./research.md#candidate-to-authoritative-migration-exposure) | **Russell: conditional non-vacuity PASS**, contingent on the same arithmetic witness and on preserving the candidate tax separately. | **Popper: NOT REVIEWED** because the reviewer failed to launch at the runtime thread ceiling. | **PROVISIONAL** — not an approved budget baseline pending independent definitional review. |

# Sensitivity and re-estimation triggers

Re-estimate rather than stretching the current high band when any of these occurs:

- an owner rejects a foundational baseline, profile, precedence, or quotient decision;
- candidate identities cannot survive authority binding without a migration map;
- the chosen source home or UI-admission boundary changes downstream roots;
- FPR-03 mapping or FPR-04 quotient work reopens a predecessor receipt;
- an independent verifier is not staffed when the comparator/acceptance path becomes ready;
- the candidate lane is not independently staffed, eliminating the modeled two-lane critical-path benefit;
- measured Task-Session duration, retry rate, or CPU telemetry materially departs from the modeled bands; or
- the executable validation census differs from 43 unique controls, at least 53 negative executions, or the approximate 70-execution planning bridge.

The most severe named tails are ontology-direction contradiction and quotient non-reversibility; either can force broad remapping or reopen earlier scope. Evidence also expires after authoritative upstream changes, so replay is expected even without semantic redesign. [Agent 3: named tail-risk triggers](./research.md#named-tail-risk-triggers)

# Reviewer result and evidence limitation

The reviewer group is **PARTIAL**. Russell returned a **conditional PASS** after requiring the corrected validation census and a reconstructable 13-SWU arithmetic witness; both corrections are incorporated above. Popper did not launch because the runtime thread ceiling was reached. Therefore this dispatch has **no independent definitional-soundness PASS**. The unit separation in this document is the writer’s application of the requested correction, not evidence that the missing reviewer gate succeeded. This reviewer-stage status came from the dispatch handoff and is not transcribed in `research.md`; downstream users must not treat it as a fully reviewed estimate.

# Bounded recommendation

Use the **assurance-first base budget of modeled 84 engineering PD plus 76 narrow owner-review hours** as the current resource-planning case, and carry the separate **modeled 20–32 week** calendar envelope for schedule planning. Preserve the low/high bands rather than turning the base into a commitment. Authorize candidate-first only as an explicitly non-authoritative, disposable learning lane when separate capacity exists and the plan owner accepts the modeled **10 PD plus 8 owner-review-hour base rebind tax**. Do not credit candidate work toward FPR closure. Before this estimate becomes a budget baseline or external commitment, rerun the missing independent definitional-soundness review and begin recording actual PD, owner-review, elapsed, execution-count, and CPU observations per SWU. [Agent 1: route recommendation](./research.md#assurance-first-versus-candidate-first) [Agent 2: sequencing implications](./research.md#sequencing-implications) [Agent 3: route recommendation](./research.md#assurance-first-versus-candidate-first-1)

## Connections

- derives-from → [research.md](./research.md)

# Open Questions

- **OQ-1 (BLOCKER)** — Does an independent definitional-soundness review accept the separation of PD, owner-review hours, TSE, E3 aggregate hours, calendar, and CPU? Recommendation: rerun Popper’s review before promoting this estimate to an approved budget baseline. Owner: Popper, Karl.
- **OQ-2** — What actual effort and latency do the next completed SWUs exhibit? Recommendation: record focused engineering time, narrow owner-review time, owner wait, retry count, negative/total executions, and CPU telemetry separately on every receipt, then recalibrate after FPR-01. Owner: Brandenburg, Martin.
- **OQ-3** — Will the candidate lane have genuinely separate capacity and explicit acceptance of rebind risk? Recommendation: default to assurance-first unless the owner records both the second-lane allocation and the candidate-tax decision. Owner: Brandenburg, Martin.
- **OQ-4** — Do source-home, identity, ontology-direction, UI-admission, or quotient decisions invalidate the current high band? Recommendation: trigger a fresh bottom-up estimate immediately after any such decision changes the artifact graph or reopens a predecessor receipt. Owner: Brandenburg, Martin.
