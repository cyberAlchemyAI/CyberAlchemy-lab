# Keep interpretation and missing meaning visible

## Purpose

Make generated schemas and translated meanings reviewable instead of silently declaring them true or complete.

## Layer and recognition

Data intake and model translation. induce, ossie and extract_scaffold modules.

## Contract and dependencies

Observed: induced statements have observed support and hypothesis labels; model translation records unsupported constructs; extraction generation is separated from output validation.

Observed dependencies: source rows/model records, explicit mapping and shape/format checks. Owner acceptance is a separate Lab responsibility.

## Testing obligations

Observed range does not become universal constraint; ambiguous repeated columns remain visible; unsupported construct produces a named issue; malformed generated JSON is rejected.

## Observable evidence

Per-statement support, assumptions, unsupported/lost constructs, mapping version and validation errors.

## Source and limits

[evidence-bearing schema proposals](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/induce.rs#L1); [translation with unsupported-construct reporting](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/ossie.rs#L1); [extraction request and output validation](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/extract_scaffold.rs#L1).

Naive header mapping is not semantic alignment. Shape validation is not domain truth or admission.
