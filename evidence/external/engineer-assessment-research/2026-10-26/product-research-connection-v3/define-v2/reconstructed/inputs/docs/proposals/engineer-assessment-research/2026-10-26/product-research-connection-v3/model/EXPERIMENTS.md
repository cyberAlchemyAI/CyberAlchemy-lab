# Prospective experiment program

Status: design candidates. No participant study has begun. Each run requires a dated protocol, accepted purpose/data decisions, version pins and a results record that preserves failures. The detailed [scoring specification](../research/scoring-model.md), [full experiment protocol](../research/full-protocol.md) and [evidence review](../research/evidence-review.md) are the current authoring inputs; role-specific registration choices remain open.

## Measurement model

The first session is deliberately an **unusual-problem creativity assessment**. Its case families include linked riddles with hidden assumptions, object/animal feature explanations, constrained counterfactuals and unfamiliar engineering analogies. A familiar elephant/fridge/jungle sequence is a development example only: it is too exposed to use as a scored item. A prompt must allow multiple defensible approaches; the key records constraints, plausible alternatives and traps. Score observable behaviors separately: problem representation, assumptions tested, generation of alternatives, useful originality, evidence/constraint evaluation, revision after a clue, and clarity of justification. Fluency alone, a single canonical punchline, humor, accent and speaking speed do not earn creativity points. Confirm which subdimensions generalize beyond a riddle.

Session 2 presents a role-relevant product and software-design problem with changing requirements. Score clarification, tradeoffs, architecture boundaries, failure and operating modes, security/privacy where relevant, product impact, and revision. Avoid trivia tied to one stack. Session 3 presents a cooperation conflict or game with incentives and incomplete information. Score stakeholder modeling, reciprocal strategy, communication, credit allocation, conflict repair and ethical constraints. A narrated answer cannot by itself establish real teamwork; observed work outcomes are a separate criterion.

The primary score is a predeclared weighted composition of anchored criteria, with separate session and uncertainty reports. Weight choices must be justified by role analysis and pilot evidence, frozen before validation, and examined in sensitivity analysis. AI extracts evidence spans and offers provisional criterion ratings. Two trained, blind human raters score a calibration subset without AI suggestions; adjudicate disagreements using a documented rule. Assess transcript-only, corrected transcript and direct-media human scoring to quantify ASR loss. Never infer emotion, personality, honesty or protected traits from voice or face.

## Experiment matrix

| ID / sequence | Design, comparator and outcome | Falsifier / stop signal |
| --- | --- | --- |
| EA-E01 role and construct map | Job analysis with engineers, managers and incumbents for one role/level; map tasks to creativity, design and cooperation behaviors; cognitive interviews on prompts. | No credible link from a case behavior to consequential job work. |
| EA-E02 case generation | Generate and review variants separately for creativity riddles, technical/product design and cooperation dilemmas; audit family coverage, solvability, role relevance, leakage, surface/reasoning repetition and ten-minute feasibility. | Any session's family produces exposed, ambiguous, culturally loaded or unstable forms. |
| EA-E03 scoring calibration | Freeze three separate rubrics; obtain blind expert/AI ratings of diverse answers for each session; measure criterion agreement, valid alternative treatment and transcript-mode error per session. | A session's rating rewards polish, jargon or an expected punchline over relevant evidence. |
| EA-E04 generalizability | Counterbalance parallel forms for each session; estimate participant, case, domain, rater, mode and interactions before considering a combined score. | A session's case sampling leaves decision error too large for its intended use. |
| EA-E05A creativity transfer | Compare Session 1 with independent creative engineering work and expert assessment; test prior exposure and added value over the other sessions. | Riddle score tracks familiarity/verbal fluency but not useful creative output. |
| EA-E05B technical design transfer | Compare Session 2 with an unseen design work sample, later design artifacts and an equal-time written/diagrammed task. | Verbal architecture score does not predict independent design quality or adds no value. |
| EA-E05C cooperation transfer | Compare Session 3 with observed team coordination, later collaboration evidence and a structured situational-judgment task; vary game versus work case and response instructions. | Stated strategy fails to predict behavior, or instruction/game familiarity dominates. |
| EA-E06 prospective prediction | For consented candidates across employers, freeze all three scores before outcomes; compare the combined policy with a longer pipeline and equal-time comparator, and run predeclared 1/2/3-session ablations. Independent work-quality, design and cooperation criteria are rated blind where possible. | The combined policy misses its target; a session adds no value; effects vanish in employer/time holdouts. |
| EA-E07 fairness and access | Audit completion, ASR error, criterion error, calibration, false rejection, accommodation and burden by session, lawful voluntary analysis group and response mode. | A session has material unexplained disparity, inaccessible administration or insufficient subgroup evidence. |
| EA-E08 product value | Randomized or phased challenge feedback and employer workflow comparison; measure useful feedback, candidate time, employer time, downstream quality and cost. | Benefit is trivial, feedback misleads, or burden exceeds accepted threshold. |

The [product success scorecard](PRODUCT-SUCCESS-METRICS.md) operationalizes phase-specific completion, usefulness, evidence quality, decision utility and economic measures. E08 satisfaction or adoption cannot substitute for E06 independent performance outcomes.

The [product–research trace](PRODUCT-RESEARCH-TRACE.md) names the product capability and claim each experiment tests, the metric/result it can inform and the versioned product decision after a supported, contradicted or inconclusive finding. No experiment below has yet produced a run or finding.

## E06 protocol choices to freeze before recruitment

Session-specific protocols: [Session 1](../research/session-1-creativity.md), [Session 2](../research/session-2-technical-design.md), [Session 3](../research/session-3-cooperation.md). E05A-C test whether each session measures and predicts its proposed construct before the E06 composite is interpreted. Do not assume a strong combined score validates a weak individual session.

Define role `R`, pool `P`, future outcome `Y` at horizon `T`, hiring capacity `C`, existing-policy comparator `L` and equal-time comparator `Q`. Predeclare the primary estimand as selection utility or quality of the top `C` under each policy, with confidence interval and a material non-inferiority margin `delta` for `3x10 - L`; also predeclare an absolute floor and superiority margin against `Q`. These values require domain and cost input and are not invented here. Secondary outcomes include rank agreement, calibration, false rejection of later strong performers, applicant burden and incremental validity conditional on existing predictors.

Outcome labels must cover more than selected hires or the study suffers selective-label bias. Prefer follow-up across all assessed candidates where lawful and feasible, or a design with randomized/stratified opportunity and defensible missing-outcome analysis. If only hired candidates have outcomes, explicitly label inference as conditional and do not claim selection utility for the entire applicant pool. Blind outcome assessors; record attrition and missingness. Split by employer and time, hold out whole case families and model versions, and do not tune on the final test. Run power and precision simulation with pilot variance, base rate, capacity and clustering before setting sample size. A single convenient cohort cannot support a broad hiring claim.

## Question and model evals

Case Generator inputs are construct, role, case grammar, constraints, difficulty target, language/access modes and forbidden/exposed items. It produces candidates only; expert review releases immutable case versions. Automated screens test semantic near-duplicates, answer leakage, repeated underlying trick, ambiguous constraints, infeasible ten-minute reasoning, cultural dependence and overlap with held-out forms. Track item exposure and post-release drift; retire compromised families. Repetition is measured at surface and reasoning-pattern levels.

The [question lifecycle](../software/QUESTION-LIFECYCLE.md) specifies the E02 software records, rules, operations, review gates and evidence packet that implement this research design. Its static and human screens are development gates; case difficulty, form equivalence and transfer remain empirical questions.

Scoring evals use frozen answer/rubric sets with expert adjudication and adversarial cases: confident wrong answer, unusual valid answer, fluent bluff, concise strong reasoning, transcription deletion, accented speech, quiet audio, accommodation, game-theory jargon without cooperation, and memorized riddle. Report criterion-level agreement, evidence citation precision, calibration, subgroup error and decision stability. A score version cannot be changed mid-cohort without separate bridging evidence.

## Reporting rule

Each experiment yields an `ExperimentRun` with planned versus actual procedure, exclusions, source/version receipts, descriptive counts, effect estimates with uncertainty, subgroup limitations, null/negative findings, deviations and an explicit supported/contradicted/inconclusive conclusion. A positive laboratory proxy never silently promotes to a hiring-use claim.
