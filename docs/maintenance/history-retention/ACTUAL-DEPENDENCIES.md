# Executable dependency cleanup - 2026-11-08

The previous 71,018-file index retained historical release trees because old closure manifests listed them. This pass does not use those listings as dependency roots.

Removed 17,084 tracked files: 14,004 superseded release files with no retained current code import, 2,310 generated formalization run files, and 770 earlier assurance attempt files. A verified local archive retains the retired bytes without keeping them in Git. Current source packages and functional fixtures remain intact; no shared runtime installation was copied.

Retention uses current executable entry points, observed read/execute activity, coherent source packages, and static code imports. Code dependencies can retain an older implementation; a manifest row alone cannot. The audit preserves latest experimental source without describing unfinished releases as usable.

## Evidence

ACTUAL-DEPENDENCIES.json.gz records the retired paths, retained release groups, static import roots, observed input hashes, check outputs, archive hash, and limitations. The large raw syscall traces remain ignored under .local/actual-dependencies-20261108.

Both native runtime snapshots retain their exact original digests. Define's 66 source API tests, seven connector workflow tests, connector integrity check, Craft's source build and ten integration checks, both Ontology crates' 31 tests, workspace mapping, and isolated website render pass. The website selects 1,241 resources.

The connector suite started before removal and finished successfully during this cleanup. The source API tests use the existing synthetic definition fixture; this does not change native authority or qualify an installed wheel.

Package staging already refused a migrated symlink parent. The integrated release prototype also had missing projected code/schema inputs before removal. Those failures are retained as negative evidence, not promoted to passing release qualification. Observed file IO is not exhaustive branch coverage.

Run python3 docs/maintenance/history-retention/check_actual_dependencies.py --verify-local-archive to check the current retirement and observed source hashes. The older REQUIRED-DEPENDENCIES.json.gz and CHECKS.json are historical evidence of the superseded conservative pass.

Counts below are refreshed from the Git index in RESULT.json and CURRENT-MAP.json after staging these evidence files.
