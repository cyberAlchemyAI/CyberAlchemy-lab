# Capacity classification — current example

This successor corrects the historical read-only Operation fixture. Operation remains a state-changing business action. No relationship signature or role criterion is broadened.

- Entity: supplied CapacitySnapshot record, with request identity and quantities.
- Rule: WithinCapacity, `requested_units < available_units`.
- Calculation: ClassifyCapacity, returning the payloadless Accept/Reject Enum under `domainspec.typed-calculation/v2`.
- Enum: CapacityDecision.

The Calculation explicitly binds the existing Rule through its expression and the snapshot through its input type. These are typed references, not `enforces` or `reads` graph edges. The latter signatures do not admit Calculation as their endpoint.

For 4 requested units and 5 available units, classification returns Accept and leaves the supplied snapshot unchanged. Equality and larger requests return Reject. Acceptance describes the snapshot, not a reservation.

A separate ReserveCapacity Operation would need a current-state guard and a coordinated state change: 5 available units become 1 and a 4-unit reservation is created. This example does not implement that storage transaction or deployment.

The original `test/fixtures/capacity-decision` is retained solely for historical compiler regression evidence. Its Operation label is superseded by this example.

## Contract scope

v1 numeric Calculations retain their UInt64 arithmetic and rounding contract. v2 adds one conditional expression, scalar or named record inputs, an existing typed Rule expression including rule_ref, and a named payloadless Enum result. Rust, TypeScript and Python source generation and the in-memory runtime share that declaration. Payload-bearing enum results, arbitrary numeric/enum expression mixtures and external effects are outside this v2 contract.

## Materialized outputs

`generated/rust`, `generated/typescript` and `generated/python` contain locally generated source and exact instantiation receipts. `example-invocation.json` records request R-104 (4/5); `example-runtime-receipt.json` records the local in-memory Calculation returning Accept. This is one example execution, not a regression-suite or deployment result.

The built Lab CLI is materialized at `craft/impl/cli/dist/cli/main.js`. The TypeScript source build used isolated staging with the preserved baseline and dependencies because the copied checkout's standard build lacks those paths. No dependency or frozen baseline was silently fabricated.

## Regression verification

The later [verification record](verification/VERIFICATION.md) covers 4/5 → Accept, 5/5 → Reject and 6/5 → Reject in the in-memory runtime and generated TypeScript, Python and Rust. All retain available capacity at 5. Numeric v1 arithmetic, rounding and rejection behavior also pass across those implementations. The earlier R-104 receipt above remains the original single execution record.

Permanent regressions live in `test/calculation-vertical.test.ts` and run through `npm test`. After building, `node tools/verify-calculation-documentation.mjs <absolute-documentation-root> <new-absolute-report-path>` independently checks the materialized capacity sources, execution results and the Craft/Lab articles. The documentation root contains the `craft-documentation-proposal` and `governance-lab-series` folders.

## Full-suite follow-up

The [full verification](verification/full-suite-2026-10-11/FULL-SUITE.md) resolves the earlier Lean and PostgreSQL test limitations: 154 implementation tests and 23 contract tests pass, with zero failures and zero skips. The partial-run record above remains historical.
