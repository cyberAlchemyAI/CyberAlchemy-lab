# L4 state-bearing sandbox prototype plan

Status: implementation candidate  
Route: `CA2-ROUTE-IMPLEMENT`  
Selected direction: `L4TGT-1`  
Candidate identity: `cal.prototype.rust-state-bearing-sandbox-target/epoch-003`

## Outcome

Build the smallest non-live state-bearing local sandbox that makes activation
observable after the activation call returns and before an explicit teardown.
The candidate remains local, path-confined, credential-free, network-free,
production-data-free, and without external-system effects.

## Construction waves

1. Bind the exact L4 selection and define a new candidate identity.
2. Add an adapter-owned process-temporary sandbox root and canonical state.
3. Add a bounded stage-and-activate harness that preserves inspectable state.
4. Require explicit exact-restore-and-remove teardown, with drop cleanup as a
   leak safety net.
5. Prove live refusal, engine-substitution refusal, failure restoration, state
   survival, teardown, and deterministic evidence twice.

## Architectural boundary

The existing `ExecutionEngine` remains unchanged: it accepts only the L1/L3
prototype bindings and always rolls them back. The L4 candidate has a distinct
binding and a separate harness. Its sandbox activation observation is not a
governed runtime activation, migration, cutover, product approval, or adapter
admission.

## Done criteria

- seven exact L4 invariants pass;
- all predecessor Rust tests remain green;
- the complete suite passes twice with identical observations;
- the L4 report is byte-deterministic;
- selected L3 and L4 decision dependencies remain current;
- no Cargo target or sandbox root remains in the repository or process temp;
- the receipt reports no live readiness, approval, admission, runtime
  activation, migration, cutover, publication, deployment, or authority effect.
