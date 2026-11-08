---
id: auth-access-control
feature: auth-access-control
title: Auth Access Control Events
summary: Domain events emitted by token issuance, revocation, and denied access.
status: implemented
pillar: platform
domain: auth-access-control-events
audience:
  - developers
priority: p1
lang: en
owners:
  - platform-core
updatedAt: 2026-04-15
dependencies:
  - SPEC.md
  - operations.md
  - states.md
includes: []
---

# Events: Authentication and Access Control

> **Capabilities using this aspect:** [Login](capabilities/login.md) · [Authorize Request](capabilities/authorize-request.md) · [Logout](capabilities/logout.md)

## LoginSucceeded

**Produced By:** [Login](operations.md#login)
**Triggers Transition:** [SessionLifecycle](states.md#sessionlifecycle) `[new] -> ACTIVE`

### Payload

| Field       | Type     | Description                |
| ----------- | -------- | -------------------------- |
| principalId | string   | Authenticated principal    |
| sessionId   | string   | Newly created session id   |
| occurredAt  | datetime | Login completion timestamp |

### Consumed By

| Consumer        | Action                  |
| --------------- | ----------------------- |
| Audit subsystem | Record successful login |
| Session tracker | Register active session |

## TokenIssued

**Produced By:** [IssueAccessToken](operations.md#issueaccesstoken)
**Triggers Transition:** [TokenLifecycle](states.md#tokenlifecycle) `[new] -> ACTIVE`

### Payload

| Field     | Type     | Description             |
| --------- | -------- | ----------------------- |
| tokenId   | string   | Issued token id         |
| sessionId | string   | Session linked to token |
| issuedAt  | datetime | Issuance timestamp      |
| expiresAt | datetime | Expiration timestamp    |

### Consumed By

| Consumer        | Action                         |
| --------------- | ------------------------------ |
| Audit subsystem | Record authentication event    |
| Session tracker | Update active session registry |

## TokenRevoked

**Produced By:** [Logout](operations.md#logout)
**Triggers Transition:** [TokenLifecycle](states.md#tokenlifecycle) `ACTIVE -> REVOKED`

### Payload

| Field     | Type     | Description                     |
| --------- | -------- | ------------------------------- |
| tokenId   | string   | Revoked token id                |
| sessionId | string   | Session linked to revoked token |
| revokedAt | datetime | Revocation timestamp            |
| reason    | string   | Revocation reason code          |

Allowed `reason` values:

- `LOGOUT_TARGETED`
- `LOGOUT_ALL_SESSION_TOKENS`
- `ADMIN_FORCED_LOGOUT`

### Consumed By

| Consumer          | Action                         |
| ----------------- | ------------------------------ |
| Audit subsystem   | Record revocation event        |
| Cache invalidator | Invalidate token cache entries |

## LogoutCompleted

**Produced By:** [Logout](operations.md#logout)
**Triggers Transition:** [SessionLifecycle](states.md#sessionlifecycle) `ACTIVE -> TERMINATED`

### Payload

| Field           | Type     | Description                 |
| --------------- | -------- | --------------------------- |
| principalId     | string   | Principal performing logout |
| sessionId       | string   | Terminated session id       |
| revokedTokenIds | string[] | Tokens revoked by logout    |
| occurredAt      | datetime | Logout completion timestamp |

### Consumed By

| Consumer        | Action                  |
| --------------- | ----------------------- |
| Audit subsystem | Record logout event     |
| Session tracker | Mark session terminated |

## AccessDenied

**Produced By:** [AuthorizeRequest](operations.md#authorizerequest)
**Triggers Transition:** None

### Payload

| Field              | Type     | Description                   |
| ------------------ | -------- | ----------------------------- |
| principalId        | string   | Authenticated subject         |
| requiredPermission | string   | Permission required by route  |
| reasonCode         | string   | `FORBIDDEN` or related reason |
| occurredAt         | datetime | Event timestamp               |

### Consumed By

| Consumer           | Action                           |
| ------------------ | -------------------------------- |
| Security analytics | Track denied access patterns     |
| Alerting pipeline  | Raise signal on repeated denials |
