---
id: player-onboarding
feature: player-onboarding
title: Player Onboarding Mappings
summary: Transformations between HTTP payloads and candidate application entity.
status: implemented
pillar: platform
domain: onboarding-candidates-mappings
audience:
  - developers
priority: p1
lang: en
owners:
  - backend-core
updatedAt: 2026-04-24
dependencies:
  - interfaces.md
  - domain.md
includes: []
---

# Mappings: Player Onboarding

## SubmitCandidateRequestToEntity

**From:** API Request (`POST /onboarding/candidates`)
**To:** CandidateApplication
**Direction:** Inbound

### Field Mapping

| Source Field              | Target Field                     | Transform        | Notes                          |
| ------------------------- | -------------------------------- | ---------------- | ------------------------------ |
| fullName                  | fullName                         | direct + trim    | remove extra spaces            |
| birthDate                 | birthDate                        | direct           | ISO date format                |
| cityState                 | cityState                        | direct + trim    | expected City/State format     |
| whatsapp                  | whatsapp                         | direct + trim    | light whitespace normalization |
| email                     | email                            | lowercase + trim | base key for duplicate checks  |
| educationLevel            | educationLevel                   | enum map         | form values mapped to enum     |
| currentWorkStatus         | currentWorkStatus                | enum map         | form values mapped to enum     |
| dailyPokerAvailability    | dailyPokerAvailability           | enum map         | form values mapped to enum     |
| preferredTimeWindows      | preferredTimeWindows             | enum array map   | minimum 1 item                 |
| weeklyDaysAvailability    | weeklyDaysAvailability           | enum map         | form values mapped to enum     |
| pokerExperienceRange      | pokerExperienceRange             | enum map         | form values mapped to enum     |
| primaryModality           | primaryModality                  | enum map         | form values mapped to enum     |
| hasOwnComputer            | hasOwnComputer                   | direct           | boolean                        |
| hasDiscordFamiliarity     | hasDiscordFamiliarity            | direct           | boolean                        |
| trackerUsage              | trackerUsage                     | enum map         | yes/no/other                   |
| trackerDetail             | trackerDetail                    | direct + trim    | required for yes/other         |
| nickPokerStars            | nickPokerStars                   | direct + trim    | optional                       |
| nickGGPoker               | nickGGPoker                      | direct + trim    | optional                       |
| nickSuprema               | nickSuprema                      | direct + trim    | optional                       |
| lgpdConsentAccepted       | lgpdConsentAccepted              | direct           | must be true                   |
| acceptedRegulationVersion | ruleAcceptance.regulationVersion | direct           | version read in flow           |
| acceptedRegulationAt      | ruleAcceptance.acceptedAt        | direct           | acceptance timestamp           |
| (system)                  | ruleAcceptance.acceptanceSource  | default          | `onboarding-flow`              |
| (system)                  | status                           | default          | `SUBMITTED`                    |
| (system)                  | submittedAt                      | default(now)     | timestamp do backend           |

### Defaults

| Target Field                    | Default Value     | Condition |
| ------------------------------- | ----------------- | --------- |
| ruleAcceptance.acceptanceSource | `onboarding-flow` | Always    |
| status                          | `SUBMITTED`       | Always    |
| submittedAt                     | `now()`           | Always    |

### Validation

| Field                        | Validation                            | On Failure                       |
| ---------------------------- | ------------------------------------- | -------------------------------- |
| email                        | valid email format                    | 400 (`VALIDATION_ERROR`)         |
| whatsapp/email               | must not duplicate existing candidate (pre-check + DB unique constraints) | 409 (`DUPLICATE_CANDIDATE`)      |
| preferredTimeWindows         | at least one option                   | 400 (`VALIDATION_ERROR`)         |
| cityState                    | strict `City/State` format            | 400 (`VALIDATION_ERROR`)         |
| birthDate                    | age must be >= 18                     | 400 (`VALIDATION_ERROR`)         |
| lgpdConsentAccepted          | must be true                          | 400 (`LGPD_CONSENT_REQUIRED`)    |
| acceptedRegulationVersion/At | both required                         | 400 (`RULE_ACCEPTANCE_REQUIRED`) |

## ReviewDecisionToRetention

**From:** Review decision (`APPROVE` or `REJECT`)
**To:** `CandidateApplication.retentionUntil`
**Direction:** Inbound (internal)

| Source Field | Target Field   | Transform      | Notes                                           |
| ------------ | -------------- | -------------- | ----------------------------------------------- |
| decision     | retentionUntil | conditional    | set only when decision is `REJECT`              |
| reviewedAt   | retentionUntil | add `365 days` | deterministic retention for rejected candidates |
