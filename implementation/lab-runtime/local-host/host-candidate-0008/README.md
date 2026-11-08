# Host broker candidate 0008

Status: **effect-disabled, disposable mechanics only**. This disjoint revision responds to 0007's independent `REQUEST CHANGES`. It does not install or run a broker on the host and changes no original T02/T35 acceptance.

The public `prepare_child`, `prepare_bound_child`, and `activation_capability` routes raise `HOST_ACTIVATION_DISABLED` before reads or writes. The internal `_prepare_fixture_child` and `_write_exclusive` refuse root effective UID and require held `instances` and `custody` descriptors under the same `/tmp/cal-host-candidate-0008-<random>` scratch root. These Python checks narrow accidental callable effects; they are not an installed privilege boundary and do not confer Root or slot authority. The future root broker requires a **new separately reviewed effectful release**, not removal of one guard in place.

The held-input helper opens a named regular file from a caller-held directory with `O_NOFOLLOW|O_NOATIME|O_CLOEXEC`. `BoundInputs.verify` checks the `O_NOATIME` descriptor flag before `pread`, then compares held device/inode, owner/mode, size, times and exact SHA-256 bytes. It refuses on platforms or filesystems where `O_NOATIME` cannot be opened; a selected host effect also requires an independent atime pre/post probe on the actual mount. In a disposable ext4 test with Root and slot atimes set 30 days old, both remained unchanged after verification. A plain read-only FD refuses **before reading**. The exact predicted future broker write set remains four entries, with the new child's directory-scan atime included in its metadata effects in `write-manifest-0008.json`. Other preflight/account/systemd/snapshot effects require separate manifests.

The inherited scratch core retains held nofollow directory traversal, exact `i-<Root SHA first 16>-e<nonzero decimal>` instance grammar, first-instant `0700` creation, durable slot/intent/prepared ordering and replay refusal. A scratch same-UID actor can replace a child entry and the held attachment check detects it afterward. Actual denial of the create-to-open race still requires continuously root-controlled ancestors and an installed hostile oracle. Exact Root issuer semantics, current period, continuously held slot lock, ancestor/alias census, held-inode bind handoff, proc/FD denial and service-tree isolation are **not implemented or proven** by this candidate. Caller-supplied bytes and hashes remain untrusted fixture values.

Run the 15 scratch tests with:

```bash
python3 -W error::ResourceWarning -m unittest -v implementation/lab-runtime/local-host/host-candidate-0008/test_broker.py
python3 -O -W error::ResourceWarning -m unittest -v implementation/lab-runtime/local-host/host-candidate-0008/test_broker.py
```
