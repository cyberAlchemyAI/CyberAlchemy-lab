# Fixture — Value Object (invalid: identity-bearing → is an Entity)

Negative fixture: declared **Value Object** but has an identity field. Expected: **REJECTED as Value Object**.

## Concept Registry
| Concept | Type |
| --- | --- |
| Account | Value Object |

## Account
| Field | Type | Required | Identity | Description |
| --- | --- | --- | --- | --- |
| id | UUID | yes | yes | account identity |
| balance | Money | yes |  | current balance |

**Equality:** two Account are equal iff `id` matches.
