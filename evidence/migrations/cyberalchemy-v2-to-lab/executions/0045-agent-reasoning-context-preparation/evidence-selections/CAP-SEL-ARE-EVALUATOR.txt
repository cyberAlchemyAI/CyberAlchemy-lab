# Semantic judgment evaluator witness

This private L0 package deterministically reduces one frozen request to one
typed semantic outcome. It binds the outcome and derivation in canonical JSON,
persists the reasoning receipt before any exact-effect decision, supports
byte-identical historical replay, and exposes only a fixed in-memory effect test
double.

For context-bound evaluation, the reducer verifies the sealed relationship
between the Context Envelope binding, bound Problem Frame, entry gate, authority
snapshot, Context Item digests, freshness, and claim ceiling before applying any
catalog rule. The resulting Reasoning Receipt carries the context epoch,
envelope digest, binding digest, and selected Context Item digests. Unbound
historical requests retain their prior receipt shape and exact bytes.

It is evidence for one bounded semantic relation. It is not a general reasoning
engine, an authority resolver, an actor runtime, a confidence calculator, or an
effect permission system.

Run the acceptance suite from the repository root:

```bash
node --test cyberAlchemy-v2/implementation/agent-reasoning-engine/packages/semantic-judgment-evaluator/test/*.test.mjs
```

Materialize a governed witness run:

```bash
node cyberAlchemy-v2/implementation/agent-reasoning-engine/packages/semantic-judgment-evaluator/scripts/run-witness.mjs \
  --output cyberAlchemy-v2/implementation/agent-reasoning-engine/generated/runs/evaluator-v1-<timestamp>
```

## Open Questions

The witness does not close the engine-level owner decisions. See
[`SPEC.md`](../../../../../development/agent-reasoning-engine/spec/SPEC.md#open-blockers--owner-decisions).
