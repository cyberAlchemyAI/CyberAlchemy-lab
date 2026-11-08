# Browser handoff and automatic enrollment

Implemented as a separate Auth Foundation consumer bound to the generated Alch
inference handler. **13 lifecycle tests and seven live-browser checks pass**.
[Plan](PLAN.md), evidence (result record excluded), [binding](binding.mjs), [live test](live.mjs).
Earlier ISB-09 and live service-client evidence remain historical and unchanged.

The browser signs in through Keycloak, then sees its current tenants and an
inference form. Tokens stay server-side behind an opaque Secure/HttpOnly/SameSite
cookie. The callback automatically enrolls the verified session for a known,
enabled principal using operator-selected `enrollment_roles`. Login creates no
principal, membership, role or permission. Current grants still flow through the
existing Rust authorization service. Bearer API clients use the same enrollment
port, independently of browser cookies.

Browser writes and logout require exact Origin and session CSRF proof. Callback
transactions are single-use; logout wins against pending callbacks, authorization
and responses. Revoked tokens cannot reenroll until expiry; registry capacity is
bounded. The operator policy is read afresh and never rewritten by enrollment.
In this successor, active sessions are registry-owned; operators revoke via the
trusted enrollment port or disable principal/membership/role policy, rather than
editing the predecessor's manually registered sessions list.

## Validation

Lifecycle tests exercise unknown/disabled principals, service identity separation,
current role/grant changes, capacity, expiry, callback reuse, CSRF, mixed bearer
and cookie rejection, issuer failure, and logout races.

The isolated browser completed real HTTPS Keycloak authentication and code+PKCE
token exchange. It exercised secure cookies, automatic enrollment, tenant selection,
the inference form, CSRF denial, current model revocation and local logout. The
application handler was reached through Playwright request interception; the
harness drove the issuer's exact callback as a new navigation because redirect
continuations otherwise reached the existing AF app. Provider output was a fixture.
This proves the browser consumer and live issuer integration under that test
transport, not application TLS ingress or a deployed replacement.

The final run closed the browser and removed its temporary policy and bundles.
One interrupted diagnostic run left a temporary bundle; it was identified by its
exact generated source and removed. Existing issuer registrations, proxy, AF app,
operator grants and frozen candidate source were not changed.

Run the AF `inference-browser/consumer.test.mjs` using Node's test runner.
Run `live.mjs` through the shared toolchain with the existing AF CA path in
`NODE_EXTRA_CA_CERTS`, the existing browser libraries in `LD_LIBRARY_PATH`, and
the selected `ALCHLANG_TYPESCRIPT_COMPILER`. AF HTTPS fixtures must already run.
The exported `createBrowserInference` constructs a Web Request handler; a trusted
application TLS ingress must supply its exact configured HTTPS origin.

## Open Questions

Next is selecting and testing the application HTTPS ingress and callback origin
without silently replacing the running AF application. The fixed predecessor
client currently uses localhost:13443. Cross-instance/persistent session and
revocation storage, silent token renewal and issuer-wide logout remain separate.
Sessions currently end at token expiry; users then sign in again. Local logout
ends this application's session only. Streams already delivered are not
continuously reauthorized. No production deployment or governance admission.
