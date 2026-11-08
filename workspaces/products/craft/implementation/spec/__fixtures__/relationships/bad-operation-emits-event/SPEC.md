# Relationship Fixture - bad Operation emits Event

## Concept Registry

| Concept | Type |
| --- | --- |
| ProcessPayment | Operation |
| PaymentCompleted | Event |

## Feature Concept Graph

| From | Edge | To |
| --- | --- | --- |
| ProcessPayment | emits | PaymentCompleted |
