# Live store to fixed reasoning input

## Source and target

GraphStore and explicit scope -> Owned input for reasoning and evidence.

## Direction and contract

In the forward/Horn assertion-extraction paths, read one pinned data state, canonicalize the selection, then pass owned data forward.

Observed intent: hashing, reasoning and certificate emission concern the same selected value. Do not read a later live state to supply a different phase.

## Testing and evidence

Change the live store during one selection and afterward; require input consistency and writer progress.

Retain: Dataset/scope fingerprints, selected graph list, refusal/truncation and temporal scope.

Sources: [stable graph reads](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/graph.rs#L1245); [writer-progress test](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/tests/read_does_not_block_writers_test.rs#L1); [src/canon.rs](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/canon.rs#L1).

## Known gap

Scope metadata can include producer attestations and is resolved before the separate data snapshot. This is not one atomic metadata-plus-data selection, nor a guarantee for every reasoner. Not every transport request carries a persistent snapshot handle.
