# Prospective experiment program

Status: design candidates. No participant study has begun. Each run requires a dated protocol, accepted purpose/data decisions, version pins and a results record that preserves failures.

## Measurement model

The first session is deliberately an **unusual-problem creativity assessment**. Its case families include linked riddles with hidden assumptions, object/animal feature explanations, constrained counterfactuals and unfamiliar engineering analogies. A familiar elephant/fridge/jungle sequence is a development example only: it is too exposed to use as a scored item. A prompt must allow multiple defensible approaches; the key records constraints, plausible alternatives and traps. Score observable behaviors separately: problem representation, assumptions tested, generation of alternatives, useful originality, evidence/constraint evaluation, revision after a clue, and clarity of justification. Fluency alone, a single canonical punchline, humor, accent and speaking speed do not earn creativity points. Confirm which subdimensions generalize beyond a riddle.

Session 2 presents a role-relevant product and software-design problem with changing requirements. Score clarification, tradeoffs, architecture boundaries, failure and operating modes, security/privacy where relevant, product impact, and revision. Avoid trivia tied to one stack. Session 3 presents a cooperation conflict or game with incentives and incomplete information. Score stakeholder modeling, reciprocal strategy, communication, credit allocation, conflict repair and ethical constraints. A narrated answer cannot by itself establish real teamwork; observed work outcomes are a separate criterion.

The primary score is a predeclared weighted composition of anchored criteria, with separate session and uncertainty reports. Weight choices must be justified by role analysis and pilot evidence, frozen before validation, and examined in sensitivity analysis. AI extracts evidence spans and offers provisional criterion ratings. Two trained, blind human raters score a calibration subset without AI suggestions; adjudicate disagreements using a documented rule. Assess transcript-only, corrected transcript and direct-media human scoring to quantify ASR loss. Never infer emotion, personality, honesty or protected traits from voice or face.

## Experiment matrix

| ID / sequence | Design, comparator and outcome | Falsifier / stop signal |
| --- | --- | --- |
| EA-E01 role and construct map | Job analysis with engineers, managers and incumbents for one role/level; map tasks to creativity, design and cooperation behaviors; cognitive interviews on prompts. | No credible link from a case behavior to consequential job work. |
| EA-E02 case generation | Generate variants from explicit case grammars; blind expert review of solvability, originality, job relevance, unintended knowledge and ambiguous keys; adversarial/test-taker review; embargo held-out variants. | Item leakage, near duplicates, single-answer bias or unstable difficulty. |
| EA-E03 scoring calibration | Freeze rubric; blind expert/AI ratings of diverse pilot answers; measure rater agreement, criterion discrimination and transcript-mode error. | Weak agreement near decision threshold, model evidence fabrication, or systematic ASR-driven score shifts. |
| EA-E04 generalizability | Counterbalanced parallel forms and repeated administrations where feasible; estimate participant, case, rater, mode and interaction variance with generalizability theory or suitable mixed models. | Three cases leave decision error too large; add stations, change cases or narrow use. |
| EA-E05 construct tests | Compare first-session ratings with independent creative engineering work samples and expert consensual ratings; test incremental value after role experience and baseline reasoning measures. | Riddle score tracks familiarity/verbal fluency but not relevant creative output. |
| EA-E06 prospective prediction | For consented candidates across employers, freeze scores before outcomes; compare three-session policy with existing longer pipeline and equal-time structured work sample. Outcomes at a declared horizon from independent work-quality, delivery, collaboration and incident evidence, scored blind to assessment where possible. | Predeclared absolute target or non-inferiority margin fails; equal-time comparator wins; effects vanish across employer/time holdouts. |
| EA-E07 fairness and access | Audit completion, ASR error, criterion error, calibration, false rejection, accommodation and participant burden by lawful, voluntary analysis groups and response mode. | Material unexplained disparity, inaccessible route, or subgroup sample too small for a use claim. |
| EA-E08 product value | Randomized or phased challenge feedback and employer workflow comparison; measure useful feedback, candidate time, employer time, downstream quality and cost. | Benefit is trivial, feedback misleads, or burden exceeds accepted threshold. |

## E06 protocol choices to freeze before recruitment

Define role `R`, pool `P`, future outcome `Y` at horizon `T`, hiring capacity `C`, existing-policy comparator `L` and equal-time comparator `Q`. Predeclare the primary estimand as selection utility or quality of the top `C` under each policy, with confidence interval and a material non-inferiority margin `delta` for `3x10 - L`; also predeclare an absolute floor and superiority margin against `Q`. These values require domain and cost input and are not invented here. Secondary outcomes include rank agreement, calibration, false rejection of later strong performers, applicant burden and incremental validity conditional on existing predictors.

Outcome labels must cover more than selected hires or the study suffers selective-label bias. Prefer follow-up across all assessed candidates where lawful and feasible, or a design with randomized/stratified opportunity and defensible missing-outcome analysis. If only hired candidates have outcomes, explicitly label inference as conditional and do not claim selection utility for the entire applicant pool. Blind outcome assessors; record attrition and missingness. Split by employer and time, hold out whole case families and model versions, and do not tune on the final test. Run power and precision simulation with pilot variance, base rate, capacity and clustering before setting sample size. A single convenient cohort cannot support a broad hiring claim.

## Question and model evals

Question generator inputs are construct, role, case grammar, constraints, difficulty target, language/access modes and forbidden/exposed items. It produces candidates only; expert review releases immutable case versions. Automated screens test semantic near-duplicates, answer leakage, repeated underlying trick, ambiguous constraints, infeasible ten-minute reasoning, cultural dependence and overlap with held-out forms. Track item exposure and post-release drift; retire compromised families. Repetition is measured at surface and reasoning-pattern levels.

Scoring evals use frozen answer/rubric sets with expert adjudication and adversarial cases: confident wrong answer, unusual valid answer, fluent bluff, concise strong reasoning, transcription deletion, accented speech, quiet audio, accommodation, game-theory jargon without cooperation, and memorized riddle. Report criterion-level agreement, evidence citation precision, calibration, subgroup error and decision stability. A score version cannot be changed mid-cohort without separate bridging evidence.

## Reporting rule

Each experiment yields an `ExperimentRun` with planned versus actual procedure, exclusions, source/version receipts, descriptive counts, effect estimates with uncertainty, subgroup limitations, null/negative findings, deviations and an explicit supported/contradicted/inconclusive conclusion. A positive laboratory proxy never silently promotes to a hiring-use claim.
