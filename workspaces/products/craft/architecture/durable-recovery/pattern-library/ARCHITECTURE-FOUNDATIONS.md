# Architecture Foundations

## Frozen semantic core

Recovery Intent, plan digest, plan occurrences, selected Operation bindings, and Invocation Identities never
change because a worker retries, crashes, loses a Lease, or is replaced.

## Safety and liveness are separate

- Claim plus fencing provides exclusive advancement safety.
- Lease expiry provides takeover liveness.
- Invocation Identity provides business-effect replay safety.

No one mechanism substitutes for either of the others.

## Contracts, bindings, and adapters

The Recovery Coordination Repository and Unit of Work are consumer-owned code contracts. D46 Persistence
Binding and D47 Transaction Guarantee Binding map those contracts to one selected store realization and its
evidence boundary. D48 classifies failures without selecting D43 Retry. The adapter, raw observation,
semantic classification, continuation, and owner decision remain separate.

No universal code-level `Port` is required. Recovery Clock, Dispatch Wakeup, Telemetry, and Binding Resolver
retain their concern-specific contracts.

## Two atomic boundaries

The Recovery Coordination Unit of Work atomically records coordination transition plus dispatch outbox. Each Operation
independently atomically records its own business state plus Operation outbox. The recovery coordinator never
combines those boundaries into a distributed transaction or absorbs an Operation's declared effects.

## Wakeups are hints

Queue messages, timers, and polling results only wake a worker. The versioned Dispatch record decides whether
work is current and eligible.
