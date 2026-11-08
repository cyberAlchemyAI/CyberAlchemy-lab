# Live service API integration result

**12 live checks passed**, with three provider attempts. Result (result record excluded)
binds the runner, security adapter, AF verifier and Rust bridge source/binary.
[Plan](PLAN.md) records the exact local scope. This is successor evidence;
ISB-09's prior signed-token fixture results remain unchanged.

The existing Auth Foundation service client obtained a token from the running
HTTPS Keycloak issuer. The unchanged protected inference service used real JWKS
verification and per-request introspection. Real loopback HTTP covered discovery,
capabilities, JSON inference, SSE, tenant isolation and principal-private replay.
Changing the disposable operator policy immediately hid revoked models and denied
saved-result replay. Disabling its current session also denied replay; restoring
that disposable session exposed the original result without another provider call.

No realm settings, existing grants, containers or frozen AF candidates changed.
Client credentials and the access token were never printed or recorded. Temporary
policy/build files and the two listeners were removed. The issued test token
expires under the existing AF token profile.

## Reproduce

From the CyberAlchemy repository root, use the existing shared toolchain and
Auth Foundation HTTPS Node dependencies. Build the bridge with locked dependencies:

```sh
tools/toolchain/run cargo build --locked --manifest-path ../domainspec-core/projects/auth-foundation/implementation/tenant-bridge/Cargo.toml
```

Run [run.mjs](run.mjs) through `tools/toolchain/run node`, with
`ALCHLANG_TYPESCRIPT_COMPILER` set to the compiler selected by the inference
`compiler-binding.json`, and `NODE_EXTRA_CA_CERTS` set to the absolute existing
`authentication-https/.runtime/tls/ca.crt` path. `TMPDIR=/dev/shm` is optional.
The local HTTPS stack and service-client fixtures must already be ready. The
runner deliberately fails if any live dependency is unavailable; it never
substitutes a mocked issuer. It prints sanitized JSON and exits nonzero on failure.

## Open Questions

Next product work is browser login-to-inference handoff and an explicit session
enrollment lifecycle, so users do not require manual token-session registration.
Those require their own bounded plan against Auth Foundation's session model.
Production issuer/audience configuration, external TLS, durable custody and
operations remain separately owned. This service-client run does not claim
browser coverage or issuer-side token-revocation testing.
