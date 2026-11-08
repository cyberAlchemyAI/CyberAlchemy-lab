# Run the integrated local Lab

This is the operator and developer path for the integrated local fixture runtime. Run from the repository root with the selected build inputs present on the prepared WSL host. The host needs Python 3, Docker Engine for the separate container check, at least 65,536 available file descriptors as a hard process limit, and the owned native build ABI at `~/.local/share/cyberalchemy-lab/native-install/t22-0001`. The native ABI contains Python 3.14.4, jsonschema 4.23.0 and cryptography 46.0.5. Keep the private build directory outside Git and provide several GB of free space.

## Build and install

```bash
LAB_RUN_ROOT="$HOME/.local/share/cyberalchemy-lab/lab-build-$(date -u +%Y%m%dT%H%M%SZ)"
python3 -B implementation/lab-runtime/local-host/t03-long-local-fixture-0001/renew_and_install_0002.py \
  --run-root "$LAB_RUN_ROOT"
```

The command creates a new signed fixture family with the real clock, runs Source and two cold Source replays, Reader, Mapper and Context construction, seals the public package, then installs its runtime and performs a fresh API cold read. It never replaces an existing installation. `RESULT.json` at the run root reports exact archive, package and installation identities. If a phase fails, `FAILED-RETAINED.json` and the original phase logs stay in that run directory; inspect those before starting a new run. The current fixture's `source_expires_at` in the installed API observation defines its actual operating period. A new run creates a new period; it does not extend an old lease.

## Use the installed API

```bash
LAB_REPO="$LAB_RUN_ROOT/installation/runtime/repository"
LAB_PY="$LAB_REPO/implementation/lab-runtime/local-host/t25-native-launcher-0001/selected-python"
LAB_OPERATOR="$LAB_REPO/implementation/lab-runtime/local-host/t21-installed-operator-0001/command.py"
"$LAB_PY" -B "$LAB_OPERATOR" status
"$LAB_PY" -B "$LAB_OPERATOR" catalog
"$LAB_PY" -B "$LAB_OPERATOR" inspect --artifact product:cyberalchemy-lab
"$LAB_PY" -B "$LAB_OPERATOR" workflow
```

`status`, `catalog` and `inspect` use the current signed Source and an authenticated temporary Reader. `workflow` creates an isolated private fixture, invokes the selected common dispatcher, consumes real typed outputs, tests an exact read-only retry, and reports its private output directory. The output includes the actual reply, original Vault archive and typed artifact files. Inspect `RESULT.json` in that directory before relying on a result; a failed attempt retains `FAILED-RETAINED.json` and the owned fixture for diagnosis. These commands use the installed launcher so the runtime verifies its own native and package selection.

## Repeat the portable Docker install check

From the same checkout, after a successful build:

```bash
LAB_ARCHIVE_SHA=$(python3 -B -c 'import json,sys; print(json.load(open(sys.argv[1]))["artifact"]["sha256"])' "$LAB_RUN_ROOT/RESULT.json")
LAB_PACKAGE_SHA=$(sha256sum "$LAB_RUN_ROOT/view/PACKAGE-MANIFEST.json" | cut -d' ' -f1)
LAB_DOCKER_OUT="$HOME/.local/share/cyberalchemy-lab/portable-runtime-installations/check-$(date -u +%Y%m%dT%H%M%SZ)"
python3 -B implementation/lab-runtime/local-host/t25-scratch-docker-0001/run_complete_qualification.py \
  --view "$LAB_RUN_ROOT/view" --archive "$LAB_RUN_ROOT/lab-runtime.tar.gz" \
  --archive-sha256 "$LAB_ARCHIVE_SHA" --package-sha256 "$LAB_PACKAGE_SHA" \
  --output "$LAB_DOCKER_OUT" --timeout 7200
```

The Docker test uses `FROM scratch`, a fresh private native installation, UID 20001, no network, a read-only root, no capabilities and a 65,536 descriptor limit. It checks the cold API, exact idle uninstall and byte-for-byte restore, then runs the selected 22 installation-release regression methods in a separate container. A passing `RESULT.json` records those outcomes and removal of this run's unique container, image, volume and build context. A failed run keeps only its named resources and logs for diagnosis; use `OWNED-RESOURCES.json` to identify them. Never substitute a global Docker prune for this scoped cleanup.

## Verification boundaries

The public archive and package digest identify the executable selection. Source and profile digests can differ between independent private installations because each constructs its own local fixture from that archive. Cold installation, the 345 maintained methods, the 34 API operations, process interruption, Session learning, and privacy checks have separate result files. A cold API result alone reports `full345_qualified: false`. The local fixture has no protected Source8 credentials or canonical admission, and an operator `workflow` result explicitly reports `work_completed: false` until real work and an authorized decision establish otherwise.

For the smaller disposable demonstration, `bash implementation/lab-runtime/local-host/run-local-product.sh` remains available; its scope is described in [LOCAL-PRODUCT.md](LOCAL-PRODUCT.md).
