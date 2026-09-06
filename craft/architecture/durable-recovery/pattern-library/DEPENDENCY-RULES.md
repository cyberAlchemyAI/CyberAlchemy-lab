# Dependency Rules

Allowed direction:

```text
Workflow -> Recovery Planner -> Recovery Coordination Repository + Unit of Work
Dispatcher/Worker -> concern-specific dependency contracts -> durable adapters
Worker -> Binding Resolver -> Operation
Operation -> Operation-owned Replay Guard
Outbox Publisher/Telemetry -> committed records
```

Forbidden direction:

- Workflow evaluation must not call the Durable Recovery Worker or a recovery Operation.
- A universal code-level `Port`, required DI container, service locator, or decorator framework must not be
  introduced as DomainSpec architecture.
- Repository is not a DS-D1 Interface unless a real logical Interface boundary independently exists.
- Persistence Binding is not Repository code; Transaction Guarantee Binding is not Unit of Work code.
- Transport, Clock, and Telemetry adapters must not author dispatch state.
- Retry Scheduler must not select a different plan, occurrence, binding, or Invocation Identity.
- Dispatch Repository must not perform Operation business effects.
- Worker process identity, Claim, Lease, and Attempt must not enter Invocation Identity.
- A stale fencing token must never commit an advancement even if its former Lease time appears valid locally.
- Terminal Disposition must not choose or execute successor work.

Cycles are forbidden in the logical component dependency graph. Runtime replay is a state-machine transition,
not an architectural dependency cycle.
