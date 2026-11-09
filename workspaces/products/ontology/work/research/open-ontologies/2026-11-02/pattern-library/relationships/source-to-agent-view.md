# Selected source to a task view

## Source and target

Source ontology and task claims -> Smaller projection and per-claim support report.

## Direction and contract

Select a subset, compare entailments under the same rules, and report each requested claim.

Selection must not add claims outside the source or silently lose load-bearing support. The Lab still chooses its version and owner interpretation.

## Testing and evidence

Remove essential fact, omit irrelevant facts, source-unsupported goal, non-subset view and budget failure.

Retain: Goal-specific support and loss, exact source/view/rule versions and known coverage.

Sources: [claim-preservation checks](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/projection_entailment.rs#L1); [src/segment_retrieve.rs](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/segment_retrieve.rs#L1).

## Known gap

RAG similarity and graph coverage are weaker signals. Natural-language task completeness is not automatically captured.
