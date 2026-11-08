# Mapper successor Docker external observer 0002

Status: **effect disabled, awaiting independent static review**. This successor
resolves the three descriptor teardown findings in the observer0001 independent
HOLD review SHA-256
`494e9d4368c212b143cb8199537d6c6e233efc8cbb6b4d9a88efeeef0faf45e0`.
The frozen observer0001 remains untouched. This is a
single-dispatch observer for the exact Mapper Docker release freeze
`ce6356ef776c20d89286cc116c1750eeae6df9fb7a640e6dc545634c5b656452`
and independent release static PASS review
`816fa66234f9ac8ccb69ca6d4d1f1657ad3f0c80e4babe644385df3ab4e94ea8`.
The reviewed release entrypoint SHA-256 is
`cf85a26da6166e96855050ae0f511d22ff260ce4f807b9c67a077391b01bf927`.
No release or Docker effect was run to prepare this candidate.

The read-only check is:

```
/usr/bin/python3 -B /home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host/mapper-successor-docker-observer-0002/observer.py --preflight
```

It rehashes the pinned release freeze/review and all three release members,
then runs the release's exact read-only preflight and requires its selected
attempt/name/Controller/Stage/no-retry bindings. Its selected observation root
is `/home/vlad_/.local/state/cyberalchemy-lab-observations/mapper-successor-docker-release-0001`.
That root must be absent under its held owner-0700 parent.

The only planned effect argv, **currently refused by `EFFECT_ENABLED=False`**,
is this observer's `--execute-reviewed-one-shot` route. It records an exclusive
0700 consumed root, fsynced `consumed.json` and intent, and owner-0600 raw
stdout/stderr files **before** spawning exactly:

```
/usr/bin/python3 -B /home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host/mapper-successor-docker-release-0001/release.py --execute-reviewed-one-shot
```

It streams both pipes without a second `communicate()` call, observes a strict
integer OS exit, keeps the child alive on SIGINT/SIGTERM until reaped, and
classifies interrupted, nonzero, late stderr, overflow, pipe-tail timeout,
capture error, missing final, or any join drift as UNKNOWN with no retry.
The raw streams remain in the restricted observation root; the CLI never
prints their bodies. Returned stream FDs enter the ownership ledger one at a
time; a stream initialization fault closes its local FD. The ledger removes
each number **before** fsync/close, so a close-after-release error cannot cause
a retry against a reused foreign number. Finalizers attempt every still-owned
descriptor independently, preserving the primary failure. `capture.json` is
written before descriptor cleanup; `observation.json` is a provisional record
published after the earlier held descriptors close and postclose custody
checks. A postpublication close error may leave this provisional file; the
external invocation still fails, and the file alone never grants PASS. Any
uncertainty preserves the consumed attempt without retry.

Even a zero OS exit only yields `PROVISIONAL_OS_ZERO_FINAL_JOIN`. The observer
joins separately canonical stdout and controller `evidence/final.json` by
parsed value (their JSON indentation differs), then
rehashes `evidence/terminal.json`, requiring the selected name, terminal PASS,
strict zero client/daemon exits, exact Docker ID form, and `container_absent`.
It checks the embedded 55-leaf output verifier summary. Independent effect
review must still inspect exact terminal/package/CID/name absence and decide
whether this provisional evidence is valid. It grants no Context or original
protected Source8 authority. Same-UID adversarial tampering and privileged
host mutation remain outside the trusted-local claim ceiling.

Fixture tests launch only disposable public Python children and run with
normal Python and `-O`. They cover canonical success, strict nonzero exit,
late stderr, final/terminal drift, overflow, SIGINT/reap, same-state refusal,
postclose publication failure, and the disabled CLI. Four additional causal
tests reproduce and defeat R01 returned-FD/local-create leaks, R02
close-then-raise numeric-FD reuse, and R03 postclose/read-finalizer skip.
The real read-only
preflight passed on this WSL host on 2026-10-20; no observation root was
claimed. A separate independent reviewer should rehash `freeze.json` and
challenge the process lifecycle, postclose evidence protocol, owner/mode/path
checks, no-retry semantics, and terminal/package joins before any effect is
enabled in a disjoint reviewed wrapper.
