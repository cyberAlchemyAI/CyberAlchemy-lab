# Epoch-002 execution-envelope prototype

This is the first runnable prototype below the `D65CUT-1` authorization. It
executes the full state machine against one generated temporary directory and
always restores and removes that target before returning.

```mermaid
flowchart LR
    A[Exact D65CUT-1 decision] --> B[Preflight]
    B --> C[Capture 7-event preimage]
    C --> D[Stage 11-event candidate]
    D --> E[Activate prototype runtime]
    E --> F[Migrate canonical events]
    F --> G[Calculate and verify ontology]
    G --> H[Cut over temporary pointer]
    H --> I[Verify postimage]
    I --> J[Rollback]
    J --> K[Verify exact preimage]
    K --> L[Remove temporary target]
```

The calculated target contains the latest state for two nodes, one relation,
one context binding, and one challenge contract. The three latest snapshots
are disposable projections; canonical events remain the only replay source.

## Run the prototype

```bash
PYTHONDONTWRITEBYTECODE=1 python3 ontology-lifecycle/execution-prototypes/cal-d65-epoch-002/runner.py --mode prototype
```

## Validate twice and prove live refusal

```bash
PYTHONDONTWRITEBYTECODE=1 python3 ontology-lifecycle/execution-prototypes/cal-d65-epoch-002/validate.py
```

The validator runs the prototype twice, requires byte-identical receipts,
checks ten hostile mutations, and then calls `--mode live`. Live mode must
return `BLOCK` because the exact live target, credential identity, maintenance
boundary, live preimages, fail-closed sequence, and independent live validation
are not bound.

## Prototype state

```text
prototype execution ready: true
live execution ready:      false
runtime activated:         false
migration performed:       false
cutover performed:         false
external effects:          false
```

This prototype proves control flow and evidence behavior. It does not operate
the admitted runtime or any production system.
