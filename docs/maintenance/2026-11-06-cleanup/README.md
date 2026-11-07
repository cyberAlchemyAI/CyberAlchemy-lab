# Lab cleanup and commit review — 6 November 2026

Removed **83,439 files from the initial inventory (7.51 GB of content)**,
plus temporary validation outputs. All **874 retained current/passing evidence
records** still match their original SHA-256. At that review checkpoint no commit or push had been created,
and the Git index was empty. The user subsequently authorized local commits
of the validated component and cleanup scope; blocked work stays uncommitted.

The recommended component changes total about **5.4 MB**, plus this audit:
small runtime v2 and checkpoint records, standalone Define, Define v2, and
website source. The website's workspace and isolated-export archives were
byte-identical. Its three migration snapshots are required source inputs.

Current Craft is blocked by stale generated U0 pins. The integrated native
installer is blocked by changed retained-helper hashes. Default Define v1
requires its 160 ignored compiled providers to be rebuilt; its legacy compiler
configuration points at an absent toolchain config. These routes are outside
the validated commit scope. No runtime pin was refreshed to suppress a failure.

- [Exact recommended scope](safe-commit-paths.json)
- [Checks and blockers](commit-readiness.json)
- [Deletion summary](cleanup-summary.json)
- [Retention exceptions](retention-exceptions.json)
- Full deletion and static-reference retention manifests are the adjacent
  compressed JSONL files. Pre-existing deletions are recorded separately.

This cleanup implements the repository owner's request to remove superseded
work evidence and reproducible build assets, then assess commit readiness.
It creates no commit, release, admission, or deployment.

## Retention

- Keep the evidence paths selected by the current local engineering ledger.
- Keep the latest work in each numbered/versioned family and its last observed
  passing summaries when a later attempt has not established success.
- Keep older source and original inputs still selected by current code or
  exact-byte manifests. Retention does not repin or approve those inputs.
- Keep unique source that has no counterpart in the proposed successor.
- Preserve authority/admission history, private stores, credential/state files,
  nested Git repositories, and shared symlink targets.
- Delete verified compiler caches, distributions with retained build recipes,
  generated repository indexes, and unselected superseded copies.
- Record removed paths and byte counts; retained current evidence must match
  its pre-cleanup SHA-256.

The deletion manifest records file content bytes, not host VHDX reclamation.
Reproducible cache entries have a reason and byte count. Pruned evidence also
has its SHA-256 and the selected successor family.

## Rebuilding local navigation

Run the inventory builders from repository root:

    python3 tooling/inventory/build_inventory.py
    python3 tooling/inventory/build_content_map.py

Generated navigation is ignored by Git. Compiler/build directories are also
local outputs. Shared runtimes and toolchains remain external dependencies.

## Validation boundaries

See commit-readiness.json for actual commands, results and limitations.
A source export or installed-package test does not qualify the complete
integrated native product. Existing mismatched pins must not be changed merely
to make a check pass.

The installed standalone Define transport suite requires an installed package
in an isolated environment; running it directly against the source directory
is not the supported test setup.

The original 36-task acceptance ledger and the local engineering ledger keep
their existing statuses. Removing old payloads does not claim that open work,
owner acceptance, live-host qualification or release has completed.
## Authorized local commit scope

The user authorized the scoped commits after the review. Exact proposed-tree
checks are in [commit-validation.json](commit-validation.json). Two hash-pinned
checkpoint input JSON files were added to complete the runtime closure; five
unrelated user-journey candidate files remain uncommitted. Existing Markdown
hard breaks and a hash-bound archival blank line are preserved.
