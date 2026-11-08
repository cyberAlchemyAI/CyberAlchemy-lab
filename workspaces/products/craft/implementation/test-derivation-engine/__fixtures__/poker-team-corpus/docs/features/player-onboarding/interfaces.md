---
id: player-onboarding
feature: player-onboarding
title: Player Onboarding Interfaces
summary: HTTP contracts for public onboarding flow and internal candidate review.
status: implemented
pillar: platform
domain: onboarding-candidates-interfaces
audience:
  - developers
priority: p1
lang: en
owners:
  - backend-core
  - web-core
updatedAt: 2026-04-24
dependencies:
  - operations.md
  - mappings.md
includes: []
---

# Interfaces: Player Onboarding

## External: PublicOnboardingAPI (REST)

### GET /onboarding/flow

**Exposes:** onboarding screen flow and candidate form metadata
**Auth:** public

**Request:**

| Field             | Type                     | Maps To                                          |
| ----------------- | ------------------------ | ------------------------------------------------ |
| regulationVersion | string (query, optional) | RuleScreenGroupingPolicy.input.regulationVersion |

**Responses:**

| Status | Condition | Body                                                                                   |
| ------ | --------- | -------------------------------------------------------------------------------------- |
| 200    | Success   | `{ regulationVersion, groups[], acceptanceRequired: true, lgpdConsentRequired: true }` |

### POST /onboarding/candidates

**Exposes:** [SubmitCandidateApplication](operations.md#submitcandidateapplication)
**Auth:** public

**Request:**

| Field                     | Type     | Maps To                                              |
| ------------------------- | -------- | ---------------------------------------------------- |
| fullName                  | string   | SubmitCandidateApplication.fullName                  |
| birthDate                 | date     | SubmitCandidateApplication.birthDate                 |
| cityState                 | string   | SubmitCandidateApplication.cityState                 |
| whatsapp                  | string   | SubmitCandidateApplication.whatsapp                  |
| email                     | string   | SubmitCandidateApplication.email                     |
| educationLevel            | string   | SubmitCandidateApplication.educationLevel            |
| currentWorkStatus         | string   | SubmitCandidateApplication.currentWorkStatus         |
| dailyPokerAvailability    | string   | SubmitCandidateApplication.dailyPokerAvailability    |
| preferredTimeWindows      | string[] | SubmitCandidateApplication.preferredTimeWindows      |
| weeklyDaysAvailability    | string   | SubmitCandidateApplication.weeklyDaysAvailability    |
| pokerExperienceRange      | string   | SubmitCandidateApplication.pokerExperienceRange      |
| primaryModality           | string   | SubmitCandidateApplication.primaryModality           |
| hasOwnComputer            | boolean  | SubmitCandidateApplication.hasOwnComputer            |
| hasDiscordFamiliarity     | boolean  | SubmitCandidateApplication.hasDiscordFamiliarity     |
| trackerUsage              | string   | SubmitCandidateApplication.trackerUsage              |
| trackerDetail             | string   | SubmitCandidateApplication.trackerDetail             |
| nickPokerStars            | string   | SubmitCandidateApplication.nickPokerStars            |
| nickGGPoker               | string   | SubmitCandidateApplication.nickGGPoker               |
| nickSuprema               | string   | SubmitCandidateApplication.nickSuprema               |
| lgpdConsentAccepted       | boolean  | SubmitCandidateApplication.lgpdConsentAccepted       |
| acceptedRegulationVersion | string   | SubmitCandidateApplication.acceptedRegulationVersion |
| acceptedRegulationAt      | datetime | SubmitCandidateApplication.acceptedRegulationAt      |

**Responses:**

| Status | Condition           | Body                                                     |
| ------ | ------------------- | -------------------------------------------------------- |
| 201    | Application created | `{ id, status, submittedAt, confirmation: 'submitted' }` |
| 400    | Rule violation      | `{ code, message, details }`                             |
| 409    | Duplicate candidate | `{ code: 'DUPLICATE_CANDIDATE', message, details }`      |

### PATCH /onboarding/candidates/{id}/review

**Exposes:** [ReviewCandidateApplication](operations.md#reviewcandidateapplication)
**Auth:** bearer token + permission `player-onboarding.review.evaluateApplication`

**Request:**

| Field              | Type        | Maps To                                       |
| ------------------ | ----------- | --------------------------------------------- |
| id                 | uuid (path) | ReviewCandidateApplication.id                 |
| decision           | string      | ReviewCandidateApplication.decision           |
| reviewDecisionNote | string      | ReviewCandidateApplication.reviewDecisionNote |

**Responses:**

| Status  | Condition             | Body                             |
| ------- | --------------------- | -------------------------------- |
| 200     | Review registered     | `{ id, status, reviewedAt }`     |
| 400     | Rule violation        | `{ code, message, details }`     |
| 401/403 | No permission         | `{ code, message }`              |
| 404     | Application not found | `{ code: 'NOT_FOUND', message }` |

### GET /admin/onboarding/candidates

**Exposes:** pending/recent candidate backlog for manual review
**Auth:** bearer token + permission `player-onboarding.review.listCandidates`

**Request:**

| Field  | Type                      | Maps To               |
| ------ | ------------------------- | --------------------- |
| status | string (query, optional)  | backlog filter status |
| page   | integer (query, optional) | pagination            |
| limit  | integer (query, optional) | pagination            |

**Responses:**

| Status  | Condition     | Body                              |
| ------- | ------------- | --------------------------------- |
| 200     | Success       | `{ items[], page, limit, total }` |
| 401/403 | No permission | `{ code, message }`               |

### GET /admin/onboarding/candidates/{id}

**Exposes:** candidate detail for review page
**Auth:** bearer token + permission `player-onboarding.review.getCandidateDetail`

**Request:**

| Field | Type        | Maps To                    |
| ----- | ----------- | -------------------------- |
| id    | uuid (path) | candidate detail lookup id |

**Responses:**

| Status  | Condition             | Body                             |
| ------- | --------------------- | -------------------------------- |
| 200     | Success               | `{ candidateApplication }`       |
| 401/403 | No permission         | `{ code, message }`              |
| 404     | Application not found | `{ code: 'NOT_FOUND', message }` |
