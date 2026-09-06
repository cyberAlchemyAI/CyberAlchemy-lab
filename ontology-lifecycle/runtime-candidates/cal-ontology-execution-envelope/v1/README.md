# Rust execution-envelope and state-bearing sandbox prototypes

This isolated Rust crate turns the validated Python execution demonstration
into a reusable state-machine engine with a public target-adapter boundary. It
binds the exact `D65CUT-1` decision,
the seven-event source cut, the eleven-event target cut, and the expected
event-calculated projection digest.

```text
ExecutionEnvelope
  -> ExecutionEngine
      -> preflight exact authority and event cuts
      -> preflight exact ExecutionTargetAdapter binding
      -> capture adapter preimage
      -> stage -> activate -> migrate -> verify
      -> cutover -> verify postimage
      -> rollback -> verify exact preimage
```

`InMemoryTarget` is the first conforming adapter, not an engine dependency.
`DisposableFilesystemTarget` is the exact L3 integration adapter. It creates
its own process-temporary directory, accepts no caller path, and has no
credential, network, service, production-data, or live-target surface.
`ExecutionMode::Live` fails before target mutation. Every failure after
preimage capture, including rollback failure, performs an emergency
restoration.

L2 adds a reusable `CertificationHarness` around that boundary:

```text
exact 18-vector contract
  -> independent disposable adapter fixture
  -> two deterministic certification runs
  -> call-order + preimage + failure-code observations
  -> mutation-resistant CertificationReport
```

The independent fixture implements `ExecutionTargetAdapter` directly and does
not wrap the reference adapter. The vector contract covers exact execution,
binding refusal, preimage drift, every post-preimage failure point, report
determinism, fixture independence, vector omission, and vector mutation.

L3 crosses a concrete operating-system boundary without crossing into a live
system:

```text
exact filesystem binding
  -> adapter-created temporary directory
  -> canonical state bytes
  -> ten-step execution sequence
  -> byte-exact rollback
  -> complete directory cleanup
  -> deterministic FilesystemRehearsalReport
```

The temporary path is never included in evidence, so two clean rehearsals
produce identical canonical report bytes. Local disposable filesystem writes
are reported explicitly and are removed before the rehearsal returns.

L4 adds a distinct state-bearing product candidate without weakening L3:

```text
exact L4TGT-1 selection
  -> distinct epoch-003 sandbox identity
  -> adapter-owned process-temporary root
  -> stage + bounded sandbox activation
  -> state survives activation observation
  -> explicit exact restore + complete teardown
  -> deterministic StatefulSandboxReport
```

The L4 binding is deliberately excluded from the existing ten-step engine's
accepted bindings. `SandboxActivationHarness` can stage and activate only the
local sandbox; migration and cutover return explicit errors. The observation
records a sandbox state transition, not activation of a governed runtime.

The progressive product plan and the separately deferred operational lane are
recorded in `implementation-layering.md`.

Run the public contract:

```bash
cargo test --locked --tests -- --test-threads=1
```

The historical L2 source epoch produced its deterministic two-run evidence
with:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 validate.py --write-receipt
```

That validator is bound to the 20-test L2 source epoch and is not an aggregate
validator for this 27-test L3 tree. The L1 receipt remains frozen at
`receipts/tests.json`; the frozen L2 receipt remains at
`receipts/certification.json`.

Produce deterministic two-run L3 evidence while preserving both predecessor
receipts:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 validate-l3.py --write-receipt
```

L3 evidence is written separately to
`receipts/filesystem-rehearsal.json`.

Produce deterministic two-run L4 evidence without changing the frozen L3
receipt:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 validate-l4.py --write-receipt
```

L4 evidence is written separately to `receipts/stateful-sandbox.json`.

These remain prototype product candidates. Passing tests do not approve or
admit the L4 candidate, activate a governed runtime, migrate, cut over, publish,
deploy, or authorize a live effect.
