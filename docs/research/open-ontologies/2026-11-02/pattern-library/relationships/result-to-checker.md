# Engine result to independently checked evidence

## Source and target

Search/reasoning/solver result -> Separate checker and scoped verdict.

## Direction and contract

Emit assertions/rules/steps or model/refutation, run the chosen checker, retain its result and binding.

Only supported accepted evidence earns the stronger result. Supplied rules remain assumptions. Do not turn an engine answer, a second solver opinion or a JSON label into checker acceptance.

## Testing and evidence

Bad conclusion, missing premise, wrong input, forged checker response and unsupported proof step.

Retain: Exact evidence and checker identity, input binding, theorem/profile and accepted/rejected/unchecked status.

Sources: [evidence-carrying verdicts](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/verdict.rs#L1); [separately built Lean checkers](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/lean/lakefile.toml#L1); [rule reasoning and certificates](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/reason.rs#L1).

## Known gap

The checker executable and live-source correspondence remain additional trust boundaries.
