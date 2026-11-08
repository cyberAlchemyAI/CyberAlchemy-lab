---
id: auth-access-control
feature: auth-access-control
title: Auth Access Control Workflows
summary: Request authentication and authorization orchestration workflow.
status: implemented
pillar: platform
domain: auth-access-control-workflows
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
  - mappings.md
includes: []
---

# Workflows: Authentication and Access Control

> **Capabilities using this aspect:** [Authenticate Request](capabilities/authenticate-request.md) · [Authorize Request](capabilities/authorize-request.md)

## EndToEndAuthFlow

**Type:** Workflow
**Triggers:** Login, protected API call, logout request
**Orchestrates:** [Login](operations.md#login), [IssueAccessToken](operations.md#issueaccesstoken), [AuthenticateRequest](operations.md#authenticaterequest), [AuthorizeRequest](operations.md#authorizerequest), [Logout](operations.md#logout)
**Compensation Strategy:** notify-only
**Idempotency:** conditional: protected calls are idempotent at auth layer, login/logout are not strictly idempotent

### Full Flow Diagram

```mermaid
flowchart TD
  A[Client submits login credentials] --> B[Login]
  B --> C{Principal active and credentials valid?}
  C -->|No| C1[Return 401 INVALID_CREDENTIALS or 403 PRINCIPAL_DISABLED]
  C -->|Yes| D[Create ACTIVE session]
  D --> E[IssueAccessToken]
  E --> F[Return access token sid+jti+iat+exp]

  F --> G[Client calls protected endpoint]
  G --> H[AuthenticateRequest]
  H --> I{Bearer token present?}
  I -->|No| I1[Return 401 AUTH_REQUIRED]
  I -->|Yes| J{Signature valid?}
  J -->|No| J1[Return 401 INVALID_TOKEN]
  J -->|Yes| K{Token expired?}
  K -->|Yes| K1[Return 401 TOKEN_EXPIRED]
  K -->|No| L{Token revoked?}
  L -->|Yes| L1[Return 401 TOKEN_REVOKED]
  L -->|No| M{sid claim present?}
  M -->|No| M1[Return 401 INVALID_TOKEN]
  M -->|Yes| N{Session ACTIVE for sid?}
  N -->|No| N1[Return 401 AUTH_REQUIRED or 403 PRINCIPAL_DISABLED]
  N -->|Yes| O[Build authContext from session]

  O --> P{Route requires permission?}
  P -->|No| Q[Execute handler]
  P -->|Yes| R[AuthorizeRequest]
  R --> S{Permission decision = ALLOW?}
  S -->|No| S1[Return 403 FORBIDDEN]
  S -->|Yes| Q

  Q --> X{Logout requested?}
  X -->|No| Y[Continue session]
  X -->|Yes| Z[Logout]
  Z --> AA{Caller owns session or admin?}
  AA -->|No| AA1[Return 403 FORBIDDEN]
  AA -->|Yes| AB[Terminate session and revoke active tokens]
  AB --> AC[Return 200 logout success]
```

## AuthorizeRequestFlow

**Type:** Workflow
**Triggers:** Incoming request to protected endpoint
**Orchestrates:** [AuthenticateRequest](operations.md#authenticaterequest), [AuthorizeRequest](operations.md#authorizerequest)
**Compensation Strategy:** notify-only
**Idempotency:** yes

### Steps

```mermaid
graph TD
    A[Receive Request] --> B[AuthenticateRequest]
    B --> C{Authenticated?}
    C -->|No| D[Return 401]
    C -->|Yes| E{Route Has Required Permission?}
    E -->|No| F[Forward to Handler]
    E -->|Yes| G[AuthorizeRequest]
    G --> H{Authorized?}
    H -->|No| I[Return 403]
    H -->|Yes| F
```

### Step Table

| #   | Step                            | Actor           | Operation                                                | On Success                     | On Failure           | Compensation     |
| --- | ------------------------------- | --------------- | -------------------------------------------------------- | ------------------------------ | -------------------- | ---------------- |
| 1   | Parse and verify credential     | Auth middleware | [AuthenticateRequest](operations.md#authenticaterequest) | Go to step 2                   | Return 401           | —                |
| 2   | Resolve route permission policy | Auth middleware | [AuthorizeRequest](operations.md#authorizerequest)       | Go to step 3                   | Return 403           | —                |
| 3   | Execute protected handler       | Feature handler | N/A                                                      | Return 2xx/4xx domain response | Return handler error | Emit audit event |

### Invariants

| ID  | Invariant                                         | Formal                                                                  |
| --- | ------------------------------------------------- | ----------------------------------------------------------------------- |
| I1  | Protected routes always authenticate first        | `route.protected = true => AuthenticateRequest executed before handler` |
| I2  | Authorization never executes without auth context | `AuthorizeRequest.input.authContext != null`                            |

---

## PermissionResolutionPolicy

**Type:** Policy
**Applies To:** [AuthorizeRequest](operations.md#authorizerequest)
**Trigger Conditions:** Evaluated for protected routes with required permission configured

### Decision Table

| Condition                                             | Selected Behavior | Notes                     |
| ----------------------------------------------------- | ----------------- | ------------------------- |
| Exact allow match exists and no deny match exists     | Allow             | Highest precedence allow  |
| Deny match exists                                     | Deny              | Deny overrides allow      |
| Scoped wildcard allow exists and no deny match exists | Allow             | Example: `service.read.*` |
| Global wildcard allow exists and no deny match exists | Allow             | Example: `*.*.*`          |
| No matches                                            | Deny              | Default deny              |

### Formula (if applicable)

```
precedence = deny > allow.exact > allow.scopedWildcard > allow.globalWildcard > noMatch
```

### Configuration Parameters

| Parameter           | Type    | Default | Description                      |
| ------------------- | ------- | ------- | -------------------------------- |
| wildcardEnabled     | boolean | true    | Enables wildcard matching        |
| denyOverrideEnabled | boolean | true    | Deny permissions override allows |
