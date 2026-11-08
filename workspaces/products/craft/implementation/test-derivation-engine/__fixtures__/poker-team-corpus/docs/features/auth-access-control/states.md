---
id: auth-access-control
feature: auth-access-control
title: Auth Access Control States
summary: Access token lifecycle states and transitions.
status: implemented
pillar: platform
domain: auth-access-control-states
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
  - events.md
includes: []
---

# States: Authentication and Access Control

> **Capabilities using this aspect:** [Login](capabilities/login.md) · [Logout](capabilities/logout.md)

## SessionLifecycle

**Entity:** Session

### States

| State      | Meaning                                                |
| ---------- | ------------------------------------------------------ |
| ACTIVE     | Session can issue and validate tokens                  |
| TERMINATED | Session was explicitly ended by logout or admin action |
| EXPIRED    | Session exceeded configured expiration                 |

### Transition Table

| From   | Event           | Guard                               | To         | Effect                                       |
| ------ | --------------- | ----------------------------------- | ---------- | -------------------------------------------- |
| [new]  | LoginSucceeded  | Credentials valid and policy allows | ACTIVE     | Persist session and issue tokens             |
| ACTIVE | LogoutCompleted | Logout operation succeeds           | TERMINATED | Revoke linked active tokens                  |
| ACTIVE | SessionExpired  | `now >= session.expiresAt`          | EXPIRED    | Reject further token issuance/authentication |

### Invalid Transitions

| From       | Event          | Why Invalid                                                               |
| ---------- | -------------- | ------------------------------------------------------------------------- |
| TERMINATED | LoginSucceeded | Login creates a new session id instead of reactivating terminated session |
| EXPIRED    | LoginSucceeded | Login creates a new session id instead of reactivating expired session    |

### Invariants

| ID  | Invariant                        | Formal                                                      |
| --- | -------------------------------- | ----------------------------------------------------------- |
| I1  | Terminal states remain terminal  | `state in {TERMINATED, EXPIRED} => no outgoing transitions` |
| I2  | Active session has future expiry | `state = ACTIVE => now < expiresAt`                         |

## TokenLifecycle

**Entity:** AccessToken

### States

| State   | Meaning                             |
| ------- | ----------------------------------- |
| ACTIVE  | Token can authenticate requests     |
| EXPIRED | Token exceeded expiration timestamp |
| REVOKED | Token invalidated before expiration |

### Transition Table

| From   | Event        | Guard                         | To      | Effect                           |
| ------ | ------------ | ----------------------------- | ------- | -------------------------------- |
| [new]  | TokenIssued  | Valid issue operation         | ACTIVE  | Persist token metadata           |
| ACTIVE | TokenExpired | `now >= expiresAt`            | EXPIRED | Reject auth with `TOKEN_EXPIRED` |
| ACTIVE | TokenRevoked | Revocation operation succeeds | REVOKED | Reject auth with `TOKEN_REVOKED` |

### Invalid Transitions

| From    | Event          | Why Invalid                                                   |
| ------- | -------------- | ------------------------------------------------------------- |
| EXPIRED | LoginSucceeded | Login creates new token(s), does not reactivate expired token |
| REVOKED | LoginSucceeded | Login creates new token(s), does not reactivate revoked token |
| EXPIRED | TokenRevoked   | Expired token is terminal; revocation has no effect           |

### Invariants

| ID  | Invariant                         | Formal                                                   |
| --- | --------------------------------- | -------------------------------------------------------- |
| I1  | Terminal states remain terminal   | `state in {EXPIRED, REVOKED} => no outgoing transitions` |
| I2  | ACTIVE tokens must not be revoked | `state = ACTIVE => revokedAt = null`                     |
| I3  | EXPIRED tokens are not accepted   | `state = EXPIRED => authDecision != ALLOW`               |
