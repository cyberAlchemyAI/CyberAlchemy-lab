# Trusted HTTPS browser ingress

The browser consumer now runs through a real local HTTPS listener. Eight live
checks passed without Playwright routing or callback navigation shims.
[Plan](PLAN.md), [live runner](live.mjs), [TLS adapter](server.mjs),
source-bound result (result record excluded), [native inventory](native-inventory.json).
Earlier browser-interception evidence remains historical.

The listener constructs application URLs from one configured HTTPS origin and
requires its exact Host. It rejects forwarding hints and absolute-form paths;
it does not derive trust from caller headers. TLS is bounded to versions 1.2/1.3,
with header/request/handshake limits. The shared Alch socket listener preserves
multiple Set-Cookie headers as separate headers, while retaining request
cancellation and response backpressure. This fixes real cookie transport for the
browser login/callback flow and remains reusable by other generated services.

The AF browser OAuth adapter accepts an explicit application origin independently
of its fixed issuer/client profile. The operator must register its exact callback.
The live rehearsal used https://localhost:14443 and the existing disposable CA
and frontend certificate. It added only that callback URI to the test browser
client, then removed it and verified the original redirect list. The running AF
application, proxy and issuer were not replaced or stopped.

## Validation

The live browser completed Keycloak authentication, real callback navigation,
automatic session enrollment, tenant selection, inference, CSRF denial, current
model revocation and local logout. The application and issuer both used verified
HTTPS; provider output remained a fixture. Socket tests also cover wrong Host,
forwarding spoofing and separate cookie headers. The prior inference suite and
browser lifecycle tests are retained in the result record.

The runner closes its listener/browser and removes temporary policy/build files.
It restores the callback registration in finally and fails if restoration cannot
be verified. It requires the existing local AF operator fixture and must not run
concurrently with another test using the same temporary callback URI. No access
tokens, passwords or private keys are written to the result.

Run the tests through the shared toolchain with AF's existing CA in
`NODE_EXTRA_CA_CERTS`, browser libraries in `LD_LIBRARY_PATH` and the selected
`ALCHLANG_TYPESCRIPT_COMPILER`. The live runner is `live.mjs`; the socket tests are
`node --test ingress.test.mjs`. The listener factory itself grants no permanent
client registration or deployment.

## Open Questions

The next product work is durable session and revocation state, followed by token
renewal behavior. Current sessions and revocation records are process-local and
end at token expiry. Permanent origin/client registration, certificate lifecycle,
production hosting, issuer-wide logout and durable inference custody remain
separate operational/product decisions. This local test is not a deployment or
production security admission.
