# Packages, installation and rollback

Select exact public bytes and protect host dependencies before changing an installation.

Draft prepared on 2026-10-14. Integration and final T21 qualification remain pending.

## Choose the package boundary

A source package, a public export, an installed dependency/runtime and an activated consumer are different artifacts. The [captured export](../../../../../../evidence/product/lab/release-candidates/v1/interface/api-integration-v16/package_export.py) and [import](../../../../../../evidence/product/lab/release-candidates/v1/interface/api-integration-v16/package_import.py) implementations bind selected records/files and prepare bounded plans; they do not grant access to every source file or admit imported candidates.

Private credentials, policy/proof bodies, Session notes and protected host dependencies are not ordinary export material. Keep selected public source bytes, manifest/digest closure, original refs and intended scope explicit.

## Check exact bytes and current effects

Before export/import, resolve the declared record revisions, source/ontology cuts, permitted targets, request/envelope keys, byte bounds and current channel. A valid package envelope without its exact payload/hash/reference closure is insufficient.

Materialization and installation must compare actual preimages and refuse unsafe paths, foreign files and changed selectors. Preserve the original signed/native source trail separately from generated files. A changed publisher destination or dependency family requires a reviewed successor selection; do not rename a stale manifest to make it current.

## Separate install from activate

| Stage | Result and limit |
| --- | --- |
| Dependency package selection | Exact executable/library/wheel/environment input pins |
| Installation | Files exist in the selected owned layout and match expected modes/bytes |
| Verification/replay | Selected code can check the declared public/current inputs |
| Release preparation | Candidate package and readiness obligations recorded |
| Activation/publication | Separate authority and actual operational outcome |

The [R02 installer](../../../../../../evidence/product/lab/release-candidates/v1/interface/api-integration-v16/r02_installer.py) and [release-readiness code](../../../../../../evidence/product/lab/release-candidates/v1/interface/api-integration-v16/release_readiness.py) own bounded development paths. The existing installation0004 supports this preparation's selected environment; its prior tests do not replace a fresh setup/upgrade/rollback witness for the final runtime.

## Rollback and interruption

Keep the prior installation and exact rollback dependencies until the new version has its own readiness and end-to-end acceptance. Inspect uncertainty after interruption before cleanup. Remove only retained-approved owned temporary files; foreign/unknown residue is preserved.

For local state, cold replay verifies original commits and current source bytes. For derived files, verify their source cut, manifest, selected attachment and complete receipt rather than trusting a directory name. The [publisher successor](../../../../../../evidence/docs/plans/0011-lab-runtime-completion/runs/0001-execution/T14/mixed-target-publisher-0002/README.md) illustrates ordinary filesystem no-replace and receipt boundaries, with native mixed-target integration still separate.

## Current blocker and next review

Changed API17 remains ineligible until new family/selector/software/source/profile closure is accepted. Its old metadata cannot qualify modified code. Family4's inherited mutable preparation inputs exposed a cycle; the [retained diagnosis](../../../../../../evidence/docs/plans/0011-lab-runtime-completion/runs/0001-execution/T02/family4-dependency-cycle-review-0001.json) requires a distinct successor, not suppressed guards.

A later installation tutorial must select that final version, execute setup/recovery/rollback in fresh owned paths and record original effects/cleanup. None of those actions is run by this documentation generator. Read [maintenance](../development-and-maintenance.md) for the full integration sequence.

## Selected public evidence

- [product/lab/release-candidates/v1/interface/api-integration-v16/r02_installer.py](../../../../../../evidence/product/lab/release-candidates/v1/interface/api-integration-v16/r02_installer.py). SHA-256 69ee671ae731a9f0e1433027610369fadd2a3984d1f89ae9b85d40464b914a2b; 10775 bytes. Public technical snapshot; no authority transfer.

- [product/lab/release-candidates/v1/interface/api-integration-v16/package_export.py](../../../../../../evidence/product/lab/release-candidates/v1/interface/api-integration-v16/package_export.py). SHA-256 3e5c898b15c94674b1d30f3f12ff21f803ea569b329e19046142004f2366b8e0; 16105 bytes. Public technical snapshot; no authority transfer.

- [product/lab/release-candidates/v1/interface/api-integration-v16/package_import.py](../../../../../../evidence/product/lab/release-candidates/v1/interface/api-integration-v16/package_import.py). SHA-256 b3f42ae5707317d4aff6786e41b6734561330be3c82dc41c31ba03e30cb25969; 17434 bytes. Public technical snapshot; no authority transfer.

- [product/lab/release-candidates/v1/interface/api-integration-v16/release_readiness.py](../../../../../../evidence/product/lab/release-candidates/v1/interface/api-integration-v16/release_readiness.py). SHA-256 e4245ff47685a370e6f5572b3daa283328934f2a503e90eea6f3167a8f16697f; 25934 bytes. Public technical snapshot; no authority transfer.

- [docs/plans/0011-lab-runtime-completion/runs/0001-execution/T02/family4-dependency-cycle-review-0001.json](../../../../../../evidence/docs/plans/0011-lab-runtime-completion/runs/0001-execution/T02/family4-dependency-cycle-review-0001.json). SHA-256 b9b282170bb00e2c0a105c16add8596444e69b9a84a51fefb80b36144269df14; 6329 bytes. Public technical snapshot; no authority transfer.

- [docs/plans/0011-lab-runtime-completion/runs/0001-execution/T14/mixed-target-publisher-0002/README.md](../../../../../../evidence/docs/plans/0011-lab-runtime-completion/runs/0001-execution/T14/mixed-target-publisher-0002/README.md). SHA-256 2f400b1e7e2f6aae62a77cb6da8225c8d607207c4b76bd22a99638f49665cc93; 3585 bytes. Public technical snapshot; no authority transfer.
