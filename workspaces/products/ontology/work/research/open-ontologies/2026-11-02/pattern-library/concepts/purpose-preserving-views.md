# Check what a smaller view loses

## Purpose

Give an agent less material while checking that the claims its task needs remain supported.

## Layer and recognition

Context selection and reasoning. projection_entailment, closure_diff, projection_check and module_extract.

## Contract and dependencies

Observed: compare support for explicit goals in a selected source and its projection under one rule table. Keep retained support, lost support, source-unsupported goals and invalid-subset outcomes distinct.

Observed dependencies: exact source/projection, rule table, goals and optional checker. A retrieval coverage percentage is a different measurement.

## Testing obligations

Remove a decisive premise; ask a source-unsupported goal; insert a projection triple outside source; exhaust budgets; mutate a checked derivation.

## Observable evidence

Per-goal result, missing support, rule profile, work budget and proof status.

## Source and limits

[claim-preservation checks](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/projection_entailment.rs#L1); [src/closure_diff.rs](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/closure_diff.rs#L1); [src/module_extract.rs](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/module_extract.rs#L1).

Supported positive ground claims under a partial table do not cover every natural-language instruction or future agent action.
