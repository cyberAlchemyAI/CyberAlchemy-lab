# L4 state-bearing sandbox product approval

Decision ID: `CAL-D65-L4PAPP-0039`  
Owner gate: `G-D65-L4-STATE-BEARING-SANDBOX-PRODUCT-APPROVAL`  
Current result: `BLOCK` pending explicit owner selection  
Authority effect before selection: `none`

## Exact candidate

- Product candidate: `CAL-D65-EPOCH-003-STATE-BEARING-SANDBOX-PROTOTYPE-005`
- Candidate identity: `cal.prototype.rust-state-bearing-sandbox-target/epoch-003`
- Product-test evidence SHA-256: `bc9f367f18ce9530e6a8cd78a6d8b3edcbe788c753505847e7e5b999e1d4ddb3`
- Evidence: 35 Rust tests per run, two deterministic runs, seven exact invariants, state surviving activation observation, exact restore, and complete teardown.

## Options

| Option | Meaning | Benefit | Cost or risk | Downstream impact |
| --- | --- | --- | --- | --- |
| `L4PAPP-1` | Approve this exact tested digest as a product. | Recognizes that the L4 candidate meets its bounded product contract. | Later byte changes require a successor candidate and new decision. | Makes a separate adapter-admission request eligible; grants no admission or live authority. |
| `L4PAPP-2` | Reject this exact candidate and preserve its evidence. | Stops this candidate from advancing. | A replacement requires a new construction and test cycle. | No downstream authority request is eligible from this candidate. |
| `L4PAPP-3` | Defer without changing candidate state. | Preserves the tested candidate for later review. | The product frontier remains waiting at approval. | No approval, admission, activation, or live work may be inferred. |
| `L4PAPP-4` | Require amendment and complete retesting. | Lets the owner name required product changes. | Invalidates this manifest as the approval target; a successor must be fully retested. | Returns work to product construction with no authority effect. |

Recommendation: `L4PAPP-1`, because all bounded L4 tests and invariants pass,
the activation observation is non-vacuous, teardown is exact, and the candidate
excludes caller paths, credentials, networks, production data, governed runtime
activation, migration, cutover, and external-system effects. This is a
recommendation only.

`Explain / more context` is always available and does not resolve the gate.

## Non-effects

No option may be inferred from silence or from this packet. Even `L4PAPP-1`
would be product approval only. It would not admit the adapter or authorize
governed runtime activation, live execution, migration, cutover, publication,
deployment, credentials, destructive action, or external effects.
