# Fixture — Entity (invalid: Value-Object-shaped)

Negative fixture: declared **Entity** but with NO identity field and an Equality clause — it is really a
Value Object. Expected: **REJECTED as Entity**.

## Concept Registry
| Concept | Type |
| --- | --- |
| Money | Entity |

## Money
| Field | Type | Required | Identity | Description |
| --- | --- | --- | --- | --- |
| amount | Decimal | yes |  | numeric amount |
| currency | Currency | yes |  | ISO 4217 currency code |

**Equality:** two Money are equal iff `amount` and `currency` are equal.
