# Existing runtime gap review

Legacy requirements -> existing Lab runtime -> missing registrations and integration.

Keep the Lab event runtime, v4 source migration/update adapters and graph read model. The legacy Python runtime is a comparison source; this review imports no replacement runtime and activates no persistent store.

## Existing coverage and remaining work

| Legacy operation | Existing Lab support | Remaining gap in the inspected integration surfaces |
| --- | --- | --- |
| Register packages | v4 manifests explicitly map source profiles, nodes, relations and supporting documents. | Add uncovered packages using validated snapshots and exact mappings. |
| Catalog currentness | v4 plan verifies selected file hashes; summary reports an imported store. | A collect-all catalog comparing selected versions, imported versions and source drift is not the same operation as summary. |
| Snapshot | Canonical events, replay, snapshots and v4 observe/export already exist. | Bind package selection to the chosen runtime cursor/head; do not add another snapshot engine. |
| Get a record | Graph read-model subject lookup exists; v4 export can select a package. | Resolve legacy ontology ID + kind + logical ID to source-qualified runtime identity and expose it through the existing interface. The graph prototype is not automatically connected to v4 by this review. |
| Validate / validate-all | Native package validators and migration receipts already exist. | Add a bounded integration that keeps execution status distinct from native proof status, and preserves PASS/BLOCK/FLAG/NOT_EVALUABLE. |
| Route preflight | Exact source checks, event heads and context projection primitives exist. | Bind the selected request/route to the exact package snapshot. Existing context adapters are projections, not this complete legacy operation. No enforcement hook is implied. |

The legacy wrapper currently rejects FLAG as an unsupported native status. Copying it unchanged would incorrectly collapse the declared result of several migrated packages. Preserve each validator's result and its exit code without interpreting FLAG as proven conformance.

## Package coverage

The inspected legacy registry has six entries; its README says five. The v4 manifest has 21 source-qualified packages. Two legacy ontology identities occur there: Ontology Product and Define system model. Matching identity does not establish matching versions or valid current evidence.

Four legacy identities are absent from this v4 manifest:

1. Shared Capability ontology (`cav2.capability`).
2. Workspace capability ontology (`cav2.workspace.capability`).
3. Durable Storage (`cav2.durable-storage.business`).
4. People and Teams (`cav2.people-and-teams.business`).

This is a comparison of the pinned registry and v4 manifest, not an exhaustive claim about every Lab runtime or every newly migrated context.

## Concrete next package

The existing v4 executable accepts `people-teams-plan.json` without runtime code changes:

21 nodes -> 26 relationships -> 18 supporting documents -> 65 planned event subjects.

All eighteen files from the verified 0072 snapshot are retained as supporting documents, including its exact dependency files. The plan's package key remains qualified by its declared source root and profile path. This is a new manifest candidate, not an edit to the frozen v4 manifest.

Two read-only plan calls agree. Four invalid plans (wrong fingerprint, missing selector, duplicate package and authority escalation) are rejected. The exact executable hash is recorded; this smoke test does not claim a new source-to-binary build verification. No event files are written by plan.

The README's `.local/ontology-source-runtime-v4-prototype` store is absent in this workspace. A read-only summary attempt therefore returned file-not-found. That says nothing about other instances; it prevents treating this documented demo location as running.

## Open Questions and next action

Next: create an isolated People and Teams runtime instance using the existing implementation, then verify import -> replay -> export preserves the exact records and restart state. Keep the prototype isolated and preserve original source files. Validate the runtime build used for that execution.

After that, address the other three missing registrations, currentness/lookup integration, native verdict preservation and request/snapshot binding. Broader 0036–0072 context-to-runtime coverage needs its own manifest reconciliation. Operational adoption or activation of any broader instance is separate from this comparison.

Reproduce the comparison smoke checks from the Lab root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/executions/0073-existing-runtime-gap-review/verify.py
```
