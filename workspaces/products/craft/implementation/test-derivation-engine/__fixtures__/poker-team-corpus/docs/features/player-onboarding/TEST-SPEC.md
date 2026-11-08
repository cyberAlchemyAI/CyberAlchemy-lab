---
id: player-onboarding-test-spec
feature: player-onboarding
title: Player Onboarding Test Specification
summary: Deterministic test catalogue derived from DomainSpec aspect documents.
status: implemented
pillar: operations
domain: onboarding-candidates
audience:
  - developers
priority: p1
lang: en
owners:
  - backend-core
  - operations-core
updatedAt: 2026-04-24
dependencies:
  - SPEC.md
  - operations.md
  - states.md
  - interfaces.md
  - mappings.md
  - workflows.md
includes: []
---

# Player Onboarding — Test Specification

> Derived from [SPEC.md](SPEC.md), [operations.md](operations.md), [states.md](states.md), [interfaces.md](interfaces.md), [mappings.md](mappings.md), [workflows.md](workflows.md).

## State Transition Tests

Source: [CandidateApplicationLifecycle](states.md#candidateapplicationlifecycle)

### Happy Path Transitions

| ID   | From         | Event                               | To           | Guard              |
| ---- | ------------ | ----------------------------------- | ------------ | ------------------ |
| ST-1 | [new]        | SubmitCandidateApplication          | SUBMITTED    | Rules R1–R9 valid  |
| ST-2 | SUBMITTED    | StartManualReview                   | UNDER_REVIEW | Application exists |
| ST-3 | SUBMITTED    | ReviewCandidateApplication(APPROVE) | APPROVED     | Review authorized  |
| ST-4 | SUBMITTED    | ReviewCandidateApplication(REJECT)  | REJECTED     | Review authorized  |
| ST-5 | UNDER_REVIEW | ReviewCandidateApplication(APPROVE) | APPROVED     | Review authorized  |
| ST-6 | UNDER_REVIEW | ReviewCandidateApplication(REJECT)  | REJECTED     | Review authorized  |

### Negative Transition Tests

| ID   | From     | Event                           | Expected                  |
| ---- | -------- | ------------------------------- | ------------------------- |
| NT-1 | APPROVED | ReviewCandidateApplication(any) | Rejected — terminal state |
| NT-2 | REJECTED | ReviewCandidateApplication(any) | Rejected — terminal state |
| NT-3 | APPROVED | SubmitCandidateApplication      | Rejected — terminal state |
| NT-4 | REJECTED | SubmitCandidateApplication      | Rejected — terminal state |

### Invariant Tests

| ID   | Invariant                                        | Formal                                                                          |
| ---- | ------------------------------------------------ | ------------------------------------------------------------------------------- |
| IV-1 | Terminal states cannot transition to active      | `status in {APPROVED, REJECTED} -> nextStatus not in {SUBMITTED, UNDER_REVIEW}` |
| IV-2 | Every submitted application has rules acceptance | `status != [new] -> ruleAcceptance.acceptedAt != null`                          |
| IV-3 | Every submitted application has LGPD consent     | `status != [new] -> lgpdConsentAccepted = true`                                 |

---

## Rule Validation Tests

### SubmitCandidateApplication Rules

Source: [SubmitCandidateApplication](operations.md#submitcandidateapplication)

| ID    | Rule                                      | Test Description                                                     | Expected |
| ----- | ----------------------------------------- | -------------------------------------------------------------------- | -------- |
| RV-1  | R1: rules acceptance mandatory            | Submit without `acceptedRegulationVersion` or `acceptedRegulationAt` | 400      |
| RV-2  | R2: LGPD consent mandatory                | Submit with `lgpdConsentAccepted = false`                            | 400      |
| RV-3  | R3: required fields present               | Submit with missing `fullName`                                       | 400      |
| RV-4  | R3: required fields present               | Submit with missing `email`                                          | 400      |
| RV-5  | R3: required fields present               | Submit with missing `whatsapp`                                       | 400      |
| RV-6  | R3: required fields present               | Submit with missing `birthDate`                                      | 400      |
| RV-7  | R4: email format validation               | Submit with invalid email format                                     | 400      |
| RV-8  | R5: duplicate WhatsApp                    | Submit with existing WhatsApp number                                 | 409      |
| RV-9  | R5: duplicate email                       | Submit with existing canonical email                                 | 409      |
| RV-10 | R6: preferredTimeWindows min 1            | Submit with empty `preferredTimeWindows`                             | 400      |
| RV-11 | R7: tracker detail conditionally required | Submit `trackerUsage=YES` without `trackerDetail`                    | 400      |
| RV-12 | R8: cityState pattern                     | Submit with `cityState` missing `/` separator                        | 400      |
| RV-13 | R9: minimum age 18                        | Submit with `birthDate` making candidate 17 years old                | 400      |

### ReviewCandidateApplication Rules

Source: [ReviewCandidateApplication](operations.md#reviewcandidateapplication)

| ID    | Rule                            | Test Description                                     | Expected |
| ----- | ------------------------------- | ---------------------------------------------------- | -------- |
| RV-14 | R1: caller must be authorized   | Review without auth token                            | 401      |
| RV-15 | R1: caller must have permission | Review with token lacking `player-onboarding.review` | 403      |
| RV-16 | R2: application must exist      | Review with non-existent `id`                        | 404      |
| RV-17 | R3: valid pre-review status     | Review application in APPROVED status                | 400      |
| RV-18 | R3: valid pre-review status     | Review application in REJECTED status                | 400      |
| RV-19 | R4: decision must be valid      | Review with invalid decision value                   | 400      |

---

## Calculation Tests

Source: [operations.md](operations.md)

| ID   | Calculation                        | Test Description                                      | Expected                                  |
| ---- | ---------------------------------- | ----------------------------------------------------- | ----------------------------------------- |
| CT-1 | Submit.C1: canonical email         | Email with mixed case and spaces → lowercased/trimmed | `canonicalEmail = lowercase(trim(email))` |
| CT-2 | Submit.C2: initial status          | Successful submission → status = SUBMITTED            | `status = SUBMITTED`                      |
| CT-3 | Review.C1: approve decision        | Decision = APPROVE → status = APPROVED                | `nextStatus = APPROVED`                   |
| CT-4 | Review.C1: reject decision         | Decision = REJECT → status = REJECTED                 | `nextStatus = REJECTED`                   |
| CT-5 | Review.C2: retention cutoff        | Reject → retentionUntil = reviewedAt + 365 days       | `retentionUntil = reviewedAt + 365d`      |
| CT-6 | Review.C2: no retention on approve | Approve → retentionUntil = null                       | `retentionUntil = null`                   |

---

## Postcondition Tests

| ID   | Operation                  | Postcondition                               | Test Description                                |
| ---- | -------------------------- | ------------------------------------------- | ----------------------------------------------- |
| PC-1 | SubmitCandidateApplication | Application persisted with SUBMITTED status | After submit, find by id returns SUBMITTED      |
| PC-2 | SubmitCandidateApplication | ruleAcceptance stored                       | Persisted record has version and timestamp      |
| PC-3 | SubmitCandidateApplication | Available for screening                     | Application visible in admin backlog            |
| PC-4 | ReviewCandidateApplication | Final status persisted                      | After review, status is APPROVED or REJECTED    |
| PC-5 | ReviewCandidateApplication | reviewedAt populated                        | Review timestamp stored                         |
| PC-6 | ReviewCandidateApplication | Review note stored when provided            | reviewDecisionNote persisted                    |
| PC-7 | ReviewCandidateApplication | Rejected retention cutoff                   | retentionUntil = reviewedAt + 365d for REJECTED |

---

## Contract Tests

Source: [interfaces.md](interfaces.md)

| ID   | Endpoint                         | Scenario            | Expected Status | Expected Body Shape                         |
| ---- | -------------------------------- | ------------------- | --------------- | ------------------------------------------- |
| CO-1 | GET /onboarding/flow             | Success             | 200             | `{ regulationVersion, groups[], ... }`      |
| CO-2 | POST /onboarding/candidates      | Valid submission    | 201             | `{ id, status, submittedAt, confirmation }` |
| CO-3 | POST /onboarding/candidates      | Validation failure  | 400             | `{ code, message, details }`                |
| CO-4 | POST /onboarding/candidates      | Duplicate candidate | 409             | `{ code: 'DUPLICATE_CANDIDATE', ... }`      |
| CO-5 | PATCH /candidates/{id}/review    | Approved            | 200             | `{ id, status, reviewedAt }`                |
| CO-6 | PATCH /candidates/{id}/review    | Unauthorized        | 401             | `{ code, message }`                         |
| CO-7 | PATCH /candidates/{id}/review    | Forbidden           | 403             | `{ code, message }`                         |
| CO-8 | PATCH /candidates/{id}/review    | Not found           | 404             | `{ code: 'NOT_FOUND', message }`            |
| CO-9 | GET /admin/onboarding/candidates | With status filter  | 200             | Paginated candidate list                    |

---

## Mapping Tests

Source: [mappings.md](mappings.md)

| ID   | Mapping                        | Test Description                                     |
| ---- | ------------------------------ | ---------------------------------------------------- |
| MT-1 | SubmitCandidateRequestToEntity | All HTTP body fields map correctly to domain entity  |
| MT-2 | SubmitCandidateRequestToEntity | Optional fields (nick\*, trackerDetail) default null |
| MT-3 | SubmitCandidateRequestToEntity | Email is canonicalized in mapping output             |

---

## Test Count Summary

| Category             | Count  |
| -------------------- | ------ |
| State transitions    | 6      |
| Negative transitions | 4      |
| Invariants           | 3      |
| Rule validations     | 19     |
| Calculations         | 6      |
| Postconditions       | 7      |
| Contract tests       | 9      |
| Mapping tests        | 3      |
| **Total**            | **57** |

---

## Traceability Matrix

| Obligation | Evidence File                                | Status  |
| ---------- | -------------------------------------------- | ------- |
| ST-1       | candidate-application-policy.service.test.ts | covered |
| ST-2       | candidate-review-policy.service.test.ts      | covered |
| ST-3       | candidate-review-policy.service.test.ts      | covered |
| ST-4       | candidate-review-policy.service.test.ts      | covered |
| ST-5       | candidate-review-policy.service.test.ts      | covered |
| ST-6       | candidate-review-policy.service.test.ts      | covered |
| NT-1       | candidate-review-policy.service.test.ts      | covered |
| NT-2       | candidate-review-policy.service.test.ts      | covered |
| NT-3       | candidate-review-policy.service.test.ts      | covered |
| NT-4       | candidate-review-policy.service.test.ts      | covered |
| IV-1       | candidate-review-policy.service.test.ts      | covered |
| IV-2       | candidate-application-policy.service.test.ts | covered |
| IV-3       | candidate-application-policy.service.test.ts | covered |
| RV-1       | candidate-application-policy.service.test.ts | covered |
| RV-2       | candidate-application-policy.service.test.ts | covered |
| RV-3       | candidate-application-policy.service.test.ts | covered |
| RV-4       | candidate-application-policy.service.test.ts | covered |
| RV-5       | candidate-application-policy.service.test.ts | covered |
| RV-6       | candidate-application-policy.service.test.ts | covered |
| RV-7       | candidate-application-policy.service.test.ts | covered |
| RV-8       | candidate-application-policy.service.test.ts | covered |
| RV-9       | candidate-application-policy.service.test.ts | covered |
| RV-10      | candidate-application-policy.service.test.ts | covered |
| RV-11      | candidate-application-policy.service.test.ts | covered |
| RV-12      | candidate-application-policy.service.test.ts | covered |
| RV-13      | candidate-application-policy.service.test.ts | covered |
| RV-14      | onboarding.routes.auth.test.ts               | covered |
| RV-15      | onboarding.routes.auth.test.ts               | covered |
| RV-16      | onboarding.routes.test.ts                    | covered |
| RV-17      | candidate-review-policy.service.test.ts      | covered |
| RV-18      | candidate-review-policy.service.test.ts      | covered |
| RV-19      | onboarding.routes.test.ts                    | covered |
| CT-1       | submit-candidate-application.test.ts         | covered |
| CT-2       | submit-candidate-application.test.ts         | covered |
| CT-3       | candidate-review-policy.service.test.ts      | covered |
| CT-4       | candidate-review-policy.service.test.ts      | covered |
| CT-5       | candidate-review-policy.service.test.ts      | covered |
| CT-6       | candidate-review-policy.service.test.ts      | covered |
| PC-1       | submit-candidate-application.test.ts         | covered |
| PC-2       | submit-candidate-application.test.ts         | covered |
| PC-3       | onboarding.routes.test.ts                    | covered |
| PC-4       | onboarding.routes.test.ts                    | covered |
| PC-5       | onboarding.routes.test.ts                    | covered |
| PC-6       | onboarding.routes.test.ts                    | covered |
| PC-7       | onboarding.routes.test.ts                    | covered |
| CO-1       | onboarding.routes.test.ts                    | covered |
| CO-2       | onboarding.routes.test.ts                    | covered |
| CO-3       | onboarding.routes.test.ts                    | covered |
| CO-4       | onboarding.routes.test.ts                    | covered |
| CO-5       | onboarding.routes.test.ts                    | covered |
| CO-6       | onboarding.routes.auth.test.ts               | covered |
| CO-7       | onboarding.routes.auth.test.ts               | covered |
| CO-8       | onboarding.routes.test.ts                    | covered |
| CO-9       | onboarding.routes.test.ts                    | covered |
| MT-1       | onboarding.routes.test.ts                    | covered |
| MT-2       | onboarding.routes.test.ts                    | covered |
| MT-3       | candidate-application-policy.service.test.ts | covered |

---

## Story To Test Mapping

| Story                                                                                    | Key test IDs                                                                                                                                                                                      |
| ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| US-01 Public Journey: Candidate Submits Onboarding Application                           | ST-1, ST-2, RV-1, RV-2, RV-3, RV-4, RV-5, RV-6, RV-7, RV-8, RV-9, RV-10, CT-1, CT-2, CT-3, PC-1, PC-2, PC-3, CO-1, CO-2, CO-3, MT-1, MT-2, MT-3                                                   |
| US-02 Admin Operations Journey: Reviewer Records Manual Decision                         | ST-3, ST-4, ST-5, ST-6, NT-1, NT-2, NT-3, NT-4, IV-1, IV-2, IV-3, RV-11, RV-12, RV-13, RV-14, RV-15, RV-16, RV-17, RV-18, RV-19, CT-4, CT-5, CT-6, PC-4, PC-5, PC-6, PC-7, CO-4, CO-5, CO-8, CO-9 |
| US-03 Cross-Feature Integration: Approved Output Feeds Player Creation                   | PC-2, PC-7, CO-5                                                                                                                                                                                  |
| US-04 Error And Edge Case Journey: Deterministic Feedback On Duplicates And Invalid Data | RV-1, RV-2, RV-3, RV-4, RV-5, RV-6, NT-1, NT-2, NT-3, NT-4, CO-2, CO-3, CO-6, CO-7                                                                                                                |

## Pilot Must-Pass Subset (Wave 1)

| Priority | Test IDs | Why it is gate-critical | Evidence file targets |
| --- | --- | --- | --- |
| P0 | RV-8, RV-9, CO-4 | Enforce candidate dedupe policy for canonical email and WhatsApp before intake write. | `backend/src/domain/onboarding/candidate-application-policy.service.test.ts`, `backend/src/infrastructure/http/routes/onboarding.routes.test.ts` |
| P0 | RV-14, RV-15, CO-6, CO-7 | Guarantee admin review endpoint auth and permission gating. | `backend/src/infrastructure/http/routes/onboarding.routes.auth.test.ts` |
| P0 | ST-3, ST-4, RV-16, RV-17, RV-18, RV-19, CO-5, CO-8 | Protect decision lifecycle correctness for approve/reject transitions and error handling. | `backend/src/domain/onboarding/candidate-review-policy.service.test.ts`, `backend/src/infrastructure/http/routes/onboarding.routes.test.ts` |
| P0 | PC-2, PC-7, CO-5 | Preserve cross-feature handoff payload completeness for approved/rejected output. | `backend/src/use-cases/onboarding/submit-candidate-application.test.ts`, `backend/src/infrastructure/http/routes/onboarding.routes.test.ts` |
| P1 | CO-1, CO-9, CT-1, CT-2 | Validate public flow rendering and admin list behavior with deterministic mapping. | `backend/src/infrastructure/http/routes/onboarding.routes.test.ts` |

## Pilot Execution Checklist

1. Freeze Wave 1 onboarding scope to P0 IDs.
Pass criteria: all P0 IDs are executable and linked to concrete test files.

2. Run dedupe and intake validation gate first.
Pass criteria: RV-8, RV-9, CO-4 pass with deterministic duplicate behavior.

3. Run admin auth/permission gate second.
Pass criteria: RV-14, RV-15, CO-6, CO-7 return expected unauthorized/forbidden responses.

4. Run review lifecycle gate third.
Pass criteria: ST-3/4 and RV-16/17/18/19 with CO-5/8 pass for valid and invalid decision flows.

5. Run cross-feature output gate fourth.
Pass criteria: PC-2, PC-7, CO-5 prove review output includes required fields for downstream intake.

6. Run optional P1 flow checks.
Pass criteria: CO-1, CO-9, CT-1, CT-2 pass and show stable public/admin views.

7. Capture blockers and evidence package.
Pass criteria: all open blockers have owner, target fix, and evidence requirements.

8. Compute final Wave 1 verdict.
Pass criteria: zero failing P0 tests and no open P0 blocker.

## Pilot Go No-Go Blockers Register

| Blocker ID | Status | Blocker | Why it blocks Wave 1 | Required evidence to clear |
| --- | --- | --- | --- | --- |
| ONB-BLK-01 | closed | Permission model drift between interfaces and route implementation for admin onboarding actions. | Admin review/list/detail authorization can diverge from documented contracts. | Closed on 2026-04-24 with split permission enforcement in routes, role definitions, and route auth tests. |
| ONB-BLK-02 | closed | Rule flow grouping/version policy is documented as configurable but implemented with hardcoded values. | Regulatory behavior cannot be evolved safely and deterministically. | Closed on 2026-04-24 via domain policy resolver and deterministic grouping tests. |
| ONB-BLK-03 | closed | Approved onboarding handoff to player-management is documented but not implemented as a concrete integration path. | Cross-feature onboarding completion cannot be verified end-to-end. | Closed on 2026-04-24 via intake handoff gateway contract, repository implementation, and review use-case tests. |
| ONB-BLK-04 | closed | Dedupe guarantees are app-level only; database uniqueness constraints are missing for candidate identity keys. | Concurrent submissions can bypass dedupe and create conflicting candidate records. | Closed on 2026-04-24 via DB unique indexes plus 23505 duplicate mapping coverage in submission use-case tests. |
| ONB-BLK-05 | closed | UI review artifact was stale relative to current onboarding implementation evidence. | Pilot decisions could rely on outdated UI blocker status even after backend closure. | Closed on 2026-04-24 by refreshing UI-REVIEW with current route/component/state/accessibility evidence and updated verdict. |

## Pilot Evidence Package

1. Intake and dedupe evidence
- Test outputs for RV-8, RV-9, CO-4 including duplicate scenario assertions.

2. Admin authorization evidence
- Route auth test outputs for RV-14, RV-15, CO-6, CO-7 and permission matrix mapping.

3. Lifecycle and decision evidence
- Transition and rule test outputs for ST-3, ST-4, RV-16, RV-17, RV-18, RV-19.

4. Cross-feature handoff evidence
- Serialized approved/rejected output payload examples and downstream intake integration assertions.

5. Decision artifact
- Final blocker register snapshot plus Wave 1 PASS/FLAG/BLOCK decision.

## Pilot Decisions Provenance

This test gate follows policy decisions recorded in [PILOT-DECISIONS.md](PILOT-DECISIONS.md).
