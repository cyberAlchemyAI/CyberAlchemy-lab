# Original gate completion API

This API implements the typed policy in `GateClosure.lean` with current source/hash checks and an owned append-only filesystem log. Human capture remains an operator trust boundary. The API is for candidate review status and issues no fresh theorem qualification, permission, deployment or admission.

`Ledger().resolve()` validates the original base plan, every published log entry, the original gate criteria/deliverables, reviewed artifact identities, actual feedback and all bound source files. It returns the original 35-task current view. `Ledger().recover()` performs those checks and reconstructs the derived view. Recovery never infers approval from orphan prepared files and always reports `fresh_event: false`.

`Ledger().record_feedback(raw_bytes, observed_direct_response=True)` requires closed source-bound response JSON. The operator sets the flag only after observing the user's direct response to the named frozen packet. Exact artifacts are resolved from the independently accepted H03 challenge registry. Actual ledgers reject `capture_kind: fixture`. Capture preserves revisions/undecided answers without accepting a gate; repeated identical capture is idempotent.

`Ledger().accept(gate, feedback_reference, expected_head=...)` checks the exact expected log head, current sources, required positive answers and original criteria, then prepares the original required artifacts and durably publishes one immutable entry. Cooperating writers serialize. A stale expected head receives `Conflict`; it must be reread and the proposal reassessed. R06 starts at an empty log. G4 requires the exact accepted R06 predecessor. Derived views can be regenerated after interruption. Uncommitted preparations remain historical and never count as accepted.

The equivalent commands are `record_feedback.py`, `accept_r06.py`, `accept_g4.py`, and `resolve_gate_status.py`. Feedback references and the expected head are structured JSON values containing repository-relative path and SHA256. The expected head is `null` only before R06. Run `resolve_gate_status.py --recover` to regenerate the current view from the checked log. Commands must consume actual response files rather than a fabricated example.

The original plan snapshot remains at its captured 33/35 acceptance state. The current checked interpretation is the base plan plus `state/entries/`; only `resolve_gate_status.py` can report later gate acceptance after validating its evidence. The interpretation and versioned original task write boundaries are explicitly declared in `scope-manifest.json`.

Fixture APIs are restricted to `execution/` and marked fixture-only. Crash injection is accepted only there. `run_controls.py h02` verifies schema/evidence/gate controls; `run_controls.py h04` also runs actual competing writers, child-process crashes around authoritative log publication, recovery and lost-view reconstruction. These controls cannot establish actual human acceptance.
