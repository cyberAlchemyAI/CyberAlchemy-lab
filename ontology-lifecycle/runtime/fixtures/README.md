# Runtime conformance fixtures

The executable fixture builder is in `tests/replay.rs`. Each test creates an
isolated empty semantic and governance event store, writes canonical v2 events,
applies one named mutation, and asserts the exact fail-closed code.

This avoids retaining a second hand-maintained ontology truth in fixture files.
`mutation-ledger.json` maps every compiled runtime obligation to at least one
positive or falsifying test. Generated snapshots and projections are never
canonical replay input.
