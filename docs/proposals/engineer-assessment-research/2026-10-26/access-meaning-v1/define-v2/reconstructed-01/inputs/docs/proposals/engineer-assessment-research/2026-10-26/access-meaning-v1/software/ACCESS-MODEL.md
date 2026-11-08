# Actors, roles and permissions for the MVP

Status: **candidate policy model, no grants active**. The Lab's accepted [Actor](../../CyberAlchemy-lab/docs/lab/reference/records/def-cal-definition-actor.md), [Principal](../../CyberAlchemy-lab/docs/lab/reference/records/def-cal-definition-principal.md), [Role](../../CyberAlchemy-lab/docs/lab/reference/records/def-cal-definition-role.md), [Role Assignment](../../CyberAlchemy-lab/docs/lab/reference/records/def-cal-definition-role-assignment.md), [Authority](../../CyberAlchemy-lab/docs/lab/reference/records/def-cal-definition-authority.md) and [Policy](../../CyberAlchemy-lab/docs/lab/reference/records/def-cal-definition-policy.md) meanings guide this candidate specialization. A concrete product user is not thereby admitted as a Lab Actor or granted Lab authority. The product's `ea.participant`, `ea.rater`, `ea.access-permission`, `ea.access-policy`, `ea.access-decision` and `ea.exception-grant` are [candidate local meanings](../model/definitions.json). A role describes duties; a role assignment says who holds it; a permission entry constrains an application operation; an owner decision establishes whether a governed effect is permitted. None implies the next.

## Actor inventory and role catalog

| Role ID | Actor kind and job | Scope and current status |
| --- | --- | --- |
| `participant` | Invited developer using the challenge and their own data controls. | Own records under one protocol; concrete people absent. |
| `recruiter` | Pilot coordinator issuing invitations and tracking denominators. | Invitation metadata only; no answers or scores. |
| `case_author` | Human author or generator operator creating briefs and drafts. | Draft bank only; cannot release own case. |
| `case_reviewer` | Independent expert screening answerability, mechanism, access and rubric fit. | Assigned candidates; cannot release or score participants by this role. |
| `case_bank_owner` | Accountable owner disposing exact case versions. | Release/hold/retire after independent review; principal unassigned. |
| `research_lead` | Protocol owner and study designer. | Protocol, assignment plan, analyses; cannot approve own privacy basis or raw export. |
| `rater` | Human evaluator applying an assigned rubric independently. | Assigned pseudonymous answers only. |
| `adjudicator` | Resolves submitted rating differences. | Assigned discrepancy after both ratings; no identity/contact. |
| `feedback_reviewer` | Checks and publishes provisional participant feedback. | Report projection and cited ratings; no employer action. |
| `research_analyst` | Reads approved aggregates and requests controlled extracts. | Purpose-eligible pseudonymous data; cannot approve own export. |
| `privacy_operator` | Handles purpose records, rights cases and extract release. | Minimum identity needed for the case; no rating edits. |
| `support_agent` | Helps with access/device/accommodation requests. | Own assigned ticket and minimum contact/status; no score or hidden key. |
| `system_operator` | Maintains runtime, jobs, backups and incident telemetry. | Operational metadata only; no standing answer/media read. |
| `security_owner` | Reviews incidents and exceptional access; can stop collection. | Security decisions only; cannot self-grant data access. |
| `privacy_owner` | Controller-side purpose, retention, vendor and exception decisions. | Decision authority requires named principal and exact scope. |
| `assessment_owner` | Owns construct/rubric and case-release policy. | Scientific criteria, not unilateral participant collection. |
| `measurement_owner` | Freezes scorer version after independent evaluation. | Score method, not employer selection. |
| `independent_reviewer` | Challenges protocol, case/scoring evidence or public claims. | Review records, not product or employer approval. |
| `product_owner` | Chooses thesis, product posture and bounded external claim. | Claim decision still depends on evidence and independent review. |
| `definitions_owner` | Reviews candidate meanings and drift. | No operational data grant from semantic ownership. |
| `asr_worker` / `ai_evidence_worker` / `assignment_worker` | Separate service principals for transcription, shadow evidence extraction and case allocation. | Job-scoped input only; no governance or interactive staff role. |
| `employer_sponsor` / `employer_decision_owner` | Future named-role research and possible employment actors. | **Disabled in MVP**; no participant report or score access. |

One person may hold multiple roles through separate time-limited assignments, but conflicts below are checked per case, answer, study and export. A service principal cannot hold an owner or reviewer role. Role names in a request body are ignored; server identity, active assignment and exact scope are resolved independently.

## Permission entries

All entries require authenticated principal, active scoped role assignment, named purpose, resource state, current protocol/owner decisions and an audit receipt. A permission entry is a proposed application allow rule, **not a Lab Authority grant**. Default is deny, including unlisted actions, cross-participant reads and employer access.

| ID | Action → resource | Eligible role | Additional guard |
| --- | --- | --- | --- |
| `P01` | issue/revoke → invitation | recruiter | Approved protocol, recruitment source and quota; no answer access. |
| `P02` | redeem/read → own invitation/challenge | participant | One-time token, eligible protocol and own identity. |
| `P03` | choose/withdraw → own purpose choice | participant | Exact notice version; withdrawal propagates to research eligibility. |
| `P04` | draft/run → generation brief/candidates | case_author | Pinned generator, restricted bank; all drafts retained. |
| `P05` | screen/review → assigned case candidate | case_reviewer | Reviewer independent of author; no release endpoint. |
| `P06` | dispose/release/retire → exact case version | case_bank_owner | Independent review, compatible rubric/policy, exposure gate and exact owner decision. |
| `P07` | draft/amend → study protocol/assignment plan | research_lead | Versioned amendment; cannot activate collection alone. |
| `P08` | activate → study protocol | research_lead | Separate privacy/security/ethics decisions and reviewed case releases. |
| `P09` | allocate → session assignment | assignment_worker | Approved protocol, released case, current purpose and quota; no arbitrary case substitution. |
| `P10` | start/upload/read/correct → own session/media/transcript | participant | Own attempt, server state/time, scoped upload grant and retention eligibility. |
| `P11` | transcribe → assigned media object | asr_worker | Approved vendor/region, job token, input digest; no bulk export. |
| `P12` | draft evidence → assigned transcript | ai_evidence_worker | Approved shadow scorer, pseudonymized input, no publish permission. |
| `P13` | read/submit → assigned pseudonymous rating | rater | Exact case/rubric; other rater output masked until submission. |
| `P14` | resolve → assigned discrepancy | adjudicator | Both independent ratings submitted; original ratings immutable. |
| `P15` | publish → participant feedback report | feedback_reviewer | Required human review and report purpose; no hiring recommendation. |
| `P16` | read → own report and rights status | participant | Own identity and published version only. |
| `P17` | read → approved aggregate/independent criterion | research_analyst | Protocol scope, small-cell rule and current research eligibility. |
| `P18` | request → research export | research_analyst | Exact field/query/recipient/expiry manifest; no media by default. |
| `P19` | approve/release/revoke → research export | privacy_operator | Different person from requester; current purpose/withdrawal/retention check. |
| `P20` | submit → own rights request | participant | Identity verification follows the selected procedure. |
| `P21` | resolve → rights request | privacy_operator | Ticket scope, source/derivative/backup lineage and exception decision where needed. |
| `P22` | read/update → assigned support ticket | support_agent | Minimum contact and device/access status; no score/raw media. |
| `P23` | read/operate → runtime metadata/job | system_operator | No answer text, contact vault or raw media through standing role. |
| `P24` | pause → collection/processing | security_owner | Incident reason, affected scope, timestamp and audit; resume requires recorded review. |
| `P25` | decide → purpose/vendor/retention exception | privacy_owner | Exact deployment, jurisdiction, basis, evidence and challenge route. |
| `P26` | decide → scorer version | measurement_owner | Evaluation and independent challenge; developer cannot self-freeze. |
| `P27` | decide → external claim/product posture | product_owner | Exact evidence and independent reviewer input; no employer action. |

The detailed [API contract](API-STATE-CONTRACT.md) maps routes onto these action families. A route's existence never supplies a grant. The [broad data matrix](DATA-MODEL.md#mvp-access-matrix) is an overview; these entries and guards are the candidate enforcement specification where the overview is less precise.

## Separation of duties and exceptional access

1. The author or generator operator of a case cannot be its sole independent reviewer or release decision maker.
2. Two independent raters cannot be the same principal for the same answer; the adjudicator cannot replace either original judgment.
3. An export requester cannot approve/release that same export; a researcher cannot grant themselves a new purpose.
4. A scorer developer cannot be the sole measurement owner freezing their own version.
5. A protocol author cannot self-supply privacy, security or independent ethics review. A product owner cannot self-supply independent scientific review of a predictive claim.
6. Staff do not read raw video by default. An exceptional evidence/rights/incident review requires exact ticket, purpose, object IDs, expiry, privacy-owner approval, security review where relevant, narrow signed access and audit. It cannot enable employer sharing or bulk export.
7. Emergency access is limited to stopping collection or restoring service metadata. It does not bypass purpose, media or export gates. An emergency data read must use the exceptional route and post-event review.

## Authorization algorithm and durable records

For every action: authenticate principal → resolve active role assignment and service/human type → match `Pxx` action/resource → check same-subject/assigned-object scope → check purpose and current choice → check protocol, case and record state → check owner decision/version/expiry → check separation-of-duties history → issue narrow operation or deny → append access-decision and audit event. A deny is logged without answer content. Revocation is evaluated at each read, not only at login.

Implementation requires `principal` (human/service identity and lifecycle), `role_assignment` (issuer, role, scope, effective/expiry/revocation), `permission_policy_version` (the exact `Pxx` set and digest), `access_decision` (principal, action, object, purpose, guards, allow/deny reason, policy version), and `exception_grant` (ticket, owner approvals, exact object/operation, expiry and use receipts). These are proposed records; there are no active principals or grants in this repository. Deletion of participant data preserves only the minimum approved security receipt.

## Open decisions and checks

- Assign named principals to governance roles and record exact decision scopes before live processing.
- Select authentication, service credential rotation, session lifetime, permission-policy owner, incident path and exceptional-access duration.
- Specify the controller and jurisdiction, including which purpose choices and lawful-basis decisions govern each action.
- Implement allow/deny tests for every `Pxx` entry, cross-subject and stale-role attempts, role combinations, export withdrawal, retired cases, media grants and emergency access. No participant data is collected until these checks and owner gates pass.
