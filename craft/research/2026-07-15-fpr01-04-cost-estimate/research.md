## Agent 1 — bottom-up FPR and learning-map work breakdown

## Explorer report — bottom-up FPR-01…04 cost

### Verdict

The 13 remaining FPR SWUs cost an estimated **26.5 / 48 / 86 engineering person-days** low/base/high, plus **24 / 52 / 100 owner-review hours**. This is assurance engineering, not release completion: FPR-04 closes only the two-node/one-edge profile; FPR-05 onward remains outside scope (`TASK-FPR-04-SPEC-PROJECTION.md:75-77`).

The existing learning-map build adds **19.5 / 36 / 64 engineering days**. Therefore:

| Route, same denominator | Engineering PD L/B/H | Owner-review h L/B/H |
|---|---:|---:|
| Assurance-first: FPR, then learning map | **46 / 84 / 150** | **36 / 76 / 148** |
| Candidate-first, later authority rebind | **50 / 94 / 174** | **40 / 84 / 164** |
| Candidate-first incremental tax | **4 / 10 / 24** | **4 / 8 / 16** |

Candidate-first is not cheaper. Its value is elapsed-time compression: with two genuinely separate engineering lanes, its technical critical path is approximately **28.5 / 54 / 102 working days**, versus **46 / 84 / 150** assurance-first. With one engineer, candidate-first simply consumes **50 / 94 / 174** sequential working days.

### Estimation basis and assumptions

One person-day means six focused engineering hours. Engineering estimates include bounded context preparation, implementation, tests, negative fixtures, deterministic replay, and receipt packaging. They exclude owner decision/review hours, owner waiting, participant recruitment/time, FPR-05 onward, production integration, publication, and unbounded redesign.

Low assumes experienced maintainers, stable sources, prompt decisions, and no material rework. Base assumes one review/revision cycle. High assumes two cycles, contract ambiguity, and limited identity migration, but not a rejected foundational decision that forces roadmap redesign. That event needs re-estimation.

Confidence is **medium on relative burden, low-medium on absolute days**: the artifact and dependency contracts are exact, but there are no measured duration records for these future validators.

### FPR bottom-up arithmetic

| FPR | Remaining SWU estimates, engineering PD L/B/H | FPR subtotal | Owner review h L/B/H |
|---|---|---:|---:|
| FPR-01 | 002 dispositions `0.75/1.5/3`; 003 baseline/schema/validator/fixtures `2.75/4.75/8`; 004 digest-bound ratification and independent verification `1/1.75/3` | **4.5 / 8 / 14** | **8 / 20 / 38** |
| FPR-02 | 001 profile Decision Gate `1/2/4`; 002 approximately eleven contract/schema/matrix/validator/digest artifacts `3/5.5/9`; 003 ten fail-closed cases run twice `1.5/2.5/5` | **5.5 / 10 / 18** | **4 / 8 / 16** |
| FPR-03 | 001 direction/precedence Decision Gate `1/2/4`; 002 six business graph/schema artifacts plus real Body War witnesses `3/5.5/10`; 003 total-map validator, separate exact-set verification, five mutants `3/5.5/10` | **7 / 13 / 24** | **8 / 16 / 30** |
| FPR-04 | 001 exact source contract `2/3.5/6`; 002 TypeScript compiler and tests `2.75/5/9`; 003 explicit quotient/code/tests `2/3.5/6`; 004 separately implemented comparator, mutants, receipt `2.75/5/9` | **9.5 / 17 / 30** | **4 / 8 / 16** |
| **Total** | `4.5+5.5+7+9.5`; `8+10+13+17`; `14+18+24+30` | **26.5 / 48 / 86** | **24 / 52 / 100** |

The census is sunk: it found 21 sources, 12 unresolved disagreements, and five owner queues without selecting a baseline (`foundation-execution/runs/SWU-FPR01-001/TASK-SESSION-RESULT.md:8-12,53-62`). Those five questions require explicit owner action; automatic continuation is unsafe (`TASK-SESSION-RESULT.md:105-115`).

The cost increases downstream because the contract shifts from decision evidence to executable assurance:

- FPR-01 requires five distinct drift failures, then a digest-bound receipt and deliberate mutation (`TASK-FPR-01-AUTHORITY-BASELINE.md:42-64`).
- FPR-02 authors a multi-artifact product/profile/pilot contract and executes ten distinct negative categories twice (`TASK-FPR-02-SUPPORTED-PROFILE.md:28-52`).
- FPR-03 creates three graphs and schemas around real `CT-1` and `EC-3/EC-4` witnesses, then proves totality with five mutants and a separable exact-set verifier (`TASK-FPR-03-BUSINESS-SPEC.md:28-55`).
- FPR-04 introduces production code, schemas, quotient semantics, and a comparator that must be independent of the compiler (`TASK-FPR-04-SPEC-PROJECTION.md:18-72`).

### Validation and compute burden

The contracts name at least **43 unique negative-control cases**:

- FPR-01: 6—five baseline drift cases plus ratification mutation.
- FPR-02: 10, each run twice.
- FPR-03: 8—three graph-integrity and five mapping mutants.
- FPR-04: 19—five input, four compiler, three quotient, and seven retraction cases.

Including positives, deterministic replays, exact-set checks, schema parses, typecheck, guard reruns, and receipt verification gives roughly **70 acceptance-path executions**. The four primary planned CLIs are explicit in `foundation-execution/EXECUTION-PACK.md:41-51`; later layers must also rerun the live guard and preserve prior receipt digests (`IMPLEMENTATION-LAYERING.md:24-30`).

These are bounded JSON/YAML/Node/TypeScript jobs over a tiny graph. Assuming commodity local hardware, the accepted final pass should consume about **1–4 CPU-hours**; iterative development likely consumes **8–30 CPU-hours**. This is not benchmark-derived. Human diagnosis dominates compute.

The learning map adds deterministic double builds, layout/search generation, API/component/browser suites, accessibility/AT procedures, performance measurements, and a human pilot (`interactive-ontology-learning-map/WORK-PACK.md:60-74`; `TASK-IOLM-006-EVIDENCE-PILOT.md:16-42`). I estimate **6–20 CPU-hours** for accepted automated evidence and **20–60** during iterative development; manual AT and pilot work remains human effort.

### Dependencies and parallelism

The FPR chain is receipt-serial:

`FPR01-002 → 003 → 004 → FPR02-001 → 002 → 003 → FPR03-001 → 002 → 003 → FPR04-001 → 002 → 003 → 004`.

The execution contract selects one SWU at a time and prohibits successor work before predecessor receipt (`foundation-execution/EXECUTION-PACK.md:28-39`; `WORK-PACK.md:104-110`). Test-harness sketches may be prepared early, but schemas, fixtures, and acceptance cannot safely finalize before their owner decisions. I assign no schedule credit for speculative parallel work.

Load-bearing owner dependencies are:

- FPR-01: five census disposition queues, particularly source homing and import-migration residue.
- FPR-02: UI formation/admission, origin, redaction, claims, rollback, and accountable roles.
- FPR-03: ontology/business/Spec precedence and contradiction policy through Decision Gate and Definitions Governance.
- FPR-04: semantic/engine agreement on quotient entries, followed by a verifier independent of the compiler owner.

### Assurance-first versus candidate-first

The current learning-map contract has 12 unstarted SWUs after its completed owner gate and blocks prototype mutation on exact FPR-01…04 receipts (`interactive-ontology-learning-map/WORK-PACK.md:45-74,84-90`). I price those shared units at **19.5 / 36 / 64 engineering days**, plus **12 / 24 / 48 review hours**.

The July 15 candidate route is proposal-only, not active. It proposes one normalized graph/read-model pipeline with `candidate` and later `authoritative` provenance postures, not two engines (`refreshes/2026-07-15-minted-runtime-route/REFRESH-REPORT.md:9-31`). Its tax is:

- **2 / 4 / 8 days** to apply/recompose the plan, add the minted-project adapter, provenance guard, candidate seed, and posture evidence.
- **2 / 6 / 16 days** later to bind the owner-issued FPR `Sg`, prove equivalence, or migrate identities.

The high migration allowance is justified because the refresh explicitly says stable concept IDs must survive or an explicit migration map is required; provenance labels cannot repair identity drift (`REFRESH-REPORT.md:142-150`).

Thus candidate-first can expose product/UX learning while FPR work proceeds in parallel, but it does not retire one FPR day or authorize one FPR claim. Assurance-first minimizes total work and migration risk. Candidate-first minimizes time to first interactive evidence only if a second engineering lane exists and the plan owner explicitly accepts the **4 / 10 / 24 day** expected rebind tax.

No files were changed.

## Agent 2 — empirical Task-Session reference-class calibration

## Cost calibration

Use one “Task-Session equivalent” (TSE) as the unit: one bounded SWU including context, implementation/evidence, negative controls, full validation, and receipt. This is more defensible than hours because receipts rarely record start/finish time.

The remaining route contains 13 SWUs: FPR-01 has 3 remaining, FPR-02 has 3, FPR-03 has 3, and FPR-04 has 4. The route is explicitly serial and decision-bearing SWUs must stop at owner gates ([WORK-PACK.md](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/development/first-production-release/foundation-execution/WORK-PACK.md:63), [gate checks](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/development/first-production-release/foundation-execution/WORK-PACK.md:104)).

| Case | Calibration factor | Expected TSE | Inferred active engineering | Owner/human waiting |
|---|---:|---:|---:|---|
| Low | 1.0× | 13 | 12–18 h | Same-day decisions; <1 working day total |
| Base | 1.5× | 19–21 | 22–32 h | 3–7 calendar days |
| High | 2.25× | 29–32 | 38–55 h | 1–3 calendar weeks |

Hours are model-derived ranges, not measured receipt duration. Owner-wait ranges are scenario assumptions, not observed SLAs.

### Why 1.5× is the defensible base

- The minted-project reference class needed 10 Task Session closures to deliver six numbered milestones: eight passes plus two correct blocker stops. Two parent-contract repairs (`MNP-001-R1/R2`) were required before retrying the blocked compiler and minter. That is 1.67 sessions per delivered milestone. Examples: compiler retry closed with targeted `17/17` and full `88/88` ([result](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/development/refinement-runs/20260714-minted-project-node-package-toy-game/task-sessions/20260715-swu-mnp-003-retry-001/TASK-SESSION-RESULT.md:1)); views closed `10/10`, full `92/92` ([result](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/development/refinement-runs/20260714-minted-project-node-package-toy-game/task-sessions/20260715-swu-mnp-004/TASK-SESSION-RESULT.md:1)); the minter first stopped at a contract contradiction ([blocked result](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/development/refinement-runs/20260714-minted-project-node-package-toy-game/task-sessions/20260715-swu-mnp-005/TASK-SESSION-RESULT.md:1)), then closed only after the parent-contract repair ([retry result](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/development/refinement-runs/20260714-minted-project-node-package-toy-game/task-sessions/20260715-swu-mnp-005-retry-001/TASK-SESSION-RESULT.md:1)).
- Guard repair was cheaper but still separated review from mutation. The exact-disposition review took 3m47s and intentionally left the audit red ([SGRM-006-R1](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/development/saga-removal/runs/SWU-SGRM-006/RETRY-001/TASK-SESSION-RESULT.md:2)); the subsequent repair added focused negatives and ran `71/71`, typecheck, links, hashes, and diff validation ([SGRM-007-R1](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/development/saga-removal/runs/SWU-SGRM-007/RETRY-001/TASK-SESSION-RESULT.md:50)).
- `SWU-FPR01-001` itself closed in one bounded session despite an in-session stale-digest repair: 21 sources, 12 unresolved disagreements, five owner queues, and two equal validation passes ([FPR01-001 receipt](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/development/first-production-release/foundation-execution/runs/SWU-FPR01-001/TASK-SESSION-RESULT.md:8)). It then correctly stopped at five owner-disposition questions ([handoff](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/development/first-production-release/foundation-execution/runs/SWU-FPR01-001/TASK-SESSION-RESULT.md:105)).
- Git timestamps are unsuitable as engineering-time evidence: commit `35b7d2ca481e6935e5a352aedab05adbd41d502d` batched 503 files and 41,376 insertions, including 166 filtered FPR/minted paths. Commit cadence therefore hides the Task Session cadence.

### Node-level base allocation

- FPR-01 remaining: 2.5–3 TSE. One owner-disposition gate, one validator/mutant implementation, one ratification receipt ([task contract](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/development/first-production-release/foundation-execution/work-pack/tasks/TASK-FPR-01-AUTHORITY-BASELINE.md:31)).
- FPR-02: 4–5 TSE. The decision envelope has many independent fields; then a multi-artifact validator and ten distinct negative classes ([task contract](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/development/first-production-release/foundation-execution/work-pack/tasks/TASK-FPR-02-SUPPORTED-PROFILE.md:18)).
- FPR-03: 5–6 TSE. This has the highest authority uncertainty: direction/precedence first, then BO/BK/B artifacts, then a total independently checked B-to-Spec map ([task contract](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/development/first-production-release/foundation-execution/work-pack/tasks/TASK-FPR-03-BUSINESS-SPEC.md:18)).
- FPR-04: 7–8 TSE. Four technical units, with compiler/quotient ownership separated from the final comparator acceptance ([task contract](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/development/first-production-release/foundation-execution/work-pack/tasks/TASK-FPR-04-SPEC-PROJECTION.md:18)).

### Sequencing implications

Assurance-first is the lower expected-cost route: use the 1.0× / 1.5× / 2.25× factors above. It minimizes discarded artifacts, but serializes at least five owner-bearing moments: FPR01 disposition, FPR01 ratification, FPR02 profile decision, FPR03 direction decision, and FPR04 independent acceptance. In the base/high cases, calendar elapsed time is likely only 35–55% / 15–35% active engineering; waiting dominates.

Candidate-first cannot validly bypass those gates. FPR-02 explicitly prohibits schema authoring before its decision, and later nodes consume verified predecessor receipts. A separately authorized, disposable candidate spike could overlap owner waiting and expose quotient/compiler problems earlier, but it cannot count toward FPR closure. Budget it as an additional 2–4 TSE; expected factors become approximately 1.15× / 1.7× / 2.5×. Its only defensible benefit is tail-risk discovery, not authority acceleration.

Most important warning: prior implementation cadence predicts validators, fixtures, compilers, and receipts reasonably well. It does not predict how quickly owners will settle count/status/source-home, product-profile, ontology direction, or quotient authority. Those are policy latencies, not engineering throughput.

No files were written.

## Agent 3 — adversarial owner-latency and tail-risk model

The adversarial conclusion: from the live state, completing FPR-01 through FPR-04 is more plausibly a multi-month authority-and-verification program than a short compiler task. The primary cost driver is not implementation volume; it is sequential owner decisions, authority migration, digest-bound replay, and independent verification.

The estimate starts after completed W0 and `SWU-FPR01-001`. That census found 21 sources, 12 unresolved disagreements, and five owner queues, while explicitly selecting no baseline or production authority ([task result](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/development/first-production-release/foundation-execution/runs/SWU-FPR01-001/TASK-SESSION-RESULT.md:8)). The immediate blocker is `SWU-FPR01-002`, which cannot execute automatically ([handoff](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/development/first-production-release/foundation-execution/runs/SWU-FPR01-001/TASK-SESSION-RESULT.md:105)).

### Estimate model

“Owner hours” means aggregate accountable-owner, implementer, reviewer, and independent-verifier effort. Calendar assumes 20–30 focused aggregate hours/week, normal 2–5-business-day decision turnarounds, and no successor starting before its predecessor receipt. This matches the explicit one-SWU-at-a-time and receipt-gated policy ([work-pack](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/development/first-production-release/foundation-execution/WORK-PACK.md:104)).

| Remaining node | Low | Base | High-tail | Main uncertainty |
|---|---:|---:|---:|---|
| FPR-01 | 25–40 h / 2–3 wk | 55–80 h / 4–6 wk | 120–180 h / 8–12 wk | Five owner queues; authority/source/projection migration |
| FPR-02 | 35–55 h / 2–4 wk | 75–110 h / 4–7 wk | 160–240 h / 8–14 wk | Exact profile, UI exclusion, origin/redaction/role decisions, ten negative classes |
| FPR-03 | 45–70 h / 3–4 wk | 90–140 h / 5–8 wk | 200–300 h / 10–17 wk | Ontology/Spec precedence and contradiction policy; total B→Spec map |
| FPR-04 | 60–95 h / 3–5 wk | 130–190 h / 7–11 wk | 300–450 h / 15–25 wk | New semantic projection module, quotient semantics, separately authored comparator |
| **Serial total** | **165–260 h / 10–16 wk** | **350–520 h / 20–32 wk** | **780–1,170 h / 45–68 wk** | Reopens and authority migration dominate the tail |

Confidence is high on the serial dependency structure, medium on the relative stage weights, and low-to-medium on absolute hours because the repository contains no calibrated historical effort data. Numeric probabilities would be false precision.

### Why the path is long

Every stage consumes a verified receipt, not merely the previous files ([traceability](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/development/first-production-release/foundation-execution/work-pack/shared/traceability.md:11)). FPR-01 alone still requires manual dispositions, a deterministic baseline validator, and independent ratification; only that receipt opens FPR-02 ([FPR-01 task](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/development/first-production-release/foundation-execution/work-pack/tasks/TASK-FPR-01-AUTHORITY-BASELINE.md:31)).

FPR-02 must decide the exact admitted/exercised/deferred boundary before schema authoring and reject ten distinct false-green cases ([FPR-02 task](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/development/first-production-release/foundation-execution/work-pack/tasks/TASK-FPR-02-SUPPORTED-PROFILE.md:18)). FPR-03 then has a separate blocker-level precedence decision before BO/BK/B authoring and total mapping ([FPR-03 task](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/development/first-production-release/foundation-execution/work-pack/tasks/TASK-FPR-03-BUSINESS-SPEC.md:18)). FPR-04 requires a new projection compiler, explicit quotient registry, and an independently implemented comparator that cannot use the compiler as its oracle ([FPR-04 task](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/development/first-production-release/foundation-execution/work-pack/tasks/TASK-FPR-04-SPEC-PROJECTION.md:61)).

### Candidate-to-authoritative migration exposure

The backend meta-type registry currently contains 13 registered members, all still `candidate`; each card’s promotion contract requires an owner decision, positive/negative fixtures, and exercise against a real aspect concept ([meta-types registry](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/definitions/meta-types/meta-types.yml:9)). Eleven UI types remain formation-deferred. Meanwhile relationship authority says 30 active signatures, but `DEFINITIONS.md` still says both 30 and 31 and the drift audit passes while citing 31 ([relationships registry](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/definitions/relationships/relationships.yml:17), [stale definition](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/definitions/DEFINITIONS.md:1030), [audit](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/definitions/DEFINITION-DRIFT-AUDIT.md:38)).

The homing decision permits only root authority plus generated-and-verified projections, but the UI taxonomy cannot be deleted until its 11 types migrate without orphaning ([ledger decision](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/.craft/ledger.yml:732), [UI migration gap](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/.craft/ledger.yml:863)). This makes candidate-first work unusually exposed: it may bake in the losing count, maturity status, source path, projection form, or UI admission boundary.

### Named tail-risk triggers

- **OD-001/OD-002 denominator or maturity reversal — high likelihood, medium/high impact.** If owners require per-card candidate→active promotion rather than a bounded baseline receipt, add roughly 60–180 hours and 4–12 weeks.
- **OD-003 source-home migration — medium likelihood, high impact.** A different compiled input home can invalidate FPR-02 roots and FPR-04 source/compiler assumptions: +30–120 hours, +2–8 weeks.
- **OD-004/OD-005 projection/import repair — medium likelihood.** The census found a transitional projection, an absent claimed vocabulary destination, and missing build proof: +20–80 hours, +2–6 weeks.
- **UI-11 scope leakage — medium likelihood.** If FPR-02 cannot cleanly exclude UI formation while retaining endpoint signatures, migration becomes critical-path work: +40–140 hours, +3–10 weeks.
- **Ontology-direction contradiction — medium likelihood, very high impact.** The live frontier explicitly says candidate ontology projections have no authority effect and blocks B→Spec promotion until precedence, supersession, provenance, and contradiction handling are decided ([ledger frontier](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/.craft/ledger.yml:954)). A late decision can force wholesale FPR-03 remapping: +60–200 hours, +4–12 weeks.
- **Quotient non-reversibility — lower likelihood, very high impact.** If local `consumes/enforces` labels cannot be represented as approved reversible quotients, FPR-04 may reopen FPR-03 or the admitted profile: +80–250 hours, +6–16 weeks.
- **Verifier independence failure — medium likelihood as a scheduling risk.** The verifier cannot accept evidence they authored, and the FPR-04 acceptance owner cannot be the compiler owner ([release contract](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/development/first-production-release/decisions/2026-07-12-product-release-contract.md:87)). Expect +1–6 calendar weeks if staffing is late-bound.
- **Evidence-expiry replay — certain after any upstream authoritative change.** Candidate SHA, profile, B/Spec, mapping, toolchain, source roots, or normalization changes expire evidence ([roadmap](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/development/first-production-release/ROADMAP.md:125)). Budget 10–30 hours per pure replay, 30–100 hours when semantic fixtures also change.

### Assurance-first versus candidate-first

| Route | Early value | Expected closure cost | Tail behavior |
|---|---|---|---|
| **Assurance-first** | Later demonstrator | Base 350–520 h, 20–32 wk | Lowest expected rework; decisions bind each downstream denominator |
| **Candidate-first** | Candidate-only prototype in roughly 70–120 h / 3–6 wk | Base 450–700 h, 25–42 wk | Mandatory rebinding/replay; base model assumes 25–45% downstream rework |
| **Candidate-first high tail** | Same early prototype | 950–1,450 h, 55–85 wk | 60–100% of profile/map/compiler artifacts rewritten after source-home, direction, or quotient decisions |

Candidate-first is defensible only as a disposable, explicitly non-authoritative spike—ideally time-boxed and kept outside proposed FPR authoritative target paths. It can reduce technical uncertainty around compiler/comparator separation, but it cannot close any FPR gate. Generated graphs remain projections rather than semantic authority, and no green component suite, digest, owner judgment, or candidate result independently establishes production ([roadmap release rule](/home/vrondelli/projects/domainspec-core/projects/domainspec-v2/development/first-production-release/ROADMAP.md:139)).

My planning recommendation is assurance-first for all artifacts that encode counts, source homes, admission, precedence, or quotient semantics; permit candidate-first only for throwaway compiler/comparator experiments with an explicit reimplementation budget.

## Connections

- derives → [findings.md](./findings.md)
