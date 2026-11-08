# Durable inference request custody

Product construction: approved tenant/principal/key identity and one-attempt,
write-once outcome semantics → explicit bounded-sqlite backend contract → encrypted
SQLite adapter and Alch binding → restart, concurrency and regression tests.
No ontology record/selector dependency. This local D65 candidate grants no
admission, publication or deployment authority.

Reuse the generated idempotency decision policy. Reservation evaluates that
policy outside database locks, then commits only against the same database
revision. Contention retries are bounded. Before provider dispatch, persist the
attempt. Completed JSON may replay only with matching identity/fingerprint and
current authorization. Streams never replay. Failed requests retain their prior
failure. Retention starts only after outcome AND transport settlement.

A process crash leaves pending/attempted requests unresolved. They remain
non-executable across restart, including after ordinary retention time. No lease,
automatic retry or inference of remote failure is introduced. Inspection reports
remote completion unknown until a completed local result was recorded.

Operational support: operator-owned private local database directory and separate
32-byte encryption key; same database/key/configuration across local instances.
Wall-clock milliseconds are required across restarts. No existing database is
migrated, no running host is switched. Rust tests use the shared toolchain.
Runnable construction: adapter, explicit backend binding, generated-source
integration and tests. No current construction blocker.

## Open Questions

Operator resolution of uncertain outcomes is the next bounded construction
candidate; pending records intentionally retain capacity until resolved.
Key rotation, backup rollback protection, multi-host storage, clock discipline,
and production deployment remain operator decisions. Restoring old snapshots
can lose deduplication evidence. Exactly-once remote execution is not claimed.
