# Rust execution-envelope engine prototype

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

`InMemoryTarget` is the first conforming adapter, not an engine dependency. The
engine intentionally has no filesystem, credential, network, service, or
live-target adapter. `ExecutionMode::Live` fails before target mutation. Every
failure after preimage capture, including rollback failure, performs an
emergency restoration.

The progressive product plan and the separately deferred operational lane are
recorded in `implementation-layering.md`.

Run the public contract:

```bash
cargo test --locked --tests -- --test-threads=1
```

Produce deterministic two-run evidence without leaving Cargo build artifacts
in the repository:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 validate.py --write-receipt
```

This remains a prototype product candidate. Passing tests do not admit,
activate, migrate, cut over, publish, deploy, or authorize a live effect.
