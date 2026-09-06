# Deterministic SFOL Test Closure

The SFOL test-closure capability derives bounded neutral fixtures and
negative-control detection evidence without an LLM, network access,
randomness, time, or filesystem enumeration.

```text
typed admitted module + exact denominator + finite domain + strategy
  -> deterministic partitions
  -> neutral cases + exact bindings
  -> real observations + semantic evaluations
  -> required negative controls + detection matrix
  -> proof receipt + exact replay
```

The stable entry surfaces are `src/sfol/index.ts`, `src/sfol/api/index.ts`,
and `src/sfol/cli.ts`. The CLI commands are `derive`, `challenge`, `verify`,
and `replay`; each consumes one versioned JSON request.

## Partition strategies

`exhaustive-finite/v1` supplies both Boolean values and every declared enum
member. Primitive comparisons derive boundary witnesses. Lists and sets derive
empty, singleton, duplicate-list, and full witnesses from declared element
domains. Other sorts require explicit finite witnesses. Quantifiers require
explicit finite universes or universe variants.

`mcdc/v1` deterministically selects Boolean independence pairs from a bounded
exhaustive analysis domain. `max_analysis_cases` bounds analysis and
`max_cases` independently bounds emitted cases.

Input names and values are canonically sorted. Strategy, domain, clause,
coverage, assignment, and universe digests participate in fixture identity.
Budget excess, duplicate values, sort mismatches, missing universes, and an
unsatisfied MC/DC independence condition fail closed.

## Negative-control discrimination

`domainspec-sfol-negative-control/v1` classifies declared known-bad controls
at semantic, derivation, binding, observation, lineage, scope, and provider
seams. Every control must have exactly one fault model and observation. A
required survivor, indeterminate result, invalid no-op control, detector
mismatch, or reason mismatch makes the detection-matrix gate fail.

## Optional AST mutation

`domainspec-sfol-mutation-catalog/v1` is an optional negative-control producer,
not the base adequacy definition. Its terminal states are:

- `killed`: a fixture distinguishes the mutant;
- `equivalent-bounded`: no fixture distinguishes it over a declared exhaustive
  finite domain;
- `survived`: no fixture distinguishes it over a non-exhaustive sample;
- `invalid-mutant`: the changed clause is not a valid evaluable mutant.

## Target and migration boundary

Neutral derivation does not construct an implementation's domain objects. A
target adapter maps semantic inputs to the real implementation and returns a
typed observation. Expected values always come from SFOL evaluation.

The additive Auth migration adapter is
`projects/auth-foundation/formalization/cases/AF-ADMIT-AUTHORIZATION-COMMAND-001/tde-api-adapter.ts`.
It owns only the Auth eight-case constraint. The Lean claim and historical v1
SFOL, EVF, and TDE carriers remain immutable predecessors.
