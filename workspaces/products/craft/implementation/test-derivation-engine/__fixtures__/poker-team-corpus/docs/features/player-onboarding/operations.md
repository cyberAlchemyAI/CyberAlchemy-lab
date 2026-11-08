---
id: player-onboarding
feature: player-onboarding
title: Player Onboarding Operations
summary: Operations for candidate submission and manual review.
status: implemented
pillar: operations
domain: onboarding-candidates-operations
audience:
  - developers
  - operations
priority: p1
lang: en
owners:
  - backend-core
  - operations-core
updatedAt: 2026-04-30
dependencies:
  - SPEC.md
  - domain.md
  - states.md
  - events.md
  - interfaces.md
  - queries.md
  - mappings.md
includes: []
---

# Operations: Player Onboarding

## Domain Policy Ownership

Onboarding validation and review transition policies are owned by domain services.

- Submission policy authority: [`backend/src/domain/onboarding/candidate-application-policy.service.ts`](../../../backend/src/domain/onboarding/candidate-application-policy.service.ts)
- Review policy authority: [`backend/src/domain/onboarding/candidate-review-policy.service.ts`](../../../backend/src/domain/onboarding/candidate-review-policy.service.ts)
- Use-case orchestrators:
  - [`backend/src/use-cases/onboarding/submit-candidate-application.ts`](../../../backend/src/use-cases/onboarding/submit-candidate-application.ts)
  - [`backend/src/use-cases/onboarding/review-candidate-application.ts`](../../../backend/src/use-cases/onboarding/review-candidate-application.ts)

## SubmitCandidateApplication

**Type:** Operation (mutation)
**Actor:** Candidate (public)
**Triggers:** POST /onboarding/candidates

### Input

| Field                     | Type                    | Required | Description                |
| ------------------------- | ----------------------- | -------- | -------------------------- |
| fullName                  | string                  | yes      | Full name                  |
| birthDate                 | date                    | yes      | Birth date                 |
| cityState                 | string                  | yes      | City and state             |
| whatsapp                  | string                  | yes      | Primary WhatsApp           |
| email                     | string                  | yes      | Primary email              |
| educationLevel            | EducationLevel          | yes      | Education level            |
| currentWorkStatus         | WorkStatus              | yes      | Employment status          |
| dailyPokerAvailability    | DailyAvailabilityRange  | yes      | Daily available hours      |
| preferredTimeWindows      | TimeWindow[]            | yes      | Preferred time windows     |
| weeklyDaysAvailability    | WeeklyAvailabilityRange | yes      | Weekly available days      |
| pokerExperienceRange      | PokerExperienceRange    | yes      | Poker experience range     |
| primaryModality           | PokerModality           | yes      | Primary modality           |
| hasOwnComputer            | boolean                 | yes      | Has own computer           |
| hasDiscordFamiliarity     | boolean                 | yes      | Familiar with Discord      |
| trackerUsage              | TrackerUsageType        | yes      | Tracker usage              |
| trackerDetail             | string                  | no       | Tracker/tool detail        |
| nickPokerStars            | string                  | no       | Nick PokerStars            |
| nickGGPoker               | string                  | no       | Nick GGPoker               |
| nickSuprema               | string                  | no       | Nick Suprema               |
| lgpdConsentAccepted       | boolean                 | yes      | LGPD consent acceptance    |
| acceptedRegulationVersion | string                  | yes      | Accepted rules version     |
| acceptedRegulationAt      | datetime                | yes      | Rules acceptance timestamp |

### Rules

| ID  | Rule                                                         | Formal                                                                                                    |
| --- | ------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------- |
| R1  | rules acceptance is mandatory                                | `acceptedRegulationVersion != '' and acceptedRegulationAt != null`                                        |
| R2  | LGPD consent is mandatory                                    | `lgpdConsentAccepted = true`                                                                              |
| R3  | required fields must exist                                   | `all(requiredFields) != null and trim(stringFields) != ''`                                                |
| R4  | email must have minimum valid format                         | `email matches ^[^@\s]+@[^@\s]+\.[^@\s]+$`                                                                |
| R5  | duplicate by WhatsApp or email must be blocked               | `count(CandidateApplication where whatsapp = input.whatsapp or email = lowercase(trim(input.email))) = 0` |
| R6  | preferredTimeWindows must include at least one option        | `len(preferredTimeWindows) >= 1`                                                                          |
| R7  | tracker detail is required when trackerUsage requires detail | `(trackerUsage in {YES, OTHER}) -> len(trim(trackerDetail)) > 0`                                          |
| R8  | city/state must follow strict City/State pattern             | `cityState matches ^[^/]+/[^/]+$`                                                                         |
| R9  | candidate must be at least 18 years old                      | `ageInYears(birthDate, now()) >= 18`                                                                      |

### Calculations

| ID  | Calculation     | Formula                                   |
| --- | --------------- | ----------------------------------------- |
| C1  | canonical email | `canonicalEmail = lowercase(trim(email))` |
| C2  | initial status  | `status = SUBMITTED`                      |

### State Transition

`CandidateApplication: [new] -> SUBMITTED`

### Postconditions

| ID  | Class                 | Guarantee                                                  | Formal Assertion                                                                                                  | Traceability |
| --- | --------------------- | ---------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- | ------------ |
| P1  | State Guarantee       | Application is persisted with `SUBMITTED` status.          | `status = SUBMITTED`                                                                                             | [CandidateApplicationLifecycle](states.md#candidateapplicationlifecycle) |
| P2  | Persistence Guarantee | `ruleAcceptance` is stored with provided version and timestamp. | `ruleAcceptance.regulationVersion = acceptedRegulationVersion and ruleAcceptance.acceptedAt = acceptedRegulationAt` | [CandidateApplication](domain.md#candidateapplication), [SubmitCandidateRequestToEntity](mappings.md#submitcandidaterequesttoentity) |
| P3  | Integration Guarantee | Application becomes available for manual screening.         | `ListCandidateApplications(status=SUBMITTED).items contains id`                                                  | [ListCandidateApplications](queries.md#listcandidateapplications), [PublicOnboardingAPI](interfaces.md#external-publiconboardingapi-rest) |
| P4  | Integration Guarantee | Submission emits deterministic onboarding intake signal.   | `emit(CandidateApplicationSubmitted where applicationId = id and canonicalEmail = lowercase(trim(email)))`      | [CandidateApplicationSubmitted](events.md#candidateapplicationsubmitted), [produces semantics](../../../domainspec/RELATIONSHIPS.md#produces--operation--event) |

### Error States

| Condition             | Result                                      |
| --------------------- | ------------------------------------------- |
| R1-R4, R6-R9 violated | Validation error (400)                      |
| R5 violated           | Conflict error (409, `DUPLICATE_CANDIDATE`) |
| Persistence failure   | Internal error (500)                        |

## ReviewCandidateApplication

**Type:** Operation (mutation)
**Actor:** Authenticated leadership/operations user
**Triggers:** PATCH /onboarding/candidates/{id}/review

### Input

| Field              | Type                  | Required | Description            |
| ------------------ | --------------------- | -------- | ---------------------- |
| id                 | uuid                  | yes      | Application identifier |
| decision           | enum(APPROVE, REJECT) | yes      | Manual review decision |
| reviewDecisionNote | string                | no       | Supporting review note |

### Rules

| ID  | Rule                                                   | Formal                                                                                                      |
| --- | ------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------- |
| R1  | caller must be authenticated and authorized for review | `AuthenticateRequest = success and AuthorizeRequest(requiredPermission='player-onboarding.review.evaluateApplication') = ALLOW` |
| R2  | application must exist                                 | `exists(CandidateApplication.id = input.id)`                                                                |
| R3  | only SUBMITTED or UNDER_REVIEW can be reviewed         | `status in {SUBMITTED, UNDER_REVIEW}`                                                                       |
| R4  | decision must be valid                                 | `decision in {APPROVE, REJECT}`                                                                             |

### Calculations

| ID  | Calculation             | Formula                                                           |
| --- | ----------------------- | ----------------------------------------------------------------- |
| C1  | next status by decision | `nextStatus = (decision = APPROVE) ? APPROVED : REJECTED`         |
| C2  | retention cutoff        | `retentionUntil = (decision = REJECT) ? reviewedAt + 365d : null` |

### State Transition

`CandidateApplication: SUBMITTED|UNDER_REVIEW -> APPROVED|REJECTED`

### Postconditions

| ID  | Class                 | Guarantee                                                                 | Formal Assertion                                                                                                                                | Traceability |
| --- | --------------------- | ------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | ------------ |
| P1  | State Guarantee       | Application is updated with final status.                                 | `status = nextStatus and nextStatus in {APPROVED, REJECTED}`                                                                                  | [CandidateApplicationLifecycle](states.md#candidateapplicationlifecycle) |
| P2  | Persistence Guarantee | `reviewedAt` is populated with review timestamp.                          | `reviewedAt != null`                                                                                                                           | [CandidateApplication](domain.md#candidateapplication) |
| P3  | Audit Guarantee       | Review note is stored when provided.                                      | `(reviewDecisionNote != null and trim(reviewDecisionNote) != '') -> persisted.reviewDecisionNote = trim(reviewDecisionNote)`                 | [CandidateApplication](domain.md#candidateapplication), [CandidateApplicationReviewed](events.md#candidateapplicationreviewed) |
| P4  | Temporal Guarantee    | Rejection retention cutoff is derived from review timestamp.              | `(decision = REJECT) -> retentionCutoff = reviewedAt + 365d`                                                                                  | [ReviewDecisionToRetention](mappings.md#reviewdecisiontoretention), [CandidateApplicationLifecycle](states.md#candidateapplicationlifecycle) |
| P5  | Persistence Guarantee | Rejected applications persist deterministic `retentionUntil` cutoff.      | `(decision = REJECT) -> retentionUntil = reviewedAt + 365d and (decision = APPROVE) -> retentionUntil = null`                                | [CandidateApplication](domain.md#candidateapplication), [ReviewDecisionToRetention](mappings.md#reviewdecisiontoretention) |
| P6  | Integration Guarantee | Approved applications publish deterministic intake handoff for player-management. | `(decision = APPROVE) -> emit(CandidateApplicationReviewed) and handoffPayload = f(candidateApplication, reviewMetadata) and deterministic(f)` | [CandidateApplicationReviewed](events.md#candidateapplicationreviewed), [SPEC Cross-Feature Dependencies](SPEC.md#cross-feature-dependencies), [produces semantics](../../../domainspec/RELATIONSHIPS.md#produces--operation--event), [produces-for semantics](../../../domainspec/RELATIONSHIPS.md#produces-for--operationa--entityb) |

### Error States

| Condition           | Result                             |
| ------------------- | ---------------------------------- |
| R1 violated         | Authentication/authorization error |
| R2 violated         | Not found (404)                    |
| R3-R4 violated      | Validation error (400)             |
| Persistence failure | Internal error (500)               |
