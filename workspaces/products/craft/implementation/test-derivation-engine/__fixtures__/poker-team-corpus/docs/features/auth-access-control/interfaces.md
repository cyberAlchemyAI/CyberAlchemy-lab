---
id: auth-access-control
feature: auth-access-control
title: Auth Access Control Interfaces
summary: Reusable route and module contracts for authentication and authorization.
status: implemented
pillar: platform
domain: auth-access-control-interfaces
audience:
  - developers
priority: p1
lang: en
owners:
  - platform-core
updatedAt: 2026-04-24
dependencies:
  - SPEC.md
  - operations.md
  - queries.md
includes: []
---

# Interfaces: Authentication and Access Control

> **Capabilities using this aspect:** [Login](capabilities/login.md) · [Logout](capabilities/logout.md) · [Introspect Token](capabilities/introspect-token.md)

## External: AuthAPI (REST)

### POST /auth/login

**Exposes:** [Login](operations.md#login)
**Auth:** Public credential entrypoint

**Request:**

| Field      | Type   | Maps To                 |
| ---------- | ------ | ----------------------- |
| identifier | string | Login.identifier        |
| secret     | string | Login.secret (password) |
| context    | object | Login.context           |

`context` payload fields:

- `ipReputation`: `TRUSTED | UNKNOWN | BLOCKED`
- `failedAttemptsLast15m`: integer
- `hasUserAgent`: boolean

**Responses:**

| Status | Condition                           | Body                                    |
| ------ | ----------------------------------- | --------------------------------------- |
| 200    | Login success                       | `{ accessToken, expiresAt, sessionId }` |
| 401    | Invalid credentials                 | Standard error payload                  |
| 403    | Principal disabled or policy denial | Standard error payload                  |

### POST /auth/token

**Exposes:** [IssueAccessToken](operations.md#issueaccesstoken)
**Auth:** Trusted internal call with pre-authenticated session context

**Request:**

| Field      | Type    | Maps To                     |
| ---------- | ------- | --------------------------- |
| sessionId  | string  | IssueAccessToken.sessionId  |
| ttlSeconds | integer | IssueAccessToken.ttlSeconds |

**Responses:**

| Status | Condition                              | Body                                    |
| ------ | -------------------------------------- | --------------------------------------- |
| 200    | Token issued                           | `{ accessToken, expiresAt, tokenType }` |
| 403    | Principal disabled or scope escalation | Standard error payload                  |
| 422    | Input contract invalid                 | Standard error payload                  |
| 500    | Unexpected signer/persistence error    | Standard error payload                  |

### POST /auth/logout

**Exposes:** [Logout](operations.md#logout)
**Auth:** JWT + active session

**Request:**

| Field                  | Type    | Maps To                       |
| ---------------------- | ------- | ----------------------------- |
| sessionId              | string  | Logout.sessionId              |
| tokenId                | string  | Logout.tokenId                |
| revokeAllSessionTokens | boolean | Logout.revokeAllSessionTokens |

**Responses:**

| Status | Condition                              | Body                   |
| ------ | -------------------------------------- | ---------------------- |
| 200    | Logout success                         | `{ status: 'ok' }`     |
| 401    | Missing or invalid auth                | Standard error payload |
| 403    | Caller cannot terminate target session | Standard error payload |
| 500    | Unexpected failure                     | Standard error payload |

Refresh token endpoint is deferred from v1 and intentionally not exposed in this contract version.

### GET /auth/introspect

**Exposes:** [IntrospectToken](queries.md#introspecttoken)
**Auth:** JWT + permission `auth-access-control.read.introspectToken`

**Request:**

| Field       | Type   | Maps To               |
| ----------- | ------ | --------------------- |
| query.token | string | IntrospectToken.token |

**Responses:**

| Status | Condition              | Body                                                         |
| ------ | ---------------------- | ------------------------------------------------------------ |
| 200    | Success                | `{ active, principalId, exp, iat, scopes, inactiveReason? }` |
| 401    | Missing or invalid JWT | Standard error payload                                       |
| 403    | Missing permission     | Standard error payload                                       |

### GET /auth/permissions

**Exposes:** [GetPermissionCatalog](queries.md#getpermissioncatalog)
**Auth:** JWT + permission `auth-access-control.admin.*`

**Request query:**

| Field             | Type    | Required | Description                                |
| ----------------- | ------- | -------- | ------------------------------------------ |
| namespace         | string  | no       | Filter by service namespace                |
| includeDeprecated | boolean | no       | Include deprecated permission keys (false) |

**Responses:**

| Status | Condition              | Body                   |
| ------ | ---------------------- | ---------------------- |
| 200    | Success                | `{ permissions[] }`    |
| 401    | Missing or invalid JWT | Standard error payload |
| 403    | Missing permission     | Standard error payload |

## Internal: AuthorizationGuard Interface

**Consumers:** API route modules, RPC handlers, queue consumers

| Method                                    | Maps To                       | Description                                    |
| ----------------------------------------- | ----------------------------- | ---------------------------------------------- |
| ensureAuthenticated(request)              | AuthenticateRequest operation | Validates credential and attaches auth context |
| requirePermission(request, permissionKey) | AuthorizeRequest operation    | Enforces route or action permission            |

## Internal: BootstrapSeed Lifecycle Hook

**Consumers:** Application entrypoint (`index.ts`)
**Triggers:** Application startup, before HTTP server listens

| Method                     | Maps To                         | Description                                                          |
| -------------------------- | ------------------------------- | -------------------------------------------------------------------- |
| seedSystemBootstrap(db)    | SeedSystemBootstrap operation   | Creates admin principal (if missing) and syncs all role permission grants |

**Contract:**
- Must run before `app.listen()` — routes should not accept traffic until seed is complete.
- Logs generated admin password to stdout exactly once on first boot.
- Idempotent: safe to call on every restart.
- Throws on database connection failure (app should not start).

## Standard Error Payload Contract

| Field   | Type   | Required | Notes                                                                    |
| ------- | ------ | -------- | ------------------------------------------------------------------------ |
| code    | string | yes      | One of [AuthErrorCode](domain.md#autherrorcode) or feature-specific code |
| message | string | yes      | Human-readable message                                                   |
| details | object | no       | Deterministic structured metadata (`required`, `reason`, `traceId`)      |
