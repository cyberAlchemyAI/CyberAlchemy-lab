# Full suite verification

Verified on 11 October 2026 against the current Lab source.

| Command | Passed | Failed | Skipped |
| --- | ---: | ---: | ---: |
| `npm test` | 154 | 0 | 0 |
| `npm run test:contract` | 23 | 0 | 0 |
| **Total** | **177** | **0** | **0** |

The build also passes. Source and test bytes stayed unchanged throughout the run, and match the Lab checkout.

## Calculation results

- 4/5 → Accept; 5/5 → Reject; 6/5 → Reject, with available capacity remaining 5.
- All cases pass in the in-memory runtime and generated TypeScript, Python and Rust.
- Numeric v1 arithmetic, literals, division rounding, zero-divisor rejection, inexact division and underflow still pass across all four implementations.
- Lean 4.33.1 certifies the conditional Calculation's four-node, zero-edge finite model, as well as the existing complete numeric corpus. This is bounded model assurance, not a universal proof of runtime behavior.
- Craft and Lab documentation match execution; repeating the checker leaves generated targets unchanged.

## Lean and PostgreSQL fixes

Missing executables now produce useful errors rather than a secondary TypeError. Tests preflight native PostgreSQL clients and Docker, use the running Node executable, retain readiness diagnostics, and clean up their private container and anonymous volume. New tests exercise unavailable Lean, an incorrect Lean version and unavailable psql. The exact package contract includes these tests and the Calculation regressions.

Real PostgreSQL 16.15 clients were extracted from the pinned local image, with native binary/library hashes retained. No global installation was performed. The PostgreSQL integration test passes transaction, replay, rollback, lease, transport, retry, quarantine, requeue, deduplication, fresh-process CLI and receipt-schema checks.

The full-suite runner checks pinned providers before running the build, implementation suite and contract suite. It refuses a successful result if any test fails, any test is skipped or the source changes.

## Evidence and repetition

- [Execution record and source hashes](execution.json)
- [Implementation test log](tests.log)
- [Contract test log](contract-tests.log)
- [Build log](build.log)
- [Structured verification report](calculation-full-suite-verification.json)
- [Capacity behavior and documentation](behavior-and-documentation.json)
- [Native client manifest](postgres-client-manifest.json)

Use `tools/run-full-suite.mjs` with the pinned Lean bin directory, the native client cache bin directory and a new report directory. The recorded workspace is an isolated reconstruction of the copied checkout's migrated baseline, canonical formalization, fixtures and dependency layout. The checkout's missing migration paths are not silently fabricated or declared repaired.

The earlier partial-suite report remains historical. This run replaces its unavailable Lean/PostgreSQL status for the exact source tested here. Deployment, capacity reservation and Lab admission remain separate actions.
