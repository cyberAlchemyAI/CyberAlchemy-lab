# Active WSL storage release candidate 0003

This is an **active but uninvoked candidate** for the exact current WSL host. It prepares only the root-owned Source8 storage tree. No host code or storage was installed or created by this candidate work. A distinct reviewer must inspect the frozen bytes and effect envelope before any administrator executes either route.

The code installer (`install_code.py`) has one fixed root-owned destination, verifies the two source payload SHA-256 values from held source descriptors, checks the exact interpreter, isolated import path and 108 pinned Python/ELF files before mutation, holds and rechecks the selected root-owned `/usr/local/libexec` ancestry, creates a private `0700` package directory and exactly two root-owned files (`release.py` `0500`, `runtime-pins.json` `0400`), fsyncs, and verifies the final name-linked tree. Its installed package cannot be reused or overwritten by this route. The installer does not create the review receipt.

After independent review and fresh WSL preflight, the narrowly scoped installer launch is the following fixed here-document. It reads the installer once from a held FD, checks the frozen digest, then passes exactly those bytes to the root interpreter through stdin. `sudo -n` requires an existing administrator authorization; the command has **not** been run. Do not execute a mutable checkout pathname as root.

```sh
/usr/bin/python3.14 -I -B -S - <<'PY'
import hashlib, os, subprocess
path = '/home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host/host-storage-release-candidate-0003/install_code.py'
fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NOATIME)
with os.fdopen(fd, 'rb') as stream:
    body = stream.read(32769)
if len(body) > 32768 or hashlib.sha256(body).hexdigest() != '3716b386377ed26baa142a32639c89fcdcb300d7fa85fcb1c11d4efcd07f3428':
    raise SystemExit('INSTALLER_HASH_REFUSED')
subprocess.run(['sudo', '-n', '/usr/bin/python3.14', '-I', '-B', '-S', '-',
                '--install-code-one-shot'], input=body, check=True)
PY
```

The storage release has a callable `--apply-reviewed-one-shot` route, but the checkout copy refuses because it is not at the fixed root-owned installed path. The installed route requires root IDs, `/usr/bin/python3.14 -I -B -S` with exact interpreter hash and import path, all frozen runtime-file hashes, a root-owned `0400` receipt whose SHA-256 is passed explicitly, and the pinned storage preimage. It checks final named top, storage and leaf inodes against held descriptors. The first exclusive top mkdir consumes the name; any partial or uncertain result must be retained for independent review, with no rollback or retry.

The receipt must be created after distinct review with `cal-host-storage-reviewed-receipt/v1`, verdict `PASS_FOR_ONE_SHOT_STORAGE_ONLY`, exact installed release/runtime hashes, target, current preimage hash and a syntactically valid reviewer identity. Missing, empty, non-string and malformed reviewer values refuse. This field does not authenticate independent origin; a distinct PASS decision and separately reviewed root-owned receipt installation are still required. The candidate does not create a service account or systemd unit and establishes no Source8 private authority or Root/slot qualification.

Read-only WSL inspections used `/usr/bin/python3.14 -I -B -S release.py --plan` and `install_code.py --plan`. `sh run-docker-test.sh --run` uses two disposable, no-host-bind containers: one exercises reviewer-field refusals, the receipt gate, internal storage transaction and UID 20001 denial on tmpfs; the other exercises installer runtime-pin mismatch refusal, code installation and replay on container tmpfs with container-specific pins. The Docker receipt/runtime pins are synthetic and do not certify WSL. All observed test containers exit and are removed.

The explicit storage record/file reads use `O_NOATIME`; Python startup/import and dynamic-loader reads can still affect access times before the runtime check. No NSS lookup occurs in the storage route. Sudo/PAM and receipt-install effects are separate from the three code entries and seven storage entries. [HOST_PREREQUISITES.md](HOST_PREREQUISITES.md) identifies the host work that remains before either WSL effect. See `write-manifest.json` for the exact effect and claim ceiling.
