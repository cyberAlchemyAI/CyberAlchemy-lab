# One fixed input for a run

## Purpose

Keep an answer about one selected dataset even while other callers change the live graph.

## Layer and recognition

Graph selection and reasoning. GraphStore::read_one_state, ScopeRequest and the input/canonicalization boundary.

## Contract and dependencies

Observed in the forward/Horn paths: assertion extraction uses a pinned store snapshot, then reasoning reads owned selected data. Scope names the graph/time selection; the same selected bytes must feed reasoning and evidence. This is not a guarantee about every engine path.

Observed dependencies: patched Oxigraph snapshot, temporal selection, canonical bytes. A later live-store reread would break the intended binding.

## Testing obligations

Writer progress during one long selection; mutation between selection and proof emission; rejection of incompatible unscoped versions.

## Observable evidence

Source/scope digest, selected graph identities, omitted/truncated data and temporal choices.

## Source and limits

[stable graph reads](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/graph.rs#L1245); [writer-progress test](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/tests/read_does_not_block_writers_test.rs#L1); [explicit time scope](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/temporal.rs#L351).

An internal per-run snapshot is not a persistent per-agent graph branch. Single store iterations are also snapshotted, but separate reads can select different states. Temporal metadata is resolved before assertion snapshot selection, not atomically with it. Source time/operator claims can remain producer attestations.
