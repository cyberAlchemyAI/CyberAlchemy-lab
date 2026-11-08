# T15 inherited regression method inventory

`INVENTORY.json` is a deterministic read-only AST inventory of the frozen original API v96 selected by `final-api-regression-plan-0274.json` and the disjoint current API36 technical cut. The builder compares all 323 original method AST hashes and original test-file bindings to that pinned historical plan, then rehashes all 207 current API36 source-manifest rows. It records each test method's AST hash and its file hash. The original 323 method identities are present in the current 345; there are 22 added installation/release methods and 20 inherited methods with changed AST bytes. Four normal and optimized tests confirm counts, byte-identical rebuild, selected file hashes, and an AST mutation negative.

Run `python3 -B -m unittest discover -s implementation/lab-runtime/local-host/t15-inherited-method-inventory-0001 -p 'test_inventory.py' -q` from the repository root and repeat with `python3 -O -B`.

This inventory executes no inherited tests and classifies none of the 20 changed methods as acceptable. T15 stays open until the other technical tasks, a single coherent final cut, explicit changed-method review, frozen manifests, and T16 execution are complete. The current API36 source here is only a technical reference, not a final release freeze.
