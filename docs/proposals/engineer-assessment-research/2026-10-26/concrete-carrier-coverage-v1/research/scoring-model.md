# Formal scoring models and interpretation limits

Status: candidate measurement specification, version `EA-SCORE-0.1`. Equations define testable models, not fitted parameters or validated hiring scores. Keep raw ratings, uncertainty and model version. The [full experiment protocol](full-protocol.md) decides whether any model is usable.

The canonical task-local meanings for Criterion Rating, Scoring Specification, Measurement Uncertainty, Estimand, Decision Threshold and the six proposed abilities are in [definitions.json](../model/definitions.json); this document specifies one candidate way to measure them.

## 1. Observation and evidence model

For participant `i`, session `s ∈ {1,2,3}`, case `c`, rubric dimension `d`, rater `r`, response mode `m` and score version `v`, store `Y[i,s,c,d,r,m,v] ∈ {0,1,2,3,4}` and linked evidence spans. `NA` means the case did not offer a fair opportunity, `UNK` means the response was inaudible/missing, and `0` means a clear opportunity with no relevant evidence. Never convert `NA` or `UNK` to zero. An answer has a timestamped case/reveal transcript, candidate correction record, rater decision, confidence and disagreement reason. Raw audio/video are held separately under the approved data schedule; visual appearance and vocal affect are outside the score.

Every rubric anchor uses the same *strength* scale: `0` absent or contradicted when elicited; `1` claim without usable reasoning; `2` plausible reasoning with a material gap; `3` defensible, specific and constraint-aware reasoning; `4` strong evidence that survives the reveal/counterargument and identifies residual risk. Case-specific exemplars explain what this means for each dimension. Raters must cite evidence for `2–4` and a missed opportunity or contradiction for `0–1`. No score for word count, accent, speed, confidence, humor, jargon or eye contact.

## 2. Session-specific rubric vectors

| Session | Dimensions `d` | What the upper anchors require |
| --- | --- | --- |
| 1 creative reasoning | `R` representation, `A` assumption/causal test, `D` diverse viable alternatives, `N` useful originality, `F` feasibility/evidence, `V` revision | Candidate reframes a constraint or mechanism, develops a non-obvious **usable** option, tests it, and revises when facts change. `N` is judged on the best developed idea by blind subject experts, not the number of ideas or rare wording. |
| 2 design judgment | `Q` requirement discovery, `P` product prioritization, `B` boundaries/data flow, `T` quality-attribute tradeoff, `O` failure/operation/security where elicited, `V` revision | Candidate links architecture decisions to users and quality goals, explains a consequential tradeoff and revises coherently under changed constraints. Correct buzzwords without mechanisms remain low. |
| 3 cooperation judgment | `S` stakeholders/incentives, `C` concrete communication, `M` credible coordination/commitment, `E` equitable credit/risk allocation, `X` conflict repair, `V` adaptation | Candidate proposes a feasible message/decision, tests how parties may respond, assigns responsibility and credit transparently, and repairs a failed interaction. A cooperative-sounding choice alone is insufficient. |

Session 3 must additionally record prompt type `Z ∈ {best_action, likely_action, interactive}`. Report the three as **different measurements** until invariance and outcome transfer are shown. A pure game choice is recorded as an experimental feature, not folded automatically into the work-case score. Session 1 records riddle exposure and case family; Session 2 records domain/stack familiarity and access to diagrams. They are audit covariates, not covert score discounts.

## 3. Transparent reference score

For development only, obtain two independent trained human ratings per elicited dimension. After predeclared adjudication for disagreements of two or more anchor levels, use the median of available independent ratings as `H[i,s,c,d]`. With role-specific, **predeclared** nonnegative dimension weights `w[s,d]` summing to one over dimensions a case actually elicits, compute:

`S_ref[i,s,c] = 25 × Σ_d w[s,d] × H[i,s,c,d]`.

The `0–100` display is an arithmetic rescale of ordinal anchors, not an interval-scale psychometric claim. Do not rank candidates across cases on `S_ref` until case difficulty/equating evidence exists. Do not select a weight by maximizing validation outcomes on the final holdout. The default research diagnostic uses equal weights to expose behavior; final weights require role analysis, expert content review, and calibration data. The score report retains the six ratings and uncertainty, because a single total can hide critical omissions.

Safety-critical omissions (for example a privacy breach in a case whose requirements explicitly include privacy) receive their anchored dimension score. A hard veto is allowed only if the job analysis identifies a true minimum qualification, the prompt elicits it fairly, and a separate validation/decision review justifies the rule. Do not invent ad hoc vetoes after viewing answers.

## 4. Rater, case and mode measurement model

Fit a hierarchical **ordinal many-facet model** on the crossed calibration data, separately by session before pooling:

`logit Pr(Y[i,s,c,d,r,m] ≥ k) = θ[i,s,d] − b[s,c,d,k] − u[r,s,d] − q[m,s,d] + ξ[i,c,s,d]`, for `k=1..4`.

`θ` is person-by-dimension signal; `b` includes case/threshold difficulty; `u` rater severity; `q` mode effect; `ξ` person-by-case deviation. Enforce ordered thresholds and identifying constraints (for example centered rater and case effects), check posterior predictive fit/ordinal residuals and compare with a simpler cumulative-link mixed model. Include domain, language, accommodation and AI-assistance interactions only under an approved analysis plan. Do not treat the latent `θ` as meaningful when the design has too few connected cases to identify it. The reference score remains the fallback descriptive score.

In a generalizability study estimate variance components for person `p`, case `c`, rater `r`, mode `m`, and person×case/other relevant interactions. For a balanced illustrative `n_c` cases and `n_r` raters, relative decision error includes approximately `σ²_pc/n_c + σ²_pr/n_r + σ²_pcr/(n_c n_r)`; absolute error also includes case/rater main effects and mode terms. Calculate `G = σ²_p/(σ²_p+σ²_relative_error)` and the absolute-decision coefficient `Φ = σ²_p/(σ²_p+σ²_absolute_error)` for the actual operational design **one case per session**, then D-study alternatives with more cases or raters. Report bootstrap/posterior intervals and threshold disagreement probabilities. Reliability from the multi-case research battery cannot be claimed for a one-case product unless the D-study supports it.

Test case-form and response-mode **measurement invariance** with differential case/dimension functioning and direct method comparisons. If the same underlying response gets a materially different score from raw ASR, corrected transcript or expert review of recording, record a mode error; do not repair only by shifting the final score distribution. Calibrate criterion-level AI against blind human ratings, but also test atypical, concise, unusual-valid and adversarial responses. AI is an evidence extractor/provisional scorer until independent criterion and subgroup evidence support its use.

Fit and compare a common interview-performance factor across sessions with three correlated session factors, using only a design with multiple cases per session and enough observations. Test whether the intended session factor adds prediction of its **aligned** criterion beyond the common factor and whether cross-criterion associations are weaker. If a single verbal-polish factor explains the scores, report that finding rather than three distinct abilities. This directly addresses the construct-separation problem reported in [interview meta-analysis](https://onlinelibrary.wiley.com/doi/10.1111/ijsa.12494).

## 5. Combining sessions and making claims

The research composite is `T_i = Σ_s α_s × Z_s(S_ref[i,s])`, with `α_s ≥ 0`, `Σ_s α_s=1`, and `Z_s` a calibration-cohort transformation frozen before validation. The simple diagnostic starts with `α_s=1/3`; alternative weights are sensitivity analyses. Do **not** interpret `T_i` as an employability probability. A predictive model, if justified, estimates `Pr(Y_future ≥ y* | S_1,S_2,S_3,R,X)` in a training set and evaluates calibration, discrimination, net benefit and interval uncertainty on employer/time holdouts. `R` is the selected role and `X` includes predeclared baseline predictors; protected attributes are used only for approved auditing, not score inference. A single global model across unlike roles is out of scope without invariance and transport evidence.

Primary domain outcomes stay separate: `Y_creative` blind creative-work quality, `Y_design` blind design-work quality, `Y_coop` observed coordination quality. The composite hiring outcome `Y_job` must be specified by role and opportunity, with assessor independence and a horizon. For each session estimate incremental held-out predictive value over the other two and equal-time alternative (`Δ_s`) with uncertainty. Interpret transfer, reliability, fairness and decision utility together; a positive correlation alone is not enough.

Near a proposed threshold `t`, report `Pr(T_i ≥ t | measurement uncertainty)` and classification stability across case/rater/mode versions. If intervals or decision changes are large, report **insufficient precision** rather than forcing a score. No employment threshold, pass/fail label, personality inference or “best engineer” badge is authorized by this specification.

## Notation key for this candidate method

The canonical meanings remain in [definitions.json](../model/definitions.json). These symbols identify quantities in this *version* of the scoring method, not universal measures.

| Symbol | Meaning and operational unit |
| --- | --- |
| `i,s,c,d,r,m,v` | Participant, session, case version, rubric dimension, rater/scorer, response mode and score version. |
| `Y[i,s,c,d,r,m,v]` | One `0–4` anchored rating or `NA`/`UNK`, with cited answer evidence. |
| `H[i,s,c,d]` | Adjudicated reference rating on one dimension, preserving both original ratings. |
| `w[s,d]`, `S_ref` | Frozen dimension weight and descriptive `0–100` session score; the numeric rescale does not establish interval measurement. |
| `θ,b,u,q,ξ` | Latent person signal, case/threshold difficulty, rater severity, mode effect and person-by-case deviation in the candidate ordinal model. These are estimated, not known traits. |
| `σ²_p`, `σ²_relative_error`, `σ²_absolute_error` | Estimated between-person variance and relative/absolute decision error for a specified case/rater/mode design. |
| `G`, `Φ` | Relative generalizability and absolute decision dependability coefficients for that design; `Φ_s` is the session-specific coefficient. |
| `α_s`, `Z_s`, `T_i` | Frozen session weight, calibration-only session transformation and research composite. The composite has no universal score scale. |
| `Y_creative`, `Y_design`, `Y_coop`, `Y_job` | Independently rated creative-work, design-work, observed-coordination and later role-specific job outcomes. Their scales and horizons are fixed in a run registration. |
| `y*`, `t`, `Δ_s` | Registered outcome threshold, proposed score boundary and incremental held-out value of session `s` against named comparators. None has a default value. |
| `R`, `X` | Selected Engineering Role Profile and registered baseline predictors; sensitive attributes have a separate audit purpose. |
