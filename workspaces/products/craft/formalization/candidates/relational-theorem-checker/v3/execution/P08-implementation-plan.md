# P08: mediated shadow commit and recovery

This is the implementation plan for the next dependent unit. P07 acceptance is still required before P08 execution begins.

## Formal boundary first

Retain P00's distinction between current saved evidence and a live fresh qualification. The publication invariant is conditional on exclusively mediated cooperating writers: a committed shadow head must name the exact registered successor of the reviewed generation, with a fresh complete qualification at its commit boundary. The Lean graph theorems do not prove SQLite, filesystem durability, operating-system exclusion or external assessment truth.

## Concrete design

Use a local transactional metadata store for the authoritative head and publication journal. Store immutable snapshot and registration files with byte bindings. A head generation and before-baseline identity are part of every review and transaction. Any human-facing HEAD file is a checked mirror rather than an atomic compare-and-swap primitive. A conflicting external edit yields reconciliation-required and preserves potentially committed state.

The public apply path obtains a new OwnedQualifier result for the exact raw request and original resource policy. It checks the exact review/proposal/before identity, all required obligations, fresh process-local completion, current imported/cache/source bindings and expected generation. It registers that exact successor separately, consumes the live application capability and commits through the transactional writer boundary. Saved result JSON, current hashes or a copied ready flag cannot authorize application.

## Implementation sequence

1. Define closed Review, ShadowHead, Registration and Transaction schemas, including candidate-only authority, expected generation, exact before/successor identities, resource outcome, registration binding and reconciliation reason.
2. Implement a store owner and cooperating-writer boundary. Initialize only owned fixture stores. Protect canonical snapshot paths and refuse symlink/path escapes. Use explicit transaction states prepared, committed, aborted and reconciliation-required.
3. Implement durable snapshot and registration writes: exclusive filenames, bounded serialization, fsync files and containing directories before committing authoritative head metadata. Document every file-versus-metadata crash window.
4. Connect fresh owned qualification and currentness checks at the commit boundary. Leave head unchanged on cancellation, exhausted work, source/context drift, stale generation and incomplete proof inventory. Consume each exact fresh qualification once for application.
5. Implement recovery. Validate bindings for prepared and committed transactions. An uncommitted preparation can be reported as aborted after verifying the authoritative head. A potentially committed successor is preserved; conflicting registration, snapshot or head state requires reconciliation rather than silent rollback.
6. Exercise two cooperating publishers of one reviewed generation, saved-receipt substitution, changed condition/context, cancelled registration and external head edits. Keep the supported scope explicit: advisory locks do not defeat same-privilege external writers.
7. Test actual process crashes at snapshot, registration, journal and authoritative-head boundaries. Distinguish metadata-only fault probes from full fresh theorem-qualified applications in the report. Do not label an injected fixture capability as a fresh kernel qualification.
8. Review exact before/after head bindings and registered successor identities. Produce a readable crash-outcome table and operator recovery explanation before accepting P08.

## Acceptance evidence

Exactly one cooperating publisher of a reviewed generation may commit; stale peers reject. Every applied successor has its own exact registration and fresh invocation evidence. Each crash phase is either explicitly recoverable or reconciliation-required, without losing a potentially committed successor. All state remains a bounded local candidate shadow with authority_effect none.

No real project head, canonical authority, deployment or external publication is changed by this task's fixture-store tests.
