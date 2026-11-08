# Observability alignment

Existing [store status/recovery](../../../implementation/lab-runtime/v2/lab_runtime/store.py), [session lifecycle](../../../implementation/lab-runtime/v2/lab_runtime/session.py) and [operation workspace journals](../../../product/lab/release-candidates/v1/interface/api-integration-v17/workspace.py) supply observation primitives. [Continuity](../../../implementation/lab-continuity/candidates/v1/README.md) and install generations provide additional reconstruction evidence. This map proposes their composition rather than asserting a deployed whole-Lab monitoring system.

| Event or state | Record for a future workspace transition |
| --- | --- |
| Compatibility inspection | Instance identity, exact before/after selection, local extensions, unsupported contracts and selected source tuple |
| Migration preparation | Work/owner references, active preimage, disposition manifest, expected outputs and recovery contract |
| Execution | Journal/cursor, attempt identity, committed versus staged effects, actual observations and interruption state |
| Verification | Exact tested source/environment, selected cases, failures, untested scope and report references |
| Adoption outcome | Actual selected generation, retained predecessor, owner/effect result and remaining restrictions |
| Recovery or rollback | Uncertain effects, reconciliation result, retained-reader/data compatibility and external-effect status |
| Later operation | Source/profile freshness, history cursors, replay results, local Work outcomes and assessed feedback |

Source currentness, test outcome, candidate/admitted standing, installation, runtime activation and Product benefit require distinct fields. A progress percentage or one successful check cannot substitute for the other dimensions. Private keys, live credentials and expired session notes are not telemetry payloads.
