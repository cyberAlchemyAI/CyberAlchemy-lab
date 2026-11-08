# Sixth API33 original Reader entry refusal

The disposable signed technical fixture constructed the original `release-proof-inputs-v2-completion-0001` `ProtectedReader` with the sixth API33 Source/profile pins. Preparation took 20.317 seconds; the selector contained 32,226 selected files, 128 roots and 32,228 ordered proof occurrences. The original `reader.boundary()` refused during its **entry** `verify()` with `fresh file bytes/attachment changed`. No entry PASS, exit pass, graph, host guard, release effect or T08 completion occurred. The guard was not patched.

A separate read-only digest sweep of every selected sixth Source/profile/external row (32,228 occurrences; 32,224 unique paths; 3,311,840,510 bytes read in 83.749 seconds) found exactly two stable mismatches. No selected path changed size, mtime or inode during that sweep:

| Table row | Selected path | Expected SHA-256 | Observed SHA-256 | Size | mtime_ns |
|---|---|---|---|---:|---:|
| profile `files[769]` | `authority/project-state-transitions/current.json` | `8ba8ee25ccbf12721d800c693120a3452ddf1ec4427c6fdf1e0655beae31bc12` | `12937950af2a00ef329deb1a922275250c61ad199b8f6216eab448e06bf49984` | 785 | 1792621366098177118 |
| profile `files[25276]` | `/usr/lib/x86_64-linux-gnu/liblzma.so.5.8.3` | `64550dc7a4dc9159d32c00d9e78ce86e0951d02b7b24827df97f090dae101a19` | `515749273a91ca5e3b273b4025dc2c1f8827f90005baea0ab85ffb594e74f72f` | 215448 | 1791561255000000000 |

Every selected source-manifest row and the external dependency row matched. The first mismatch explains the observed Reader entry refusal. The second would be another refusal if the first row alone were repaired. A successor must reselect current bytes with explicit authority-state lineage and liblzma ABI/dependency review; replacing expected hashes without that review would overstate qualification. The sixth package and authority files were not edited by this attempt.
