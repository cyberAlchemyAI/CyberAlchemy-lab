# Calculation support verification

This records the earlier partial run. The later [full-suite verification](full-suite-2026-10-11/FULL-SUITE.md) resolves the Lean and PostgreSQL limitations described below.

Verified on 11 October 2026 against the then-current Lab source.

| Requested / available | Decision | Available capacity after classification |
| --- | --- | --- |
| 4 / 5 | Accept | 5 |
| 5 / 5 | Reject | 5 |
| 6 / 5 | Reject | 5 |

All three cases pass in the in-memory runtime and the materialized TypeScript, Python and Rust implementations. Exact target observation and receipt JSON Schema checks pass in every generated language.

Numeric v1 compatibility passes in all four implementations: addition, subtraction, multiplication, literal expressions, floor and ceil division, exact division, and rejection of division by zero, inexact division and unsigned underflow. Tests also cover invalid conditional inputs, invalid contracts, deterministic receipts, typed dependencies and causal Rule changes.

## Changes made while testing

- Fixed Rust type inference for numeric literals nested inside arithmetic.
- Allowed Calculation typed contracts in the published instantiation-receipt schema.
- Replaced obsolete machine-specific test executable paths and updated the cross-document JSON Schema test resolver.
- Updated Craft draft 0.21 and the Lab guide to state the tested results, including strict equality rejection and unchanged snapshots.

## Scope and limitations

The final selected regression run has **144 passes, zero failures and one skipped Lean compilation check**, including **18 new Calculation tests**. The initial full-suite attempt also encountered unavailable Lean certification and PostgreSQL readiness; these external checks are not included in the successful regression result. The CLI build uses isolated staging with preserved migrated baseline, toolchain configuration and dependencies. It does not repair the checkout's missing dependency layout.

Classification is a pure derivation. Reservation, concurrent state changes, deployment and admission remain separate work.

## Evidence

- [Structured report](calculation-support-verification.json)
- [Capacity execution and documentation checks](behavior-and-documentation.json)
- [Final regression log](regression.tap)
- [Build log](build.log)
- [Initial full-suite attempt](initial-full-suite-attempt.log)

The permanent tests are `test/calculation-vertical.test.ts`, registered in `npm test`. The repeatable documentation checker is `tools/verify-calculation-documentation.mjs`; supply the documentation root and a new report path after building.
