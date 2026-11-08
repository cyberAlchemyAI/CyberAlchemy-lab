# Model Choice For DCB Saga Correctness

Status: decision
Date: 2026-06-15
Dispatch: `domainspec-v2-dcb-saga-correctness-research-20260615`

## Decision

Use a TypeScript bounded witness first, with TLA+/PlusCal as the first formal
promotion path if the witness shows temporal behavior is the hard part.

Decision state: `borrow-carefully`.

## Rationale

TypeScript gives the fastest repo-local path to a useful first artifact:

- it can express a small `SagaSpec` DSL directly from DomainSpec concepts;
- it can run in existing repo tooling patterns (`tsx`, `vitest`, or `tsx --test`);
- it can produce a concrete witness with trace, graph validation result,
  compensation outcome, read-set hash, stale fact, and claim verdict.

This is not a full proof. It is a bounded executable witness.

TLA+/PlusCal is the preferred next formal surface if the toy's hard problem is
temporal execution: compensation ordering, retries, timeouts, races, and safety
or liveness invariants.

Alloy is the preferred alternate if the toy's hard problem is graph completeness:
participants, typed edges, required compensation links, and relationship
coverage counterexamples.

Lean is deferred. It may become useful after the theorem is small and stable,
but it is too heavy for the first feasibility pass.

## Decision Table

| Candidate | Verdict | Use when |
| --- | --- | --- |
| TypeScript DSL + bounded/property tests | first pilot | Need a fast repo-local witness and extraction path. |
| TLA+/PlusCal | formal promotion path | Temporal saga behavior is the core risk. |
| Alloy | alternate formal path | Relationship graph completeness is the core risk. |
| Lean | deferred | A narrow theorem is stable enough to justify proof effort. |

## Guardrails

- Do not call the TypeScript result a proof. Call it a bounded witness.
- Do not call DCB the proof engine. DCB guards acceptance freshness.
- Do not mutate taxonomy, relationships, templates, validators, or generated
  registries from this research packet.

