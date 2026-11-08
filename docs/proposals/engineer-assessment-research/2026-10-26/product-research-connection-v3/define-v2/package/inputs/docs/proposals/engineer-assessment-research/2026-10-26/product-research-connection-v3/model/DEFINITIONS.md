# Definition map

The exact candidate statements and exclusions are in [definitions.json](definitions.json). Define v2 packages them for the named consumer and intended use. The following map explains the distinction between reused Lab meanings and assessment-specific proposals.

## Reuse from the current Lab registry

| Concept | Lab definition | Local use |
| --- | --- | --- |
| Product | `cal.definition.product` | Durable value identity, separate from research project and implementation. |
| Product Thesis | `cal.definition.product-thesis` | Owner-held value and evidence proposition. |
| Product Capability | `cal.definition.product-capability` | Product outcome, separate from feature and realization. |
| Project | `CAV2-D60` | Bounded coordination effort, separate from the durable Product. |
| Goal | `CAV2-D59` | Desired result and success condition, separate from an achieved result. |
| Research Inquiry | `cal.definition.research-inquiry` | Question, source policy, method and stopping condition before investigation. |
| Experiment Design | `cal.definition.experiment-design` | Prospective comparison and falsifier, separate from run. |
| Measurement Method | `cal.definition.measurement-method` | Bounded scoring procedure and interpretation, not the score itself. |
| Evidence | `cal.definition.evidence` | Source-bound observation supporting or contradicting a claim. |
| Authority | `cal.definition.authority` | Exact decision permission, separate from a receipt or recommendation. |

The original exact versions, source paths and digests are in the [Lab's frozen Define requests](../integration/lab/README.md). They bind the original snapshot. Six additional access meanings are selected in the [current candidate preparation](../integration/lab/DEFINE-2026-10-26.md). The Lab registry decides standing; this document does not.

Seven additional Lab meanings are selected for candidate reuse in the expanded research model: [Experiment Run](../../CyberAlchemy-lab/docs/lab/reference/records/def-cal-definition-experiment-run.md), [Research Run](../../CyberAlchemy-lab/docs/lab/reference/records/def-cal-definition-research-run.md), [Evidence Set](../../CyberAlchemy-lab/docs/lab/reference/records/def-cal-definition-evidence-set.md), [Hypothesis](../../CyberAlchemy-lab/docs/lab/reference/records/def-cal-definition-hypothesis.md), [Finding](../../CyberAlchemy-lab/docs/lab/reference/records/def-cal-definition-finding.md), [Measurement Result](../../CyberAlchemy-lab/docs/lab/reference/records/def-cal-definition-measurement-result.md) and [Decision](../../CyberAlchemy-lab/docs/lab/reference/records/def-cal-definition-decision.md). They are listed as `proposed_external_meanings` in [ontology.json](ontology.json); the historical frozen Define requests did **not** bind them. `OwnerDecision` is a role-scoped use of the Lab Decision meaning, not a new power granted by this workspace.

## Assessment-specific meanings

The [canonical local statements](definitions.json) now contain **78 candidate terms**. The original 16 are: Engineering Role Profile, Target Outcome, Assessment Construct, Case Family, Case Version, Assessment Session, Candidate Response, Transcript, Rubric, Scoring Run, Score Report, Validation Study, Claim Tier, Consent Record, Cohort, and Decision Policy. `ea.participant` defines the type; each person's concrete identity remains a separate private record.

The 11 additional terms make the new research methods explicit. This table is a lookup aid; the JSON statements govern the task-local meanings.

| ID | Term | Plain-language use |
| --- | --- | --- |
| `ea.criterion-rating` | Criterion Rating | One anchored, evidence-linked dimension judgment, including `NA` and `UNK` states. |
| `ea.independent-criterion` | Independent Criterion | Different work evidence used to test whether a case score transfers. |
| `ea.response-mode` | Response Mode | How a case and answer are presented and captured. |
| `ea.rater` | Rater | A trained human evaluator whose variation is measured. |
| `ea.scoring-specification` | Scoring Specification | Versioned mapping from ratings to score, uncertainty and interpretation. |
| `ea.measurement-uncertainty` | Measurement Uncertainty | How much case, rater and mode variation could change a conclusion. |
| `ea.calibration-set` | Calibration Set | Development responses used to build and tune scoring. |
| `ea.validation-holdout` | Validation Holdout | Untouched responses, cases, employers or time periods for locked evaluation. |
| `ea.estimand` | Estimand | Exact population-level quantity an experiment tries to learn. |
| `ea.case-exposure` | Case Exposure | Evidence of prior access to a question or its underlying trick. |
| `ea.decision-threshold` | Decision Threshold | A justified, versioned score boundary inside an authorized policy. |

The formal notation and intuition for Criterion Rating, Scoring Specification, Measurement Uncertainty, Estimand and Decision Threshold are colocated with their canonical statements in JSON. The [scoring model](../research/scoring-model.md) and [experiment protocol](../research/full-protocol.md) apply these meanings to proposed methods; neither is an independent definition authority.

`ea.feedback-metric` describes one versioned participant-facing value or status, including its source, rule, unit, missingness, uncertainty and allowed interpretation. The [participant metric specification](../software/PARTICIPANT-METRICS.md) selects `FM-01`–`FM-08` for the challenge report. `ea.product-success-metric` is the 78th candidate meaning: a phase- and population-bound measure for deciding whether the product creates value or violates a guardrail. The [product success scorecard](PRODUCT-SUCCESS-METRICS.md) selects `PS-01`–`PS-17`. Neither type confers prediction or decision authority.

The seven product-claim terms added after the measurement audit are `ea.analytical-reasoning`, `ea.creative-reasoning`, `ea.ingenuity`, `ea.technical-design-judgment`, `ea.cooperation-judgment`, `ea.communication-judgment`, and `ea.high-performing-engineer`. They make the proposed constructs explicit. In particular, “high-performing engineer” depends on a declared role, independent Target Outcome and observation horizon; it is not a global label. Their separability and predictive value remain experimental questions.

Four earlier question/scorer development terms start the workflow vocabulary: `ea.case-generator` proposes drafts, `ea.item-bank` tracks candidate/released/held-out/retired forms, `ea.case-evaluation` tests case quality, and `ea.scorer-evaluation` tests the scoring method. None of these records validates a candidate or authorizes use by itself.

Twelve additional question-lifecycle terms define a Generation Brief, Generation Run, Case Candidate, Reasoning Mechanism Fingerprint, Similarity Assessment, Case Trial, Case Review, Case Disposition, and the distinct Rule, Use Case, Operation and Workflow types. The [question lifecycle](../software/QUESTION-LIFECYCLE.md) gives Q-R/Q-U/Q-O/Q-W instances, state transitions, tracking and evaluation gates. A question is a draft Case Candidate until an independently released immutable Case Version exists.

Four access-specific terms now distinguish Application Access Permission, Application Access Policy, Access Decision Receipt and Exceptional Access Grant. The [access model](../software/ACCESS-MODEL.md) reuses the Lab Actor, Principal, Role, Role Assignment, Authority and Policy meanings for the proposed actor/role model; these local terms describe application enforcement and receipts, not Lab authority.

Twenty-two software and pilot terms define the MVP's challenge, invitation, participant, protocol, purpose/notice, attempt/allocation, session policy/events, media/ASR/correction, scoring evidence/adjudication, export, rights, retention and asynchronous audit work. Their exact statements, boundaries and intuition are in [definitions.json](definitions.json); the [software coverage map](../software/DEFINITION-COVERAGE.md) links every durable MVP record to those meanings. API routes and storage fields implement these concepts; they do not redefine them. A Purpose Choice records an action for one use; the revised Consent Record means evidence of consent only when consent is the approved basis for that use. Both remain candidate meanings pending semantic review.

The most important non-collapse relations are:

1. `Case Version != Response != Transcript != Scoring Run != Score Report`.
2. `Construct != Rubric != Model`; a score estimates a construct under a declared method and population.
3. `Research Inquiry != Experiment Design != Experiment Run != Evidence != Finding != Owner Decision`.
4. `Product != Project != Goal != Product Capability != Implementation`.
5. `Challenge feedback != employment decision`; the same recording cannot change purpose silently.
6. `Candidate ranking != observed future performance`; selection quality requires independent later outcome evidence.
7. `Criterion Rating != Independent Criterion != Target Outcome`; an answer score, a separate validation task and future job performance support different claims.
8. `Calibration Set != Validation Holdout`; tuning on a holdout destroys its locked-test status.
9. `Decision Threshold != Decision Policy != Owner Decision`; a number, a rule and authorization are separate.
10. `Challenge != Study Protocol != Invitation != Assessment Attempt != Session Assignment != Assessment Session`.
11. `Purpose Choice != Consent Record != lawful-basis decision`; a UI action cannot choose the legal basis.
12. `Media Object != ASR Run != Transcript != Transcript Correction`; scoring evidence retains lineage to the source.
13. `Rights Request != Outbox Job != completed deletion`; intent, execution and effect have separate receipts.

## Open definition decisions

- "Best engineer" needs a selected role, level, candidate pool, performance criterion, time horizon, and capacity. The proposed Target Outcome definition forces those parameters.
- Creativity, analysis and ingenuity now have candidate canonical meanings and operational anchors in Session 1, but construct validity, separability and relation to future work remain research questions.
- "Cooperation" inferred from a recorded scenario may differ from observed team behavior; the two are separately measured in validation.
- The named accountable human principal for each role and the exact retention schedule remain open.
- Role-specific outcomes, sample and horizon, case-bank versions, score weights, uncertainty tolerances, material effect sizes and any threshold values remain unfilled design parameters. Defining their *types* does not select their values or validate a score.

## Coverage audit and next remediation

| Area | Current state | Target for remaining work |
| --- | --- | --- |
| Critical product, case, score, research, software and decision vocabulary | 78 candidate local meanings in [definitions.json](definitions.json); ontology and software coverage synchronized. | Human semantic review before any proposed admission. |
| Lab lifecycle meanings | Ten bound in the 2026-10-25 historical Packs; six Actor/Principal/Role/Role Assignment/Authority/Policy meanings selected in the 2026-10-26 access Pack; seven further research meanings selected for candidate reuse. That Pack captured 76 local meanings; the two metric meanings and revised sources have a fresh local [Define handoff](../integration/lab/METRICS-DEFINE-REQUEST.md) and need a new Lab capture. | Exact owner semantic review, current host qualification and any canonical admission remain open. |
| Session-specific construct meanings | Analysis, creative reasoning, ingenuity, design, cooperation and communication defined as bounded hypotheses. | Test separability and transfer through [session protocols](../research/README.md). |
| Role-specific interpretation | Role, outcome, horizon and capacity are required by Target Outcome; values are open. | Fill the registration sheet in the [full protocol](../research/full-protocol.md) for the first named role. |
| Scoring anchors and policy values | The `0–4` strength scale and score model are proposed, but case-specific exemplars, weights, margins and thresholds are not selected. | Freeze case/rubric versions and numerical decision criteria under [scoring model](../research/scoring-model.md) and the first registered study. |
| Custody and use | Owner roles, participant purposes and decision gates are described; principals and retention values are open. | Record exact owner and privacy decisions in [AUTHORITY.md](AUTHORITY.md) and corresponding controlled records before collection/use. |

The mapped MVP records, question workflow and access model have candidate meanings. Exact human review of all case and scoring consumers and a repository-wide undefined-term audit remain open. The `16` count in [VALIDATION.md](VALIDATION.md) is explicitly a historical snapshot count, not a claim about the current workspace. Unresolved values, evidence and approvals are tracked above. Reaudit when new capabilities or study designs introduce terms.
