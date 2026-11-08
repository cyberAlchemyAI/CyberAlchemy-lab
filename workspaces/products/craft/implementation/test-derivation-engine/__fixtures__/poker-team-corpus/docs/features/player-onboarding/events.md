---
id: player-onboarding
feature: player-onboarding
title: Player Onboarding Events
summary: Event contracts for candidate submission and review decisions.
status: implemented
pillar: operations
domain: onboarding-candidates-events
audience:
  - developers
  - operations
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
includes: []
---

# Events: Player Onboarding

## CandidateApplicationSubmitted

**Produced by:** [SubmitCandidateApplication](operations.md#submitcandidateapplication)
**Triggers transition:** [CandidateApplicationLifecycle](states.md#candidateapplicationlifecycle)

### Payload

| Field | Type | Description |
| ----- | ---- | ----------- |
| applicationId | string | Candidate application identity |
| canonicalEmail | string | Lowercased candidate email |
| acceptedRegulationVersion | string | Rules version acknowledged by candidate |
| acceptedRegulationAt | datetime | Rules acceptance timestamp |
| occurredAt | datetime | Event timestamp |

### Consumed by

| Consumer | Action |
| -------- | ------ |
| operations candidate queue | Refresh pending application list |

## CandidateApplicationReviewed

**Produced by:** [ReviewCandidateApplication](operations.md#reviewcandidateapplication)
**Triggers transition:** [CandidateApplicationLifecycle](states.md#candidateapplicationlifecycle)

### Payload

| Field | Type | Description |
| ----- | ---- | ----------- |
| applicationId | string | Reviewed application identity |
| decision | string | `APPROVE` or `REJECT` |
| nextStatus | string | Final status after review |
| reviewedBy | string | Reviewer principal id |
| reviewedAt | datetime | Review timestamp |
| retentionUntil | datetime \| null | Retention cutoff for rejected applications |

### Consumed by

| Consumer | Action |
| -------- | ------ |
| player-management intake | Consume approved applications for player creation handoff from deterministic handoff persistence |
| operations audit trail | Register review decision history |
