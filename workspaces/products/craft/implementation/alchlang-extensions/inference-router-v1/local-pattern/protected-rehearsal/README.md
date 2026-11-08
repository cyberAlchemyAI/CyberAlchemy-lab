# Protected and durable API rehearsal

Candidate integration evidence around the existing Alch/DomainSpec protected
service, Auth Foundation and SQLite custody. The accepted public/memory bundle
remains unchanged. Authority effect: none.

Run from the repository root:

```bash
tools/toolchain/run node language/capabilities/alchlang/plans/general-compiler-v1/extensions/inference-router-v1/local-pattern/protected-rehearsal/run.mjs
```

The launcher verifies the current pinned compiler and builds the existing Rust
authorization bridge through the shared toolchain. The rehearsal compiles the
protected service with durable custody and local outbound v2, then launches a
separate Node service process against a real loopback mock engine. All keys,
signed tokens, policy files, generated artifacts and encrypted database state
are disposable. Nothing is installed or deployed.

The 15 checks cover public health/protected discovery, invalid signatures,
tenant denial, authorized discovery and execution, JSON replay after process
restart, conflicting request rejection, grant removal/restoration before replay,
principal and tenant isolation, stream non-replay after restart, SIGKILL during
an unsettled attempt, authorization-session revocation, and encrypted storage.
Provider call counts demonstrate when a replay or denial avoided execution.

Identity boundary: RSA-signed fixture access tokens are checked by the actual
Auth Foundation verifier. The actual Rust bridge evaluates current memberships,
roles and sessions from the disposable policy file. Online token introspection
is a trusted no-op fixture; no live Keycloak login, introspection, issuer logout
or browser renewal is claimed. Session revocation here is an authorization-policy
change. The engine returns deterministic text; no LLM is needed.

The service is restarted in a new process with the same database and encryption
key. A completed JSON response replays only with current authorization. A killed
worker's uncertain attempt remains unresolved and cannot execute again under
the retained key. This does not prove engine cancellation or exactly-once remote
execution. The ephemeral ports, child processes and temporary directory are
cleaned up at completion or failure.

## Validation

All 15 checks passed in one process integration test. Receipt (result record excluded) and
[execution log](/home/vlad_/projects/cyberAlchemy-v2/language/capabilities/alchlang/plans/general-compiler-v1/extensions/inference-router-v1/local-pattern/protected-rehearsal/rehearsal.log) bind this source snapshot. The accepted bundle was
verified before and after the rehearsal. No active test listener or worker remains.

## Product progress and Open Questions

This rehearsal integrates previously tested protected access and durable custody
through HTTP. It is a source-checkout rehearsal, not a new standalone protected
distribution. Remaining product work: consolidate operator instructions and
package/validate the exact complete reference product for review. The public
demo and accepted pattern remain available independently.

Live issuer configuration, long-term key/backup custody and deployment are
operator-owned follow-ups. A real engine and hardware performance measurements
remain optional; neither blocks the mocked reference product.
