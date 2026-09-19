# SQL Three-Layer Durable Storage Definitions

Status: authored successor candidate

These definitions specialize the accepted Durable Storage capability without
changing its immutable v1 definition set. They govern SQL portability,
three-layer protection, and verified restoration.

## DST3-D1 — Three-Layer Protection

Three-Layer Protection is the state in which one immutable knowledge-material
object is represented in an operational SQL store, an append-only recovery
journal, and an immutable SQL-independent archive, with each layer assigned a
distinct failure-domain identity and each representation bound to the same
qualified byte identity.

Three rows, schemas, databases, containers, or volumes sharing one effective
failure domain do not constitute Three-Layer Protection.

## DST3-D2 — Failure Domain

A Failure Domain is the exact set of infrastructure, authority, credentials,
process, locality, and operational dependencies whose common failure can make a
storage representation unavailable, corrupt, or untrustworthy.

Failure-domain identity is realization evidence and never object identity.

## DST3-D3 — Operational SQL Layer

The Operational SQL Layer is the database-backed representation used for normal
reads and writes. It implements a database-neutral SQL storage contract through
one dialect adapter. Success in this layer alone is not backup or recoverability.

## DST3-D4 — Recovery Journal Layer

The Recovery Journal Layer is an append-only sequence of immutable object events
stored outside the operational layer's failure domain. It supports deterministic
reconstruction at a named Recovery Point without becoming the operational store.

## DST3-D5 — Immutable Archive Layer

The Immutable Archive Layer is a SQL-independent, content-addressed backup of
encrypted object bytes and canonical manifests. Existing archive identities may
not be overwritten; changed bytes create a new identity.

## DST3-D6 — Recovery Point

A Recovery Point is a deterministic boundary over journal events and archive
manifests from which one declared object set can be reconstructed. It binds the
policy version, source layer, event or manifest frontier, and expected object
identities.

## DST3-D7 — Restore Candidate

A Restore Candidate is reconstructed bytes and context obtained from a recovery
layer but not yet trusted for dependent use. It remains a candidate until exact
identity, policy, object-set closure, and destination binding are verified.

## DST3-D8 — Verified Restoration

A Verified Restoration is the successful reconstruction of every required
object into a declared destination, followed by retrieval and verification of
all qualified byte identities and context under the current recovery policy.

Copy, import, replay, or database-start success alone is not restoration proof.

## DST3-D9 — Recovery Evidence

Recovery Evidence is an immutable record binding the failed or bypassed layer,
selected recovery point, source and destination realizations, exact object set,
verification results, observation interval, and any rejected candidates.

Recovery Evidence cannot claim availability outside its observed environment.

## DST3-D10 — SQL Portability Contract

The SQL Portability Contract is the database-neutral behavior contract for
persisting, retrieving, journaling, and restoring durable objects. SQL dialects,
placeholders, binary types, connection protocols, and migration syntax belong
to adapters and cannot enter object identity or product meaning.

PostgreSQL is the first adapter, not the definition of SQL storage.

## DST3-D11 — Recovery Policy

A Recovery Policy is the versioned rule set that names required layers, distinct
failure-domain constraints, protection completion rules, recovery order,
retention, recovery-point objectives, and restoration verification obligations.

No default policy may silently relax three-layer protection.

## DST3-D12 — Immutable Backup Set

An Immutable Backup Set is a canonical manifest plus the closed collection of
content-addressed encrypted objects it names. Its identity covers manifest
version, policy, object identities, creation frontier, and exact manifest bytes.

Changing membership or metadata creates a new Backup Set identity.

## Required relationships

- Three-Layer Protection requires exactly one Operational SQL Layer, one
  Recovery Journal Layer, and one Immutable Archive Layer for the protected
  object.
- Every required layer belongs to a distinct Failure Domain.
- The Operational SQL Layer and Recovery Journal Layer implement the SQL
  Portability Contract through independently identified adapters.
- The Immutable Archive Layer stores Immutable Backup Sets rather than SQL
  database internals as the portable recovery authority.
- A Recovery Point selects Restore Candidates.
- Restore Candidates may produce Verified Restoration only after complete
  verification.
- Verified Restoration produces Recovery Evidence.

## Claim ceiling

These definitions select no production database, cloud, region, credential,
retention period, RPO, RTO, deployment, or external effect. A Dockerized
PostgreSQL realization may provide local conformance evidence only.

