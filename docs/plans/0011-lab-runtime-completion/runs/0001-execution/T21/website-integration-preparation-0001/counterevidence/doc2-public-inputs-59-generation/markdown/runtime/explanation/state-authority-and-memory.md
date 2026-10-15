[Documentation home](../../README.md)

<a id="runtime-state-memory"></a>

Lab runtime · proposed documentation

# State, authority and short memory

Know which records endure and what a later process must recheck.

Draft prepared on 2026-10-14. Integration and final T21 qualification remain pending.

<a id="runtime-state-memory-use-the-canonical-meanings"></a>

<a id="runtime-state-memory-use-the-canonical-meanings-title"></a>

## Use the canonical meanings

This chapter applies existing [Project State](../../reference/records/def-cal-definition-project-state.md#def-cal-definition-project-state) , [Session Memory](../../reference/records/def-cal-definition-session-memory.md#def-cal-definition-session-memory) , [authority](../../guide/authority.md#governance) and [provenance](../../guide/provenance.md#evidence) definitions. It does not introduce another semantic model.

Runtime admission, a record's lifecycle, committed history, accepted meaning, action permission and an observed outcome remain independent. A message Actor may claim an identity; only the actual selected channel/grant/source checks can support that requested operation.

<a id="runtime-state-memory-five-storage-boundaries"></a>

<a id="runtime-state-memory-five-storage-boundaries-title"></a>

## Five storage boundaries

| Surface | What persists | Currentness/recovery |
| --- | --- | --- |
| Local runtime store | Config, baseline, immutable transactions and HEAD | Cold signed/semantic replay, expected HEAD and source freshness |
| Native ontology/governance inputs | Original event bytes and separate cursors | Native replay/projection joins and independently supplied pins |
| Private API workspace/journal | Owned request material, claim/result/effect evidence | Current owner/scope, exact fingerprints and guarded inspection |
| Derived SQLite/graph/files | Disposable source-bound representations | Rebuild/verify at exact source cut; no replay authority |
| Session resource/notes/signer | Process-bound temporary state | Expiry/revocation/close disposes it; no public receipt restores RAM |

The [SQLite generation](../../assets/9b3d300682c5-projection.py) checks its row/content/source bindings. It is an optimization of selected queries, not a replacement canonical database.

<a id="runtime-state-memory-cuts-and-histories"></a>

<a id="runtime-state-memory-cuts-and-histories-title"></a>

## Cuts and histories

Project semantic/governance event histories, native ontology cursors, source transaction HEAD and representation revisions use their selected namespaces. Joining them requires actual contracts and exact inputs, not a common-looking timestamp.

The admitted v1 executable reads D74 while repository admission is D75. An independently initialized local store begins from its chosen baseline and records its own subsequent scope. No store or executable is silently rebased when the repository adds a decision.

<a id="runtime-state-memory-authority-at-every-boundary"></a>

<a id="runtime-state-memory-authority-at-every-boundary-title"></a>

## Authority at every boundary

A policy/key/nonce channel identifies a current Principal and permitted operations. Views, graph nodes, source hashes, receipts and instruction advice supply information; they grant no effect authority. Before an effect, recheck source cut, expiry/revocation, gates, allowed scope and budget under the original lock where required.

Three composite branches authenticate independently. Catalog membership and a common Principal across policies do not merge permissions. Session opening does not create Action rights; a custody signature does not issue a new grant. [The operator contract](../../assets/c034636b312a-README.md) retains these independent boundaries.

<a id="runtime-state-memory-what-happens-when-a-process-ends"></a>

<a id="runtime-state-memory-what-happens-when-a-process-ends-title"></a>

## What happens when a process ends

Closing a borrower releases its own resources, not the parent's custody. Closing/expiring the Session erases its bounded notes and signer. Durable Work/evidence/history remains at its own posture and can seed a new checked context.

A public Session export is historical metadata. Source period, old signed grant and expired policy remain immutable history; a fresh instance needs a distinct current selection and permission. Host restart/replayed receipts cannot reconstruct the old live resource. The [Session how-to](../how-to/agent-sessions.md) and [recovery route](../how-to/recover-and-retry.md) keep knowledge reconstruction separate from authority.

<a id="runtime-state-memory-sources"></a>

## Selected public evidence

- [product/lab/release-candidates/v1/interface/api-integration-v16/projection.py](../../assets/9b3d300682c5-projection.py). SHA-256 9b3d300682c587745a0c057409a18c814cf8a76e7a7a8d08dc7c5de4d344ca4f; 13317 bytes. Public technical snapshot; no authority transfer.
- [product/lab/release-candidates/v1/interface/composite-operator-v1-completion-0001/revision-0003/README.md](../../assets/c034636b312a-README.md). SHA-256 c034636b312ac42c3ecd25b6c8e5ec0586cbf606459a9ab1cd37343a3b541a1e; 11032 bytes. Public technical snapshot; no authority transfer.
