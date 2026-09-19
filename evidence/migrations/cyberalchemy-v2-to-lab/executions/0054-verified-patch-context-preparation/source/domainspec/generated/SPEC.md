# Are Coding Agent Runtime Specification

Generated human view. Canonical semantics live in the project-local machine sources.
Graph digest: `84d84ecb30a855e018dd55cd45cc1c903e49560ec1f54c835cb9ec38efa9cb62`.

## Nodes

| Node | Kind | Intent |
| --- | --- | --- |
| `are-coding-agent-runtime.CodingRequest` | Entity | Bind one exact coding request to one immutable fixture base tree and mutation allowlist. |
| `are-coding-agent-runtime.ModelTurnOutput` | Entity | Bind one deterministic prompt to exact final model bytes and a non-authorizing transport receipt before candidate parsing. |
| `are-coding-agent-runtime.NextActionCandidate` | Entity | Represent one untrusted replace-file candidate bound to exact base, file, path, and output bytes. |
| `are-coding-agent-runtime.PatchCandidate` | Entity | Bind one verified fixture postimage to the exact action, before and after trees, changed paths, and verifier receipt. |
| `are-coding-agent-runtime.SafeEffectInvariant` | Rule | Permit patch-candidate status only after exact approval, one allowlisted no-follow replacement, and separate postimage verification; uncertain post-effect outcomes block retry. |

## Edges

| Edge | From | Type | To |
| --- | --- | --- | --- |

This file is generated; edit machine sources and rebuild.
