# ISB-09 tenant security candidate

The [approved structural model](STRUCTURAL-MODEL-APPROVAL.json) is implemented
as a local candidate. [Plan](PLAN.md), [source inventory](native-inventory.json).
No production deployment, live issuer exercise or formal security admission is
claimed by these local tests. Earlier approval and ISB-08 evidence remain historical.

## Application flow

1. `GET /healthz` is public. All three `/v1/` routes require bearer authentication
   and `X-Tenant-Id`. The tenant header selects a membership; it does not grant it.
2. Reuse the Auth Foundation HTTPS verifier (source binding requires reconciliation): RS256 signature,
   issuer, prototype-api audience, token type, client, timestamps and token ID.
   The production adapter calls its online introspection on every security check.
   No successful authorization decision is cached.
3. The new trusted bridge (source binding requires reconciliation) reads one bounded operator policy snapshot,
   verifies issuer/subject/kind/client, active session and enabled tenant membership,
   and materializes trusted evidence and active-role grants. The existing
   [Auth Foundation authorization service](/home/vlad_/projects/domainspec-core/projects/auth-foundation/implementation/authorization-service/src/lib.rs) makes the final exact
   resource/action/tenant-scope decisions. No credential or policy input is accepted
   as a public authorization API. This bridge is a handwritten trusted adapter;
   it is not a claim of full compiler-generated security correspondence.
4. [Alch permission mapping](requirement.alch) supplies exact typed permissions.
   [Catalog policy](catalog.alch) retains enabled authorized rows. Generated
   discovery exposes permitted aliases/streaming and permitted routing strategies.
   Native binding translates permission outcomes into facts for these queries.
5. Inference checks strategy/model grants, then compiled selection chooses among
   the permitted catalog. Current token status and selected model grants are
   checked again immediately before the sole provider attempt. Streaming needs
   both `invoke` and `stream`. Provider credentials remain in fixed native bindings.
6. Custody keys combine tenant, issuer, subject, kind and client idempotency key.
   Session/token ID is deliberately excluded so a new valid session of the same
   principal can replay. A replay checks current grants for the saved model and
   original strategy; it cannot silently reroute or expose a revoked result.
   Streams remain non-replayable. Memory custody does not survive restart.

The DomainSpec security contract (source binding requires reconciliation) rejects partial/mixed profiles and
missing route access declarations. `protected-service.alch` declares each route;
its generated runtime rejects construction without a trusted request preparation
port. `public-service.alch` and `host.mjs` remain named historical anonymous
fixtures for regression coverage. The normal `serve` and `build-service` commands
now select the protected service.

## Operator binding and API use

Existing operator catalog/provider/estimator configuration is retained. Add an
`authFoundation` object with absolute `binary` and `policy` paths plus `profile`:

```js
authFoundation: {
  binary: '/absolute/auth-foundation/implementation/tenant-bridge/target/debug/auth-tenant-bridge',
  policy: '/absolute/operator/tenant-policy.json',
  profile: {
    issuer: 'https://localhost:18443/realms/auth-https',
    origin: 'https://localhost:13443',
    browserClient: 'prototype-browser',
    serviceClient: 'prototype-service',
    apiSecret: process.env.AUTH_FOUNDATION_API_SECRET
  }
}
```

These are the existing AF test profile values, not a new public issuer deployment.
The API secret is supplied by the operator and never written to evidence. The
bridge README defines its closed policy objects. Register exact current token
`jti` sessions and active roles in that operator-managed policy. The candidate
has no automatic session enrollment or membership administration API. Human
browser login and service-token acquisition remain Auth Foundation responsibilities;
this inference service accepts their bearer tokens rather than AF browser cookies.
Use the existing AF HTTPS test CA through Node's explicit trust configuration.
Never disable TLS verification. The inference listener remains numeric loopback;
external exposure requires a separately configured trusted TLS edge.

API requests use `Authorization: Bearer <access-token>` and `X-Tenant-Id: <tenant>`.
JSON inference additionally uses `Content-Type: application/json`; retries use
`Idempotency-Key`. Auth failures return 401; unavailable/denied current policy
returns 403. Discovery can return empty offerings when catalog discovery is
allowed but model or strategy grants are absent.

## Validation and limitations

[Security tests](security.test.mjs) use real ephemeral RSA signatures, the actual
AF token verifier, the actual Rust authorization service and disposable policy
files. Online issuer status is an explicit fixture; no live Keycloak or TLS/browser
result is inferred. HTTP socket, JSON/SSE, current-grant and replay boundaries are
exercised. The full prior inference and independent quote-service suite remains
part of validation: 121 service tests, 16 DomainSpec contract tests and three
legacy compatibility tests pass. Run the service suite through the repository
`tools/toolchain/run node` wrapper with the inference `run.mjs test` entry; it
rebuilds the tenant bridge with locked Cargo dependencies. Auth Foundation HTTPS
Node dependencies must be installed from its existing package lock. [Evidence](evidence.json) binds the final sources and results.

Authorization is checked at request preparation, immediately before provider
attempt, and before replay exposure. This candidate does not continuously poll
revocation after an SSE attempt begins. There are no background administrative
writes, credential provisioning, cross-principal sharing or inherited tenant grants.

## Open Questions

SEC-Q1 is resolved to the exact imported verifier, new trusted bridge and existing
Rust authorization service (source hashes in evidence). SEC-Q2 remains operational:
production issuer/audience/client registration, policy/session lifecycle and live
TLS deployment. SEC-Q3 remains excluded future policy: hierarchy, delegation and
shared replay. No additional owner decision blocks this local candidate. A future
live Auth Foundation + inference rehearsal must explicitly provision its selected
sessions/memberships and restore any disposable fixture changes.
