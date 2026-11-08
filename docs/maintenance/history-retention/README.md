# Current source and evidence retention

Cleanup applied and verified on 8 November 2026.

Tracked files: **82330 -> 71018** in this pass. Total reduction from 127,409: **56391 paths (44.26%)**.

This pass removed 11312 files, including 3873 obsolete release-candidate files. Current source, selected package inputs, current task capsules, referenced inputs and compact distinct-case results remain. Retained older source/data is required by existing package construction or current results; it was not promoted to a new qualification.

## Remaining tracked files

| Scope | Files |
| --- | ---: |
| Other Product/shared source, docs, imports, tests and tools | 17381 |
| Canonical authority and native histories | 3203 |
| Craft checker source, fixtures and retained results | 6866 |
| Selected earlier runtime dependencies | 1808 |
| Current runtime plan and retained evidence | 4040 |
| Formal assurance source and bound results | 12033 |
| Research source and retained evidence | 4749 |
| Lab release source and selected predecessor/package inputs | 20938 |

## Preservation and checks

All removed working-tree bytes were archived and SHA-256 verified before removal. Archives are ignored local recovery artifacts, not runtime installations and not tracked source. Existing staged removals are preserved, and all unrelated index entries retain their original mode/object/stage. No commit or push was made.

Retained package inputs were checked for unexpected changes; .gitignore is the explicitly recorded policy update. Ten current checks pass, including both Lab runtime verifiers, workspace catalog, Define connector/standalone routes, Craft application and Ontology-reader checks, Website tests, and both Ontology Rust packages. Runtime verifier outputs match pre-cleanup snapshots byte for byte. These checks do not establish full integrated runtime qualification.

The integrated package-view construction already failed before this cleanup on a missing API75 schema. Its declared dependency set was retained; no new package-builder success or cold installation is claimed. See the local baseline in .local/history-cleanup-20261108-apply/package-view-baseline.json.

## Policy

Keep the latest usable source/result for each distinct scope and its exact required inputs. Preserve distinct negative findings. A newer unfinished candidate cannot replace the last usable source. Archive superseded trial data and candidate generations locally; future generated run stores and retired source generations are ignored. Do not delete canonical/native event history by age.

The dated REMAINING-MAP.md describes the pre-cleanup 82,330-file inventory. CURRENT-MAP.json and RESULT.json describe the applied result.

- [Final result](RESULT.json)
- [Current tracked map](CURRENT-MAP.json)
- [Current checks](CHECKS.json)
- [Exact combined removal inventory](selection.json.gz)
- [Required dependency/reference map](REQUIRED-DEPENDENCIES.json.gz)

Local archives:
- .local/history-cleanup-20261107/historical-payloads.tar.gz; SHA-256 0ac21ece50b7106fb467f7e8e0c403cdad27e46e217b31d630ac6fccd8bf99e4
- .local/history-cleanup-20261108-apply/historical-payloads.tar.gz; SHA-256 ec05648b403b7b0edc051fc414defd69a19f4e4a804054847c345a1e0c714089

Repeat the complete retention audit with: python3 -B docs/maintenance/history-retention/check_retention.py --verify-local-archive --verify-required-inputs
