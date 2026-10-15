# Exact artifact reader successor

Four original API handlers are available: `lab.status`, `catalog.get`, `artifact.inspect` and `artifact.query`. The successor preserves the original authenticated stdio protocol and verifies independently selected signed candidate archives.

Inspection checks exact identity/version/carrier/bytes and requested sections. Queries disclose canonical versus SQLite basis, applied/requested cuts, freshness and cursor generation. SQLite is a disposable complete read generation in an owned temporary root. Closing the context removes it; cold reconstruction replays original signed history.

The complete plan still requires thirty API handlers, full descriptor-envelope coverage, broader candidate/Decision/ontology joins, operational workflows and S02/R08 review. Read metadata and schema-valid results grant no admission or owner authority. See `DESIGN.md` and the coverage audit for exact limits.

## Observe the implementation

- `receipts/attempts/0005/tests.stderr`: full inherited and new reader guards.
- `examples/operator-journeys/api/0009`: three real inspection/SQL/historical/cold-rebuild reader episodes.
- `examples/operator-journeys/api/0010`: eight real authentication/transport cases against this successor.
- `receipts/coverage.json`: exact body, connection and ambiguous-head coverage gaps.
- `receipts/R03-0004.json`: exact code, source and original evidence closure.

Example paths are relative to `product/lab/release-candidates/v1`; receipt paths are relative to this directory.

To run fresh reader episodes from the repository root:

```bash
python3 product/lab/release-candidates/v1/interface/api-v2/exercise_readers.py \
  product/lab/release-candidates/v1/examples/operator-journeys/api/NEW-UNUSED-DIRECTORY
```

The runner provisions only independently owned fixture reader keys/policies and removes them at close. The server creates no live operational store, listener or canonical transaction. Retained evidence contains public keys/signatures and exact frames, with no private key or Session memory.
