# Fixture — Value Object (valid)

Positive fixture for the Value Object criterion. Expected: **PASS**.

## Concept Registry
| Concept | Type |
| --- | --- |
| Money | Value Object |

## Money
A value defined entirely by its fields; no identity.

| Field | Type | Required | Identity | Description |
| --- | --- | --- | --- | --- |
| amount | Decimal | yes |  | numeric amount |
| currency | Currency | yes |  | ISO 4217 code |

**Equality:** two Money are equal iff `amount` and `currency` are equal.
