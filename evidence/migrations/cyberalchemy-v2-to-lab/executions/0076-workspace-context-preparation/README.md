# Workspace context preparation

Workspace model -> exact definition/evidence bindings -> external endpoints -> runtime registration.

Pinned only the 34 files declared by Workspace's semantic validator and its seven external source files. The changing dashboard/runtime implementation is outside this preparation. The model contains twelve nodes and fourteen relationships plus a nine-node/eight-edge generated system model; generated files are preserved, not recompiled or treated as runtime conformance evidence.

The original validator reports one stale whole-file definitions binding. Its historical whole-file fingerprint was not recovered from inspected local snapshots or path histories in the three sibling repositories. A definitions document already pinned by 0064 contains all five selected sections byte-identically. A separate successor changes only that enclosing file fingerprint in `sources.json`; definition selectors, hashes and meanings remain unchanged. All other six source files are pinned; the registry reference uses the source's self-registration posture.

The unchanged native validator passes on the successor. Two gaps remain outside what that validator proves:

- The legacy registration's material digest does not match the successor package. The validator checks the self-registration marker, not an actual current runtime snapshot.
- Three authored relationships target external identities: CAV2-D60 (Project), CAV2-D67 (Product Capability), and ESSAYS-REALIZATION-BASELINE-003. They are allowed by the source validator but absent from its node registry.

A manifest for the existing v4 runtime preserves every relationship and correctly fails with `unresolved relation endpoint`. No placeholder records were invented, no edges discarded, and no runtime store was created. Workspace nodes use the source field `kind`; the adapter records that mapping explicitly.

The original source package is archived. `successor-sources.json` and `repair-report.json` record the bounded repair and the five exact selections. Historical source ownership and no-effect posture remain intact.

## Open Questions

Next: bind the three external references to source-owned records with exact evidence and explicit runtime package identities. Then refresh the candidate registration and verify import/replay/export through the existing runtime. The definitions are references, not newly adopted Lab definitions; the Essays explorer baseline remains historical design evidence.

Workspace dashboard work, system recompilation, conformance and operational activation remain separate. No changes were made to the sibling source checkout or the frozen runtime.

Reproduce preparation checks from the Lab root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 evidence/migrations/cyberalchemy-v2-to-lab/executions/0076-workspace-context-preparation/verify.py
```
