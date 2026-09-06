---
id: financial-settlement-observability-report
feature: financial-settlement
title: Financial Settlement Observability Alignment Report
summary: Static OTel coverage audit for financial-settlement against the feature observability contract.
status: in-progress
pillar: finance
domain: financial-settlement-observability
audience:
  - developers
priority: p1
lang: en
owners:
  - backend-core
updatedAt: 2026-04-30
dependencies:
  - observability.md
  - operations.md
includes: []
---

# Financial Settlement Observability Alignment Report

> Compares declared obligations in [observability.md](observability.md) against static code evidence under backend/src.
> Verification mode: static only (no live collector query).

## Summary

| Metric | Status | Detail |
| --- | --- | --- |
| Total declared instruments | 27 | From [observability.md](observability.md) declarations |
| Instrumented in code | 22 | ✅ Found with matching type and required attributes |
| Partially instrumented | 3 | ⚠️ Found with type/attribute drift |
| Missing from code | 2 | ❌ Declared but no recording evidence found |
| Extra (undeclared) | 5 | 🔄 Recorded in code but not declared in observability.md |

**Verdict:** FLAG

Coverage is 92.6% (25/27) including partials.

## Coverage by Rule

| Rule | Declared | Instrumented | Status | Notes |
| --- | --- | --- | --- | --- |
| O4 | 2 | 2 | PASS | All declared obligations evidenced |
| O8 | 1 | 0 | PARTIAL | 1 partial |
| O9 | 3 | 3 | PASS | All declared obligations evidenced |
| O10 | 3 | 1 | FAIL | 2 missing |
| O12 | 4 | 4 | PASS | All declared obligations evidenced |
| O13 | 5 | 3 | PARTIAL | 2 partial |
| O15 | 3 | 3 | PASS | All declared obligations evidenced |
| O16 | 6 | 6 | PASS | All declared obligations evidenced |

## Instrument Detail

| Instrument Name | Type | Source Rule | Code Location | Status | Issue |
| --- | --- | --- | --- | --- | --- |
| `operation.invocation` | Counter | O4 | `backend/src/use-cases/financial-settlement/generate-settlement.ts:572` | ✅ | — |
| `operation.duration` | Histogram | O4 | `backend/src/use-cases/financial-settlement/generate-settlement.ts:578` | ✅ | — |
| `http.server.request.duration` | Histogram | O8 | `backend/src/infrastructure/telemetry/metrics-plugin.ts:21` | ⚠️ | missing required attrs: feature=financial-settlement |
| `idempotency.violation` | Gauge | O9 | `backend/src/use-cases/financial-settlement/generate-settlement.ts:268` | ✅ | — |
| `idempotency.dedup` | Counter | O9 | `backend/src/use-cases/financial-settlement/generate-settlement.ts:311` | ✅ | — |
| `exposure.amount` | Gauge | O9 | `backend/src/use-cases/financial-settlement/generate-settlement.ts:254` | ✅ | — |
| `event.emit` | Counter | O10 | `backend/src/use-cases/financial-settlement/generate-settlement.ts:425` | ✅ | — |
| `event.consume` | Counter | O10 | `—` | ❌ | No recording call found |
| `event.consumer.lag` | Histogram | O10 | `—` | ❌ | No recording call found |
| `workflow.invocation` | Counter | O12 | `backend/src/use-cases/financial-settlement/generate-settlement.ts:583` | ✅ | — |
| `workflow.duration` | Histogram | O12 | `backend/src/use-cases/financial-settlement/generate-settlement.ts:589` | ✅ | — |
| `workflow.failed` | Counter | O12 | `backend/src/use-cases/financial-settlement/generate-settlement.ts:555` | ✅ | — |
| `workflow.step.duration` | Histogram | O12 | `backend/src/use-cases/financial-settlement/generate-settlement.ts:115` | ✅ | — |
| `business.settlements_executed` | Counter | O13 | `backend/src/use-cases/financial-settlement/generate-settlement.ts:504` | ✅ | — |
| `business.payout_amount` | Counter | O13 | `backend/src/use-cases/financial-settlement/generate-settlement.ts:508` | ✅ | — |
| `business.makeup_recovered` | Counter | O13 | `backend/src/use-cases/financial-settlement/generate-settlement.ts:512` | ✅ | — |
| `business.avg_settlement_value` | Gauge | O13 | `backend/src/use-cases/financial-settlement/generate-settlement.ts:519` | ⚠️ | type mismatch: expected Gauge, found Histogram |
| `business.preview_before_settlement` | Gauge | O13 | `backend/src/use-cases/financial-settlement/generate-settlement.ts:525` | ⚠️ | type mismatch: expected Gauge, found Histogram |
| `reconciliation.mismatch` | Gauge | O15 | `backend/src/use-cases/financial-settlement/generate-settlement.ts:374` | ✅ | — |
| `transaction.duplicate` | Counter | O15 | `backend/src/use-cases/financial-settlement/generate-settlement.ts:262` | ✅ | — |
| `exposure.amount` | Gauge | O15 | `backend/src/use-cases/financial-settlement/generate-settlement.ts:254` | ✅ | — |
| `settlement.cycle.invocations` | Counter | O16 | `backend/src/use-cases/financial-settlement/generate-settlement.ts:485` | ✅ | — |
| `settlement.cycle.payout_amount` | Counter | O16 | `backend/src/use-cases/financial-settlement/generate-settlement.ts:488` | ✅ | — |
| `settlement.cycle.makeup_applied` | Counter | O16 | `backend/src/use-cases/financial-settlement/generate-settlement.ts:494` | ✅ | — |
| `settlement.cycle.avg_value` | Gauge | O16 | `backend/src/use-cases/financial-settlement/generate-settlement.ts:500` | ✅ | — |
| `settlement.cycle.error_rate` | Gauge | O16 | `backend/src/use-cases/financial-settlement/generate-settlement.ts:530` | ✅ | — |
| `settlement.recalculation.drift` | Gauge | O16 | `backend/src/use-cases/financial-settlement/generate-settlement.ts:222` | ✅ | — |

## Undeclared Metrics

- `calculation.drift`
- `postcondition.check`
- `query.duration`
- `query.result_size`
- `rule.violation`

## Change Requests

| # | Priority | Action | Target File | Instrument | Detail |
| --- | --- | --- | --- | --- | --- |
| 1 | P1 | Add | `backend/src/use-cases/financial-settlement/generate-settlement.ts` | `event.consume` | No recording call found |
| 2 | P1 | Add | `backend/src/use-cases/financial-settlement/generate-settlement.ts` | `event.consumer.lag` | No recording call found |
| 3 | P1 | Fix | `backend/src/infrastructure/telemetry/metrics-plugin.ts` | `http.server.request.duration` | missing required attrs: feature=financial-settlement |
| 4 | P2 | Fix | `backend/src/use-cases/financial-settlement/generate-settlement.ts` | `business.avg_settlement_value` | type mismatch: expected Gauge, found Histogram |
| 5 | P3 | Fix | `backend/src/use-cases/financial-settlement/generate-settlement.ts` | `business.preview_before_settlement` | type mismatch: expected Gauge, found Histogram |

## Next Actions

1. Run `domainspec-instrument-otel financial-settlement --change-requests docs/features/financial-settlement/OBSERVABILITY-REPORT.md`.
2. Re-run `domainspec-otel-verify financial-settlement` to confirm coverage.
3. If verdict is PASS, proceed to `domainspec-verify-feature`.
