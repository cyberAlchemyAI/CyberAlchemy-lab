# Mapping inventory and evidence

- [Product / Project workspace catalog](workspace-catalog.json): current source-pinned subject classification, proposed locations, imported references and explicit missing identities.
- [Workspace checker](check_workspaces.py): exact source/identity/admission-overlay checks, coverage and generated explanation.
- [Path regions](path-map.json): longest-prefix classification, ownership anchors, candidate homes and unresolved dispositions.
- [Source baseline](source-baseline.json): selected file SHA-256/length, source revision, collision assertions, missing references and external consumer link metadata.
- [Coverage](coverage.json): counts for the captured Git path selection by region/root, with missing tracked paths separated.
- [Inspector](check_mapping.py): repeatable read-only checks and explicit package-only capture.

```sh
# Inspect the saved map and compare selected evidence with current source.
python3 architecture/workspace-model-mapping/inventory/check_mapping.py --check

# After reviewing changes, refresh only this package's dated evidence snapshot.
python3 architecture/workspace-model-mapping/inventory/check_mapping.py --capture
```

Git selection is tracked paths plus non-ignored untracked files. Already tracked generated material remains included even if an ignore rule now matches it. Missing tracked files remain separately accounted for; their absence is pre-existing state, not deletion by this mapping. The mapping package excludes itself from path counts. Ignored dependencies/private state and Git internals are not scanned. Large saved execution trees are counted by path region without content ingestion.

Every selected path must match an explicit prefix; there is no catch-all rule. Mixed classifications deliberately defer per-file semantic selection. Exhaustive region coverage is not exhaustive ownership/admission certification or a ready-to-run move manifest.

Evidence comes from three completed read-only mapper passes: `structure_mapper` (ownership/layout), `capability_mapper` (reusable source/dependencies), and `verification_mapper` (tests, observations and upgrade mechanisms), followed by parent synthesis and package validation. These names identify this chat's mapper work, not cryptographic attestations. The existing governance map and historical receipts retain their separate scope.

The workspace catalog has a 7 November hosting revision and content audit; the 6 November catalog is retained separately. Run `python3 architecture/workspace-model-mapping/inventory/check_workspaces.py` independently of the older path/source snapshot. The new naming does not silently recapture that historical baseline or change the previous concrete model.

The [external content audit](external-comparison-20261107.json) records every selected file disposition. The historical catalog and checker snapshots are evidence, not active validation entrypoints.
