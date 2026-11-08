# Complete mocked reference product: review scope

Status: candidate pending exact validation and owner review. Authority effect: none.
Open questions: [OPERATOR.md](OPERATOR.md#open-questions).

The deliverable is a workspace reference package with one operator command,
an unchanged accepted standalone public bundle, a complete mock API walkthrough,
an integrated protected/durable process rehearsal, an operator guide, exact file
identity and a consolidated validation receipt. The protected composition is built
and tested from the source checkout; it is not a standalone protected distribution.

Acceptance criteria:

1. `verify` identifies every packaged source/runtime input and rejects drift.
2. `demo` starts two mocks and the service, completes the API walkthrough and closes
   all listeners. `serve` supports manual calls and clean interruption.
3. `rehearse` proves current authorization and tenant/principal isolation with real
   Auth Foundation verification/authorization, real HTTP, encrypted SQLite and new
   service processes. Online introspection is explicitly a fixture.
4. Clean restart replays completed JSON; revoked permission blocks replay;
   SIGKILL during inference leaves an unresolved request without another attempt.
5. `validate` passes all 217 tests against the same manifest, preserves logs, and
   records failures as failures. Its receipt distinguishes checks from test totals.
6. Operator/caller roles, limits, security modes, storage and recovery boundaries
   are documented; no model download or commercial provider is required.

The accepted base pattern remains independently accepted. This candidate adds
operator packaging and consolidated evidence, not new inference policies. Its
approval would not establish real-model quality, third-party engine compatibility,
live issuer behavior, production readiness, Rust service parity or deployment.

Construction frontier: final validation of this exact workspace kit, then product
review. All implementation work for this candidate is runnable with existing local
dependencies. Operational residue (optional live issuer/engine, persistent key
operations, hosting and deployment) has no causal dependency on this mock validation.
