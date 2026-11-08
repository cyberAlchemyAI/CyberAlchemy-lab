# What a local shadow application changes

An application advances one owned candidate store from generation *g* to *g+1*. The authoritative head is the `head` row in `metadata.db`. `HEAD.json` is a checked mirror. A successful file rename alone is not publication. A review binds the exact starting head, raw proposal bytes, successor identity, condition/context identity and ordered mapped requests. The writer compares both generation and complete starting head inside a SQLite transaction.

Each application obtains a fresh complete proposal qualification and a separate fresh identity-extension qualification of the exact successor baseline. The successor's registration retains the stronger twenty-obligation check and the seventeen-obligation registration inventory. Mapped delegation and inheritance requests have their own fresh concrete Lean witnesses and individually named contexts. Their truth is not merged across epochs. Unknown conditions, negative delegation and active require/forbid conflicts refuse the application. Activation still does not prove fulfillment.

Saved qualifications, current hashes and `fresh_at_creation` describe evidence. The public `ShadowContext` requires process-local events from its own newly completed invocations and consumes a preparation handle once. Reading saved evidence, opening another context, or recovering a store cannot recreate those events.

## Transaction and crash windows

The table describes actual process-exit probes, not simulated power loss. The metadata-only probes use `io-probe-unqualified` stores and make no kernel-qualification claim. Full applications must additionally pass the public fresh-qualification controls.

| Last durable phase | What exists | Recovery |
| --- | --- | --- |
| Journal | Prepared row; old committed head | Abort preparation; retain partial files; preserve old head. |
| Snapshot | Bound immutable snapshot; prepared row | Verify durable snapshot; abort preparation; preserve old head. A changed snapshot requires reconciliation. |
| Registration | Bound snapshot and registration; prepared row | Verify both durable artifacts; abort preparation; preserve old head. Cancellation here cannot advance the head. |
| Metadata head | New head and committed transaction in one database commit; mirror may still equal exact old head | Preserve new committed head. Repair the mirror only when the journal records this exact window and its bytes equal the exact prior head. |
| Mirror | New authoritative head and matching mirror; completion marker may be pending | Preserve new head and complete the recorded transaction. |
| Complete | New authoritative head, matching mirror and complete journal | Verify. A later mirror edit, including restoring the old head, requires reconciliation. |

The implementation selects rollback journaling and `synchronous=FULL`, checks those effective settings, fsyncs immutable files and their directories, then commits the head and journal together. These choices rely on SQLite, operating-system locking and successful storage synchronization. SQLite documents those assumptions in [atomic commit](https://www.sqlite.org/atomiccommit.html) and [synchronous settings](https://www.sqlite.org/pragma.html#pragma_synchronous). The Lean theorem describes the publication guard and generation rule; it does not prove these filesystem or database implementations.

## Operator response to reconciliation

Call `Store.recover()` before preparing another application. `head-current` includes the verified authoritative head and any narrowly permitted recovery actions. It remains recorded inspection, with `fresh_qualification=false`. `reconciliation-required` means the code could not safely establish a consistent committed chain. Stop publication to that store and preserve the database, journal, owner, mirror, immutable snapshots, registrations and qualification evidence together.

Compare the database's committed transaction chain and exact bound artifacts before deciding which external change to retain. Do not delete SQLite recovery files, overwrite the head, automatically replay a preparation, or restore an earlier generation as a repair. A postcommit exception may have occurred after the new head became durable: the public application path checks for its own committed fresh run and reports the durable application after permitted recovery. Conflicting evidence remains reconciliation-required.

Store creation is exclusive. Interrupted initialization leaves a partial owned directory for inspection; retrying cannot overwrite it. These local stores support cooperating writers through the mediated API and advisory lock. A same-privilege process can bypass Python, change permissions or edit the database; detecting conflicts does not establish hostile-host exclusion. The stores carry `authority_effect=none` and never change a real project head or admission.
