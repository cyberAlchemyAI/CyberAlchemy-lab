# Architecture Pattern Library

The machine inventory is [operation-patterns.json](operation-patterns.json).
Load only the selected pattern and its prerequisite records.

| Pattern | Availability | Architecture status | Reason |
| --- | --- | --- | --- |
| `operation-port` | available | candidate | All four generation prerequisites are closed. |
| `transactional-outbox` | blocked | candidate | Explicit effect syntax, provider runtime, generator and conformance are absent. |

Pattern availability and architecture stability are independent axes. A
pattern may be locally available while still awaiting owner-controlled stable
promotion.

See [pattern-library/README.md](pattern-library/README.md) for selective views.
