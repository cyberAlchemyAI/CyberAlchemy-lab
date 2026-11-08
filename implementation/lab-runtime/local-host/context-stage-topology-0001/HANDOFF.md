# Context stage topology 0001 — compatibility amendment

Status: **requirements only; effect and Context launch refused.** This small amendment pins the stage0001 selection, stage-effect0001 freeze, and the JIT owner's required-topology draft. It does not rewrite the 1,570-path stage manifest or create an AUTH leaf.

The future versioned stage selection must explicitly project the Source role directory from 0755 to owner-0700, add an exclusive owner-0700 `authorization/` directory and a fresh owner-0600 `context-development.json` leaf, and close a 1,571-file namespace after that leaf exists. The Source role file bytes remain pinned; same-UID Source/Reader/Mapper import and the Source `packages/0001` namespace check must be rerun after this metadata projection. The two Context role byte replacements are pinned to the JIT draft, but an AUTH digest/issuer and a selected final stage manifest are still absent.

The stage0001 Context output mount is `rw`. The reviewed bridge requires the child output view to be **read-only**, with the parent as sole writer and the child able to read emitted leaves after ACK. A versioned final layout must make that mount change explicit while preserving the root and native read-only mounts. Neither stage-effect0001 nor this compatibility amendment is launch approval.

`check.py` verifies the pinned predecessor/draft joins and the exact 1570→1571, two-role, mount-mode requirements under normal Python and `-O`. It reads no protected archive body and mutates no stage, grant, key, or policy.
