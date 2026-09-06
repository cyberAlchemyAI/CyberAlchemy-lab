# L4 state-bearing target selection

Decision ID: `CAL-D65-L4TGT-0038`  
Owner gate: `G-D65-L4-STATE-BEARING-TARGET-SELECTION`  
Current result: `PASS` — owner selected `L4TGT-1`  
Authority effect: `product-direction-selection-only`

The admitted L3 adapter is a successful disposable rehearsal target, but it
cannot be activated as a persistent runtime target: every run restores the
exact preimage, removes the complete target directory, rejects live mode, and
reports `runtime_activated: false`. Reusing it as an activation target would be
vacuous.

## Admissible options

| Option | Meaning | Benefit | Cost or risk | Downstream impact |
| --- | --- | --- | --- | --- |
| `L4TGT-1` | Select a new non-live state-bearing local sandbox successor. | Proves meaningful activation without credentials, network, production data, or live effects. | Requires a new identity, definitions, implementation, tests, product approval, and admission. | Opens prototype construction only; grants no approval, admission, or activation. |
| `L4TGT-4` | Defer L4 construction. | Preserves the admitted L3 product and all evidence. | No state-bearing activation product is built. | No new construction frontier opens. |
| `L4TGT-5` | Stop at the admitted disposable rehearsal adapter. | Keeps the terminal boundary small and fully evidenced. | No durable activation model is added. | Closes this continuation route without changing existing state. |

Selected: `L4TGT-1`, from the user's exact selection `` `L4TGT-1` `` on
2026-09-03. The L4 product direction is a new non-live state-bearing local
sandbox target. Prototype construction is eligible to begin through its
separate implementation route with a new identity and digest.

## Rejected before presentation

- `L4TGT-2` — reusing the admitted disposable adapter cannot yield surviving
  activation state; changing rollback or cleanup semantics requires a new
  product identity.
- `L4TGT-3` — a live service target has no exact target, owners, credentials,
  maintenance boundary, tested product, approval, or admission.

`Explain / more context` is always available and does not resolve the gate.

The product direction is selected, but no successor identity or implementation
exists yet. Construction, approval, admission, activation, live execution,
migration, cutover, publication, deployment, and external effects remain false.
