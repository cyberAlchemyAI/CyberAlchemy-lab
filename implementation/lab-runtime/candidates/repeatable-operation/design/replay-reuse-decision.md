# Replay reuse decision

Status: candidate implementation decision. C06 selects its expressly permitted measured no-op.

C03 measured full replay at zero and one transactions and preserved session/setup timeouts. The stack evidence identifies repeated schema construction. It does not establish a safe compiler-cache key or acceptable performance at five transactions. Retain uncached full verification while the integrated transaction and schema resolver are constructed. This decision grants no domain or action authority.

The public replay function invokes the full verifier on every call. No mtime, projection digest, session history or persistent checkpoint substitutes for original committed transactions, actual signatures or consequences. Future reuse requires a new exact measured implementation and parity evidence; a checkpoint's self digest is insufficient.

ReplayPins come from trusted local adapter inputs: exact legacy executable manifest bytes, immutable store configuration bytes, independently recorded baseline digest and optionally an exact expected HEAD. Obtaining those values from an untrusted store itself defeats the trust boundary. No wire endpoint grants trusted-adapter status.

The bridge loads only manifest-bound legacy runtime bytes into a private temporary package, performs strict JSON reads, verifies the external baseline/configuration pins, and executes the preserved complete replay. It rechecks transaction, configuration, HEAD and executable bindings afterward. Current reads require current source hashes. Historical reads preserve a stale/historical distinction. Checkpoint inputs have no supported trust path and are rejected. The read-only facade has no signing, provisioning, application or recovery methods.

This bridges legacy v1/v2 branch inspection during candidate construction. It is not the final general artifact handler or publisher. Later C05/C09 integration must select exact current branch and source-profile contracts. The isolated tests cover one real signed fixture transaction, historical signature/transaction edits, resealed baseline/configuration edits, wrong profile, independent HEAD and executable pins, source changes, JSON duplication, symlinks and fresh-process reconstruction. The paired timing sample demonstrates identical outputs, not an optimization or Product SLA.
