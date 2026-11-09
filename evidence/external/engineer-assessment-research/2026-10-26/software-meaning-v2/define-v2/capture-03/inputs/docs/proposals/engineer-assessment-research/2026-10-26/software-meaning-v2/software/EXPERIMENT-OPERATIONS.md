# Running the MVP as a research instrument

Status: prospective operations design. The first pilot audience is **mixed software developers**. The challenge can collect useful evidence from real developers **after** protocol, privacy/security, item and reviewer approvals. The first cohort tests usability, case quality, transcription and scoring across declared experience/role/stack strata. It does not validate hiring selection, because a single role-specific outcome, future job outcomes and an applicant-like pool are absent. Research consent/eligibility is checked separately from challenge use.

## First permissioned pilot: three sessions, one case each

| Research question | Collected measure | Interpretation limit |
| --- | --- | --- |
| Can developers understand and finish the experience? | Invitation denominator, start/completion/dropout by slot, active/wall time, retries, device failure, comprehension check and voluntary burden response. | A fun challenge's completion rate does not imply applicant acceptability. |
| Do the cases elicit the intended evidence? | Blind response-process interviews, valid alternative counts, missing facts/ambiguity flags, prior exposure, case-family/version and expert case-evaluation record. | One case per session cannot establish broad construct coverage. |
| Can two humans apply the anchors? | Independent criterion ratings with evidence spans, disagreement and adjudication reasons, per-session/mode error. | Agreement alone does not prove job relevance or prediction. |
| What does ASR lose? | Raw ASR, participant-corrected transcript, human transcription subset, evidence-span deletion and score change under transcript modes. | Error must be remeasured for this stack, languages and participant population. |
| Is feedback useful and understood? | Comprehension questions, actionability rating, correction/appeal requests and a later optional reflection. | Positive feedback reactions do not establish a hiring score. |

### Experimental allocation

Before invitations, freeze an `assignment_manifest` with cohort strata, case versions, order rules, mode availability, inclusion/exclusion and analysis code. Randomize among **reviewed parallel case variants** only when there are enough approved forms; otherwise use one fixed form and label case-form comparison unavailable. Log the randomization probability and actual allocation for every eligible invitation. Do not change assignment after seeing responses. The pilot may randomize feedback wording or case order for a bounded UX question, but keep scoring/rubric and time limits fixed in the primary comparison. Optional extra validation tasks are a separate research invitation outside the three-session product experience.

### Enrollment and procedure

1. Invite adult developers from declared source channels across a mixed software-development background. Record role, experience, dominant stack and channel for stratified description without treating them as a hidden score adjustment. Record invitations and refusals without pretending nonresponders have performance data. Choose language, geography, compensation, access route, stratum plan and sample precision before release.
2. Record purpose choices and the necessary processing basis/notice. Run practice, then three scored sessions with server receipts. A participant declining optional research still receives the challenge if that service is offered under an approved basis; their answers are excluded from research extraction.
3. Collect a short **post-session** process check: familiarity with the case/trick, clarity of facts, tool use and any missing information. Ask after the scored answer to avoid cueing it.
4. Produce transcript/correction versions. Blind two human raters on a predeclared subset or all pilot answers, retaining both ratings. Run a pinned AI scorer in shadow mode only after its prompt and data handling are approved; never let it silently publish a hiring-like judgment.
5. Deliver provisional feedback after human review. Capture feedback comprehension and rights requests. A participant should be able to opt out of optional follow-up without losing the already offered challenge report.
6. Produce a dated pilot report with flow counts, errors, estimates and intervals, negative examples, mode limits, consent exclusions, deviations and a `supported/contradicted/inconclusive` conclusion per question.

## Event and version ledger

The minimum append-only event taxonomy is `invited`, `invite_redeemed`, `notice_viewed`, `purpose_chosen`, `practice_started/completed`, `assigned`, `case_shown`, `recording_started`, `reveal_shown`, `recording_stopped`, `media_committed`, `technical_failure`, `retry_assigned`, `asr_completed/failed`, `transcript_corrected`, `rating_submitted`, `adjudication_recorded`, `report_published/viewed`, `research_withdrawn`, `rights_requested/resolved`, `export_created/revoked`, `case_retired`. Each event includes event ID, pseudonymous subject/attempt, protocol/case version where relevant, server time, actor, purpose and causal parent. Do not log answer text in telemetry.

The export manifest pins `study_protocol`, case/rubric/ASR/scorer versions, assignment method, eligible cohort definition, inclusion/exclusion rules, raw-to-derived lineage, outcome/rater version, missingness state and query/code hash. The research dataset uses pseudonyms; the reidentification key and participant contact remain outside it. Withdrawal changes future access and triggers lineage review for existing extracts under the approved protocol.

## What the first pilot can and cannot decide

It can decide whether the challenge journey works, which cases are ambiguous or exposed, whether raters understand anchors, whether ASR harms evidence, and whether provisional feedback is comprehensible across the sampled developer backgrounds. It may inform sample-size simulation and case/rubric revision. It cannot establish a stable one-case-per-session score or future job prediction from three answers; a mixed cohort must not be collapsed into one role-specific hiring score. The next study needs a multi-case research subset plus independent creative/design/team criteria as specified in the [full protocol](../research/full-protocol.md). Employer selection utility requires a later prospective, separately authorized **named-role** cohort and outcome design.

## Release evidence and operational stop triggers

The launch packet must contain the declared mixed-developer cohort and source, approved purpose/legal-basis/retention decisions, accessible journey review, reviewed three case/rubric versions, registered pilot outcomes and precision targets, approved vendors/region, security and restore test, rater training, rights exercise, incident route and on-call owner. These are concrete records, not a request to assume approval. Stop new collection if consent/notice version is wrong, media custody fails, access control leaks answers, case bank is exposed, deletion cannot be honored under the approved policy, or the participant journey materially misstates what scores mean. Negative measurement results trigger redesign, not data deletion from the scientific record.
