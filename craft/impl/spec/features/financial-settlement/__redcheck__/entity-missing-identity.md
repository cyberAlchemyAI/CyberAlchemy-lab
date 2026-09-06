# Red-check — SettlementTransaction with NO identity (MUST FAIL)

Deliberate negative fixture for L0 (`SWU-APE-003`). The Entity criterion `identity`
(`at-least-one` Identity=yes, from `spec/meta-types/structural/entity.schema.yml`) must **reject**
this — the identity flag is dropped on purpose. Not named `SPEC.md`, so the walk mode skips it; run
it explicitly:

```
npx tsx tools/validate-content.ts --file spec/features/financial-settlement/__redcheck__/entity-missing-identity.md
```

Expected: non-zero exit with `criterion 'identity': no field flagged in column 'Identity'`.

## Concept Registry

| Concept | Type |
| --- | --- |
| SettlementTransaction | Entity |

## SettlementTransaction

| Field | Type | Required | Identity | Description |
| --- | --- | --- | --- | --- |
| transactionId | UUID | yes |  | identity flag dropped on purpose |
| amount | integer | yes |  | transaction amount |
