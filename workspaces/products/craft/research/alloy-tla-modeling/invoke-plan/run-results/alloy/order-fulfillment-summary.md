# Order Fulfillment Alloy Validation Summary

Timestamp: 2026-06-16T21:40:00Z
Result: pass-with-syntax-repair

## Inputs

- Model: `projects/domainspec-v2/research/alloy-tla-modeling/examples/OrderFulfillmentSaga.alloy`
- Command listing receipt: `order-fulfillment-commands.md`
- Execution receipt: `order-fulfillment-exec.md`
- JSON output directory: `order-fulfillment-output/`

## Syntax Repair

The first `commands` run failed because Alloy 6 treats `steps` as a reserved temporal-scope word. The model field was renamed from `steps` to `forwardSteps`; references were updated without changing graph-completeness semantics.

## Commands Discovered

```text
0 . Run showCompleteSaga for 8
1 . Run findMissingCompensation for 8
2 . Check checkCompensationCompleteness for 8
```

## Execution Result

Command:

```bash
projects/domainspec-v2/research/alloy-tla-modeling/tooling/run-alloy-check.sh \
  --receipt projects/domainspec-v2/research/alloy-tla-modeling/invoke-plan/run-results/alloy/order-fulfillment-exec.md \
  exec -f -t json \
  -o projects/domainspec-v2/research/alloy-tla-modeling/invoke-plan/run-results/alloy/order-fulfillment-output \
  -c '*' \
  projects/domainspec-v2/research/alloy-tla-modeling/examples/OrderFulfillmentSaga.alloy
```

Result:

```text
00. run   showCompleteSaga              1/1     SAT
01. run   findMissingCompensation       UNSAT
02. check checkCompensationCompleteness UNSAT
```

## Reading

- `showCompleteSaga` is satisfiable within scope 8.
- `findMissingCompensation` is unsatisfiable for the current complete graph because every forward operation has a compensation.
- `checkCompensationCompleteness` is unsatisfiable in Alloy's check output, meaning no counterexample was found within scope 8.

This is bounded Alloy evidence, not an unbounded proof.

## JSON Validation

`python3 -m json.tool` passed for:

```text
projects/domainspec-v2/research/alloy-tla-modeling/invoke-plan/run-results/alloy/order-fulfillment-output/receipt.json
```
