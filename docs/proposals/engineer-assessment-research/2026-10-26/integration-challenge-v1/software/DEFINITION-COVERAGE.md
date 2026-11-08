# MVP semantic coverage

Status: candidate task-local meanings. The [canonical statements](../model/definitions.json) govern this project's proposed terms; this map only links the software model to them. Lab admission and exact owner review have not occurred.

## Product and procedure

| Software concept or behavior | Meaning ID | Boundary to preserve |
| --- | --- | --- |
| Private developer challenge | `ea.challenge` | Experience and feedback offer, not hiring validation. |
| Invite and redemption | `ea.invitation` | Entry route, not research permission. |
| Pilot procedure and release gate | `ea.study-protocol` | Mixed-developer formative protocol; a named-role protocol is a later version. |
| Practice flow | `ea.challenge` | Unscored rehearsal outside an Assessment Attempt. |
| Scored three-slot journey | `ea.assessment-attempt` | Distinct from each Assessment Session. |
| Allocation and randomization | `ea.assignment-manifest` | Rule and realized assignment retained before seeing answers. |
| One pinned slot | `ea.session-assignment` | Pins case, rubric, mode and administration policy. |
| Timer, reveals, help and retries | `ea.administration-policy` | Server event evidence and policy are separate. |
| Failure rule and disposition | `ea.recovery-rule`, `ea.recovery-decision` | Rule is normative candidate; decision is one attributed evaluation, not an observed event or owner approval. |
| Case delivery/state history | `ea.session-event` | Event is not source media. |
| Session and answer | `ea.assessment-session`, `ea.candidate-response` | Distinct from Attempt, assignment, recording and transcript. |

## Data-model record coverage

| `DATA-MODEL.md` record | Meaning ID | Distinction |
| --- | --- | --- |
| `participant` | `ea.participant` | Pseudonym is not anonymity. |
| `identity_vault` | `ea.identity-vault` | Restricted identity mapping, excluded from scorer and default export. |
| `notice_version` | `ea.notice-version` | Exact wording, separate from display or choice receipt. |
| `purpose_choice` | `ea.purpose-choice` | Action for one purpose; `ea.consent-record` only where consent is the selected basis. |
| `study_protocol` | `ea.study-protocol` | Draft record cannot enroll people. |
| `cohort_membership` | `ea.cohort` | Membership is not outcome or permission. |
| `assignment_manifest` | `ea.assignment-manifest` | Allocation rule and realized bindings. |
| `assessment_attempt` | `ea.assessment-attempt` | Groups scored slots; practice stays separate. |
| `generation_brief`, `generation_run` | `ea.generation-brief`, `ea.generation-run` | Frozen request and producing execution are separate. |
| `case_candidate`, `mechanism_fingerprint` | `ea.case-candidate`, `ea.mechanism-fingerprint` | Draft wording and underlying solution move are separate. |
| `similarity_assessment` | `ea.similarity-assessment` | Surface and mechanism screening, not novelty proof. |
| `case_trial`, `case_review`, `case_evaluation` | `ea.case-trial`, `ea.case-review`, `ea.case-evaluation` | Volunteer evidence, reviewer judgment and evaluation synthesis are separate. |
| `case_disposition`, `case_exposure` | `ea.case-disposition`, `ea.case-exposure` | Exact release/retirement choice and exposure evidence are separate. |
| `case_family`, `case_version` | `ea.case-family`, `ea.case-version` | Family is not an administered form. |
| `rubric_version` | `ea.rubric` | Anchors, not evidence of validity. |
| `session_assignment` | `ea.session-assignment` | Frozen binding, not a viewed answer. |
| `session_event` | `ea.session-event` | Append-only transition or observation. |
| `recovery_decision` | `ea.recovery-decision`, `ea.recovery-rule` | Pinned operational disposition and rule remain separate from failure event and Lab owner Decision. |
| `upload_attempt` | `ea.upload-attempt` | Part transfer and receipt are not a verified Media Object. |
| `media_object` | `ea.media-object` | Protected source bytes and custody. |
| `transcript_version` | `ea.transcript`, `ea.asr-run`, `ea.transcript-correction` | Text, generation and correction have distinct provenance. |
| `scoring_run` | `ea.scoring-run`, `ea.scoring-specification` | Run and rule set are different. |
| `criterion_rating` | `ea.criterion-rating`, `ea.evidence-span`, `ea.adjudication` | Original judgments, citations and resolution stay separate. The [candidate carrier](../model/carriers/criterion-rating/v1/README.md) specifies one rating record. |
| `feedback_report` | `ea.score-report`, `ea.feedback-metric` | Purpose-limited projection with pinned metric rules; no employer action. |
| `criterion_observation` | `ea.independent-criterion` | External task evidence, not the answer score or later job outcome. |
| `research_export` | `ea.research-export` | Exact filtered delivery and withdrawal lineage. |
| `rights_request` | `ea.rights-request` | Request, decision and completed effect are separate. |
| `retention_schedule` | `ea.retention-schedule` | Owner-reviewed rules; no invented duration. |
| `audit_event`, `outbox_job` | `ea.audit-event`, `ea.outbox-job` | Observed action and queued intent are different. |
| `principal`, `role_assignment` | Lab `cal.definition.principal`, `cal.definition.role-assignment` | Identity and scoped assignment do not imply access. |
| `permission_policy_version`, `access_decision` | `ea.access-policy`, `ea.access-permission`, `ea.access-decision` | Policy rule and per-action result are distinct. |
| `exception_grant` | `ea.exception-grant` | Narrow ticket-bound access, not a standing role. |

The [question lifecycle](QUESTION-LIFECYCLE.md) distinguishes `ea.case-rule`, `ea.case-use-case`, `ea.case-operation` and `ea.case-workflow`. Its Q-R, Q-U, Q-O and Q-W IDs are proposed instances of those types, with checks and boundaries in that document. The HTTP routes implement operations over these objects. Opaque IDs, hashes, MIME types, timestamps, status codes and storage keys are implementation fields; their accepted values and constraints live in the [API/state contract](API-STATE-CONTRACT.md) and [data model](DATA-MODEL.md). Research constructs and score interpretation remain in the [assessment definitions](../model/DEFINITIONS.md). A new business object or changed meaning must first update `definitions.json`, then this map, the ontology and a fresh exact Define request before being described as governed.

The [participant metric specification](PARTICIPANT-METRICS.md) instantiates `ea.feedback-metric` for the first challenge report. Its formulae and display gates are method rules under that candidate meaning; they do not grant an employment interpretation.

The [product success scorecard](../model/PRODUCT-SUCCESS-METRICS.md) instantiates `ea.product-success-metric` for product phase decisions. It derives aggregate measures from approved events, study results and finance evidence; those aggregates remain distinct from a participant's Score Report and from an owner decision.

The [access model](ACCESS-MODEL.md) maps concrete human and service actors to candidate roles and guarded permissions. It reuses exact Lab meanings for Actor, Principal, Role, Role Assignment, Authority and Policy; product-local access rules and receipts remain candidate `ea.*` meanings. Neither a role name nor a permission entry creates an active grant in this repository.

The [integration records](../model/integration/README.md) apply `ea.integration-option-review` and `ea.integration-verification-contract` to capture, transfer, storage, transcription, blur and assistance safeguards. A provisional technology preference is separate from a Lab owner Decision; a prospective technical check is separate from a run or result. The reused Lab [Challenge Contract/v1](../model/lab-records/integration-choice-challenge-contract.json) defines how changed cost, requirements, quality or terms can reopen a future selection; its policy remains a draft.

The [technology catalog](../model/integration/STACK-COVERAGE.md) applies `ea.technology-component` to 24 named candidates. A library or service name is separate from an approved vendor, exact version, license, processor permission and installation. `ea.integration-binding` is the intended record for an owner-selected release configuration; no binding instance exists. Unnamed API framework, database driver, migration, hosting, telemetry and scoring choices remain explicit gaps.

The [recovery protocol](RECOVERY-PROTOCOL.md) applies `ea.recovery-rule`, `ea.recovery-decision` and `ea.upload-attempt`. Its twenty-one rule records are candidate instructions, while the decision and upload fixtures are synthetic shape witnesses. They do not describe real participant failures.
