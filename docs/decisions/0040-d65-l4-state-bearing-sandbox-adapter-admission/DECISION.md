# L4 state-bearing sandbox adapter admission

Decision ID: `CAL-D65-L4AADM-0040`  
Owner gate: `G-D65-L4-STATE-BEARING-SANDBOX-ADAPTER-ADMISSION`  
Current result: `PASS` for exact `L4AADM-1` selection  
Authority effect: `adapter-admission-only`

## Exact candidate

- Identity: `cal.prototype.rust-state-bearing-sandbox-target/epoch-003`
- Scope: bounded non-live sandbox activation observation and explicit teardown only.
- Product approval: `PASS`, decision SHA-256 `6f57ea86f8547fece058fa70e01c7afe4ed65bc97ec6b3a4f66f774a1f6301f3`.
- Evidence: 35 Rust tests per run, two deterministic runs, seven invariants, observable surviving state, exact restore, cleanup, live refusal, and engine-substitution refusal.

## Options

| Option | Meaning | Downstream impact |
| --- | --- | --- |
| `L4AADM-1` | Admit the exact adapter for its bounded non-live sandbox scope. | Records adapter admission only; no runtime activation or effect authority. |
| `L4AADM-2` | Reject the exact adapter admission candidate. | Preserves evidence; no admission. |
| `L4AADM-3` | Defer without changing state. | Candidate remains frozen and unadmitted. |
| `L4AADM-4` | Require amendment and complete retesting. | Returns to construction with a successor candidate. |

Selected: `L4AADM-1`. The exact adapter is admitted only for bounded non-live
sandbox activation observation and explicit teardown. No runtime activation,
live execution, migration, cutover, or external effect is authorized.
