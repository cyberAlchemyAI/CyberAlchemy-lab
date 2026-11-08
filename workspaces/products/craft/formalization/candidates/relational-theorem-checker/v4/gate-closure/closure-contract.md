# Original R06/G4 closure contract

This follow-up implements Track H of the reviewed plan. The original task identities, criteria, profiles and accepted mathematical evidence remain the inputs. New gate receipts resolve current status through a checked overlay; the captured original plan and its generated documents remain historical snapshots. The current-state reader must check that every overlay receipt addresses the original exact criteria and outputs. This is local candidate review bookkeeping.

## Formal meaning

`Reviewed(challenge, feedback)` requires a nonempty unique mandatory artifact set and exactly that unique set in the feedback. Membership includes both file path and digest. `Eligible` adds the exact gate/scope, both required positive answers, faithful human capture, candidate-only use and the gate prerequisites. R06 starts only with both gates pending; G4 requires accepted R06 and pending G4. `transition` appends one gate to history and preserves every predecessor evidence binding.

The nine theorems in `GateClosure.lean` establish binding-check equivalence, eligibility equivalence, exact transition, complete mandatory bindings, rejection across scopes, rejection of nonpositive feedback, G4's R06 prerequisite, predecessor-evidence preservation and appended history. Their scope is the typed gate model. Raw JSON, SHA256, filesystem durability, the Python implementation and faithful capture of an actual human response remain explicit boundaries.

## Review scopes and answers

- R06: `original-v1-pilot-meaning-diagnostics`. Required answers: meanings and diagnostics, each accepted/revisions/undecided. Machine coverage is independently audited.
- G4: `original-v1-l4-bounded-use`. Required answers: layer audit understood/accepted and bounded-use recommended, represented as accepted/revisions/undecided. Acceptance additionally checks current layer evidence and accepted R06.
- The extension annex has its own scope. Reading or commenting on it does not establish either original gate's required answers. Earlier v3 P11 feedback is not reused as original-gate feedback.

Mandatory reviewed identities: packet, supported-use matrix, pilot report and current evidence audit for R06; packet, supported-use matrix, layer alignment audit and bounded-use recommendation for G4. The exact manifest is additionally bound. Every emitted receipt binds the feedback, manifest, gate implementation, formal evidence and complete predecessor/source evidence; it retains all original criteria and required outputs.

## State and durability

The authoritative closure log is an append-only sequence in an owned directory, serialized with a cooperating filesystem lock. A gate entry contains the exact predecessor-log identity and original base-plan identity. Immutable generation folders are durably written before atomically publishing the next log entry. The validated log is authoritative; the current view is derived and repairable. Orphan preparations are retained as uncommitted records and never count as acceptance. Recovery cannot create human feedback or qualification events.

Use a separate directory for every fixture/control. Production candidate capture accepts observed direct user feedback; fixtures are explicitly marked and cannot enter the actual closure. Human authenticity is an operator premise, not something proven from `source: direct-user-message` or a JSON quote. No response is fabricated.

## Ownership and scope

The explicitly adopted status-overlay interpretation is recorded in `scope-manifest.json`. R06 artifacts are versioned under the original `v1/pilot/` write boundary; G4 artifacts under `v1/gates/l4/`. New implementation and log files live in `v4/gate-closure/`. Current task views name the overlay so that 33 historical acceptances and later original-gate acceptances are not confused with mutations of the historical plan. No deployment, organizational admission, authority publication or fresh proof event follows from a gate receipt.
