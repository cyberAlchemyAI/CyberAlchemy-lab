# Recover and retry safely

Distinguish an absent effect, a committed outcome and uncertainty before repeating work.

Draft prepared on 2026-10-14. Integration and final T21 qualification remain pending.

## Select the state you are recovering

A v1 store recovers staged local transactions around an atomic HEAD commit. The API Vault journals candidate operation claims/material/results. Action has its own tool-effect/reconciliation boundary; Governance owns separate native commits. SQLite projections, exports and managed files are derived or external publications with their own guards.

Keep each store identity, owner, source cut, exact request and effect boundary. A timeout or missing final response does not prove no effect. Source/profile mismatches and expired permission do not authorize inspection of foreign private state.

## Follow v1 HEAD recovery

Read the selected store's status under current scope, then verify its committed chain. recover requires --expected-head with the exact digest from that store; do not substitute this handbook's D74 repository-inspection digest. The [original Store recovery](../../../../../../evidence/implementation/lab-runtime/v1/lab_runtime/store.py) preserves committed transactions and removes only recognized pending/staging material or an immediate uncommitted next transaction.

Unknown future transactions remain for inspection. Controlled process interruption on the observed local filesystem is the supported verification scope. Power-loss durability and multi-host consensus are not established. Rebuild a disposable graph only after source/HEAD freshness; a graph file cannot become replay authority.

## Handle API idempotency and pending effects

The exact key belongs to an authenticated Principal/authority/scope/operation namespace. Keep the original control-input fingerprint. Same-key changed bytes conflict. Completed retries return or locate their guarded historical result; pending or uncertain keys request inspection/reconciliation and do not automatically redispatch.

The [captured Vault claim code](../../../../../../evidence/product/lab/release-candidates/v1/interface/api-integration-v16/workspace.py) looks up prior state under the original writer lock before fresh allocation. The reviewed margin gate belongs only to a new fresh application/assessment claim; it must not make an old recorded outcome depend on a new Session. Original source, authorization, cut, deadline and journal guards still apply.

````mermaid
flowchart TD
  Q[Exact request and key] --> J[Inspect owned journal]
  J -->|Completed| R[Read guarded recorded result]
  J -->|Pending / uncertain| I[Operation inspection]
  I --> A[Authorized reconciliation]
  A --> C[Cold replay / exact observed outcome]
  J -->|Fresh and authorized| G[Current pre-effect guards]
  G --> E[Effect and durable evidence]
  E --> C
````

Completed outcomes are read as history. Pending or uncertain outcomes require current owned inspection and authorized reconciliation before a new effect. A fresh request follows current guards, then records observed effects. The diagram does not authorize redispatch.

Explanatory component/sequence map, not a declaration of new ontology relation kinds or qualified runtime execution.

## Preserve committed work when derived output fails

A committed native transaction stays committed if a later projection/export/file generation fails. Reconcile the selected output boundary instead of applying the transaction again. The [mixed-target publisher successor](../../../../../../evidence/docs/plans/0011-lab-runtime-completion/runs/0001-execution/T14/mixed-target-publisher-0002/README.md) stages ordinary filesystem/receipt behavior; its scoped controls are not proof of every native mixed-target admission.

The capture4 writer also replaces several metadata files source-last without a cross-file transaction. An interrupted replacement can leave mixed generations. Its reviewer flags that standing; Root must inspect and use exact retained preimages through a separately reviewed recovery. Do not call source-last publication atomic across files.

## What to retain

Retain permitted public request/result digests, exact selected version, observed phase/terminal, pending/committed posture, current authority scope and uncertainty. Never log private proof/key bodies or Session notes. Preserve unknown residue and failed candidates. Cleanup removes only exactly owned disposable objects whose retention decision is established.

The integrated full positive/security/recovery/native qualification is still pending. Use [the dated evidence](../status.md) to tell an implemented recovery path from a current successful witness.

## Selected public evidence

- [product/lab/release-candidates/v1/interface/api-integration-v16/integration_dispatch.py](../../../../../../evidence/product/lab/release-candidates/v1/interface/api-integration-v16/integration_dispatch.py). SHA-256 240dbfa9faa79b33e59d423343f23e4b86aaa8c962579c730ec7785275cfe0ea; 4440 bytes. Public technical snapshot; no authority transfer.

- [product/lab/release-candidates/v1/interface/api-integration-v16/workspace.py](../../../../../../evidence/product/lab/release-candidates/v1/interface/api-integration-v16/workspace.py). SHA-256 84623256b4efd3eff8e3ec44cac14d76cbe2264514f1a1609f492e9b68ead433; 15533 bytes. Public technical snapshot; no authority transfer.

- [implementation/lab-workflows/candidates/v1/authority/dispatch.py](../../../../../../evidence/implementation/lab-workflows/candidates/v1/authority/dispatch.py). SHA-256 b4f22eb96952b7e1dabf13ae93d567502eea70078d35ec938623ae6ff40a266e; 12509 bytes. Public technical snapshot; no authority transfer.

- [docs/plans/0011-lab-runtime-completion/runs/0001-execution/T14/mixed-target-publisher-0002/README.md](../../../../../../evidence/docs/plans/0011-lab-runtime-completion/runs/0001-execution/T14/mixed-target-publisher-0002/README.md). SHA-256 2f400b1e7e2f6aae62a77cb6da8225c8d607207c4b76bd22a99638f49665cc93; 3585 bytes. Public technical snapshot; no authority transfer.

- [implementation/lab-runtime/v1/lab_runtime/store.py](../../../../../../evidence/implementation/lab-runtime/v1/lab_runtime/store.py). SHA-256 ed2eaafd299f6ec942016e078c029a847b54269c7eb91bb970275ac0bdaf1910; 18220 bytes. Public technical snapshot; no authority transfer.
