# Trusted HTTPS ingress and callback rehearsal

Product construction: expose the tested browser consumer through direct TLS;
reuse the generic socket listener with separate Set-Cookie header preservation.
Use one exact configured origin and reject caller forwarding hints, wrong Host,
absolute-form paths and insecure profile configuration. Keep request/header/TLS
bounds explicit. Existing Alch policy and AF identity/grant meanings remain owners.

Construction chain: approved structural model → existing typed/generated service
and browser candidate → bounded TLS adapter → current socket/browser tests.
No ontology selectors or governance admission are involved.

Operational support: the existing AF operator client temporarily adds exactly
`https://localhost:14443/callback` to prototype-browser redirectUris. Restore that
addition in finally; preserve any unrelated concurrent entries. Use existing local
frontend certificate and CA without printing key material. The separate listener
binds 127.0.0.1; running AF app/proxy/issuer processes remain intact.

Tests: real HTTPS health/host/forwarding/cookie transport checks; real browser
login, callback, enrollment, inference, CSRF, revocation and logout without route
interception. Close listener/browser and remove disposable tenant policy/builds.

## Open Questions

Persistent/cross-instance sessions and revocation, renewal, issuer-wide logout,
production origins/certificates, durable custody and deployment remain separate.
This is a local rehearsal; the temporary origin is not a permanent client change.
