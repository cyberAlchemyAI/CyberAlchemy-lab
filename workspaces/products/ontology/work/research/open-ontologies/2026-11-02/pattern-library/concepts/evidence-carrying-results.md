# A result label needs checked evidence

## Purpose

Make an unchecked result harder to mistake for a checked one.

## Layer and recognition

Result and checker boundary. CheckerBinary, CheckerRun, Certified and verdict types in src/verdict.rs.

## Contract and dependencies

Observed: private evidence constructors and no Deserialize implementation for earned verdicts. A successful checker process creates a token bound to named input digests.

Observed dependencies: input files, process invocation and checker discovery. Recommended Lab dependency: independently trusted binary identity and immutable exact source binding.

## Testing obligations

Forged output, changed input, wrong goal, absent checker, nonzero exit and proof-result vocabulary boundaries.

## Observable evidence

Checker identity/output, exact input digests, encoding/rule scope, checked versus unverified result.

## Source and limits

[evidence-carrying verdicts](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/verdict.rs#L1); [remaining checker trust boundaries](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/src/verdict.rs#L34).

An operator-selected executable can lie. A caller can name the wrong inputs. A theorem about those files does not authenticate their source.
