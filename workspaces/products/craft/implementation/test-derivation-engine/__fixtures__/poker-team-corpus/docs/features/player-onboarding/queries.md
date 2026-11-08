---
id: player-onboarding
feature: player-onboarding
title: Player Onboarding Queries
summary: Read models for candidate review backlog and candidate detail.
status: implemented
pillar: operations
domain: onboarding-candidates-queries
audience:
  - developers
  - operations
priority: p1
lang: en
owners:
  - backend-core
  - web-core
updatedAt: 2026-04-08
dependencies:
  - domain.md
  - interfaces.md
includes: []
---

# Queries: Player Onboarding

## ListCandidateApplications

**Type:** Query
**Actor:** Authenticated leadership/operations user
**Exposed By:** `GET /admin/onboarding/candidates`

### Input

| Field  | Type    | Required | Description                              |
| ------ | ------- | -------- | ---------------------------------------- |
| status | string  | no       | Optional status filter (`SUBMITTED`, `UNDER_REVIEW`, `APPROVED`, `REJECTED`) |
| page   | integer | no       | Page number (default `1`)               |
| limit  | integer | no       | Page size (default `20`, max `100`)     |

### Result

| Field | Type   | Description                              |
| ----- | ------ | ---------------------------------------- |
| items | array  | Candidate summary rows                   |
| page  | number | Current page                             |
| limit | number | Page size                                |
| total | number | Total rows for current filter            |

## GetCandidateApplicationById

**Type:** Query
**Actor:** Authenticated leadership/operations user
**Exposed By:** `GET /admin/onboarding/candidates/{id}`

### Input

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| id    | uuid | yes      | Candidate application identifier |

### Result

| Field                | Type    | Description                          |
| -------------------- | ------- | ------------------------------------ |
| candidateApplication | object  | Full candidate application payload   |
