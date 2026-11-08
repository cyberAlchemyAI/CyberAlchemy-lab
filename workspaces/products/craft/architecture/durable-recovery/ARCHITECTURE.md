# Durable Recovery Architecture

## Purpose

This architecture turns one immutable Recovery Intent and its frozen recovery plan into restart-safe execution
of existing DomainSpec Operations. It implements coordination; it does not create a new meta-type, relationship
verb, or business-effect authority.

The design is technology-neutral. A reference runtime may begin with an in-process adapter, but the portable
properties below must remain observable when a durable store, transport, and worker topology are selected.

## Research and admission provenance

The Operation, Workflow, and Infrastructure-Binding Pattern Tower supplies the non-collapse spine from
semantic subject through concern-specific code contract, optional infrastructure binding, adapter, bounded
observation, finding, receipt, and separate owner decision. System Integration Contract Layer Revision 2
supplies the candidate ownership split and the first portable persistence, transaction, and failure records.
The explicit owner admission accepts D45-D49 and this successor architecture.

The two research records remain evidence with no authority effect. Since that historical Revision 2 result,
the provider-neutral `impl/system-integration/` package has implemented closed D45-D49 records, reference
closure, three-language contract generation, CLI receipt binding, and exact static observation. The package
still selects no provider, database, ORM, broker, provider runtime, publication, release, deployment, or
production state; its generated manifests explicitly keep runtime guarantees unobserved.

## Logical layers

| Layer | Components | Responsibility |
| --- | --- | --- |
| Semantic production | Recovery Planner | Derive one immutable intent and deterministic plan; never invoke recovery Operations. |
| Code seams | Recovery Coordination Repository, Recovery Coordination Unit of Work, Clock, Wakeup, Binding Resolver | Expose responsibility-specific consumer-owned contracts without a universal code-level Port or required DI framework. |
| Infrastructure bindings | Persistence Binding, Transaction Guarantee Binding, Failure Outcome Binding, Durable Workflow Runtime Binding | Connect exact logical concerns and code contracts to selected adapters, profiles, guarantees, and evidence boundaries. |
| Durable coordination | Coordination Store Adapter, Claim/Lease Coordinator | Persist progress, serialize advancement, fence stale workers, and atomically record dispatch outbox entries. |
| Execution | Durable Recovery Worker, Operation Binding Resolver | Preflight exact bindings, create attempts, invoke the current plan occurrence, and preserve Operation authority. |
| Continuation | Retry Scheduler, Restart Reconciler | Persist explicit retry choices and recover expired or interrupted work without replanning. |
| Business replay safety | Operation Replay Guard | Deduplicate semantic application using the stable Invocation Identity inside the Operation or its adapter boundary. |
| Delivery and evidence | Dispatch Outbox Publisher, Recovery Telemetry | Publish committed coordination events and expose property observations without becoming architecture authority. |
| Environment contracts | Recovery Clock, Dispatch Wakeup | Supply time and wakeup hints; neither contract owns dispatch truth. |

## Runtime flow

```text
Workflow evaluation
  -> Recovery Planner
  -> Recovery Coordination Repository
  -> Recovery Coordination Unit of Work (intent + frozen plan + version + outbox, atomically)
  -> selected Coordination Store Adapter through Persistence/Transaction/Failure bindings
  -> Dispatch Wakeup
  -> Claim/Lease Coordinator (CAS + monotonic fence + bounded lease)
  -> Durable Recovery Worker
       -> exact Binding Resolver preflight
       -> durable Attempt start
       -> Operation Replay Guard
       -> ordinary Operation execution
       -> durable outcome + progress + outbox
       -> Retry Scheduler | Terminal Disposition
  -> Dispatch Outbox Publisher

Restart Reconciler
  -> expires invalid authority
  -> records an executing lost attempt as unknown
  -> makes the first incomplete occurrence eligible without changing intent, plan, binding, or replay identity
```

## State ownership

- The Recovery Planner owns semantic projection only.
- The Dispatch Repository owns coordination records: dispatch, progress journal, attempts, claims, leases,
  retry schedules, terminal disposition, version, and dispatch outbox.
- The Claim/Lease Coordinator may advance coordination only through repository compare-and-set operations.
- The Durable Recovery Worker owns no durable truth outside repository transitions.
- Each Operation or its bound adapter owns the durable Invocation Identity result and all business state,
  declared effects, Events, and state-and-outbox atomicity.
- Wakeup transport and telemetry are projections. Losing or duplicating a wakeup cannot change dispatch truth.

## Contract and binding separation

The architecture has no universal code-level `Port`. Each executable seam is named for its responsibility:
Recovery Coordination Repository, Recovery Coordination Unit of Work, Recovery Clock, Dispatch Wakeup,
Recovery Telemetry, or Operation Binding Resolver. These are D45 concern-specific dependency contracts.

The code seams remain separate from metadata and provider realization:

```text
Recovery semantic subject
  -> concern-specific dependency contract
  -> D46 Persistence Binding or D47 Transaction Guarantee Binding when that guarantee is claimed
  -> D48 Failure Outcome Binding for provider and transaction failures
  -> selected store adapter and implementation profile
  -> raw runtime observation
  -> independent finding and receipt

Durable Workflow profile
  -> D49 Durable Workflow Runtime Binding
  -> exact persistence + transaction + failure + Clock + Wakeup + replay + version bindings
```

A D46 Persistence Binding may reference a real DS-D1 Interface when one owns the logical boundary, but a
Repository does not become an Interface merely because it is a dependency. The current architecture selects
no database or ORM.

The Recovery Coordination Unit of Work covers one coordination transition plus its dispatch outbox. A
recovery Operation separately owns its business-state-and-Operation-outbox transaction. No binding joins
those local boundaries into one Workflow-wide transaction.

## Portable architecture properties

The canonical profile requires:

1. one immutable intent and frozen plan per Workflow failure occurrence;
2. versioned compare-and-set dispatch transitions;
3. atomic dispatch transition and dispatch-outbox recording;
4. monotonic durable progress;
5. one current claim with a monotonic fencing token;
6. current Claim plus active Lease before every advancement;
7. stale-worker commit rejection;
8. unique attempt identity per executor episode;
9. stable Invocation Identity across attempts for one plan occurrence;
10. at-most-once semantic application inside the Operation boundary;
11. complete exact-binding preflight before the first invocation;
12. `unknown` outcome after authority loss during an invocation;
13. persisted bounded retry selected by an explicit continuation;
14. no replanning or Operation substitution;
15. terminal disposition with no implicit successor;
16. restart from the first incomplete occurrence;
17. at-least-once invocation, never a universal exactly-once process claim;
18. concern-specific dependency contracts rather than a universal Port;
19. distinct Repository/Persistence Binding and Unit of Work/Transaction Guarantee Binding records;
20. typed failure classification without implicit retry authority;
21. a complete D49 binding only for the durable Workflow profile; and
22. `unsupported` when required observation evidence is absent.

Machine definitions and enforcement stages are in [`properties.json`](properties.json) and
[`constraints.json`](constraints.json).

## Observed versus designed

Observed today:

- deterministic recovery planning in TypeScript, Python, and Rust;
- complete in-process D37 Recovery Intent identity and integrity checks;
- distinct stable plan-occurrence identities, including repeated use of one Operation;
- complete in-process D40 Invocation Identity over intent, plan, Operation, and occurrence;
- external executor ownership;
- complete binding preflight before invocation;
- ordered stop-on-failure execution;
- generated TypeScript, Python, and Rust recovery surfaces with the same claim ceiling;
- preservation of Operation effect ownership.

Partial today:

- D37 and D40 identity are complete in process, but durable uniqueness, reread, restart, and Operation-owned
  result recognition remain unimplemented adapter responsibilities;
- the executor models explicit retry/escalation/terminal-failure continuation but does not persist scheduling.

Designed only:

- durable Dispatch storage and compare-and-set transitions;
- atomic dispatch outbox;
- fenced Claims and renewable Leases;
- durable Attempts, Retry schedules, and Terminal Dispositions;
- restart reconciliation, dispatch wakeups, publication, and recovery telemetry.

## Deferred adapter choices

The design deliberately does not choose durable-store technology, ORM, queue versus polling, clock implementation,
lease duration, renewal cadence, worker partitioning, throughput/backpressure policy, retry configuration
storage, Event transport, telemetry backend, or archive/retention policy. These are adapter/profile decisions.
They do not block a deterministic reference implementation of the responsibility-specific contracts, binding
schemas, and state machine.

`cancelled`, `abandoned`, and dead-letter states are outside the admitted D36-D44 model and cannot be added by
an adapter.
