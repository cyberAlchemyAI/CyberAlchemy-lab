# Engineer assessment: product and research brief

Status: **proposal, 2026-10-25**. This is a candidate product direction and prospective research program, not an admitted Lab product, validated hiring test, or authorization to collect applicant data.

## Product thesis

**Ambition.** Test the strongest version of the compact-assessment thesis: for a specified engineering role and candidate pool, no more than three recorded case sessions of ten minutes each can identify candidates who later perform best at the job at least as well as a substantially longer hiring process. Give participants useful, specific feedback on the reasoning they demonstrated. Test whether AI can make question generation, transcription, scoring, and evidence review affordable.

**Central research question.** How much future engineering performance can be inferred from three short, carefully chosen responses? The 30-minute limit and three-session maximum are hypotheses to challenge experimentally. A case answer is an observation under one condition; the project investigates whether the *combined observations* are sufficient for accurate selection. Until tested, any candidate ranking is an experimental prediction, not an established fact about the person. A public challenge score and an employment selection score require different evidence and governance.

**Customers and participants.** Engineering hiring teams are the possible paying users. Engineers taking a challenge are participants, potential beneficiaries, and the people exposed to the greatest assessment risk. The first research cohort can be voluntary challenge participants; that cohort alone cannot establish predictive validity for hiring.

**Product promise to test.** For a defined software engineering role, a candidate can complete up to three sessions of at most ten minutes each and receive a clear report with behavior-level evidence and uncertainty. Test whether the resulting score can support the selection decision itself, including whether it outperforms existing processes at finding later high performers. Any actual employment use needs role-specific validity and fairness evidence.

## Assessment blueprint

Begin with one role family and level, for example a mid-level backend engineer, and a job analysis of actual tasks and critical incidents. The [US Office of Personnel Management](https://www.opm.gov/policy-data-oversight/assessment-and-selection/job-analysis/) describes job analysis as the basis for selection design. Its [structured interview guidance](https://www.opm.gov/policy-data-oversight/assessment-and-selection/other-assessment-methods/structured-interviews/) supports predetermined, job-related questions, rating anchors, and consistent administration. The three sessions below are candidate designs, not validated measures.

| Session | What the candidate does | Intended observations | Open question |
| --- | --- | --- | --- |
| 1. Creative problem solving | Work through a short chain of riddles, an unusual object or animal explanation, or a surprising constraint change; invent and test possible answers aloud. | Creativity, analysis, and ingenuity: assumption shifts, distinct plausible ideas, causal reasoning, useful invention, and revision. | Does performance on these unfamiliar problems predict creative engineering problem solving and later work outcomes? |
| 2. Design under constraints | Propose a small service or feature from a product brief, then respond to a changed constraint such as scale, privacy, or failure recovery. | Requirement discovery, trade-offs, interfaces, failure modes, and user impact. | Does this response predict later implementation and design performance? |
| 3. Coordinate a decision | Respond to a realistic disagreement about ownership, deadlines, risk, or credit; prepare a message and a decision process for teammates. | Stakeholder awareness, explicit trade-offs, conflict handling, and communication. | Can a compact case predict observed cooperation and communication at work? |

The Lab's [novelty preparation](../../../../docs/proposals/hammer-bias-strategies/novelty/future-preparation/2026-10-09/NOVELTY-LAB-PROMPT.md) offers useful patterns for session 1: preserve the desired outcome, name the assumption being changed, compare rival explanations, and propose a separating probe. That prompt is explicitly unrun and grants no evidence that its questions predict engineering performance.

### Session 1: what the riddles are for

Riddles and tricky problems are the **primary material** in session 1. Their purpose is to elicit creative problem solving, not just a correct punchline. The elephant-in-the-fridge followed by the jungle-party question is a useful *illustration* of a linked case: it can reveal whether a candidate recognizes that an earlier move changed the state of the later problem. It is already familiar to many people, so use new, unreleased variants for scored research and ask about prior exposure. Other families can ask why an object or animal has certain characteristics, invite multiple causal explanations, and then reveal a new observation that makes the candidate revise them. Give enough facts to reason from so the exercise does not mainly test trivia knowledge.

Use the ten-minute response budget for a short sequence within one case: initial answer, alternative explanation or construction, changed constraint or new fact, then a revised answer and a way to test it. This lets the assessment observe both idea generation and selection. The first-session construct is **creative reasoning under constraints**: generate an unexpected but usable move, analyze why it could work, and revise it when reality pushes back. The engineering-hiring hypothesis is that this pattern transfers to unfamiliar technical work. The case can be playful while the scoring remains tied to observable reasoning.

Creativity research offers useful measurement starting points. [Amabile's consensual assessment technique](https://doi.org/10.1037//0022-3514.43.5.997) motivates independent expert judgments of creative products; research on [divergent-thinking scoring](https://doi.org/10.1002/j.2162-6057.2011.tb01081.x) shows that scoring method changes conclusions. [Engineering-design assessment research](https://www.cambridge.org/core/journals/ai-edam/article/systematic-approach-to-assessing-novelty-requirement-satisfaction-and-creativity/3385C36C4678F2223535AC90D681AD5D) pairs novelty with requirement satisfaction. These sources support evaluating *what the candidate constructs and whether it works under the stated conditions*, rather than counting unusual words or rewarding surprise alone. An [insight-problem study](https://pubmed.ncbi.nlm.nih.gov/18411549/) also shows why assumption changes and problem structure deserve explicit study. None of these sources establishes predictive validity for this exact session.

Proposed session-1 rubric, each dimension scored with anchored examples and an evidence excerpt:

| Dimension | Observable evidence |
| --- | --- |
| Analysis | Identifies operative facts, dependencies, hidden assumptions, and consequences of earlier moves. |
| Divergence | Produces meaningfully different plausible approaches, without rewarding sheer answer count. |
| Ingenuity | Changes a constraint, representation, mechanism, or use of available resources to create an effective option. |
| Evaluation | Checks a proposed answer against the goal and constraints; distinguishes clever wording from a workable solution. |
| Revision | Updates the model after a new fact, explains what changed, and proposes a discriminating test or counterexample. |

Keep an independent expert creativity judgment as a comparator to the analytic rubric. Ask raters to score the *best developed idea* and its reasoning as well as the whole response, so verbosity does not automatically win. Compare three families: linked-state riddles, causal explanation puzzles, and constraint-changing invention problems. Test which family or mixture best predicts later creative engineering tasks. Record prior exposure, language, cultural familiarity, and the effect of coaching or AI assistance. A poor result from one riddle family calls for a better family or scoring model before rejecting the creativity-session thesis.

Session 3 separately investigates strategic cooperation. A prisoner's dilemma case can test strategic reasoning and willingness to revise after another actor responds. A branching case can make the stated strategy more informative. [OPM's SJT guidance](https://www.opm.gov/policy-data-oversight/assessment-and-selection/other-assessment-methods/situational-judgment-tests/) supplies a job-related comparator for that session.

For every session, freeze the brief, allowed preparation time and tools, language, recording rules, follow-up policy, and scoring anchors. Test whether ten minutes gives enough evidence for each construct. If the cap fails, report that result explicitly while retaining it as the central research constraint. Within ten minutes, test both a single monologue and a case with two or three information reveals or decisions. Video may help candidates present themselves, but the initial scoring path should use response content only. Do not infer emotion, personality, honesty, or "culture fit" from faces, voice, accent, timing, or background.

## Question generation and item bank

1. **Blueprint.** Define the role, construct, difficulty target, case family, evidence expected, and prohibited cues before generating prompts. For session 1, make creativity, analysis, and ingenuity explicit targets and vary the kind of assumption or mechanism the riddle requires.
2. **Generate.** Produce multiple candidates from distinct incident templates and controlled constraint variations. Save generator model/version, prompt, source packet, random seed when available, and generation date.
3. **Review.** Engineering subject-matter experts and assessment specialists check job relevance, plausibility, solvability in the time limit, multiple defensible answers, accessibility, and unintended cultural knowledge.
4. **Control exposure.** Store a canonical item ID, family ID, semantic similarity cluster, version, exposure count, leak status, and retired status. Use similarity checks as triage, then human review for near-duplicate reasoning paths. Keep scored and development items separate.
5. **Pilot and calibrate.** Randomize comparable items across participants; retain common anchor cases so form difficulty can be estimated. Report item difficulty, score distribution, rater disagreement, time to complete, and subgroup signals. Generated items are not automatically equivalent. Test equating and item response methods only once sample sizes and model fit support them; [ETS guidance on test equating](https://www.ets.org/Media/Research/pdf/LIVINGSTON2ed.pdf) explains the common-item design.

**Question evals:** novelty relative to the bank, construct coverage, answerability, constraints that allow ingenious moves, reasoned alternatives, leakage, language burden, and discriminating value. For session 1, reviewers should show at least two defensible approaches or transformations and identify what new information would distinguish them. An item passes only if reviewers can explain which observable response would support each rubric anchor. Fluency, surprise, and a low similarity score are insufficient quality evidence.

## Scoring and feedback

Use an analytic rubric for each observable construct. For session 1, anchor analysis, divergence, ingenuity, evaluation, and revision separately. An example ingenuity progression is **0 = no usable construction**, **1 = repeats the obvious move**, **2 = changes a relevant assumption or mechanism**, **3 = creates a distinct, feasible move, tests it against the constraints, and improves it after a challenge**. A candidate can also earn analysis credit by finding a flaw in the riddle's premise. An unconventional but sound answer must remain scoreable. Score missing evidence as missing evidence, not as a personality deficit.

Two trained human raters independently score a development set before AI scoring is evaluated. Keep response excerpts linked to every criterion. Resolve disagreements under a written rule and preserve both original ratings. Compare AI suggestions against independent raters, consensus, and adjudicated cases. Inspect systematic severity, false confidence, and whether the model rewards polish or jargon over substance. The [AERA/APA/NCME testing standards](https://www.testingstandards.net/uploads/7/6/6/4/76643089/standards_2014edition.pdf) frame validity around the intended interpretation and use of scores; agreement with a rater is one piece of evidence, not the whole claim.

Transcription is a separate measurement stage: preserve source recording, transcript, corrected transcript when supplied, ASR confidence or error markers, model/version, and scoring input. Make uncertain passages reviewable and allow correction or an alternative response mode. [Koenecke et al.](https://pubmed.ncbi.nlm.nih.gov/32205437/) found large racial disparities in the speech recognizers they tested; our exact stack and participant languages need their own error study. Run a controlled comparison of scores from verified transcripts and machine transcripts before allowing unreviewed transcription to affect feedback.

The first release should show criterion-level feedback with evidence and limits. Avoid a single percentile or pass/fail hiring threshold until forms are comparable, score error is measured, and intended decision use is validated. Evaluate feedback usefulness separately from assessment validity.

### Formal scoring models to compare

Treat these as competing research models, not an escalation ladder that guarantees a valid score:

| Model | Question it answers | Test before adoption |
| --- | --- | --- |
| Transparent rubric sum/profile | Can trained raters apply observable anchors consistently? | Criterion-level agreement, score stability, sensitivity to item choice, and usefulness of feedback. |
| Generalizability analysis | How much score variation comes from candidate, case, rater, occasion, and their interactions? | Whether three cases and the planned number of raters yield tolerable decision error; [performance-assessment comparison](https://pubmed.ncbi.nlm.nih.gov/19934528/). |
| Many-facet ordinal/Rasch model | Can case difficulty and rater severity be estimated without distorting the construct? | Model fit, connected rating design, subgroup invariance, calibrated uncertainty; [rater severity study](https://onlinelibrary.wiley.com/doi/10.1111/j.1745-3984.1994.tb00436.x). |
| AI rubric assistant | Can a pinned model identify relevant evidence and suggest a rating? | Held-out agreement and calibration against humans, especially for ambiguous and unconventional valid answers; [constructed-response validity argument](https://arxiv.org/abs/2501.02334). |

Never choose a formal model because it outputs a precise number. Compare it against a simple transparent baseline on preregistered outcomes, including error and subgroup behavior. Keep the dimension profile even if a composite eventually becomes useful. Determine any weights and cut score from the role and validation evidence, not from model convenience.

## Research program and predeclared experiments

### Break the 30-minute assumption

**Assumption under attack:** three ten-minute answers cannot contain enough information to identify the engineers who will perform best. The literature does not establish that limit. A [meta-analysis of interview length](https://doi.org/10.1111/joop.12186) found no association between length and interview reliability or predictive validity across its included studies. In another field, a [three-station, eight-minute-per-station medical admissions study](https://pubmed.ncbi.nlm.nih.gov/26873767/) found correlations between total interview scores and later academic outcomes ranging from 0.17 to 0.43. These findings make a compact test plausible; neither validates three recorded engineering cases. A [12-station medical study](https://pubmed.ncbi.nlm.nih.gov/19659490/) also illustrates a competing concern: independent situations may be needed to average away case-specific noise. A [2025 meta-analysis](https://doi.org/10.1111/ijsa.12494) found interview ratings predicted aligned task and contextual outcomes, with question-level scoring especially useful for contextual performance. The open question is how much *our three cases* can capture.

The strongest mechanism hypothesis is **information density, not duration**. A well-designed case may elicit several diagnostic moves: a first model, response to new evidence, a revised decision, and a concise explanation. AI may extract and compare these moves consistently. Three deliberately different cases may capture enough transferable strategy to beat a longer process dominated by redundant or weak questions. This is a proposed mechanism, not a finding. A rival hypothesis is that three cases mainly capture case familiarity, verbal fluency, or luck; then ranking will change substantially with different cases.

Define **"best" before seeing scores**: for a specified role and level, candidates whose later, independently assessed work outcomes fall in a predeclared high-performance band. Use a multidimensional criterion: quality and maintainability of shipped work, novel and effective solutions to unfamiliar problems, useful collaboration, and delivery under the job's actual constraints. Give the creative-problem-solving outcome its own measure so session 1 can be tested directly before testing the whole three-session selection claim. Avoid using the hiring decision or the assessment score itself as the outcome. Specify the time horizon, who rates the work, and how disagreements are resolved. There is no universal best engineer independent of the role and criterion.

**Prospective comparison:** give every research participant the same 30-minute maximum assessment, a conventional structured interview, and a role-relevant work sample, in randomized order where feasible. Collect an independent outcome for *all* participants through a later standardized, unseen engineering simulation; where possible, also follow hired participants' job outcomes under a blinded evaluation plan. Keep the 30-minute score hidden from hiring decisions in the initial study. This avoids defining success only among people selected by an existing process, although the simulation remains an imperfect proxy for real work. A later controlled hiring-partner study can test actual decision use.

Compare four locked decision policies: (A) the current pipeline, (B) the three-case score alone, (C) current pipeline plus three-case score, and (D) the best conventional method that fits the same 30-minute candidate-time budget. Also compare 1, 2, and 3 cases to estimate information gained per minute. Freeze cases, scoring model, weights, thresholds, outcome definition, and analysis before the confirmatory cohort. Use held-out people, case families, employers, and time periods; a validation result on reused items is development evidence.

Report **top-group recall and precision, pairwise ranking quality, calibration, false-negative rates, and selection utility at the same hiring capacity**, with uncertainty intervals and subgroup results. Also report candidate burden and employer cost. Predeclare a minimum absolute decision-quality target, a meaningful non-inferiority margin against the current pipeline, and a superiority test against the equal-time comparator. Choosing these targets requires a power and decision-cost analysis, not a convenient round number. The strong thesis survives only if three cases reach those decision-quality targets on independent cohorts without unacceptable fairness or access costs. A weaker but still useful outcome is that the score improves an existing process; report that as a different finding.

**Defeat conditions:** rankings swing sharply across equivalent case sets; transcript or response mode changes alter selection; the model mainly rewards polished speech; results disappear after accounting for prior question exposure; subgroup error is unacceptable; the score fails on held-out employers or later job outcomes; or a cheaper equal-time method performs as well. Preserve these failures in the public research record.

| Study | Comparison and outcome | Counterevidence / gate |
| --- | --- | --- |
| Job analysis and construct map | Interview hiring managers and engineers, sample real incidents, map each rubric criterion to role tasks. | If a construct lacks job relevance, remove it from hiring use. |
| Creativity case-family pilot | Compare linked-state riddles, causal explanation puzzles, and constraint-changing invention problems with a conventional engineering case. Measure creativity ratings, analytic-rubric stability, prior-exposure effects, and later creative engineering outcomes. Randomize order and freeze prompts. | If a family mostly measures recognition of known answers or verbal fluency, redesign that family and test whether another riddle type captures the intended construct. |
| Recording mode pilot | Compare video, audio, and text on completion, accessibility, rater stability, and candidate reactions. | If video adds little relevant evidence or creates inequitable burden, offer an equivalent mode. |
| Rubric and AI pilot | Score frozen cases with independent trained humans, a simple rules baseline, and version-pinned AI. Use held-out candidates and items. | If agreement is weak on ambiguous answers or group error differs, AI remains a review aid. |
| Transcript perturbation | Compare expert-corrected and ASR transcripts across languages, accents, audio quality, and assistive speech. | Material score changes from transcription require correction or human review. |
| Form comparability | Repeated/parallel items and anchor cases; estimate test-retest stability, item effects, and uncertainty. | Unstable or incomparable forms block ranking. |
| Criterion and incremental validity | With consenting hiring partners, compare the three-case policy, the current pipeline, their combination, and an equal-time comparator against later independent outcomes, using a preregistered analysis. | Failure to meet the predeclared selection-quality margin or unacceptable adverse impact defeats the strong thesis. |

Define sampling, exclusion rules, sample-size/power plan, subgroup analysis, stopping conditions, and analysis code before each study. Voluntary challengers are a convenience sample with self-selection and practice effects; leaderboards intensify those effects. They are useful for usability, question diagnostics, and early rubric tuning, but cannot alone establish who employers should hire. Preserve untouched cases and participants for final tests. Do not tune on the held-out set.

The recent [Sackett et al. reanalysis](https://pubmed.ncbi.nlm.nih.gov/34968080/) cautions against treating familiar meta-analytic validity estimates as fixed promises for a new local assessment. The [OPM assessment strategy](https://www.opm.gov/policy-data-oversight/assessment-and-selection/assessment-strategy/) calls for role analysis, consistency, validation, and candidate feedback. The [NIST AI RMF measurement guidance](https://airc.nist.gov/airmf-resources/airmf/5-sec-core/) supplies a useful process for documenting uncertainty, fairness, privacy, and ongoing evaluation.

## Product flow and data boundary

The first useful prototype can be: role selection -> one case -> accessible response capture -> transcript review -> rubric-based draft feedback -> human quality review -> participant report. Add the second and third sessions only after each contributes distinct, stable evidence. Track invitation, consent, exposure, completion, transcript correction, scoring, appeal, and deletion as separate events. Pin the exact item, rubric, model, prompt, transcription version, and report for reproducibility.

As a Lab portfolio project, publish the product thesis, case-design method, rubric examples, evaluation code, model/version cards, aggregate experiment results, and failures or revisions. Use synthetic or expressly licensed examples in the public demo. Real participant recordings and transcripts need a separate access and retention policy; public reproducibility does not require exposing them.

Explain the purpose, scoring inputs, retention, sharing, and deletion before recording. Separate consent to receive feedback from consent to use the response for research or model improvement. Publish aggregate findings only after privacy review and with small-group protection. Provide a non-video route, accessible controls and captions/transcripts, clear accommodation request path, and a human review/contest path before any employment use.

Jurisdiction-specific legal review is a launch gate, not a feature toggle. The [EEOC](https://www.eeoc.gov/laws/guidance/employment-tests-and-selection-procedures) says US employers remain responsible for job-related, validated selection procedures; its [disability guidance](https://www.eeoc.gov/laws/guidance/visual-disabilities-workplace-and-americans-disabilities-act) addresses alternative assessment formats. The [EU AI Act](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32024R1689) treats AI used to evaluate candidates as high risk. [New York City's AEDT rules](https://www.nyc.gov/site/dca/about/automated-employment-decision-tools.page) may require audit and notice for covered uses. Brazil's [ANPD guidance](https://www.gov.br/anpd/pt-br/assuntos/titular-de-dados-1/direito-dos-titulares) explains rights around automated decisions and information about their criteria. Applicability depends on the exact product and deployment; counsel should review the intended markets before hiring use.

## Blind spots and decisions

- **"Best" is undefined.** Specify role, level, team context, and future outcome before ranking anyone.
- **Coverage is unresolved.** Coding, debugging in a real codebase, review, sustained delivery, and live collaboration are not directly performed in three recorded cases. Test whether case responses nevertheless predict those outcomes well enough for selection.
- **Stated cooperation differs from observed cooperation.** Consider a later interactive simulation with another person or agent, and validate whether its behavior relates to workplace outcomes.
- **Dynamic questions damage comparability.** Generated prompts need family controls, anchors, calibration, and item exposure management.
- **Practice, coaching, and AI assistance change the signal.** State an allowed-AI policy. Measure coached and uncoached performance rather than treating either as inherently illegitimate; real engineering often uses AI.
- **Transcript errors can become score errors.** Measure both stages separately and offer correction.
- **Video introduces avoidable personal signals.** Begin with content scoring and test the need for video at all.
- **Challenge data has selection bias.** Recruitment source, dropout, repeat attempts, language, and motivation must be measured; a public score is not a representative norm.
- **A single score hides uncertainty.** Report dimensions, evidence, confidence limits, and unobserved skills.
- **Employer incentives may conflict with participant welfare.** Participant feedback, appeals, privacy, and fair access are part of the product promise, not merely compliance work.

## Market and research scan: starting sources

The peer-reviewed [algorithmic hiring practices study by Raghavan et al.](https://doi.org/10.1145/3351095.3372828) is a useful warning about vendor validation and bias claims. [Karat's 2024 hiring survey](https://connect.karat.com/hubfs/Karat_2024_Hiring_Trends_Report.pdf) reports widespread structured interviewing and meaningful invitation-to-completion friction among surveyed engineering leaders. [HackerRank's 2025 developer survey](https://embed.hackerrank.com/reports/developer-skills-report-2025) reports a preference for realistic tasks and concerns about test relevance and AI gaming. These vendor studies provide market hypotheses and candidate-experience questions; they do not validate this product. A systematic literature review remains to be done across personnel selection, situational judgment tests, work samples, asynchronous interviews, automated scoring, ASR fairness, accessibility, and test security, with inclusion criteria and a dated evidence table.

## First build and advancement gates

1. Write one role-specific job analysis and a reviewed bank with multiple cases for each of the three sessions. Keep frozen anchor and held-out families.
2. Build the three-session challenge prototype within the 30-minute total answer limit, with transcript correction and evidence-linked scoring. Test usability and access.
3. Run human-rater, ASR, case-sampling, and repeated-form pilots; publish methods, negative results, and uncertainty alongside any promising result.
4. Run the prospective comparison of the three-case policy, current pipeline, combined policy, and equal-time comparator. Publish the 1/2/3-case information curve.
5. Seek actual hiring-use validation after the research protocol, privacy design, accommodations, and legal review are ready. Do not use an experimental score as an employment filter before those gates pass.

**First falsifiable product question:** Can three recorded cases, each at most ten minutes, identify later high-performing engineers as accurately as the current longer pipeline, and better than a conventional equal-time assessment, for one defined role? Case quality, scoring, and response mode are experimental variables inside that fixed budget.
