# D65-S8 integration conformance epoch 001

This package independently evaluates the exact D65-S7 Rust postimages against
the accepted D65-S6 binding, the selected source and Context bytes, the
admitted event/system contract, and the frozen W8 runtime contract.

Run the validator without writing repository evidence:

```sh
python3 validate.py
```

Write `verdict.json` only after inspecting the check-only result:

```sh
python3 validate.py --write-verdict
```

All Rust build output and hostile mutations are created beneath temporary
directories. The validator does not mutate the runtime or any accepted input.
It collects all six validations and reports dependent checks as
`not_evaluable` when a prerequisite fails.

`PASS` is candidate evidence for `G-D65-CONFORMANCE`; it is not admission,
acceptance, adapter export, migration, cutover, publication, or deployment.
