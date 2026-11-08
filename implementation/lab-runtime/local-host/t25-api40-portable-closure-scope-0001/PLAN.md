# API40 portable closure: bounded T25 scoping design

The current [API40 contract profile](../../../../product/lab/release-candidates/v1/interface/api-integration-v40-current-t06-0001/contract-profile.json) is SHA-256 `cbfd53a80f41a2ffd7ac28b88fa9e19a232ad291c8cb3791a302a4e8349c7614`. A metadata-only scan of its `files` rows on this WSL host found **33,424 distinct paths, all currently regular files, totaling 3,383,118,291 bytes**. This is a host observation, not an immutable copied closure or a determination that each file must be shipped. The row distribution is:

| Path group | Rows | Current bytes |
| --- | ---: | ---: |
| `product/` | 22,352 | 2,293,007,767 |
| `docs/` | 4,882 | 591,402,534 |
| `implementation/` | 4,494 | 370,284,765 |
| Absolute host paths | 857 | 100,870,215 |
| `authority/` | 753 | 5,739,380 |
| Other relative paths | 86 | 21,813,630 |

The 857 absolute bindings divide into 709 `/usr` paths, 65 Cargo-cache paths, 69 paths under other projects/repositories, and 14 other host paths. The existing T25 archive selects 681 original public files plus 12 API40 additions. Compared by exact path **and SHA-256**, all 681 originals and only 3 of those 12 API40 additions occur among the profile's 33,424 rows: **684 matching selected profile rows**. The other 787 fixture additions support the local Docker product and have a different archive namespace. The 32,740 remaining profile rows are an **unclassified coverage gap**, not automatically 32,740 runtime files to copy.

The next executable stream is:

1. Freeze this API40 profile as a predecessor and make an exact 33,424-row disposition table. Every row must be assigned one of: packaged portable byte, generated/rebuilt dependency, independently verified host prerequisite, protected/live authority input excluded from the archive, or evidence-only historical input. Each assignment needs a consuming operation or guard and an exact replacement binding. Resolve all rows before claiming installed API40 closure; keep ambiguous rows open.
2. Start with one named API40 read operation in a clean extracted root. Trace Python imports and file reads inside that root, then cross-check against the profile and source guard. An observed trace is only a lower bound; static dependencies and fail-closed missing-file probes must cover paths not exercised by the trace. Preserve the original profile hash and create a versioned portable successor profile rather than changing existing API40 authority or source bytes.
3. Replace absolute host paths with explicit installation prerequisites or reproducible builds. Prove the selected Python/stdlib/native ABI and external executable from the installed environment. Other-repository and Cargo-cache paths require a declared vendored/rebuilt artifact or remain host-only; do not copy personal cache or another repository into the release by default. Keep live `authority/` and protected Source8 inputs outside the portable package, with their own host qualification and grants.
4. Assemble a deterministic minimal archive from the classified portable rows, install it into a fresh private root, run the named operation and negative missing/changed dependency checks, then repeat across all selected API40 operations/checks. Record archive hash, installed source mapping, complete file-closure check, runtime result, uninstall and restore evidence. Independently review before upgrading T25 or T30.

The current local Docker fixture and API40 WSL CLI remain different products until that installed closure is proven. This plan copies no profile files, absolute host paths, live authority, or protected bodies and makes no release claim.
