# L3 filesystem adapter admission

Decision ID: `CAL-D65-L3AADM-0037`  
Owner gate: `G-D65-L3-FILESYSTEM-ADAPTER-ADMISSION`  
Current result: `PASS` — owner selected `L3AADM-1`  
Authority effect: `adapter-admission-only`

The exact product-approved adapter passed 27 Rust tests per run across two
deterministic runs, six filesystem invariants, byte-exact rollback, and complete
temporary-directory cleanup.

## Options

| Option | Meaning | Benefit | Cost or risk | Downstream impact |
| --- | --- | --- | --- | --- |
| `L3AADM-1` | Admit the exact adapter for governed non-live disposable rehearsal only. | Establishes an exact admitted adapter identity and scope. | Changed bytes require a successor admission. | Does not activate the runtime or authorize live effects. |
| `L3AADM-2` | Reject the candidate and preserve its evidence. | Stops this candidate from entering admitted scope. | A successor requires reconstruction and testing. | No adapter admission is created. |
| `L3AADM-3` | Defer without changing adapter or runtime state. | Preserves the approved product for later review. | The adapter remains unadmitted. | No downstream runtime state changes. |
| `L3AADM-4` | Require amendment and complete new product tests. | Allows a targeted successor design. | Requires construction, tests, product approval, and a new admission candidate. | The current candidate remains approved as a product but unadmitted. |

Selected: `L3AADM-1`, from the user's exact selection `` `L3AADM-1` `` on
2026-09-03. The exact adapter is now admitted only for governed non-live
disposable-filesystem rehearsal.

`Explain / more context` is always available and does not resolve the gate.

`L3AADM-1` grants adapter admission only. It does not activate the
runtime, authorize live execution, migration, cutover, publication, deployment,
credentials, destructive action, or external effects.
