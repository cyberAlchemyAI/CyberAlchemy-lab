---
id: player-onboarding
feature: player-onboarding
title: Player Onboarding Domain
summary: Structural concepts for candidate applications, rules acceptance, and review status.
status: implemented
pillar: operations
domain: onboarding-candidates-domain
audience:
  - developers
  - operations
priority: p1
lang: en
owners:
  - operations-core
updatedAt: 2026-04-08
dependencies:
  - SPEC.md
  - states.md
includes: []
---

# Domain: Player Onboarding

## Entities

### CandidateApplication

Represents a candidate application submitted after reading and accepting team rules.

| Field                  | Type                                                | Required | Description                                |
| ---------------------- | --------------------------------------------------- | -------- | ------------------------------------------ |
| id                     | uuid                                                | yes      | Unique application identifier              |
| fullName               | string                                              | yes      | Candidate full name                        |
| birthDate              | date                                                | yes      | Candidate birth date                       |
| cityState              | string                                              | yes      | City and state                             |
| whatsapp               | string                                              | yes      | Primary WhatsApp contact                   |
| email                  | string                                              | yes      | Contact email and duplicate key            |
| educationLevel         | [EducationLevel](#educationlevel)                   | yes      | Education level                            |
| currentWorkStatus      | [WorkStatus](#workstatus)                           | yes      | Current employment status                  |
| dailyPokerAvailability | [DailyAvailabilityRange](#dailyavailabilityrange)   | yes      | Daily hours available for play and study   |
| preferredTimeWindows   | [TimeWindow](#timewindow)[]                         | yes      | Preferred availability windows             |
| weeklyDaysAvailability | [WeeklyAvailabilityRange](#weeklyavailabilityrange) | yes      | Weekly days available                      |
| pokerExperienceRange   | [PokerExperienceRange](#pokerexperiencerange)       | yes      | Total poker experience range               |
| primaryModality        | [PokerModality](#pokermodality)                     | yes      | Main game modality                         |
| hasOwnComputer         | boolean                                             | yes      | Whether candidate has own computer         |
| hasDiscordFamiliarity  | boolean                                             | yes      | Whether candidate is familiar with Discord |
| trackerUsage           | [TrackerUsageType](#trackerusagetype)               | yes      | Tracker usage category                     |
| trackerDetail          | string                                              | no       | Tracker/tool detail when applicable        |
| nickPokerStars         | string                                              | no       | PokerStars nickname                        |
| nickGGPoker            | string                                              | no       | GGPoker nickname                           |
| nickSuprema            | string                                              | no       | Suprema nickname                           |
| lgpdConsentAccepted    | boolean                                             | yes      | Explicit LGPD consent acceptance           |
| ruleAcceptance         | [RuleAcceptance](#ruleacceptance)                   | yes      | Accepted rules version and timestamp       |
| status                 | [ApplicationStatus](#applicationstatus)             | yes      | Current application status                 |
| submittedAt            | datetime                                            | yes      | Submission timestamp                       |
| reviewedAt             | datetime                                            | no       | Review completion timestamp                |
| reviewedBy             | uuid                                                | no       | Reviewer user identifier                   |
| reviewDecisionNote     | string                                              | no       | Approval/rejection review note             |
| retentionUntil         | datetime                                            | no       | Retention cutoff for rejected applications |

**Lifecycle:** See [CandidateApplicationLifecycle](states.md#candidateapplicationlifecycle)
**Operations:** [SubmitCandidateApplication](operations.md#submitcandidateapplication), [ReviewCandidateApplication](operations.md#reviewcandidateapplication)

---

## Value Objects

### RuleAcceptance

Represents acceptance metadata for the rules version shown during onboarding.

| Field             | Type     | Constraint                    |
| ----------------- | -------- | ----------------------------- |
| regulationVersion | string   | non-empty                     |
| acceptedAt        | datetime | required                      |
| acceptanceSource  | string   | fixed value `onboarding-flow` |

**Equality:** Two objects are equal when `regulationVersion`, `acceptedAt`, and `acceptanceSource` are identical.

---

## Enums

### ApplicationStatus

| Value        | Description                                         |
| ------------ | --------------------------------------------------- |
| SUBMITTED    | Application submitted and waiting for manual review |
| UNDER_REVIEW | Application currently under leadership review       |
| APPROVED     | Application approved for next internal step         |
| REJECTED     | Application closed as rejected                      |

### EducationLevel

| Value               | Description                 |
| ------------------- | --------------------------- |
| FUNDAMENTAL         | Elementary education        |
| MEDIO               | High school education       |
| SUPERIOR_INCOMPLETO | Incomplete higher education |
| SUPERIOR_COMPLETO   | Completed higher education  |

### WorkStatus

| Value       | Description           |
| ----------- | --------------------- |
| FULL_TIME   | Works full-time       |
| PART_TIME   | Works part-time       |
| NOT_WORKING | Not currently working |
| OTHER       | Other status          |

### DailyAvailabilityRange

| Value        | Description               |
| ------------ | ------------------------- |
| LT_2H        | Less than 2 hours per day |
| FROM_2_TO_4H | 2 to 4 hours per day      |
| FROM_4_TO_6H | 4 to 6 hours per day      |
| GT_6H        | More than 6 hours per day |

### TimeWindow

| Value      | Description |
| ---------- | ----------- |
| MORNING    | Morning     |
| AFTERNOON  | Afternoon   |
| NIGHT      | Night       |
| LATE_NIGHT | Late night  |

### WeeklyAvailabilityRange

| Value    | Description          |
| -------- | -------------------- |
| DAYS_3   | 3 days per week      |
| DAYS_4_5 | 4 to 5 days per week |
| DAYS_6_7 | 6 to 7 days per week |

### PokerExperienceRange

| Value         | Description        |
| ------------- | ------------------ |
| LT_6_MONTHS   | Less than 6 months |
| FROM_6M_TO_1Y | 6 months to 1 year |
| FROM_1Y_TO_3Y | 1 to 3 years       |
| GT_3Y         | More than 3 years  |

### PokerModality

| Value      | Description    |
| ---------- | -------------- |
| MTT        | Tournaments    |
| CASH_GAME  | Cash game      |
| SIT_AND_GO | Sit n Go       |
| OTHER      | Other modality |

### TrackerUsageType

| Value | Description          |
| ----- | -------------------- |
| YES   | Uses tracker         |
| NO    | Does not use tracker |
| OTHER | Uses other tool      |
