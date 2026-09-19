# Agent Reasoning Engine — evidence recovery

Recover original evidence -> verify exact fingerprints -> identify remaining claim repairs.

Five of the seven previously unresolved references now match their original SHA-256 fingerprints. Four were recovered from Git objects: route registry, capability router source, request decision profile and Product profile. The original Product record was reconstructed by removing the later interaction-context entry; the resulting complete bytes exactly match the original fingerprint. This historical evidence does not remove that capability from the current Product.

Two implementation references remain unresolved: the journaled wrapper and evolution runtime. Searches covered path history and all stored Git blobs up to 2 MB in both local repositories, including unreachable objects. Current versions remain available, but do not match the original fingerprints. `remaining-impact.json` identifies every affected bridge claim and pins each current implementation file for subsequent verification.

No source registry fingerprints were refreshed, no implementation claim was promoted, and no context import or contract admission occurred. The two candidate schema repairs from 0045 remain prepared. Next: verify current wrapper and evolution code against the affected claims, produce explicit successor evidence bindings, then apply the schema repairs and repeat package validation.

`verify.py` checks the five recovered snapshots, the exact remaining set, the bridge impact mapping, current file stability and unchanged migration contract. `verification.json` binds this recovery evidence and the predecessor preparation receipt.
