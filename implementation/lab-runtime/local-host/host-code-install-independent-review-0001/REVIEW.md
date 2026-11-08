# Independent review: inactive host code-install candidate 0001

Reviewed 2026-10-21. Verdict: **PASS-BOUNDED for the read-only preflight and hard-disabled apply route; HOLD for any host installation or storage effect.** The reviewed candidate has no installer. It does not install an executable, allocate UID 20001, create storage, or establish G01/G02, T02, or T35.

## Exact reviewed inputs

| Input | SHA-256 |
| --- | --- |
| `host-code-install-candidate-0001/verify.py` | `6dcf1001b45c9b1ea9060a328006b15dc2f8d1121d6445a08a257350d5e1c437` |
| `host-code-install-candidate-0001/test_verify.py` | `de4c0037b241f6a9fa781093a1fe97aae14774e9876a4c966ec64d680e92d4cd` |
| `host-code-install-candidate-0001/write-manifest.json` | `11b4c3dc8f9e89ad739f666b0bb26b219288c897f270ac1ca81023eb3b5bd625` |
| `host-code-install-candidate-0001/README.md` | `b0c4602844d530dfa09ee66f828cad1757738fde6faf89c46e1bd763f355767f` |
| Referenced `host-storage-release-candidate-0001/release.py` | `dcbf8d6c8ddad7f77a2f55ba6f95a77f5936456853cb8145b517ef3e22ff53c4` |

The source is 13,669 bytes and has `LIVE_RELEASE_ENABLED = False`. Its effect path rejects before storage creation. Installing those exact bytes would leave storage creation disabled. A future active successor must have its own frozen bytes, exact manifest, independent code review, and separate installation decision; the current manifest cannot be reinterpreted as its release.

## Observations

- `python3 -B .../verify.py --plan` exited 0, returned `INACTIVE_PREFLIGHT_ONLY`, `apply_enabled: false`, the exact source digest and size, and root-owned `0755` `/usr`, `/usr/local`, and `/usr/local/libexec` device/inode witnesses. These are point-in-time observations, not an installed-tree or exclusive-custody proof.
- `python3 -B .../verify.py --apply` exited 3 with `REFUSED:HOST_CODE_INSTALL_NOT_RELEASED`. In `main()`, this branch precedes `preflight()` and its host/source reads. There is no write or install function in `verify.py`.
- The supplied eight tests pass under normal and optimized Python (`-B -W error::ResourceWarning` and `-O -B -W error::ResourceWarning`). They cover source hash/symlink/old-atime handling, absent package, writable/symlink ancestor refusal, and apply refusal. They are synthetic and do not simulate a root-owned install or hostile concurrent writer.
- The proposed manifest accounts for **two named host entries** in order: root-owned `0700` package directory at `/usr/local/libexec/cal-host-storage-release-0001`, then root-owned `0500` regular `release.py` underneath. It calls for exclusive held-descriptor creation, fsync of file and parent directories, consumed-name retention after uncertainty, and post-exit independent installed-file hash/identity verification. Those are proposed obligations, not implemented behavior. The manifest also identifies parent mtime/ctime changes; exact ancillary filesystem and runtime effects remain unbounded.

## Findings that keep installation on hold

1. **No active executable or installer is selected.** The only pinned storage release disables its live route. The preflight has no `--apply` implementation, no payload write, no atomic installed-tree validation, and no failure journal. An installer must be reviewed against the eventual active successor and fresh host preimage. The first exclusive package-directory creation would consume this package name; an ambiguous partial state must not be overwritten or retried.
2. **The proposed two-entry account is not a full execution effect account.** A root Python invocation can read the interpreter, imports, shared objects, NSS files/services, and runtime metadata. `-B` prevents bytecode writes but does not bound all read-atime/cache/socket effects. The storage release calls `pwd`/`grp`; this host's `/etc/nsswitch.conf` routes passwd and group through `files systemd`, and the release reads `/etc/subuid`, `/etc/subgid`, `/proc`, and mountinfo. The observed unchanged atimes from one unprivileged plan run do not prove a future privileged invocation has no auxiliary effects. Freeze the interpreter/import invocation and either replace NSS with bounded held reads or include its effects in a separately reviewed transaction.
3. **The current preflight cannot establish final pathname custody.** Held nofollow ancestor descriptors and ACL checks help inspect `/usr/local/libexec`, but the check is point-in-time; it does not compare a future installed leaf back through a still-linked root-to-leaf tree after installer exit. The synthetic prefix option also does not pin every prefix ancestor. A future host effect needs fresh mount/ACL/alias/owner checks, attached-tree inode and nlink verification, and an independent WSL service-UID/post-effect oracle. None is supplied here.
4. **Host service custody is absent.** UID/GID 20001 is only proposed. This review saw no installed root-owned unit, exclusive cgroup/namespace/proc custody, protected Source8 authority, or actual G01/G02 qualification. Docker host-bind installation would add a separate daemon/image/mount/UID-map effect envelope and would not itself establish the WSL installed-executable claim.

No proposed host entry or protected input was written by this review. This verdict must not be used as authorization to run the disabled release as root, to flip its live flag, or to execute either proposed host write.
