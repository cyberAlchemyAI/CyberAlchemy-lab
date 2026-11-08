# Original-role Reader Docker release 0002 — one-shot candidate

Status: **effect-enabled disjoint release candidate, Reader effect NOT RUN**.
This wrapper pins immutable effect-disabled controller 0003 freeze SHA-256
`cc8a24271b58551b82a295a3cd8faaddd068e4bc6f50e6430388c5dc69f51b11`
and independent static PASS review SHA-256
`b5dc21c8f52d420203ee41a9c6898a9a5a198e94d97ef59ec5cb5916918b1351`.
It verifies all three frozen controller members before import. Only the exact
one-shot command temporarily enables that controller in memory, prepares a
fresh exclusive attempt, runs its bounded Docker protocol, restores the flag,
and returns OS exit zero only for final `overall=PASS`. The controller mounts
the separately reviewed Reader entrypoint release bundle and invokes
`/tool/reader_entry.py`; the original cold-open source remains disabled on
disk and is enabled in memory only inside that verified container wrapper.

Selected Reader attempt:
`/home/vlad_/.local/state/cyberalchemy-lab/context-successor-20261020-0001/reader-attempt`.
Selected exclusive Docker name:
`cal-reader-only-20261020-0002-successor-0001`. Selected image ID:
`sha256:7ca5c679c6d8931d268bf5111cb7156a6eeadd9a267bc73f247cd0f0b0428874`.
The read-only `--preflight` verifies the selected Docker binary, exact image
ID/architecture/default user, and exact absent-name daemon grammar, then
invokes the controller's full 986-file staged-input and current-period check.
The observed image is amd64 with default `Config.User=20001:20001`; the
controller explicitly selects `--user 1000:1000`. The name was absent and
the Reader attempt unoccupied at construction. These observations must be
refreshed immediately before dispatch.

The one-shot controller uses a read-only/no-network/cap-drop-all container,
one-process UID-1000 private tmpfs cold-open, exact stage/tool bind mounts,
bounded daemon create/start/wait/inspect and logs, owned-only cleanup,
postclose 986-file and output revalidation, current period at final commit,
provisional UNKNOWN terminal, final file and observed finalization marker.
Loss of the marker after a crash downgrades retained evidence to UNKNOWN.
No retry or replacement of an occupied attempt is permitted. Release 0001 is
HOLD because a signal during attempt preparation could leave a consumed root
without an explicit UNKNOWN receipt. This disjoint successor checks the
sticky stop flag immediately after preparation and retains a no-replace,
fsynced `reader-release-unknown.json` on any post-claim exception, including
an interruption between that check and the controller's consumed marker.
The original failure remains primary. If a competing process wins the root
claim after preflight, the release does not write into that attempt. A release
UNKNOWN receipt overrides any apparent PASS; externally observed process
termination and independent effect review still determine the disposition.

Normal and optimized tests each pass **8/8**, including exact host
observation refusal, freeze/review drift, scoped effect enablement, causal
post-create and signal-race UNKNOWN cases, and competing-claim isolation. The
reviewed controller's fake-daemon suite
passes **42/42** in both modes; the Reader cold-open synthetic suite passes
**21/21** in both modes. Live read-only preflight passes, selecting 986
staged files and leaving the exclusive attempt/name unused. It hashes the
retained private archive without printing its body. No Reader container was
created by this construction.

An independent exact-byte static review of this release freeze is required
before the single effect command below. Capture its external OS exit and
bounded stdout/stderr. A subsequent independent effect review must verify
the consumed marker, create response, daemon identity and wait/inspect,
pre-removal and cleanup, output receipt, provisional/final hash join,
finalization marker, postclose inputs, period and container absence. A clean
PASS demonstrates only a disposable local Reader cold-open of the current
Source fixture; it does not qualify protected Source8, Mapper/Context, host
G01/G02, or the full original runtime plan.

```sh
/usr/bin/python3 -B /home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host/reader-successor-docker-release-0002/release.py --preflight
/usr/bin/python3 -B /home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host/reader-successor-docker-release-0002/release.py --execute-reviewed-one-shot
```
