# Remaining tracked files: 8 November 2026

The previous cleanup removed generated payloads and already-missing paths. It retained entire candidate/history scopes rather than selecting the minimum current source and evidence set in each scope. That is why 82,330 paths remain. They have not all been proven necessary.

Counts below come from the current Git index. Legacy index paths such as craft/, define/, website/ and docs/plans/definition-formal-assurance/ address source physically migrated into Product workspaces or root work/. A counted index path does not mean a second physical Product exists.

| Scope | Tracked files | Extra occurrences of identical Git blobs within scope | Next retention action |
| --- | ---: | ---: | --- |
| lab-release-candidates | 24811 | 15906 | Select the currently usable portable package plus construction/test closure; retire obsolete API/version families together with their validation inventories. |
| definition-formal-assurance | 13168 | 4628 | Keep source snapshot, latest usable per-definition manifest/coverage and their exact dependencies; archive prior attempts, prepared episodes and redundant command transcripts. |
| craft-formalization | 7624 | 2930 | Keep latest checker and imported ancestor source; remove completed generated run stores after retaining the final result for each distinct case. |
| hammer-research | 6351 | 959 | Keep current consolidated research, latest usable case result and required raw evidence; retire intermediate receipt versions, abandoned preparation and redundant replay/event records. |
| runtime-completion-evidence | 4768 | 1327 | Keep current handoff/state and accepted-evidence dependencies; archive superseded maps and unselected inactive preparations. |
| one-shot-runtime-history | 4349 | 298 | Retire old construction runs after replacing legacy full-history source inventories with selected current runtime closure. |
| migration-evidence | 3351 | 113 | Keep current imported sources selected by the workspace map and native histories; archive obsolete preparation/debug outputs. |
| workflow-candidates | 2176 | 1068 | Keep imported source/schema/fixtures; trim unselected historical execution and receipt generations. |
| ontology-candidates | 1864 | 1229 | Keep current source and selected migrations; trim superseded query/coherence/review outputs. |
| define-source-and-work | 1858 | 329 | Keep current standalone release and active development source; archive superseded preview and trial package outputs. |
| website-source-and-review | 1297 | 142 | Keep current source/content and latest review per scope; archive obsolete promotions and duplicated review payloads. |
| canonical-authority | 3203 | 346 | Retain canonical identities and exact history required by current state; numeric age alone does not authorize deletion. |
| other-craft-source | 2412 | 12 | Keep current code/model contracts and source-bound fixtures; evaluate old research separately from Product source. |
| other-shared-operations | 1200 | 168 | Keep selected operation implementations and required versioned dependencies; consolidate obsolete capability versions through their owners. |
| other-plans-and-proposals | 2534 | 13 | Keep current docs/plans and source-bound decisions; prune completed obsolete proposals and superseded projection assets. |
| lab-product-metadata | 156 | 0 | Keep selected Product identity, package bindings and current metadata. |
| navigation-tests-and-other | 1208 | 21 | Keep current navigation, regression tests and tools; retire only superseded audit snapshots. |

Total: **82,330 tracked paths**. 29489 occurrences repeat a Git blob already present within their category. These are index-content duplicates; modified working-tree bytes can differ. Equal content does not by itself make a path removable: imports, selected manifests and proof inventories may require that path.

## Next candidates, with exact counts

These buckets identify where to inspect next. They are not a deletion allowlist and do not promise every contained file is obsolete. Rooting in latest usable results and checking their references is still required.

| Candidate group | Paths to review | Keep/remove boundary |
| --- | ---: | --- |
| formal-assurance-command-streams | 4527 | Keep compact final results and every stream still bound by the latest selected manifest; archive unselected prior command output. |
| formal-assurance-old-preparation | 2201 | Preserve latest usable per-definition/unit source and imported fixture dependencies; archive superseded construction attempts. |
| checker-generated-run-stores | 3817 | Keep selected current proof result and inputs; archive finished unselected generated job/store directories, retaining distinct failures. |
| research-lifecycle-and-replay | 1447 | Keep last usable result for each experiment and its evidence dependencies; archive intermediate event/replay/preparation material. |
| research-raw-calls | 577 | Raw native calls may be required to substantiate current research. Retire only superseded/unreferenced calls, never every raw result. |

Candidate union: **12569 files**, with overlapping paths assigned once. The [compressed per-file list](NEXT-REVIEW-CANDIDATES.json.gz) records the review group. Ten older files also occur in strictly matched numbered receipt/map families; their [supersession list](SUPERSESSION-CANDIDATES.json) still needs result-standing and reference checks.

## Why the largest cut needs source selection

Lab release candidates contain 24,811 files, but only 8,905 distinct Git blobs. The 15,906 repeated occurrences are the largest consolidation opportunity. There are many copied API/package generations, along with helper modules, fixtures, guards, dependency installs and their historical inventories.

For example, api-v96/source-manifest.json declares 20,590 source rows; api-integration-v30 declares 32,011. The later portable integration-v73 manifest declares 228 rows. Integration-v74, v75 and v76 do not have a frozen source-manifest.json in their source directories: the portable installer materializes selected per-install metadata. The current installation checkpoint identifies API75 as selected and still distinguishes cold fixture success from incomplete full qualification. Highest numeric version alone is not the latest usable package.

The correct retirement boundary is the selected current public package, its generation/build inputs, imported helper modules, current tests, exact native source/authority dependencies and latest usable evidence. Old validation-family inventories can be retired with their old code; they should not force retention forever merely because they list the past. Conversely, deleting their pinned inputs while continuing to claim their validation would be false. No canonical admission or source pin was changed by this map.

## Order of the next reduction

1. Formal assurance: select the current snapshot and final per-definition/unit result; archive obsolete command streams, prepared episodes and earlier attempts. Preserve definitions/ and units/ inputs actually imported by current assurance code.
2. Checker/research: keep current source and one last usable result for each distinct case; archive completed unselected job stores and superseded lifecycle records. Preserve negative outcomes and raw calls supporting current conclusions.
3. Release candidates: extract and verify the actual maintained package/build/test closure, then retire whole legacy API and validation generations. This is the largest source-level cut, not another browser-cache cleanup.
4. Workflow/Ontology and the old one-shot plan: retire their superseded receipts/construction history after resolving the same legacy source inventories.

## Evidence

- [Complete category/count/decision map](REMAINING-MAP.json)
- [Every remaining index path and Git blob](remaining-files-20261108.json.gz)
- [Exact next-review candidates](NEXT-REVIEW-CANDIDATES.json.gz)
- [Same-scope numbered supersession candidates](SUPERSESSION-CANDIDATES.json)

This turn produced a remaining-file map and bounded removal candidates. It did not remove additional files or claim that unreviewed candidates are safe deletions. The earlier 45,079 staged removals and existing user work are preserved.
