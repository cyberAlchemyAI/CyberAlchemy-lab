# Relationship Fixture - bad State Machine enforces Operation

## Concept Registry

| Concept | Type |
| --- | --- |
| PaymentStatus | State Machine |
| ProcessPayment | Operation |

## Feature Concept Graph

| From | Edge | To |
| --- | --- | --- |
| PaymentStatus | enforces | ProcessPayment |
