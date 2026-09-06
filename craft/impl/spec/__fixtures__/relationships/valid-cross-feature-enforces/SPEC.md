# Relationship Fixture - valid cross-feature enforces

## Concept Registry

| Concept | Type |
| --- | --- |
| compliance.AccessRule | Rule |
| payments.ProcessRefund | Operation |

## Cross-Feature Dependencies

| From | Edge | To |
| --- | --- | --- |
| compliance.AccessRule | enforces | payments.ProcessRefund |

## payments.ProcessRefund

| Attribute | Value |
| --- | --- |
| state_change | yes |
