# Bounded browser renewal

The inference browser can continue an existing session through Auth Foundation's
OIDC code/PKCE flow and issuer SSO. Renewal keeps the same principal, issuer
session and authentication time. It rotates the app cookie and CSRF value,
revokes the previous token, and preserves the original idle/absolute limits.
No refresh token or ID token is retained. Existing durable browser composition
picks up the new behavior; no running application is switched by this change.

The browser offers **Continue session**. Its same-origin `POST /renew` uses the
opaque session cookie and `x-csrf-token`, returning an `authorization_url` and a
login transaction cookie. Navigate the returned URL; the verified callback
returns to the application. API clients can initiate the same flow, but the OIDC
step still requires the user's browser SSO session. Independent bearer clients
continue to acquire tokens through their existing issuer flow.

When only the access token expires, cookie-authenticated inference returns
`409 {"error":"RENEWAL_REQUIRED"}` without reaching the provider. `/session`
returns `renewal_required: true`, CSRF and the app expiry, with an empty tenant
list. Renew, then explicitly send the inference request again. No request is
replayed automatically. Idle/absolute expiry or silent SSO failure requires
fresh sign-in. Legacy stored sessions lacking verified renewal metadata retain
their original expiry and require fresh login to acquire renewal support.

[The bounded plan](PLAN.md) describes the construction contract and remaining
operator work. RESULT.json (result record excluded) binds current sources and test logs.
Tests include real SQLite reopening, cross-instance races, expired-token denial,
identity substitution, unchanged session deadlines and silent-SSO failure.
[The browser rehearsal](live.mjs) uses real Keycloak HTTPS and native OIDC code,
with browser-local application interception and a fixture authorization port;
it does not claim a new deployed HTTPS application or Rust decision rehearsal.

From the checkout, run:

```sh
node --test ../domainspec-core/projects/auth-foundation/implementation/inference-browser/{consumer,state,renewal}.test.mjs
ALCHLANG_TYPESCRIPT_COMPILER="$PWD/language/capabilities/alchlang/plans/general-compiler-v1/implementation/node_modules/typescript/bin/tsc6" TMPDIR=/dev/shm tools/toolchain/run node language/capabilities/alchlang/plans/general-compiler-v1/extensions/inference-router-v1/run.mjs test
```

The explicit repository compiler path survives host restarts; historical evidence
used a temporary compiler path. Tests do not change the pinned compiled package.

## Open Questions

Owned by [PLAN.md](PLAN.md#open-questions): operator key management and backups,
production deployment, multi-host login affinity, issuer-wide logout, and durable
inference request custody. No outstanding decision blocks this local candidate.
