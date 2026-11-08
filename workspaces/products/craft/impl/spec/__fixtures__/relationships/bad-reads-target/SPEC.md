# Relationship Fixture - reads requires an Entity target

## Concept Registry

| Concept | Type |
| --- | --- |
| GetPaymentHistory | Query |
| RetryPolicy | Policy |

## Feature Concept Graph

| From | Edge | To |
| --- | --- | --- |
| GetPaymentHistory | reads | RetryPolicy |
