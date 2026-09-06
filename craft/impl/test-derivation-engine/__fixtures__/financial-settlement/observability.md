---
id: financial-settlement
feature: financial-settlement
type: observability
title: "Financial Settlement — Observability Spec"
summary: Observability contract for settlement generation, payout calculations, and financial integrity safeguards.
derived-from: OBSERVABILITY.md rules O1–O16
status: draft
pillar: finance
domain: financial-settlement-observability
audience:
  - developers
  - finance
priority: p1
lang: en
owners:
  - finance-core
  - backend-core
updatedAt: 2026-04-17
dependencies:
  - SPEC.md
  - operations.md
includes: []
---

# Financial Settlement — Observability Spec

> Derived from feature docs using [OBSERVABILITY.md](../../../domainspec/OBSERVABILITY.md) derivation rules.
> Instrumented via OpenTelemetry API. Meter scope: `poker-team`. All instruments carry `feature: financial-settlement`.
> Financial-pillar features have mandatory integrity monitors (O15–O16).

---

## Domain Fidelity Metrics

### Operation Metrics (O4–O7)

#### GenerateSettlement

**Base metrics (O4):**

*@source [operations.md#GenerateSettlement](operations.md#GenerateSettlement)*

```yaml
# Counts each call to GenerateSettlement, grouped by success or error outcome
- name: operation.invocation
  instrument: Counter
  unit: "{invocation}"
  description: "Counts each call to GenerateSettlement, grouped by success or error outcome"
  attributes:
    {
      feature: financial-settlement,
      operation: GenerateSettlement,
      result: success|error,
    }

# Measures execution time of GenerateSettlement in seconds
- name: operation.duration
  instrument: Histogram
  unit: "s"
  description: "Measures execution time of GenerateSettlement in seconds"
  attributes: { feature: financial-settlement, operation: GenerateSettlement }
```

**Rule violation rates (O5):**

| Rule | Expression                                                   | Instrument                                | Alert Threshold                           |
| ---- | ------------------------------------------------------------ | ----------------------------------------- | ----------------------------------------- |
| R1   | `exists(Player.id == playerId)`                              | `rule.violation` Counter `{rule_id="R1"}` | rate > 5% of attempts → P2                |
| R2   | `playerId != null and startDate != null and endDate != null` | `rule.violation` Counter `{rule_id="R2"}` | rate > 1% → P2 (upstream issue)           |
| R3   | `startDate <= stats.date <= endDate`                         | `rule.violation` Counter `{rule_id="R3"}` | informational                             |
| R4   | `count(tx[type=MAKEUP_APPLIED,date=endDate]) <= 1`           | `rule.violation` Counter `{rule_id="R4"}` | **any > 0 → P0** (duplicate financial tx) |
| R5   | `count(tx[type=PAYOUT,date=endDate]) <= 1`                   | `rule.violation` Counter `{rule_id="R5"}` | **any > 0 → P0** (duplicate payout)       |

**Calculation drift (O6):**

| Calc | Formula                                        | Instrument                                            | Frequency             | Alert          |
| ---- | ---------------------------------------------- | ----------------------------------------------------- | --------------------- | -------------- |
| C1   | `sum(relevantRecords.profit)`                  | `calculation.drift` Histogram `{calculation_id="C1"}` | After each settlement | drift > 0 → P0 |
| C2   | `sum(relevantRecords.rakeback)`                | `calculation.drift` Histogram `{calculation_id="C2"}` | After each settlement | drift > 0 → P0 |
| C3   | `playerShare = limit >= NL100 ? 0.5 : 0.4`     | `calculation.drift` Histogram `{calculation_id="C3"}` | After each settlement | drift > 0 → P0 |
| C4   | `applyMakeupPolicy(debt, C1, C2, playerShare)` | `calculation.drift` Histogram `{calculation_id="C4"}` | After each settlement | drift > 0 → P0 |

> C1–C4 drift is **P0** because any miscalculation directly causes over/under-payment.

**Postcondition verification (O7):**

| Postcondition                      | Instrument                                                                     | Alert                    |
| ---------------------------------- | ------------------------------------------------------------------------------ | ------------------------ |
| Returns one SettlementResult       | `postcondition.check` Counter `{postcondition_id="result_returned", result}`   | any result=violated → P1 |
| Makeup updated when changed        | `postcondition.check` Counter `{postcondition_id="makeup_updated", result}`    | any result=violated → P0 |
| MAKEUP_APPLIED tx created (no dup) | `postcondition.check` Counter `{postcondition_id="makeup_tx_created", result}` | any result=violated → P0 |
| PAYOUT tx created (no dup)         | `postcondition.check` Counter `{postcondition_id="payout_tx_created", result}` | any result=violated → P0 |

---

## Operational Health Metrics

### Endpoint SLOs (O8)

*@source [interfaces.md#external-settlementapi-rest](interfaces.md#external-settlementapi-rest)*

| Endpoint               | Method | Availability SLO | Latency p99 SLO | Throughput Baseline |
| ---------------------- | ------ | ---------------- | --------------- | ------------------- |
| `/settlements`         | POST   | ≥ 99.9%          | ≤ 2000ms        | ~50 req/day         |
| `/settlements/preview` | GET    | ≥ 99.9%          | ≤ 500ms         | ~200 req/day        |

*@source [interfaces.md#external-settlementapi-rest](interfaces.md#external-settlementapi-rest)*

```yaml
# Uses OTel HTTP semantic conventions with custom `feature` attribute:
- name: http.server.request.duration # OTel semconv
  instrument: Histogram
  unit: "s"
  attributes:
    {
      http.request.method: POST|GET,
      url.path: /settlements|/settlements/preview,
      http.response.status_code: int,
      feature: financial-settlement,
    }
```

### Idempotency Monitors (O9)

| Rule | Constraint                                      | Instrument                                                                   | Alert            |
| ---- | ----------------------------------------------- | ---------------------------------------------------------------------------- | ---------------- |
| R4   | `count(MAKEUP_APPLIED, playerId, endDate) <= 1` | `idempotency.violation` Gauge `{operation: GenerateSettlement, rule_id: R4}` | **any > 0 → P0** |
| R5   | `count(PAYOUT, playerId, endDate) <= 1`         | `idempotency.violation` Gauge `{operation: GenerateSettlement, rule_id: R5}` | **any > 0 → P0** |

*@source [operations.md#GenerateSettlement](operations.md#GenerateSettlement) rules R4, R5*

```yaml
# @rule O9: Idempotency Monitor
# Detects duplicate operations that violate idempotency constraints
- name: idempotency.violation
  instrument: Gauge
  unit: "{violation}"
  description: "Detects duplicate operations that violate idempotency constraints"
  attributes:
    {
      feature: financial-settlement,
      operation: GenerateSettlement,
      rule_id: R4|R5,
    }
  check: "periodic scan — group transactions by (type, playerId, date), flag count > 1"
  frequency: every 15 minutes
  alert:
    condition: value > 0
    severity: P0
    runbook: |
      1. Query settlement_events WHERE player_id AND date GROUP BY type HAVING count > 1
      2. Identify which settlement execution created the duplicate
      3. Compare transaction amounts — if identical, safe to soft-delete duplicate
      4. If amounts differ, escalate to finance lead — manual reconciliation required

# Counts how many times dedup logic successfully prevented a duplicate
- name: idempotency.dedup
  instrument: Counter
  unit: "{dedup}"
  attributes:
    {
      feature: financial-settlement,
      operation: GenerateSettlement,
      rule_id: R4|R5,
    }
  purpose: "tracks how often dedup logic prevents a repeat execution"
```

**Monetary exposure estimation:**

```yaml
# Estimates total monetary exposure from detected duplicate transactions
- name: exposure.amount
  instrument: Gauge
  unit: "{currency_minor}" # BRL cents
  description: "Estimates total monetary exposure from detected duplicate transactions"
  attributes: { feature: financial-settlement, operation: GenerateSettlement }
  formula: "sum(amount) WHERE duplicate detected"
  alert: value > 0 → P0 with estimated R$ impact in alert body
```

### Event Flow (O10)

| Event               | Producer           | Consumers         | Lag SLO |
| ------------------- | ------------------ | ----------------- | ------- |
| SettlementGenerated | GenerateSettlement | finance reporting | ≤ 5s    |
| PayoutCreated       | GenerateSettlement | accounting        | ≤ 5s    |

*@source [events.md](events.md)*

```yaml
# Counts domain events published by this feature
- name: event.emit # Counter {feature: financial-settlement, event_type: SettlementGenerated|PayoutCreated}
# Counts domain events consumed by downstream listeners
- name: event.consume # Counter {feature: financial-settlement, event_type, consumer}
# Measures delay in seconds between event publish time and consumer processing
- name: event.consumer.lag # Histogram (s) {feature: financial-settlement, event_type, consumer}
```

### Query Performance (O11)

*@source [interfaces.md#external-settlementapi-rest](interfaces.md#external-settlementapi-rest)*

| Query                | p95 Latency SLO | Max Result Size | Cache TTL                   |
| -------------------- | --------------- | --------------- | --------------------------- |
| GetSettlementPreview | ≤ 200ms         | 1 row           | 0 (no cache — always fresh) |

### Workflow Completion (O12)

*@source [workflows.md#SettlementWorkflow](workflows.md#SettlementWorkflow)*

```yaml
# Counts end-to-end SettlementWorkflow executions, grouped by outcome
- name: workflow.invocation
  instrument: Counter
  unit: "{invocation}"
  description: "Counts end-to-end SettlementWorkflow executions, grouped by outcome"
  attributes:
    {
      feature: financial-settlement,
      workflow: SettlementWorkflow,
      result: completed|failed,
    }

# Measures total wall-clock time for SettlementWorkflow execution
- name: workflow.duration
  instrument: Histogram
  unit: "s"
  description: "Measures total wall-clock time for SettlementWorkflow execution"
  attributes: { feature: financial-settlement, workflow: SettlementWorkflow }

# Counts SettlementWorkflow failures, tagged by the step where failure occurred
- name: workflow.failed
  instrument: Counter
  unit: "{failure}"
  description: "Counts SettlementWorkflow failures, tagged by the step where failure occurred"
  attributes:
    {
      feature: financial-settlement,
      workflow: SettlementWorkflow,
      failed_at_step: validate_request|load_dependencies|compute_policy|persist_side_effects,
    }

- name: workflow.step.duration
  instrument: Histogram
  unit: "s"
  attributes:
    {
      feature: financial-settlement,
      workflow: SettlementWorkflow,
      step_name: validate_request|load_dependencies|compute_policy|persist_side_effects,
    }
```

**Workflow invariant monitors:**

| ID  | Invariant                          | Check                                   | Alert              |
| --- | ---------------------------------- | --------------------------------------- | ------------------ |
| I1  | Makeup debt cannot be negative     | `newMakeup >= 0` after every settlement | any violation → P0 |
| I2  | No duplicate payout per period end | `count(PAYOUT where date=endDate) <= 1` | any violation → P0 |

---

## Business Effectiveness Metrics

### Capability KPIs (O13)

#### Settlement Execution

*@source [operations.md#GenerateSettlement](operations.md#GenerateSettlement) capability*

```yaml
- name: business.settlements_executed
  instrument: Counter
  unit: "{settlement}"
  attributes: { feature: financial-settlement, capability: GenerateSettlement }
  business_question: "How many settlements are we processing daily?"
  healthy_range: "> 0 on business days"
  alert: 0 settlements on business day → P2

- name: business.payout_amount
  instrument: Counter
  unit: "{currency_minor}" # BRL cents
  attributes: { feature: financial-settlement, capability: GenerateSettlement }
  business_question: "How much are we paying out daily?"
  healthy_range: "within 2 stddev of 30-day moving average"
  alert: deviation > 2 stddev → P2 (unusual payout volume)

- name: business.makeup_recovered
  instrument: Counter
  unit: "{currency_minor}" # BRL cents
  attributes: { feature: financial-settlement, capability: GenerateSettlement }
  business_question: "How much debt are we recovering daily?"
  healthy_range: "trending stable or down (debt being paid off)"

- name: business.avg_settlement_value
  instrument: Gauge
  unit: "{currency_minor}" # BRL cents
  attributes: { feature: financial-settlement, capability: GenerateSettlement }
  business_question: "What is the average settlement size?"
  healthy_range: "within historical range"
```

#### Settlement Preview Usage

```yaml
- name: business.preview_before_settlement
  instrument: Gauge
  unit: "1" # ratio
  attributes:
    { feature: financial-settlement, capability: GetSettlementPreview }
  formula: "previews in 1h before settlement / total settlements"
  business_question: "Are operators previewing before executing?"
  healthy_range: "> 80% (operators should preview first)"
  alert: ratio < 50% → P3 (operators skipping preview)
```

---

## Financial Integrity Metrics (O15–O16)

### Transaction Integrity (O15)

*@source [operations.md#GenerateSettlement](operations.md#GenerateSettlement), [OBSERVABILITY.md rule O15](../../../domainspec/OBSERVABILITY.md)*

```yaml
# Mandatory for pillar: finance

# Detects discrepancies between computed (from event replay) and stored financial values
- name: reconciliation.mismatch
  instrument: Gauge
  unit: "{currency_minor}" # BRL cents
  description: "Detects discrepancies between computed (from event replay) and stored financial values"
  attributes: { feature: financial-settlement, entity: Player }
  check: |
    For each player with settlements in the period:
      computed_makeup = replay all MAKEUP_APPLIED transactions
      stored_makeup = Player.makeup current value
      mismatch = |computed_makeup - stored_makeup|
  frequency: hourly
  alert: mismatch > 0 → P0
  runbook: |
    1. Identify affected player(s)
    2. Replay transaction log to determine correct makeup value
    3. Compare with current stored value
    4. If stored > computed: player is being overcharged (fix immediately)
    5. If stored < computed: team is losing money (fix within 1 hour)

# Detects duplicate financial transactions that violate uniqueness constraints
- name: transaction.duplicate
  instrument: Counter
  unit: "{duplicate}"
  description: "Detects duplicate financial transactions that violate uniqueness constraints"
  attributes:
    { feature: financial-settlement, transaction_type: MAKEUP_APPLIED|PAYOUT }
  check: |
    SELECT player_id, type, date, COUNT(*)
    FROM settlement_events
    GROUP BY player_id, type, date
    HAVING COUNT(*) > 1
  frequency: every 15 minutes
  alert: any increment → P0

# Estimates total monetary exposure from detected duplicate transactions
- name: exposure.amount
  instrument: Gauge
  unit: "{currency_minor}" # BRL cents
  description: "Estimates total monetary exposure from detected duplicate transactions"
  attributes: { feature: financial-settlement }
  check: "sum of potentially duplicated transaction amounts"
  alert: exposure > 0 → P0 with R$ amount in alert body
```

### Settlement Cycle Metrics (O16)

*@source [workflows.md#SettlementWorkflow](workflows.md#SettlementWorkflow), [OBSERVABILITY.md rule O16](../../../domainspec/OBSERVABILITY.md)*

```yaml
- name: settlement.cycle.invocations # Counter {feature: financial-settlement}
- name: settlement.cycle.payout_amount # Counter {currency_minor} {feature: financial-settlement}
- name: settlement.cycle.makeup_applied # Counter {currency_minor} {feature: financial-settlement}
- name: settlement.cycle.avg_value # Gauge {currency_minor} {feature: financial-settlement}
- name: settlement.cycle.error_rate # Gauge (ratio) {feature: financial-settlement}

# Drift detection — recompute all calculations and compare:
- name: settlement.recalculation.drift
  instrument: Gauge
  unit: "{currency_minor}"
  attributes: { feature: financial-settlement, calculation_id: C1|C2|C4 }
  check: |
    For the last batch of settlements:
      recompute C1 (total profit) from raw stat records
      recompute C2 (total rakeback) from raw stat records
      recompute C4 (makeup policy) from recomputed inputs
      compare with stored settlement results
  frequency: after each settlement batch
  alert: drift > 0 → P0 (money is being miscalculated)
```

---

## Metric Summary

| Rule                                                           | Metric Count                     | Layer                  | Severity              |
| -------------------------------------------------------------- | -------------------------------- | ---------------------- | --------------------- |
| O4: GenerateSettlement execution                               | 2 (invocation + duration)        | Operational            | P1                    |
| O5: Rule violations (R1–R5)                                    | 5                                | Domain Fidelity        | R4/R5 = P0, others P2 |
| O6: Calculation drift (C1–C4)                                  | 4                                | Domain Fidelity        | P0                    |
| O7: Postconditions                                             | 4                                | Domain Fidelity        | P0–P1                 |
| O8: Endpoint SLOs                                              | 1 (OTel HTTP semconv)            | Operational            | P1                    |
| O9: Idempotency (R4, R5)                                       | 3 (violation + dedup + exposure) | Financial Integrity    | P0                    |
| O10: Event flow                                                | 3 (emit + consume + lag)         | Operational            | P1                    |
| O11: Query performance                                         | 1                                | Operational            | P2                    |
| O12: Workflow completion                                       | 4                                | Operational            | P1                    |
| O13: Business KPIs                                             | 5                                | Business Effectiveness | P2–P3                 |
| O15: Transaction integrity                                     | 3                                | Financial Integrity    | P0                    |
| O16: Settlement cycle                                          | 6                                | Financial Integrity    | P0                    |
| **Total**                                                      | **~41 instruments**              |                        |                       |
