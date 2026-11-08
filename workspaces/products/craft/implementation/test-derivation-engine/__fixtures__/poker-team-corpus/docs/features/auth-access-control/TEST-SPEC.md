---
id: auth-access-control
feature: auth-access-control
title: Auth Access Control Test Specification
summary: Deterministic test obligations for reusable authentication and authorization behavior.
status: implemented
pillar: platform
domain: auth-access-control-tests
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
  - interfaces.md
  - states.md
  - mappings.md
includes: []
---

# Auth Access Control TEST-SPEC

## Derivation Basis

- Framework constraints: `domainspec/CHANGELOG.md`.
- Pipeline rules: `domainspec/TEST-PIPELINE.md`.
- Feature sources:
  - `docs/features/auth-access-control/operations.md`
  - `docs/features/auth-access-control/interfaces.md`
  - `docs/features/auth-access-control/states.md`
  - `docs/features/auth-access-control/mappings.md`
  - `docs/features/auth-access-control/queries.md`

## Test Catalogue

| Test ID        | Type                | Source        | Obligation                                  | Deterministic Assertion                                                                                                              |
| -------------- | ------------------- | ------------- | ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| AUTH-RULE-001  | Rule validation     | operations.md | Login R1                                    | Disabled or missing principal is rejected with `PRINCIPAL_DISABLED`.                                                                 |
| AUTH-RULE-002  | Rule validation     | operations.md | Login R2                                    | Invalid identifier/password combination is rejected with `INVALID_CREDENTIALS`.                                                      |
| AUTH-RULE-003  | Rule validation     | operations.md | Login R3                                    | Login is rejected with `FORBIDDEN` when IP is blocked, failed attempts >= 5, or user-agent signal is missing.                        |
| AUTH-RULE-004  | Rule validation     | operations.md | IssueAccessToken R1                         | Non-active session cannot receive token and maps to `AUTH_REQUIRED`.                                                                 |
| AUTH-RULE-005  | Rule validation     | operations.md | IssueAccessToken R2                         | `ttlSeconds` outside bounds is rejected as validation error.                                                                         |
| AUTH-RULE-006  | Rule validation     | operations.md | AuthenticateRequest R1                      | Missing bearer prefix returns `AUTH_REQUIRED`.                                                                                       |
| AUTH-RULE-007  | Rule validation     | operations.md | AuthenticateRequest R2                      | Invalid signature/claims parsing returns `INVALID_TOKEN`.                                                                            |
| AUTH-RULE-008  | Rule validation     | operations.md | AuthenticateRequest R3                      | Expired token returns `TOKEN_EXPIRED`.                                                                                               |
| AUTH-RULE-009  | Rule validation     | operations.md | AuthenticateRequest R4                      | Revoked token returns `TOKEN_REVOKED`.                                                                                               |
| AUTH-RULE-010  | Rule validation     | operations.md | AuthenticateRequest R5                      | Missing sid claim returns `INVALID_TOKEN`.                                                                                           |
| AUTH-RULE-011  | Rule validation     | operations.md | AuthenticateRequest R6                      | Missing, terminated, or expired session for sid returns `AUTH_REQUIRED`.                                                             |
| AUTH-RULE-012  | Rule validation     | operations.md | AuthorizeRequest R1                         | Non-canonical `requiredPermission` is rejected as validation error.                                                                  |
| AUTH-RULE-013  | Rule validation     | operations.md | AuthorizeRequest R2                         | No matching allow permission returns `FORBIDDEN`.                                                                                    |
| AUTH-RULE-014  | Rule validation     | operations.md | AuthorizeRequest R3                         | Any matching deny rule returns `FORBIDDEN` even with allow entries.                                                                  |
| AUTH-RULE-015  | Rule validation     | operations.md | Logout R1                                   | Logout rejects non-active or missing target session with `AUTH_REQUIRED`.                                                            |
| AUTH-RULE-016  | Rule validation     | operations.md | Logout R2                                   | Caller can logout only own session unless `auth-access-control.admin.logoutAnySession` is present.                                   |
| AUTH-RULE-017  | Rule validation     | operations.md | Logout R3                                   | Logout fails if revocation evidence cannot be persisted.                                                                             |
| AUTH-CALC-001  | Calculation         | operations.md | Login C1                                    | Session expiration equals login instant + 8h.                                                                                        |
| AUTH-CALC-002  | Calculation         | operations.md | Login C2                                    | Session permissions equal deterministic resolution of roleKeys + directPermissions + grants.                                         |
| AUTH-CALC-003  | Calculation         | operations.md | IssueAccessToken C1                         | Token expiration equals issuedAt + ttlSeconds.                                                                                       |
| AUTH-CALC-004  | Calculation         | operations.md | IssueAccessToken C2                         | JWT claims are exactly `{sid,jti,iat,exp}` for minimal token set.                                                                    |
| AUTH-CALC-005  | Calculation         | operations.md | AuthenticateRequest C1                      | Auth context merges claims and session resolution using sid.                                                                         |
| AUTH-CALC-006  | Calculation         | operations.md | AuthorizeRequest C1                         | Precedence resolution follows `exact > scopedWildcard > globalWildcard`.                                                             |
| AUTH-CALC-007  | Calculation         | operations.md | Logout C1                                   | Revocation set equals `{tokenId}` when provided, else all active session tokens.                                                     |
| AUTH-POST-001  | Postcondition       | operations.md | Login postconditions                        | Successful login persists session and issues access token.                                                                           |
| AUTH-POST-002  | Postcondition       | operations.md | IssueAccessToken postconditions             | Token metadata is persisted and sid is authoritative identity claim.                                                                 |
| AUTH-POST-003  | Postcondition       | operations.md | AuthenticateRequest postconditions          | Request receives normalized authContext for downstream authorization.                                                                |
| AUTH-POST-004  | Postcondition       | operations.md | AuthorizeRequest postconditions             | ALLOW path forwards request; DENY path returns deterministic `FORBIDDEN`.                                                            |
| AUTH-POST-005  | Postcondition       | operations.md | Logout postconditions                       | Session terminates, token(s) revoked, and revocation evidence persisted in database.                                                 |
| AUTH-ERR-001   | Error state         | operations.md | Login error mapping                         | Login R1/R2/R3 violations map to `PRINCIPAL_DISABLED`, `INVALID_CREDENTIALS`, `FORBIDDEN`.                                           |
| AUTH-ERR-002   | Error state         | operations.md | IssueAccessToken error mapping              | Session activity violations map to `AUTH_REQUIRED`; ttl/signing failures map to documented validation/internal contracts.            |
| AUTH-ERR-003   | Error state         | operations.md | AuthenticateRequest error mapping           | R1-R6 violations map to `AUTH_REQUIRED`, `INVALID_TOKEN`, `TOKEN_EXPIRED`, `TOKEN_REVOKED`.                                          |
| AUTH-ERR-004   | Error state         | operations.md | AuthorizeRequest error mapping              | Rule violations map to validation error or `FORBIDDEN` as documented.                                                                |
| AUTH-ERR-005   | Error state         | operations.md | Logout error mapping                        | Ownership and persistence failures map to `FORBIDDEN` or internal error consistently.                                                |
| AUTH-API-001   | Contract            | interfaces.md | POST /auth/login responses                  | Statuses `200/401/403` and response shapes match contract.                                                                           |
| AUTH-API-002   | Contract            | interfaces.md | POST /auth/token responses                  | Statuses `200/403/422/500` and response shapes match contract.                                                                       |
| AUTH-API-003   | Contract            | interfaces.md | POST /auth/logout responses                 | Statuses `200/401/403/500` and response shapes match contract.                                                                       |
| AUTH-API-004   | Contract            | interfaces.md | GET /auth/introspect responses              | Statuses `200/401/403` match contract and 200 payload includes `inactiveReason?` when inactive.                                      |
| AUTH-API-005   | Contract            | interfaces.md | Refresh endpoint deferred in v1             | `/auth/refresh` is not exposed in current contract version.                                                                          |
| AUTH-API-006   | Contract            | interfaces.md | Standard auth error payload                 | Error body is always `{ code, message, details? }`.                                                                                  |
| AUTH-STATE-001 | Transition          | states.md     | Session [new] -> ACTIVE                     | `LoginSucceeded` transitions session to ACTIVE and records effect.                                                                   |
| AUTH-STATE-002 | Transition          | states.md     | Session ACTIVE -> TERMINATED                | `LogoutCompleted` transitions session to TERMINATED and revokes active tokens.                                                       |
| AUTH-STATE-003 | Transition          | states.md     | Session ACTIVE -> EXPIRED                   | `SessionExpired` transitions session when `now >= expiresAt`.                                                                        |
| AUTH-STATE-004 | Negative transition | states.md     | Session TERMINATED + LoginSucceeded invalid | Terminated session cannot be reactivated by login event.                                                                             |
| AUTH-STATE-005 | Negative transition | states.md     | Session EXPIRED + LoginSucceeded invalid    | Expired session cannot be reactivated by login event.                                                                                |
| AUTH-STATE-006 | Invariant property  | states.md     | Session I1                                  | Terminal session states have no outgoing transitions.                                                                                |
| AUTH-STATE-007 | Invariant property  | states.md     | Session I2                                  | ACTIVE session always has future `expiresAt`.                                                                                        |
| AUTH-STATE-008 | Transition          | states.md     | Token [new] -> ACTIVE                       | `TokenIssued` creates ACTIVE token state.                                                                                            |
| AUTH-STATE-009 | Transition          | states.md     | Token ACTIVE -> EXPIRED                     | `TokenExpired` transition occurs at `now >= expiresAt`.                                                                              |
| AUTH-STATE-010 | Transition          | states.md     | Token ACTIVE -> REVOKED                     | `TokenRevoked` transition occurs after successful revocation operation.                                                              |
| AUTH-STATE-011 | Negative transition | states.md     | Token EXPIRED + LoginSucceeded invalid      | Expired token remains terminal and cannot be reactivated.                                                                            |
| AUTH-STATE-012 | Negative transition | states.md     | Token REVOKED + LoginSucceeded invalid      | Revoked token remains terminal and cannot be reactivated.                                                                            |
| AUTH-STATE-013 | Negative transition | states.md     | Token EXPIRED + TokenRevoked invalid        | Expired token revocation path is rejected/no-op as documented terminal behavior.                                                     |
| AUTH-STATE-014 | Invariant property  | states.md     | Token I1                                    | EXPIRED and REVOKED token states are terminal.                                                                                       |
| AUTH-STATE-015 | Invariant property  | states.md     | Token I2                                    | ACTIVE token always has `revokedAt = null`.                                                                                          |
| AUTH-STATE-016 | Invariant property  | states.md     | Token I3                                    | EXPIRED token is never accepted by authorization decision.                                                                           |
| AUTH-MAP-001   | Mapping             | mappings.md   | LoginRequestToSession field mapping         | `identifier/context/now/now+8h` map deterministically to session fields.                                                             |
| AUTH-MAP-002   | Mapping validation  | mappings.md   | LoginRequestToSession validation            | Missing identifier or secret returns `INVALID_CREDENTIALS`.                                                                          |
| AUTH-MAP-003   | Mapping             | mappings.md   | JWTClaimsToAuthContext field mapping        | `sid/jti/iat/exp` and session lookup map exactly to AuthContext fields.                                                              |
| AUTH-MAP-004   | Mapping validation  | mappings.md   | JWTClaimsToAuthContext validation           | Missing `sid`/`jti` yields `INVALID_TOKEN`; expired `exp` yields `TOKEN_EXPIRED`.                                                    |
| AUTH-MAP-005   | Mapping             | mappings.md   | LogoutRequestToTermination                  | logout request maps to revocation input with default `revokeAllSessionTokens=false`.                                                 |
| AUTH-MAP-006   | Mapping validation  | mappings.md   | LogoutRequestToTermination validation       | Empty `sessionId` is rejected as validation error.                                                                                   |
| AUTH-MAP-007   | Mapping             | mappings.md   | RoutePermissionBinding                      | Route metadata normalizes permission key and forwards authContext from authentication step.                                          |
| AUTH-MAP-008   | Mapping validation  | mappings.md   | RoutePermissionBinding validation           | Non-canonical `requiredPermission` fails startup/config validation.                                                                  |
| AUTH-MAP-009   | Mapping             | mappings.md   | ErrorToHttpResponse                         | Error fields map directly to HTTP payload with optional details omission.                                                            |
| AUTH-QUERY-001 | Query               | queries.md    | GetPermissionCatalog filtering              | `namespace` and `includeDeprecated` filters are deterministic.                                                                       |
| AUTH-QUERY-002 | Query               | queries.md    | GetPermissionCatalog canonical entries      | Active catalog includes `auth-access-control.read.introspectToken` and `auth-access-control.admin.logoutAnySession`.                 |
| AUTH-QUERY-003 | Query               | queries.md    | IntrospectToken output shape                | Returns `active, principalId, exp, iat, scopes, inactiveReason?` with source-consistent values.                                      |
| AUTH-QUERY-004 | Query               | queries.md    | IntrospectToken inactive reason precedence  | Inactive reason is deterministic with precedence `NOT_FOUND > TOKEN_REVOKED > TOKEN_EXPIRED > SESSION_TERMINATED > SESSION_EXPIRED`. |
| AUTH-EVT-001   | Event producer      | events.md     | LoginSucceeded                              | Login success emits event with `principalId, sessionId, occurredAt`.                                                                 |
| AUTH-EVT-002   | Event producer      | events.md     | TokenIssued                                 | Token issuance emits event with `tokenId, sessionId, issuedAt, expiresAt`.                                                           |
| AUTH-EVT-003   | Event producer      | events.md     | TokenRevoked                                | Logout revocation emits event with `tokenId, sessionId, revokedAt, reason` and reason value in allowed enum set.                     |
| AUTH-EVT-004   | Event producer      | events.md     | LogoutCompleted                             | Logout completion emits event with `principalId, sessionId, revokedTokenIds, occurredAt`.                                            |
| AUTH-EVT-005   | Event producer      | events.md     | AccessDenied                                | Authorization deny emits event with `principalId, requiredPermission, reasonCode, occurredAt`.                                       |
| AUTH-EVT-006   | Event consumer      | events.md     | Audit subsystem consumption                 | Audit consumer records all auth events with required payload fields.                                                                 |
| AUTH-EVT-007   | Event consumer      | events.md     | Session tracker consumption                 | Session tracker updates active/terminated session registry on login/logout/token events.                                             |
| AUTH-EVT-008   | Event consumer      | events.md     | Cache invalidator consumption               | Cache invalidator invalidates revoked token cache entries on TokenRevoked.                                                           |
| AUTH-EVT-009   | Event consumer      | events.md     | Security analytics consumption              | Security analytics consumes AccessDenied to record denied patterns.                                                                  |
| AUTH-EVT-010   | Event consumer      | events.md     | Alerting pipeline consumption               | Alerting pipeline processes repeated AccessDenied events per policy.                                                                 |
| AUTH-WF-001    | Workflow            | workflows.md  | EndToEndAuthFlow login branch               | Login success/failure branches match documented outcomes.                                                                            |
| AUTH-WF-002    | Workflow            | workflows.md  | EndToEndAuthFlow protected request branch   | Protected request branch enforces auth checks in sequence and expected error outputs.                                                |
| AUTH-WF-003    | Workflow            | workflows.md  | EndToEndAuthFlow logout branch              | Logout branch enforces ownership/admin decision and transition effects.                                                              |
| AUTH-WF-004    | Workflow            | workflows.md  | AuthorizeRequestFlow step ordering          | Authenticate step always executes before authorize and handler execution.                                                            |
| AUTH-WF-005    | Policy decision     | workflows.md  | PermissionResolutionPolicy precedence       | Decision table applies deny override and wildcard precedence deterministically.                                                      |

## Coverage Summary

- Rule validation: 17
- Calculations: 7
- Postconditions: 5
- Error states: 5
- Interface contracts: 6
- State transitions/invariants: 16
- Mappings: 9
- Queries: 4
- Event flow (producer+consumer): 10
- Workflows/policies: 5
- Total obligations: 84

## Uncovered Or Under-Specified Areas

None blocking deterministic test derivation for current v1 scope.

---

## Story To Test Mapping

| Story                                                                   | Key test IDs                                                                                                                                                                                                |
| ----------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| US-01 User logs in with valid credentials                               | AUTH-RULE-001, AUTH-RULE-002, AUTH-RULE-003, AUTH-CALC-001, AUTH-CALC-002, AUTH-POST-001, AUTH-STATE-001, AUTH-STATE-008, AUTH-MAP-001, AUTH-MAP-002, AUTH-EVT-001, AUTH-EVT-002, AUTH-API-001, AUTH-WF-001 |
| US-02 Login rejected for invalid credentials or disabled principal      | AUTH-RULE-001, AUTH-RULE-002, AUTH-RULE-003, AUTH-ERR-001, AUTH-API-001                                                                                                                                     |
| US-03 Protected endpoint validates bearer token and builds auth context | AUTH-RULE-006, AUTH-RULE-007, AUTH-RULE-008, AUTH-RULE-009, AUTH-RULE-010, AUTH-RULE-011, AUTH-CALC-005, AUTH-POST-003, AUTH-MAP-003, AUTH-MAP-004, AUTH-WF-002, AUTH-WF-004                                |
| US-04 Authentication fails deterministically per rule                   | AUTH-RULE-006, AUTH-RULE-007, AUTH-RULE-008, AUTH-RULE-009, AUTH-RULE-010, AUTH-RULE-011, AUTH-ERR-003, AUTH-API-006                                                                                        |
| US-05 Route permission is enforced with deny-overrides policy           | AUTH-RULE-012, AUTH-RULE-013, AUTH-RULE-014, AUTH-CALC-006, AUTH-POST-004, AUTH-ERR-004, AUTH-EVT-005, AUTH-MAP-007, AUTH-MAP-008, AUTH-WF-005                                                              |
| US-06 User terminates own session                                       | AUTH-RULE-015, AUTH-RULE-016, AUTH-RULE-017, AUTH-CALC-007, AUTH-POST-005, AUTH-STATE-002, AUTH-STATE-010, AUTH-MAP-005, AUTH-MAP-006, AUTH-EVT-003, AUTH-EVT-004, AUTH-API-003, AUTH-WF-003                |
| US-07 Admin force-terminates another user's session                     | AUTH-RULE-016, AUTH-ERR-005, AUTH-API-003                                                                                                                                                                   |
| US-08 Inspect token state with explicit inactive reason                 | AUTH-QUERY-003, AUTH-QUERY-004, AUTH-API-004                                                                                                                                                                |
| US-09 Admin lists available permissions                                 | AUTH-QUERY-001, AUTH-QUERY-002                                                                                                                                                                              |

## Pilot Must-Pass Subset (Wave 1)

| Priority | Test IDs | Why it is gate-critical | Evidence file targets |
| --- | --- | --- | --- |
| P0 | AUTH-RULE-006, AUTH-RULE-008, AUTH-RULE-009, AUTH-RULE-010, AUTH-RULE-011 | Prevent invalid, expired, revoked, and orphaned tokens from reaching protected handlers. | `backend/src/infrastructure/http/auth/auth-access-control.test.ts` |
| P0 | AUTH-RULE-012, AUTH-RULE-013, AUTH-RULE-014, AUTH-WF-005 | Enforce canonical permission format and deny-override authorization policy. | `backend/src/infrastructure/http/auth/auth-access-control.test.ts` |
| P0 | AUTH-API-001, AUTH-API-003, AUTH-API-004, AUTH-ERR-003, AUTH-ERR-004 | Lock external auth contracts for login/logout/introspect and deterministic auth failures. | `backend/src/infrastructure/http/routes/auth.routes.contract.test.ts` |
| P0 | AUTH-STATE-002, AUTH-STATE-010, AUTH-POST-005 | Guarantee session termination and token revocation persistence for logout flows. | `backend/src/infrastructure/http/auth/auth-access-control.test.ts` |
| P1 | AUTH-QUERY-001, AUTH-QUERY-002, AUTH-QUERY-003, AUTH-QUERY-004 | Validate admin/operator visibility and token introspection details. | `backend/src/infrastructure/http/routes/auth.routes.contract.test.ts` |

## Pilot Execution Checklist

1. Freeze Wave 1 auth scope to the P0 rows above.
Pass criteria: all P0 test IDs are mapped to executable tests and tracked in one run artifact.

2. Run token validation gate first.
Pass criteria: AUTH-RULE-006/008/009/010/011 all pass with expected `AUTH_REQUIRED`, `TOKEN_EXPIRED`, `TOKEN_REVOKED`, and `INVALID_TOKEN` behavior.

3. Run authorization policy gate second.
Pass criteria: AUTH-RULE-012/013/014 and AUTH-WF-005 prove deny-override policy enforcement.

4. Run route contract gate third.
Pass criteria: AUTH-API-001/003/004 and AUTH-ERR-003/004 pass with deterministic status and payload shape.

5. Run session termination gate fourth.
Pass criteria: AUTH-STATE-002, AUTH-STATE-010, AUTH-POST-005 pass and show persisted revocation evidence.

6. Execute optional P1 admin/introspection checks.
Pass criteria: AUTH-QUERY-001/002/003/004 pass without regressions.

7. Record blockers and evidence package.
Pass criteria: blocker register is updated and all open blockers include owner and remediation evidence target.

8. Compute pilot verdict.
Pass criteria: zero failing P0 tests and no open P0 blocker.

## Pilot Go No-Go Blockers Register

| Blocker ID | Status | Blocker | Why it blocks Wave 1 | Required evidence to clear |
| --- | --- | --- | --- | --- |
| AUTH-BLK-01 | closed | Runtime guard does not delegate authorization decisions to `AuthorizeRequest` deny-override flow. | Policy drift can allow requests that should be denied by grant precedence rules. | Closed on 2026-04-24 via guard wiring to `authorizeRequestUseCase` and route auth test coverage. |
| AUTH-BLK-02 | closed | In-memory auth repository fallback remains in production guard module path. | Violates production binding gate and risks non-deterministic auth behavior in runtime path. | Closed on 2026-04-24 by removing production in-memory repositories and restricting fallback to test runtime only. |
| AUTH-BLK-03 | closed | Login abuse status semantics were inconsistent between contract/test artifacts and runtime behavior. | Client and operations handling of abuse events was non-deterministic at API boundary. | Closed on 2026-04-24 by canonicalizing login abuse denials to `403` across interfaces/UI/docs and adding deterministic route contract tests in `auth.routes.contract.test.ts`. |
| AUTH-BLK-04 | closed | Alignment and layering reports are stale relative to current framework and implementation state. | Readiness decisions rely on outdated evidence artifacts. | Closed on 2026-04-24 with refreshed alignment/layering snapshots for current implementation state. |

## Pilot Evidence Package

1. Auth gate run evidence
- Command output for backend typecheck and auth-related tests.
- Explicit pass list for all P0 IDs.

2. Authorization policy evidence
- Test logs proving deny-override path is exercised in runtime request flow.
- Traceable link from route guard to `AuthorizeRequest` use-case invocation.

3. Revocation and session lifecycle evidence
- Assertions proving `LogoutCompleted` and `TokenRevoked` side effects persist.
- Database-side verification for session/token revocation state.

4. Contract evidence
- Route-level contract assertions for login/logout/introspect status and payload shape.

5. Decision artifact
- Final blocker register snapshot and computed PASS/FLAG/BLOCK decision for Wave 1.

## Pilot Decisions Provenance

This test gate follows policy decisions recorded in [PILOT-DECISIONS.md](PILOT-DECISIONS.md).
