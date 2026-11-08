# Body War Candidate-Path Rollback Lab

This repository-local lab defines a later local Docker experiment without
running it. Stable and candidate Body War services use identical application
bytes. Candidate identity exists only in the gateway's route and fault state.

The gateway deterministically selects the candidate for sequence positions
divisible by ten, injects candidate-only HTTP 503 responses before forwarding,
and exposes fixed low-cardinality metrics. A separate evaluator may decide
rollback; a rollback actuator removes the gateway candidate reference before
container removal; an independent observer verifies five candidate-reference
classes without trusting actuator success.

All implementation validation is pure or static. Docker, Compose, network
access, workload, faults, rollback effects, commissioning, deployment, and
runtime admission require a separate exact owner authorization.

Runtime-derived projections remain
`runtime-receipt-derived-offline-snapshot`, `runtime_admission: denied`, and
`authority_effect: none`.
