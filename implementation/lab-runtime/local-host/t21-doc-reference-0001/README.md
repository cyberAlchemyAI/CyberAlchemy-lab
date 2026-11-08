# T21 exact declared-operation reference

`generate.py` verifies the frozen public API catalog SHA-256 and the original request, result and error schema hashes for all 34 declared operations. It writes an index and 34 pages to `docs/lab/runtime/reference/api/`. Each page includes the original contract's authority, effect, schema, currentness, deadline, idempotency, error and recovery rules and says that current runtime qualification is pending. The generated pages do not assert that the developing composite API has passed an operation.

From the repository root, run `python3 -B implementation/lab-runtime/local-host/t21-doc-reference-0001/generate.py --verify` to check the generated files. `--write` regenerates them from the exact same catalog. Run `python3 -B -m unittest -q implementation/lab-runtime/local-host/t21-doc-reference-0001/test_generate.py` and repeat with `-O` for changed catalog, schema and generated-page refusals.

This is the declared-contract reference slice of T21. Final-cut implementation paths, per-operation observed evidence, clean-install operator walkthrough, website integration and full T21 closure remain open.
