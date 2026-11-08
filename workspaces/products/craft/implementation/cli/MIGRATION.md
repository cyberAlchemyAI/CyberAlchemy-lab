# Migration to 1.0

1. Replace package version `0.0.0-candidate.5` with `1.0.0`.
2. Replace current compiler/assurance schema identifiers ending in `-candidate` with their stable identifier shown by 1.0 output.
3. Import runtime APIs from `@domainspec-v2/cli/experimental/runtime`; the package root now contains stable compiler-product APIs only.
4. Run `domainspec-v2 capabilities`, then `domainspec-v2 doctor`.
5. Recompile, regenerate, and recertify from authored source. Candidate-era compiled graphs and certificates are intentionally not accepted as 1.0 artifacts.

Frozen predecessor foundation-contract files retain their original names and bytes. They are historical inputs, not 1.0 package output contracts.

## Explicit source-contract migrations

The stable package root exports three pure migration helpers for the source
contracts that need caller-supplied meaning:

- `migrateTypedPolicyV1(source, ruleNames)` extracts each legacy inline Policy
  predicate into an explicitly named Rule and returns the candidate Policy and
  Rules.
- `migrateLegacyStateMachine(source, bindings)` requires a trigger and the
  applicable guard/output bindings for every legacy transition and returns a
  candidate typed State Machine plus the relationship review.
- `planWorkflowOccurrenceMigration(graph, selector, selection)` assigns explicit
  step and compensation occurrence identities to one checked legacy Workflow.

All three functions return reviewable candidate data. They do not edit source,
add graph relationships, register a replacement graph, publish output, or change
the compiler default. Apply a reviewed candidate in caller-controlled source,
then run normal project validation and compilation. Ambiguous, incomplete,
coercive, stale, or version-incompatible inputs fail instead of being guessed.
