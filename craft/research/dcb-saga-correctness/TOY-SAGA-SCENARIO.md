# Toy Saga Scenario

Status: toy scenario
Date: 2026-06-15
Dispatch: `domainspec-v2-dcb-saga-correctness-research-20260615`

## Scenario

Use `OrderFulfillmentSaga`.

Participants:

- ordering
- payment
- inventory
- shipping

Forward operations:

- `CreateOrder`
- `AuthorizePayment`
- `ReserveInventory`
- `CreateShipment`

Compensation operations:

- `CancelOrder`
- `VoidPayment`
- `ReleaseInventory`
- `CancelShipment`

Policies:

- `RetryPolicy`
- `TimeoutPolicy`
- `DeadLetterPolicy`
- `CompensationOrderPolicy`

Non-rerunnable fact:

- `HumanWaiverApplied(waiver:ship-after-payment-timeout-v1)`

This waiver allows `CreateShipment` after a payment provider timeout when an
external authorization receipt exists. It is deliberately non-rerunnable because
it represents human authorization at a point in time.

## Behavioral Witness

Bounded run:

1. `CreateOrder` succeeds.
2. `AuthorizePayment` times out but records external receipt
   `ExternalEvidenceReceiptRecorded(payment-auth-provider-r42)`.
3. `HumanWaiverApplied(waiver:ship-after-payment-timeout-v1)` permits the saga
   to continue.
4. `ReserveInventory` succeeds.
5. `CreateShipment` fails.
6. Compensation should run for completed compensatable steps:
   `ReleaseInventory`, `VoidPayment`, `CancelOrder`.

Expected behavioral assertion:

```text
If CreateShipment fails after ReserveInventory succeeds, the saga cannot end in
success. It must either compensate completed steps or reach a policy-declared
terminal failure state.
```

## Freshness Witness

Claim:

```text
AcceptSagaProofFreshnessClaim(
  claim_id = order-fulfillment-saga-proof-c1,
  read_set = [
    SagaDeclared(OrderFulfillmentSaga),
    SagaStepDeclared(CreateShipment),
    CompensationOperationDeclared(ReleaseInventory),
    PolicyObserved(CompensationOrderPolicy),
    PropertyTestRunRecorded(run-ts-bounded-001),
    HumanWaiverApplied(waiver:ship-after-payment-timeout-v1),
    ExternalEvidenceReceiptRecorded(payment-auth-provider-r42)
  ],
  read_marker = per_dependency_hash_set(...)
)
```

Stale mutation:

```text
HumanWaiverApplied(waiver:ship-after-payment-timeout-v2)
```

or:

```text
PolicyObserved(CompensationOrderPolicy changed after run-ts-bounded-001)
```

Expected freshness result:

```text
Reject claim order-fulfillment-saga-proof-c1 because a matching non-rerunnable
waiver or policy fact changed after the read marker.
```

## Why This Toy Is Sufficient

It checks both sides of the research question:

- TypeScript can produce a bounded behavioral witness over saga traces.
- DCB adds value only at the acceptance boundary where a non-rerunnable waiver
  or external receipt participates in the claim.

If the waiver/external receipt is removed, the toy should downgrade to content
hash plus rerun-before-use.

