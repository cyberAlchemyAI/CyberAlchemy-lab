# Authority and data custody proposal

Status: candidate; no operational permission. A prepared Definition Pack, AI score, study result, and researcher's recommendation are evidence inputs, never an approval to recruit, process recordings, screen applicants, or publish claims.

| Decision | Proposed accountable role | Required recorded decision before effect |
| --- | --- | --- |
| Accept product thesis, first role/level, target market and budget | Product owner (principal unassigned) | Scope, outcome, capacity and claim ceiling. |
| Approve study protocol and participant materials | Research lead plus independent ethics/privacy reviewer | Population, consent, risk, compensation, withdrawal, and analysis plan. Formal ethics review where applicable. |
| Approve data processing, retention and vendors | Data controller/privacy owner plus security owner | Purpose, lawful basis, processors, region, deletion schedule, access and incident route. |
| Release a question/rubric version | Assessment science owner plus engineering subject expert | Construct map, answerability, exposure, accessibility, key and error review. |
| Freeze a model/scoring version | Measurement owner independent of model developer | Reproducibility, uncertainty, subgroup and failure review. |
| Start an employer validation study | Employer research sponsor plus research/privacy owners | Data-sharing terms and outcome collection plan. |
| Use a score in employment selection | Employer decision owner and jurisdictional legal reviewer | Role-specific validation, accommodations, human review, notice, challenge route and current local rules. |
| Make an external predictive or fairness claim | Product owner plus independent scientific reviewer | Exact claim, cohort, outcome, effect estimate, interval, limitations and release scope. |

No principal is assigned by this proposal. The owner role is a requested governance slot, not a delegation of authority. Jurisdiction-specific rules must be checked at deployment time.

The MVP [actor, role and permission model](../software/ACCESS-MODEL.md) specifies candidate application actions and guards. Its access policy can enforce a separately authorized owner decision; it cannot create one. Employer actors and employer score access remain disabled in the first pilot.

The [candidate policy set](policies/README.md) records the owner routes and unresolved values for privacy, assistance, assessment, research, scoring, access, vendors, rights and claims. No Policy/v2 candidate is issued or active merely because its rules and schema are recorded.

For cases, the assessment owner decides the release criteria and exact authorization; the case-bank owner executes a disposition after independent review. Those roles may be assigned to different principals. For research exports, the analyst requests and the privacy operator approves; neither role can supply the other's action on the same export.

## Purpose and custody boundaries

The public challenge has a feedback purpose. Optional research participation needs a separately recorded, understandable choice. Employment use requires its own employer process and notice; a challenge participant's recording must not be silently reused to rank applicants. An employment applicant may use an accessible alternative path without being coded as a poor performer. Compensation, if offered, must not make the optional research choice coercive.

Store the minimum necessary audio/video, transcript, item version, rubric version, score evidence, consent, and access log under separate identifiers. Restrict raw media to approved reviewers; score service receives the minimum view needed. Pseudonymize analysis data, maintain a reidentification key under separate custody, and log every export. Define retention separately for raw media, transcripts, scores, study extracts and consent receipts before collecting data. Deletion and correction requests must propagate to derivatives where feasible, with documented exceptions. Do not invent a duration in this proposal.

## Gates and claim ceiling

`A0` author candidate material -> `A1` owner accepts study scope -> `A2` privacy/security and ethics review -> `A3` permissioned pilot -> `A4` independent validation -> `A5` employer-specific selection decision -> `A6` public claim release. Each is an actual owner record with exact subject, version and expiry/refresh trigger. Missing records stop the dependent effect. A prior gate never supplies a later one. Negative subgroup or access findings can pause use even if aggregate prediction is promising.

Current ceiling: **concept and research proposal only**. The package can be inspected and challenged. It cannot invite identifiable participants, ingest media, make hiring recommendations, or claim validated selection performance.
