# Compatible upgrade prototype definitions

Private candidate terms. Canonical vocabulary remains owned by CyberAlchemy-v2 authority/definitions. These specialize the existing local control-plane definitions.

## CU-STATE: Function-owned state

Formal prototype meaning: one durable SQLite state/outbox/inbox bound to the tuple (control-plane root, tenant, project, function), independent of revision ID. An exclusive host lock permits one live revision writer.

Plain language: upgrading the code keeps the function’s orders and message receipts.

Alch context: RWO/Ansible provisions one opaque root; compatible generated Rust revisions reuse its runtime database.

## CU-COMPAT: Compatible revision

Formal prototype meaning: exact canonical equality of compiled event configuration after excluding only its source binding digest, selected host semantic fields, and generated storage/runtime source and Cargo lock hashes. Only source comments and host timeout/request-size limits may vary without changing this contract. The contract is fixed by first activation.

Plain language: a conservative check that both revisions interpret the same stored records and messages.

Alch context: rule, mapping, field, identity, delivery, consumer or runtime changes are rejected. This is not a general schema-migration or behavioral-equivalence proof.

## CU-DRAIN: Drained handoff

Formal prototype meaning: stop accepting producer calls, finish in-flight work and settle all outbox rows to published before releasing the old host’s exclusive state lock. Dead rows or a bounded drain timeout reject the handoff. Start a verified compatible host before atomically selecting its route.

Plain language: finish recorded work before handing the database to the next revision.

Alch context: the existing lease-fenced claim/consume/settle adapter performs delivery; the controller never rewrites queue statuses to force a switch.

## CU-ROLLBACK: Compatible code rollback

Formal prototype meaning: reselect a previously built compatible revision using the same drained handoff and current database. No previous database snapshot is restored.

Plain language: switch the code back while retaining all committed orders and message receipts.

Alch context: v1 -> v2 -> v1 retains both versions’ committed data and producer/consumer deduplication.

## Open Questions

See [README](README.md#open-questions).
