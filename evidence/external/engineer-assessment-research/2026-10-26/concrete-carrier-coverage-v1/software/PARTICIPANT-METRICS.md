# Participant feedback metrics — `EA-FEEDBACK-0.1`

Status: candidate display and calculation specification for the invited mixed-developer challenge. It instantiates the task-local [Feedback Metric meaning](../model/definitions.json) in a [Score Report](../model/definitions.json). No participant report has been issued, case calibrated or comparison population established. The three [case protocols](../research/cases/README.md) supply case-specific evidence opportunities; the [scoring model](../research/scoring-model.md) supplies the universal anchors and research-only composite.

## What the participant sees

The default report has **three session cards** and a short methodology panel. Each card shows six named dimensions with an evidence-linked observation, one useful strength or effective move, one next exercise, and an assessment status. An experimental `0–4` rating may appear beside a dimension only after the numerical-display gate below passes. The report shows no global rank, “best engineer” label, hiring recommendation, job-match percentage or percentile in the mixed-developer pilot.

| ID / visible label | Calculation or source | Unit/status and participant interpretation | Display gate |
| --- | --- | --- | --- |
| `FM-01` Cases completed | Count distinct scored session slots whose committed response and administration checks passed, out of the three offered slots; voided attempts do not add to the count. | `0–3 of 3`; journey progress only. | Show from server receipts, even while feedback is pending. |
| `FM-02` Dimension observation | One `Criterion Rating` for each fairly elicited dimension: two independent human `0–4/NA/UNK` ratings, preserved separately, with declared adjudication; report the adjudicated `H` and cited answer evidence. | Initial display: evidence-linked wording. Numeric display: experimental `0–4` anchor with its meaning. This describes the **answer to this case**, not a stable trait. | Qualitative: reviewed response and readable evidence. Numeric: numerical-display gate. |
| `FM-03` Assessment coverage | `N_rated / N_planned`, where `N_planned = 6` for the frozen session rubric and `N_rated` counts `0–4` results after review. Also list `NA`, `UNK` and pending dimensions by reason. | “4 of 6 areas assessable”; **data completeness**, not a performance score. A genuine omission after a fair prompt is rating `0` and counts as assessable. | Show only after administration/evidence review; before that, show “review in progress.” |
| `FM-04` Evidence and transcript status | Source media receipt, ASR status, participant correction version, evidence-span verification and human review state. | `transcript ready`, `correction saved`, `evidence review pending`, `reviewed`; process status only. No ASR confidence percentage presented as ability. | Show current state with correction/review route. |
| `FM-05` Result stability status | `pending`, `reviewed`, `needs resolution`, or `insufficient evidence`, using reviewer discrepancy, transcript uncertainty and administration exceptions. A disagreement of two or more anchor levels follows the predeclared adjudication rule. | A disclosure of whether feedback can be read; **not** a probability that the person has an ability. | Withhold affected dimension rating while unresolved or `UNK`. Case/rater generalizability intervals require E04 and are not fabricated for an individual. |
| `FM-06` Next exercise | A rule-bound suggestion linked to a low or incomplete *observable response behavior*, a citation, and a small practice action. After numeric review, prioritize one rated dimension at `≤2` with a specific missed opportunity; if all rated dimensions are `3–4`, offer a refinement exercise. | Actionable practice, never a deficit diagnosis. The participant can inspect why it was suggested. | Human-reviewed evidence and no unresolved transcript/case issue for that dimension. |
| `FM-07` Session score | Research reference formula `25 × Σ w_d H_d` over predeclared elicited dimensions. It is a rescaled ordinal summary with case and rater error, not an ability percentage. | **Hidden in first mixed-developer MVP.** Future display, if approved, must say “experimental score for this case” and show dimensions plus uncertainty. | Requires frozen weights, case calibration/equating for the intended comparison, acceptable E04 precision, owner-approved interpretation and display review. |
| `FM-08` Peer comparison / percentile | Future empirical position in a named, compatible reference cohort using calibrated forms and a declared estimator with interval. No default calculation. | **Unavailable in first MVP.** Never compare unlike roles or case forms as though equated. | Requires cohort definition, representativeness assessment, form/mode invariance, sample precision, fairness review and exact owner approval. |

The score engine must store `FM-01`–`FM-08` as projections from pinned source versions, with display-rule version `EA-FEEDBACK-0.1`, not as free text detached from ratings. A hidden metric may retain a research calculation under an approved protocol, but the participant API must return only authorized display fields and reasons for withheld fields. No metric is silently backfilled after a rubric change; publish a new report version with lineage and a correction note.

## The 18 session dimensions

These are the visible **behavior labels** for `FM-02`. Their IDs and anchors come from the [formal scoring model](../research/scoring-model.md) and the three case protocols. The short explanation tells the participant what evidence was sought; case-specific reviewer anchors govern the rating.

| Session | ID | Participant label | What the feedback points to |
| --- | --- | --- | --- |
| Creative reasoning | `R` | Problem framing | How the answer represented facts, goal, constraints and uncertainty. |
| Creative reasoning | `A` | Assumption testing | Whether a proposed observation/test could distinguish explanations. |
| Creative reasoning | `D` | Distinct viable options | Meaningfully different paths that could satisfy the constraints. |
| Creative reasoning | `N` | Useful originality | The best developed non-obvious idea and why it could help. |
| Creative reasoning | `F` | Feasibility and evidence | Cost, constraints, failure conditions and a test of the preferred idea. |
| Creative reasoning | `V` | Revision after new evidence | How the explanation or plan changed after the reveal. |
| Technical design | `Q` | Requirement discovery | Questions about users, invariants, ambiguous rules and workload. |
| Technical design | `P` | Product priority | What to protect or deliver first and the customer consequence. |
| Technical design | `B` | System and data boundaries | Request flow, authoritative state, concurrency and retry boundaries. |
| Technical design | `T` | Design tradeoffs | Consistency, latency, throughput and implementation/operating complexity. |
| Technical design | `O` | Failure and operation | Incident diagnosis, monitoring, safe retries, rollout and rollback. |
| Technical design | `V` | Revision under new load | How the design responds to the hot-account reveal. |
| Cooperation | `S` | Stakeholder understanding | Incentives, information, authority and user impact. |
| Cooperation | `C` | Concrete communication | The actual message/agenda, clear request and respectful disagreement. |
| Cooperation | `M` | Shared commitments | Owners, dependencies, verification and fallback. |
| Cooperation | `E` | Credit and risk allocation | Transparent recognition and consent by risk owners. |
| Cooperation | `X` | Conflict repair | Response to refusal and omitted credit without evasion or coercion. |
| Cooperation | `V` | Adaptation to response | How the plan changes after another party's move. |

The two `V` labels above have different case-specific meanings; the report always names the session. Session 3's `best_action`, `likely_action` and interactive variants are distinct measures and must display the instruction used. A hypothetical cooperation rating describes the response, not observed teamwork. Session 1 `N` uses the best developed useful idea, not idea count. Session 2 `B/T/O` require mechanisms, so jargon alone does not raise the rating.

## Calculation and display rules

1. The scoring run pins case, reveal events, rubric, response mode, source and transcript versions, scorer and report policy. The `0–4` universal anchors mean `0` no relevant evidence despite a fair opportunity; `1` unsupported claim; `2` plausible with a material gap; `3` specific and constraint-aware; `4` strong evidence surviving the reveal with residual risk. `NA` means no fair opportunity; `UNK` means unusable evidence. Raters cite evidence for `2–4` and a missed opportunity/contradiction for `0–1`.
2. Research `H_d` is the median of available independent human ratings after the predeclared disagreement procedure. With exactly two ordinal ratings, the midpoint may be fractional. Participant numeric display requires a separately documented **adjudicated integer anchor**; if raters differ and no such anchor exists, withhold the number. Do not silently round a midpoint or imply it is a rubric level. The first pilot's default qualitative wording avoids this ambiguity.
3. If a transcription gap could change a rating, `FM-02` is `UNK` or pending human review until the source/corrected text is checked. A candidate correction creates a new transcript and scoring-run version; the report states which was used.
4. If a case flaw or missed reveal removed an opportunity, mark affected dimensions `NA` with a reason and consider holding the case. If a participant did not address a clearly offered dimension, use the anchored `0`/`1` decision; never turn that into `NA` to improve appearance.
5. Feedback text is generated from cited evidence plus the frozen anchor/exercise library and reviewed before publication. It cannot attribute motives, personality, emotions or future work behavior. The participant can see the excerpt and request correction/contest.
6. Report `FM-03` and `FM-05` separately from performance. `6/6 assessable` and `reviewed` are **quality of evidence**, not high ability. No color or graph should imply they are grades. A future `FM-07` is withheld whenever a required rating is `UNK` or pending unless its frozen scoring specification contains an approved missing-data rule.

## Numerical-display gate

The default for an early formative pilot is **qualitative evidence and exercises**. An assessment owner can authorize `FM-02` numeric `0–4` display only for exact case/rubric/mode versions after E03 shows trained-rater agreement, treatment of valid alternatives, transcription error and access review good enough for formative feedback. The acceptance thresholds and minimum calibration sample must be fixed in the Study Protocol before examining results. Any material disagreement, case defect or mode uncertainty withholds the affected number. `FM-07` and `FM-08` have stronger gates and remain hidden for this pilot. This is a display decision, separate from whether a research team stores ratings for analysis.

## Example participant card (illustrative wording, no actual score)

> **Technical design · feedback reviewed**  
> **System and data boundaries:** You described a transaction boundary for the allowance update and ledger entry, and allowed unrelated accounts to proceed independently.  
> **Design tradeoffs:** You noted lock waits on the hot account. The answer did not yet explain how you would distinguish ordinary contention from deadlocks or what p99/queue signal would trigger a redesign.  
> **Practice next:** Sketch two requests racing on the same account, then one timed-out retry. State the invariant after each step.  
> **Assessment coverage:** 6 of 6 areas assessable. This is feedback on one case response, not a job-readiness rating.

## Report acceptance checks

Use synthetic scored responses to verify every `0–4/NA/UNK` state, missing reveal, ASR deletion and correction, independent-rater disagreement, retired case, withdrawn purpose and report version update. Check that the API never returns hidden `FM-07/08`, raw other-rater notes, protected cohort labels or a percentile placeholder. Participant comprehension interviews must test whether readers mistake `FM-03/05` for ability and whether an exercise feels grounded in their actual answer. E08 measures feedback usefulness and burden; it cannot establish hiring validity.
