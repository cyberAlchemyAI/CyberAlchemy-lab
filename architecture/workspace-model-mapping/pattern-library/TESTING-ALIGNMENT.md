# Testing and verification alignment

## This mapping task

Run from the Lab root:

```sh
python3 architecture/workspace-model-mapping/inventory/check_mapping.py --check
```

This checks package-relative Markdown targets and file anchors, path-rule identity/coverage, captured source digests and sizes, declared missing source references, collision assertions, external symlink metadata and the snapshot's count arithmetic. The mapping's own generated files are excluded from path coverage to avoid self-reference. It reads Git's path selection without following dependency trees or reading private ignored stores.

An inspected source or link that changes invalidates the relevant baseline assertion. Re-capture only after reviewing the new source cut; `--capture` writes this package's navigation evidence, not authority or runtime state.

No Craft build, runtime transaction, installation or full product test suite was executed for this map. [Existing Craft local qualification](../../../craft/work/outcomes/current-verification/lab-qualification.json) and historical runtime receipts are saved evidence with their own exact scope. The referenced broader Craft report was absent at capture; see the baseline's explicit missing references. Do not equate a README link with a passing test.

## Checks for a future migration

| Concern | Existing test owner / source | Required migration evidence |
| --- | --- | --- |
| Exact source/state continuity | [Runtime validation](../../../implementation/lab-runtime/v2/validate.py), [source repair](../../../implementation/lab-runtime/v2/SOURCE-PROFILE-REPAIR.md) | Before/after source tuples, unchanged historical packages, successor ancestry, changed-source refusal and stale-store behavior |
| Work/context reconstruction | [Work candidate](../../../implementation/lab-work/candidates/v1/README.md), [continuity](../../../implementation/lab-continuity/candidates/v1/README.md) | Preserved Work identity/outcomes, fresh-process replay and fresh context after session closure |
| Install/upgrade/rollback | [Installation tests](../../../product/lab/release-candidates/v1/interface/api-installation-release-v4/test_installation_release.py), [operations](../../../product/lab/release-candidates/v1/packaging/R02/OPERATIONS.md) | Exact preimage, isolated new generation, interrupted-stage reconciliation and retained-reader compatibility |
| Current Craft relocation | [Implementation guide](../../../craft/implementation/README.md), [broader test guide](../../../craft/implementation/verification/README.md) | Selected build/check cases and source-pin validation; full verify/provider qualification only when included in the chosen scope |
| Existing external consumers | Baseline's twelve Body War links, explicit launchers/manifests | Same resolved dependency behavior or reviewed successor bindings; no writes through shared reference links |
| Documentation/navigation | This inspector, existing inventory tooling | Valid links, no missing selected current targets, refreshed selectors and explicit dated projections |

Existing commands can write reports or exercise disposable branches. Select exact checks for the eventual change; do not overwrite historical receipts merely to document the mapping.
