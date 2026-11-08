# Toy Run Result: OrderFulfillmentSaga

Status: pass
Witness kind: bounded
Recommendation: borrow-carefully

## Summary

| Check | Result |
| --- | --- |
| Graph witness | flag |
| Behavioral witness | pass |
| Freshness claim | rejected |
| Command | AcceptSagaProofFreshnessClaim |
| Deterministic fact mechanism | per-dependency-hash |
| Non-rerunnable fact | HumanWaiverApplied:waiver:ship-after-payment-timeout-v1 |

## Graph Residue

- orchestrates signature for Saga is residue: RELATIONSHIPS.md types orchestrates as Workflow -> Operation[].

## Bounded Trace

1. forward: CreateOrder -> success
2. forward: AuthorizePayment -> timeout (ExternalEvidenceReceiptRecorded:payment-auth-provider-r42)
3. waiver: HumanWaiverApplied:waiver:ship-after-payment-timeout-v1 -> waived (ExternalEvidenceReceiptRecorded:payment-auth-provider-r42)
4. forward: ReserveInventory -> success
5. forward: CreateShipment -> failed
6. compensation: ReleaseInventory -> compensated
7. compensation: VoidPayment -> compensated
8. compensation: CancelOrder -> compensated
9. terminal: DeadLetterPolicy -> terminal-failure (CreateShipment failed after ReserveInventory succeeded)

## Behavioral Assertions

| Assertion | Result | Detail |
| --- | --- | --- |
| success-not-accepted-after-shipment-failure | pass | CreateShipment failed; the bounded run must not accept saga success. |
| completed-compensatable-steps-compensated | pass | Expected compensations: ReleaseInventory, VoidPayment, CancelOrder. |
| missing-compensation-detected | pass | Removing ReleaseInventory from ReserveInventory must produce a graph violation. |

## Read Set

| Fact | Mechanism | Marker |
| --- | --- | --- |
| SagaDeclared:OrderFulfillmentSaga | hash | 38986d2966bed44c... |
| SagaStepDeclared:CreateShipment | hash | c4bad0dcd6e3cd12... |
| CompensationOperationDeclared:ReleaseInventory | hash | cc4e2849f445d169... |
| PolicyObserved:CompensationOrderPolicy | hash | 363bb57329f8eba1... |
| PropertyTestRunRecorded:run-ts-bounded-001 | hash | e1f87b1a8a275596... |
| HumanWaiverApplied:waiver:ship-after-payment-timeout-v1 | dcb | 60a40fc4dc10aa27... |
| ExternalEvidenceReceiptRecorded:payment-auth-provider-r42 | dcb | 085963f6fb7dbf92... |

## Freshness Verdict

REJECTED: Non-rerunnable fact HumanWaiverApplied:ship-after-payment-timeout changed after the read marker; DCB freshness rejects acceptance.

Stale fact: HumanWaiverApplied:waiver:ship-after-payment-timeout-v1
Current fact: HumanWaiverApplied:waiver:ship-after-payment-timeout-v2

## Notes

- This is a TypeScript bounded witness, not a formal proof.
- DCB guards acceptance freshness; it does not prove saga behavior.
- Saga orchestrates relationship signature is preserved as residue instead of mutating RELATIONSHIPS.md.
