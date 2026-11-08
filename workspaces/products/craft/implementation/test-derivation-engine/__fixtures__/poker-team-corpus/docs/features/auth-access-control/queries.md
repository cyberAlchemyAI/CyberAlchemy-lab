---
id: auth-access-control
feature: auth-access-control
title: Auth Access Control Queries
summary: Read models for permission catalogs and token introspection.
status: implemented
pillar: platform
domain: auth-access-control-queries
audience:
  - developers
priority: p1
lang: en
owners:
  - platform-core
updatedAt: 2026-04-15
dependencies:
  - SPEC.md
  - domain.md
includes: []
---

# Queries: Authentication and Access Control

> **Capabilities using this aspect:** [Introspect Token](capabilities/introspect-token.md) · [Browse Permission Catalog](capabilities/browse-permission-catalog.md)

## GetPermissionCatalog

**Type:** Query (read-only)
**Actor:** Admin, platform operator

### Input

| Field     | Type   | Required | Description                 |
| --------- | ------ | -------- | --------------------------- |
| namespace | string | no       | Filter by service namespace |

### Filters

| Field             | Type    | Default | Description                        |
| ----------------- | ------- | ------- | ---------------------------------- |
| includeDeprecated | boolean | false   | Include deprecated permission keys |

### Output

| Field                     | Type     | Source                        | Description                           |
| ------------------------- | -------- | ----------------------------- | ------------------------------------- |
| permissions[]             | object[] | PermissionGrant               | Catalog entries with key and metadata |
| permissions[].key         | string   | PermissionGrant.permissionKey | Canonical permission key              |
| permissions[].description | string   | Catalog metadata              | Human-readable meaning                |
| permissions[].status      | string   | Catalog metadata              | active/deprecated                     |

Canonical examples that must be present in active catalog entries:

- `auth-access-control.read.introspectToken`
- `auth-access-control.admin.logoutAnySession`

### Reads From

| Entity          | Relationship | Fields Used           |
| --------------- | ------------ | --------------------- |
| PermissionGrant | queries      | permissionKey, effect |

Catalog governance is registry-first; registry entries define canonical keys and descriptions.

## IntrospectToken

**Type:** Query (read-only)
**Actor:** Service admin, security tooling

### Input

| Field | Type   | Required | Description         |
| ----- | ------ | -------- | ------------------- |
| token | string | yes      | Token to introspect |

### Filters

| Field         | Type    | Default | Description                       |
| ------------- | ------- | ------- | --------------------------------- |
| includeScopes | boolean | true    | Include resolved scopes in output |

### Rules

| ID  | Rule                                   | Formal                                                                                 |
| --- | -------------------------------------- | -------------------------------------------------------------------------------------- |
| R1  | Token lookup must be deterministic     | `tokenRecord = findToken(token)`                                                      |
| R2  | Active depends on token and session    | `active = (token.revokedAt = null) and (now < token.expiresAt) and (session.status = ACTIVE)` |
| R3  | Inactive reason must be explicit       | `active = false => inactiveReason in {TOKEN_REVOKED, TOKEN_EXPIRED, SESSION_TERMINATED, SESSION_EXPIRED, NOT_FOUND}` |

### Output

| Field       | Type     | Source                  | Description               |
| ----------- | -------- | ----------------------- | ------------------------- |
| active      | boolean  | AccessToken             | Token active state        |
| principalId | string   | Session.principalId     | Token subject             |
| exp         | integer  | AccessToken.expiresAt   | Expiration unix timestamp |
| iat         | integer  | AccessToken.issuedAt    | Issuance unix timestamp   |
| scopes      | string[] | AccessToken.scope       | Effective token scopes    |
| inactiveReason | string | Derived               | Present only when `active = false` |

`inactiveReason` precedence:

1. `NOT_FOUND` when token record does not exist.
2. `TOKEN_REVOKED` when `revokedAt != null`.
3. `TOKEN_EXPIRED` when `now >= expiresAt`.
4. `SESSION_TERMINATED` when session status is TERMINATED.
5. `SESSION_EXPIRED` when session status is EXPIRED.

### Reads From

| Entity      | Relationship | Fields Used                                                 |
| ----------- | ------------ | ----------------------------------------------------------- |
| AccessToken | queries      | tokenId, sessionId, issuedAt, expiresAt, revokedAt, scope |
| Session     | queries      | principalId, status                                        |
