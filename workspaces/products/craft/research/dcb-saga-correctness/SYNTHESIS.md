# DCB Saga Correctness Synthesis

Status: synthesis
Date: 2026-06-15
Dispatch: `domainspec-v2-dcb-saga-correctness-research-20260615`

## Verdict

DCB is feasible for saga correctness only as a freshness and concurrency guard
around accepted proof evidence.

It is not feasible as the behavioral proof engine.

Bridge decision: `borrow-carefully`.

## Core Finding

The right first command is:

```text
AcceptSagaProofFreshnessClaim
```

not:

```text
AcceptSagaCorrectnessClaim
```

The name matters. The proof surface owns the saga behavior claim. DCB owns
whether the evidence, waiver, model result, or receipt can still be accepted
after relevant facts changed.

## Main Tensions

### Tension 1: DomainSpec Graph Coverage vs Temporal Saga Correctness

Layer A:

- DomainSpec has useful saga vocabulary: Saga, Operation, Rule, Policy, Event,
  State Machine, Interface, Mapping, and cross-context relationship edges.

Layer B:

- The current graph vocabulary is not enough for full temporal saga correctness.
  Compensation ordering, participant ownership, and specific state transitions
  need additional structure in the toy model.

Impact:

- Use DomainSpec as the extraction/source vocabulary, not as the complete proof
  language.

Decision:

- TypeScript bounded witness first.
- TLA+/PlusCal later if temporal behavior is the hard part.
- Alloy later if graph completeness is the hard part.

### Tension 2: DCB Value vs Cheaper Freshness Mechanisms

Layer A:

- DCB can reject a stale acceptance claim when a non-rerunnable fact, waiver,
  external receipt, model verdict, or concurrent promotion input changes after
  the read marker.

Layer B:

- Most saga structure is deterministic and should be rerun or content-hashed
  before acceptance.

Impact:

- A DCB toy without non-rerunnable evidence is over-built.

Decision:

- Include a human waiver or external receipt in the first toy.
- Use content hashes or rerun-before-use for deterministic facts.
- Use DCB only for residual hard facts and acceptance races.

### Tension 3: TypeScript Adoption vs Formal Proof Signal

Layer A:

- TypeScript fits the repo and can quickly produce a bounded witness.

Layer B:

- TypeScript alone is not a proof. TLA+/PlusCal or Alloy gives stronger formal
  confidence, depending on the obligation class.

Impact:

- The first artifact should be named "bounded witness," not "proof."

Decision:

- Start with TypeScript harness.
- Promote to TLA+/PlusCal if the witness exposes temporal risk.
- Promote to Alloy if the witness exposes graph completeness risk.
- Defer Lean.

## Open Semantic Residue

- `orchestrates` is currently typed as `Workflow -> Operation[]`; the saga toy
  must either treat Saga as a Workflow specialization or record a relationship
  signature residue.
- Compensation semantics are under-modeled in the relationship vocabulary.
- Participant or bounded-context ownership is implicit, not a canonical
  meta-concept.
- Proof verdicts, waivers, external receipts, read markers, and acceptance
  claims should remain in a DCB evidence vocabulary unless a later governance
  task promotes them.

## Next Move

Run a bounded `task-session` to implement the TypeScript toy harness and produce
`toy-run-result.md` plus `toy-run-result.json`.

The task-session must not mutate DomainSpec taxonomy, relationships, templates,
validators, or generated registries.

