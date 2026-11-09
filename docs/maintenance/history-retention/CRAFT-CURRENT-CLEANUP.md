# Craft current-version cleanup

Completed: 2026-11-08T17:18:16.235754+00:00

Retained Core **1.3.0** and AlchLang **0.7.0-candidate.0**, all **5,864** current implementation files unchanged, current functional fixtures, shared dependencies, current semantic/authority records, and useful consolidated evidence for each tested scope.

## Removal

- **6,167 tracked entries removed:** 6,164 entries in superseded source/history/prototype trees, plus three obsolete aliases.
- **6,102 untracked staging files** and **943 untracked historical run files** removed.
- Old implementation, theorem-checker v1-v5, standalone SFOL capability, legacy research/discovery/configuration, old Product snapshot and first-capability prototype removed.
- Five compatibility aliases now resolve to current areas. The two-file pinned Project identity package remains because the selected shared runtime reads it; it is not an older compiler or runtime installation.
- Define's directly imported semantic-contract vendor files remain required dependencies.
- The compressed cleanup manifest records paths and hashes only, with no old source contents or runtime archive.

## Verification

| Check | Result |
|---|---|
| Full current build | Passed after exact shared toolchain restoration |
| Relocation and native Ontology | 10/10 passed |
| Fresh offline unpacked package installation; finite binding tests | 8/8 passed |
| EVF kernel | 8/8 passed |
| Body War reference | 33 Node + 16 Python tests; validators passed |
| Define API | 66/66 passed |
| Workspace model | Seven profiles/homes, one shared runtime, zero copies |
| Native runtime v1/v2 integrity | Passed |
| Website render | 1,241 resources |
| TDE | 381 passed, 77 failed, 17 pending; identical failure titles to before cleanup |

The initial build and EVF check exposed an already-missing shared toolchain. All 39 package archives were verified against the existing lock; the three unavailable apt versions were recovered from Ubuntu Launchpad. The exact user-owned shared installation was restored without changing upstream source, lock versions, or installing a runtime in any workspace. C, C++, Rust and Cargo/C static-archive compile/link/run witnesses passed. The affected build and EVF checks were rerun successfully. Temporary package-install trees and toolchain download archives were removed after use.

Original proof files retain their original scope and timestamps. Current post-cleanup evidence is `craft/work/outcomes/current-verification/cleanup-verification.json`; the evidence index selects it as latest local verification. Full connected/portfolio matrices were not rerun. The pre-existing TDE failures remain failures.

## Tracked count

**67,947 → 61,783 tracked entries**, including three new compact cleanup/evidence records. Net reduction: **6,164**. Current Craft home: **6,314** tracked entries after adding the new verification record.

Changes are staged locally; this cleanup creates no commit or push. Existing migration changes and unrelated untracked work were preserved.
