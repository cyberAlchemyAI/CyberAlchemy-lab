# MVP API and state contract

Status: proposed HTTP contract for a private browser pilot. This is implementation guidance, not an exposed service. All writes use authenticated identity, an `Idempotency-Key`, optimistic record version and server timestamp. Client state is a view of server state. Return stable error codes, not stack traces or hidden rubric content.

## Participant routes

| Route | Purpose and state rule |
| --- | --- |
| `POST /v1/invitations/redeem` | Exchange one-time invite for participant session; bind protocol version and invitation source. |
| `GET /v1/challenge` | Return public purpose/notice, permitted modes, topics, timing, tool rules and current participant state. No hidden bank or scoring key. |
| `PUT /v1/purpose-choices/{purpose}` | Write one choice/notice receipt. Research, follow-up and subgroup purposes are separate. A refusal does not rewrite earlier choices. |
| `POST /v1/practice-attempts` | Start a non-scored device/timing exercise; no scoring or research inclusion. |
| `POST /v1/assessment-attempts` | Create scored attempt only under an approved study protocol and necessary processing basis. Freeze assignment manifest and up to three slots. |
| `GET /v1/assessment-attempts/{id}/sessions/{slot}` | Return that slot's released case slice, allowed actions, server deadline, mode and latest upload state. |
| `POST /v1/sessions/{id}/start` | Atomically move `shown → recording`; return server `started_at`, deadline and reveal schedule. No restart of the same active capture. |
| `GET /v1/sessions/{id}/events?after={cursor}` | Read server reveal/state events; browser can reconnect without changing the schedule. |
| `POST /v1/sessions/{id}/media-upload` | Issue short-lived private upload grant and chunk manifest for authorized active slot. |
| `POST /v1/sessions/{id}/media-commit` | Verify digest, MIME, duration, declared chunks and server timing before `uploaded`; duplicate commit returns same receipt. |
| `GET /v1/sessions/{id}/transcripts` / `POST .../corrections` | Read a permitted transcript; corrections create successor versions and keep the original separate. |
| `GET /v1/reports/{id}` | Read own purpose-limited report after human review policy; include rubric version, evidence, `NA/UNK` and caveat. |
| `POST /v1/rights-requests` / `GET .../{id}` | Request/track export, correction, research withdrawal or deletion. Do not promise instant erasure before policy resolution. |

The first pilot can deliver transcripts and feedback asynchronously; participants receive a status page and optional contact notification only if they opted into that channel. API response never reveals a participant's cohort assignment or hidden case family in a way that leaks future items.

## Staff routes

| Route | Role and boundary |
| --- | --- |
| `POST /v1/staff/generation-briefs` / `POST .../{id}/runs` | Research designer freezes a brief; case author/generator runs a pinned batch and retains every candidate or failure. No direct release. |
| `POST /v1/staff/case-candidates/{id}/screen` | Produce mechanism fingerprint and surface/mechanism/exposure assessment against a versioned corpus. Flags require reviewer resolution. |
| `POST /v1/staff/case-candidates/{id}/reviews` / `POST .../{id}/trials` | Independent reviewers submit findings; an approved non-scored trial route records comprehension, time and alternatives under its protocol. |
| `POST /v1/staff/case-candidates/{id}/dispositions` | Authorized case-bank owner rejects, requests revision, holds or releases an exact candidate after compatible rubric/policy and evaluation. Release creates an immutable Case Version. |
| `POST /v1/staff/cases/{id}/exposures` / `POST .../{id}/dispositions` | Record exposure and hold/retire an exact released version; new assignment stops while historical pins remain. |
| `GET /v1/staff/rating-queue` / `POST /v1/staff/ratings` | Rater sees pseudonymous assigned answer only and submits evidence-linked independent ratings. |
| `POST /v1/staff/adjudications` | Adjudicator resolves a declared discrepancy while preserving both prior ratings. |
| `POST /v1/staff/reports/{id}/publish` | Release feedback after required checks; cannot trigger employer action. |
| `GET /v1/staff/studies/{id}/quality` | Researcher sees approved aggregate completion, assignment, ASR and rater metrics with small-cell controls. |
| `POST /v1/staff/research-exports` | Researcher requests a purpose-filtered export; privacy operator approves and grants a time-limited download. |
| `POST /v1/staff/rights-requests/{id}/resolve` | Privacy operator records deletion/export/correction steps and any documented exception. |

Authorization policy is evaluated server-side for **every** read and write. Staff cannot grant themselves a different role through an API payload. Raw media access is a separate operation requiring an approved purpose and audit event.

These case-bank routes implement [question-lifecycle operations](QUESTION-LIFECYCLE.md). A generator token cannot call disposition routes. Case Trials require a separately approved participant protocol and cannot be disguised as practice in a scored attempt.

## State transitions and responses

```text
Session: assigned -> shown -> recording -> upload_pending -> uploaded
                                          \-> technical_failure
         uploaded -> transcript_ready -> scoring_pending -> feedback_ready
         any nonterminal -> withdrawn or voided (reason required)
```

`start` fixes the server deadline. If the browser disconnects, recording may continue locally until the pinned cap, but the client cannot extend the deadline. A timed reveal is emitted by server rules; a late client receives the same reveal event and timestamp. Pause/retry is not a generic button: the protocol must name allowed reasons, maximum attempts and handling of partial source media. A retry creates a successor assignment in the same slot linked to the voided predecessor.

Example `GET /v1/sessions/{id}` projection:

```json
{
  "session_id": "opaque-id",
  "slot": 1,
  "state": "shown",
  "case_version_id": "case-v-opaque",
  "case_prompt": "Visible prompt text only",
  "response_mode": "video",
  "recorded_seconds_limit": 600,
  "server_deadline": null,
  "allowed_actions": ["start", "request_access_help"],
  "record_version": 1
}
```

Example error shape: `{"code":"UPLOAD_INCOMPLETE","message":"Your answer has not finished uploading.","retryable":true,"request_id":"opaque-id"}`. Other stable codes include `PURPOSE_REQUIRED`, `PROTOCOL_NOT_APPROVED`, `CASE_RETIRED`, `SESSION_EXPIRED`, `MEDIA_INVALID`, `TRANSCRIPT_PENDING`, `REVIEW_PENDING`, `RIGHTS_REQUEST_PENDING`, `CONFLICT_VERSION` and `FORBIDDEN`. Error messages shown to participants must be understandable and must not leak case keys or protected details.

## Contract checks before launch

Exercise state transitions with a fake clock; duplicate and reordered requests; media duration just below/above the cap; upload reconnection; case retirement during an in-progress attempt; withdrawn research choice before/after extract; rater masking; transcript correction and rescore; report access by another participant; and a deletion request spanning source/derived objects. The application is ready for real participants only after the separate decisions in [PRIVACY-ACCESS.md](PRIVACY-ACCESS.md) and the relevant case/rubric release records exist.
