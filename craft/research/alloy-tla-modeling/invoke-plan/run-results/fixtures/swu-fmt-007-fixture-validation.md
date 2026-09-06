# SWU-FMT-007 Fixture Validation Receipt

Timestamp: 2026-06-16T21:46:00Z
Result: pass

## Files

- `projects/domainspec-v2/research/alloy-tla-modeling/fixtures/formal-saga-fixture.schema.json`
- `projects/domainspec-v2/research/alloy-tla-modeling/fixtures/order-fulfillment.formal-fixture.json`
- `projects/domainspec-v2/research/alloy-tla-modeling/fixtures/README.md`

## Validation

Commands:

```bash
python3 -m json.tool projects/domainspec-v2/research/alloy-tla-modeling/fixtures/formal-saga-fixture.schema.json
python3 -m json.tool projects/domainspec-v2/research/alloy-tla-modeling/fixtures/order-fulfillment.formal-fixture.json
bash tools/check_markdown_links.sh projects/domainspec-v2/research/alloy-tla-modeling/fixtures/README.md
```

Result:

```text
OK: all markdown links resolve
fixture JSON and README links validated
```

## Review Notes

- The fixture preserves TypeScript `SagaSpec` participants, operations, policies, state machines, and relationship edges.
- Deterministic facts are classified with `mechanism: "hash"`.
- DCB waiver and external receipt facts are classified as `non-rerunnable`.
- The fixture records both current formal-model outcomes: Alloy bounded pass and TLA freshness counterexample residue.
