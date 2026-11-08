# Check that checks really ran

## Purpose

Prevent a green job caused by missing tools, skipped cases or an empty comparison.

## Layer and recognition

Testing and CI evidence. OO_REQUIRE_FIXTURES, SKIPPED_FIXTURE, ci_gate_coverage_test and dedicated checker jobs.

## Contract and dependencies

Observed: strict-fixture jobs, skip-coverage accounting and mutation gates distinguish actual checking from absent/declined work.

Observed dependencies: declared fixture/tool inventory, strict jobs and test collection. Installing a feature is not evidence that a test exercised it.

## Testing obligations

Remove required checker; omit collection; supply empty corpus; corrupt a valid proof; require the expected failure.

## Observable evidence

Ran/skipped/not-run counts, compared-case counts, tool/profile identity, deliberate opt-ins and baseline differences.

## Source and limits

[CI skip-coverage checks](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/tests/ci_gate_coverage_test.rs#L1); [docs/ci-gates.md](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/docs/ci-gates.md#L1).

A benchmark target that swallows errors can still report success. Source CI configuration was inspected here, not run.
