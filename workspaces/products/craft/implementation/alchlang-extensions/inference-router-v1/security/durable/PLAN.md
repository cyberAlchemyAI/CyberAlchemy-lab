# Durable application authentication state

Product construction: approved structural identity/tenant/role model → existing
service security contracts → synchronous state port → encrypted SQLite adapter
and browser composition → restart, race, failure and regression evidence.
No ontology records/selectors are dependencies. This is a local D65 candidate;
testing does not grant admission, promotion or deployment authority.

The state port has `sessions` and `records` collections (`get`, `set`, `delete`,
`size`, iteration), synchronous `transaction(fn)`, `mode`, and `close()`.
Session values retain the existing verified identity, bearer token, opaque CSRF,
tenants, last-use and expiry fields. Enrollment records retain token expiry and
revoked status. These are native custody records, not new permission definitions.
Auth Foundation's Rust SQLite provider continues to own authorization snapshots;
its schema is not repurposed for browser secrets. DomainSpec/Alch compiled
security requirements and current Rust decisions are unchanged.

SQLite BEGIN IMMEDIATE serializes enrollment capacity, replacement and logout.
Logout atomically deletes the browser session and retains its token tombstone.
After asynchronous work, authorization and browser forwarding re-read current
state. Session touch cannot recreate a deleted session. Tombstones survive until
token expiry; an unknown verified token can also be revoked before registration.
Ciphertext uses AES-256-GCM with record-location associated data and HMAC keys;
bearers, cookie identifiers and identity values are not stored as plaintext.
Full synchronous commits use rollback journaling. Wrong keys, unknown schemas,
corruption, lock timeout and unavailable storage fail closed without reset/fallback.

Operational support, operator-owned, no construction stage: choose a private
local directory and retain a separate 32-byte key across restarts. Use the same
DB and key for instances of the same application on one host. No existing AF
policy database is migrated and no running service is switched. Node's bundled
SQLite supports this native JavaScript adapter; Rust regression builds use the
repository toolchain launcher. Disposable tests own their databases and keys.

Runnable frontier: complete adapter, explicit durable binding, tests and paired
Craft evidence. No construction blocker. Operational residue does not block tests.

## Open Questions

- Production key custody, rotation, backup/restore and deployment remain operator
  decisions. Restoring old database state can restore old revocation state; no
  backup rollback defense is claimed. Directory ancestors must be operator-owned.
- Multi-host storage/coordination is outside this single-host SQLite candidate.
- Access-token renewal, issuer-wide logout and durable inference request custody
  remain separate work. Existing access-token and idle expiry limits still apply.
- OAuth transactions remain process-local: restart requires beginning login again;
  multiple listeners need affinity while a login is in progress.
- Authorization is checked at the existing request boundaries; already-returned
  streams are not continuously reauthorized.
