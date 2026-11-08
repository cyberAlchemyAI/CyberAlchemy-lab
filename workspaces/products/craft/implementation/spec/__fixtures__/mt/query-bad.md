# Fixture — Query (invalid: mutates state → is an Operation)

Declared Query but `state_change=yes`. Expected: **REJECTED as Query**.

## Concept Registry
| Concept | Type |
| --- | --- |
| ChargeCard | Query |

## ChargeCard
| Attribute | Value |
| --- | --- |
| state_change | yes |
