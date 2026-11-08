# API34/T06 live invocation envelope

This command sequence is prepared but unexecuted. Use it only after the T02 Session run releases its CPU/lease-sensitive slot. Run from `/home/vlad_/projects/CyberAlchemy-lab`; it creates a fresh protected `/tmp` root and a separate `/tmp` lock. It does not reuse the failed API33 root or write to API33 seventh, Source8, or `authority/`.

```bash
set -euo pipefail
cal_t06_producer=docs/plans/0011-lab-runtime-completion/runs/0001-execution/T06/branch-fixtures-current-api34-0001/revision-0001
cal_t06_sdk=product/lab/release-candidates/v1/interface/composite-operator-v1-current-api34-0001/revision-0001
cal_t06_lock=/tmp/cal-T06-api34-lease-sensitive-runtime.lock
cal_t06_selection_sha=62b9ef33ee73d29b4bb5c8182f892238baac4cad6ca6309c4fa024637cd17504
cal_t06_source_sha=4a47f51f9b93e7a51ed3fe4b59c340ac0c8f0dabc19eb851392dbd64b608b9bd
cal_t06_profile_sha=371e305e053cfcb88aa318149b8c47298af38f2d567599c6d935808a1be7d835
cal_t06_sdk_sha=dcdce5fb77666b19cae377e0decbdbe27b848d970c81b817c8dccb62c4eee413
cal_t06_provision_sha=81920701206b6e8556b973c975c0c6dd00fb83c2f21a3bea42b472d834cb117d
test "$(sha256sum "$cal_t06_producer/driver-selection.json" | cut -d' ' -f1)" = "$cal_t06_selection_sha"
test "$(sha256sum product/lab/release-candidates/v1/interface/api-integration-v34-current-t06-0001/source-manifest.json | cut -d' ' -f1)" = "$cal_t06_source_sha"
test "$(sha256sum product/lab/release-candidates/v1/interface/api-integration-v34-current-t06-0001/contract-profile.json | cut -d' ' -f1)" = "$cal_t06_profile_sha"
test "$(sha256sum "$cal_t06_sdk/source-manifest.json" | cut -d' ' -f1)" = "$cal_t06_sdk_sha"
test "$(sha256sum docs/plans/0011-lab-runtime-completion/runs/0001-execution/T34/task-session-result-v4.json | cut -d' ' -f1)" = "$cal_t06_provision_sha"
cal_t06_private_root=$(python3 -B "$cal_t06_producer/prepare_branches.py" stage-keys --selection "$cal_t06_producer/driver-selection.json" --selection-sha256 "$cal_t06_selection_sha")
python3 -B "$cal_t06_producer/prepare_branches.py" prepare --selection "$cal_t06_producer/driver-selection.json" --selection-sha256 "$cal_t06_selection_sha" --root "$cal_t06_private_root" --source-sha256 "$cal_t06_source_sha" --profile-sha256 "$cal_t06_profile_sha" --lease-lock "$cal_t06_lock" 2>"$cal_t06_private_root/prepare-stderr.log"
cal_t06_private_selection_sha=$(sha256sum "$cal_t06_private_root/private-branch-selection.json" | cut -d' ' -f1)
python3 -B "$cal_t06_producer/drive_operator.py" --branch-selection "$cal_t06_private_root/private-branch-selection.json" --branch-selection-sha256 "$cal_t06_private_selection_sha" --sdk-directory "$PWD/$cal_t06_sdk" --sdk-source-sha256 "$cal_t06_sdk_sha" --provisioning-path docs/plans/0011-lab-runtime-completion/runs/0001-execution/T34/task-session-result-v4.json --provisioning-sha256 "$cal_t06_provision_sha" --lease-lock "$cal_t06_lock" 2>"$cal_t06_private_root/drive-stderr.log"
```

The final stdout is a public bounded startup result; stderr and all private selectors remain under the owned `/tmp` root. On failure, retain the root for diagnosis and use a fresh root on retry. A PASS requires a fresh-lease request, three branch challenges, common 34-operation ready frame, owned shutdown, and child exit 0. This executes zero dispatch operations and establishes no admitted authority or whole API qualification.
