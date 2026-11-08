---
id: auth-access-control
feature: auth-access-control
title: Auth Access Control Mappings
summary: Deterministic transformations for auth headers, claims, and permission resolution.
status: implemented
pillar: platform
domain: auth-access-control-mappings
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
  - interfaces.md
includes: []
---

# Mappings: Authentication and Access Control

> **Capabilities using this aspect:** [Login](capabilities/login.md) · [Authenticate Request](capabilities/authenticate-request.md) · [Authorize Request](capabilities/authorize-request.md) · [Logout](capabilities/logout.md)

## LoginRequestToSession

**From:** Login API Request
**To:** Session
**Direction:** Inbound

### Field Mapping

| Source Field                 | Target Field | Transform            | Notes                              |
| ---------------------------- | ------------ | -------------------- | ---------------------------------- |
| `identifier`                 | principalId  | principal-resolution | Resolve identifier to principal id |
| `context`                    | metadata     | direct               | Persist auditable login context    |
| `now`                        | createdAt    | direct               | Session creation timestamp         |
| `now + 8h`                   | expiresAt    | computed             | Fixed v1 session expiration window |

### Defaults

| Target Field | Default Value | Condition      |
| ------------ | ------------- | -------------- |
| status       | `ACTIVE`      | Login succeeds |

### Validation

| Field      | Validation       | On Failure            |
| ---------- | ---------------- | --------------------- |
| identifier | non-empty string | `INVALID_CREDENTIALS` |
| secret     | non-empty string | `INVALID_CREDENTIALS` |

## JWTClaimsToAuthContext

**From:** JWT Claims
**To:** AuthContext
**Direction:** Inbound

### Field Mapping

| Source Field            | Target Field | Transform                       | Notes                                               |
| ----------------------- | ------------ | ------------------------------- | --------------------------------------------------- |
| `sid`                   | sessionId    | direct                          | Required session identifier                         |
| `jti`                   | tokenId      | direct                          | Required token identifier                           |
| `iat`                   | issuedAt     | unix-to-datetime                | Convert seconds to datetime                         |
| `exp`                   | expiresAt    | unix-to-datetime                | Convert seconds to datetime                         |
| session lookup by `sid` | principalId  | session-to-principal resolution | Principal identity comes from server-side session   |
| session lookup by `sid` | permissions  | session permission resolution   | Effective permissions come from server-side session |

### Defaults

| Target Field | Default Value | Condition                            |
| ------------ | ------------- | ------------------------------------ |
| permissions  | `[]`          | Session has no effective permissions |

### Validation

| Field | Validation                                 | On Failure      |
| ----- | ------------------------------------------ | --------------- |
| sid   | non-empty string                           | `INVALID_TOKEN` |
| jti   | non-empty string                           | `INVALID_TOKEN` |
| exp   | valid future timestamp for active decision | `TOKEN_EXPIRED` |

## LogoutRequestToTermination

**From:** Logout API Request
**To:** Logout Operation Input
**Direction:** Inbound

### Field Mapping

| Source Field                   | Target Field           | Transform     | Notes                   |
| ------------------------------ | ---------------------- | ------------- | ----------------------- |
| request.sessionId              | sessionId              | direct        | Target session id       |
| request.tokenId                | tokenId                | direct        | Optional targeted token |
| request.revokeAllSessionTokens | revokeAllSessionTokens | default false | Revoke set selection    |

### Defaults

| Target Field           | Default Value | Condition     |
| ---------------------- | ------------- | ------------- |
| revokeAllSessionTokens | `false`       | Field omitted |

### Validation

| Field     | Validation       | On Failure       |
| --------- | ---------------- | ---------------- |
| sessionId | non-empty string | Validation error |

## RoutePermissionBinding

**From:** Route Metadata
**To:** AuthorizeRequest Input
**Direction:** Inbound

### Field Mapping

| Source Field        | Target Field       | Transform              | Notes                                |
| ------------------- | ------------------ | ---------------------- | ------------------------------------ |
| route.permission    | requiredPermission | normalizePermissionKey | Lowercase service and scope segments |
| request.authContext | authContext        | direct                 | Produced by AuthenticateRequest      |

### Defaults

| Target Field       | Default Value | Condition    |
| ------------------ | ------------- | ------------ |
| requiredPermission | `null`        | Public route |

### Validation

| Field              | Validation                  | On Failure                 |
| ------------------ | --------------------------- | -------------------------- |
| requiredPermission | canonical permission format | Route startup/config error |

## ErrorToHttpResponse

**From:** Auth Operation Error
**To:** HTTP Error Payload
**Direction:** Outbound

### Field Mapping

| Source Field  | Target Field | Transform | Notes                    |
| ------------- | ------------ | --------- | ------------------------ |
| error.code    | code         | direct    | Deterministic error code |
| error.message | message      | direct    | Human-readable context   |
| error.details | details      | direct    | Structured metadata      |

### Defaults

| Target Field | Default Value | Condition              |
| ------------ | ------------- | ---------------------- |
| details      | omitted       | No additional metadata |

### Validation

| Field | Validation       | On Failure     |
| ----- | ---------------- | -------------- |
| code  | non-empty string | Internal error |
