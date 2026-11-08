# Order Fulfillment TLA+ Validation Summary

Timestamp: 2026-06-16T21:37:00Z
Result: counterexample-captured

## Commands

- SANY parse receipt: `order-fulfillment-sany.md`
- TLC safety receipt: `order-fulfillment-tlc-safety.md`
- Config: `projects/domainspec-v2/research/alloy-tla-modeling/examples/OrderFulfillmentSaga.cfg`

## Outcome

- SANY parsed `OrderFulfillmentSaga.tla` successfully.
- TLC ran with `SPECIFICATION Spec` and invariants `SuccessSafety`, `FailureSafety`, and `FreshnessSafety`.
- TLC found a violation of `FreshnessSafety`.

## Counterexample Reading

The counterexample reaches `Accepted` while `waiverRead = waiverCurrent`, then allows `WaiverChangesAfterRead` to change `waiverCurrent` afterward while `status` remains `Accepted`.

That means the sketch currently permits a stale accepted claim after acceptance. This is useful repair residue for the freshness guard boundary; it should not be labeled proof.

## Next Repair Options

- Restrict `WaiverChangesAfterRead` so it cannot occur after terminal acceptance.
- Move freshness acceptance into a terminal absorbing state.
- Split accepted proof freshness from later world changes with an explicit validity interval.
- Treat `FreshnessSafety` as an acceptance-time property instead of an always-after property, if that is the intended semantics.
