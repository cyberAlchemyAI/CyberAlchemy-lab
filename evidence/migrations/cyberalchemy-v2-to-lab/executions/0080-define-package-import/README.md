# Define package source import

Captured on **2026-10-11** from the clean selected trees of `cyberAlchemy-v2`. This execution imports **1,023 exact files** into [Define's source snapshot](../../../../../define/source/cyberAlchemy-v2/): 260 package files and 763 CLI implementation files. The source commit and individual file digests are recorded in [manifest.json](manifest.json).

Start with the [Lab Define entry point](../../../../../define/README.md) and [integration report](../../../../../define/INTEGRATION.md).

## Authorization and standing

The user instructed: “now we need to go to define package in .../cyberalchmey-v2 and import it to the lab”. [Import authorization](authorization.json) records that exact scope. This is owner-directed candidate source import, not canonical definition admission, authority transfer, source retirement, publication or runtime adoption. Source visibility remains private and `authority_effect` remains `none`.

The source router selected CA2-ROUTE-DEFINE because of the package name, then gated implementation effects. Its request, route, context, read-effect and continuation results are retained under `routing/`. This is a routing mismatch for importing existing bytes. No upstream mutation was performed under that route. The destination import follows the explicit user instruction and does not claim a successful CA2-ROUTE-IMPLEMENT decision.

## Inventory and evidence

| Classification | Files |
| --- | ---: |
| Parent declared material | 25 |
| Business child package | 22 |
| System child package | 101 |
| Capability package | 30 |
| Source review/intake evidence | 74 |
| Source receipt/collaboration evidence | 8 |
| Candidate CLI source | 763 |

- [manifest.json](manifest.json): selected roots, source commit, standing, file classifications and exact bytes.
- [import-integrity.json](import-integrity.json): all copied bytes and the closed destination inventory match.
- [predecessor-comparison.json](predecessor-comparison.json): 34 overlapping Define files changed; 114 match; 112 were not in 0064; three predecessor paths are absent from the current selection.
- [dependency-standing.json](dependency-standing.json): observed fingerprint standing without changing any source pins.
- [external-code-imports.json](external-code-imports.json): literal relative code dependencies outside the imported trees, with an explicit non-exhaustive scope.

Historical receipts and tests are imported source evidence. No source validation or behavioral test suite was run. The import-integrity PASS is a byte and inventory check, not a validation of the capability's meaning, behavioral conformance or operational readiness.

## Reproduce and inspect

From the Lab root, inspect the committed snapshot without the source checkout:

```bash
python3 tooling/importers/import_define_package.py --inspect
```

To create a fresh source import in an empty review destination that also contains the preserved 0064 predecessor archive:

```bash
python3 tooling/importers/import_define_package.py \
  --source ../cyberAlchemy-v2 --destination /path/to/review-lab \
  --captured-on 2026-10-11
```

The importer refuses overwrite, untracked/ignored or missing source files, symlinks, missing parent material and source-byte changes during copying. Re-running against a later source checkout produces a different snapshot; the recorded source commit and per-file hashes identify this import.

## Open questions

Dependency version selection, Lab contract mapping, ownership decisions and runtime adoption remain in the [integration queue](../../../../../define/INTEGRATION.md#next-integration-steps). Earlier migrations and the admitted Lab runtime remain unchanged.
