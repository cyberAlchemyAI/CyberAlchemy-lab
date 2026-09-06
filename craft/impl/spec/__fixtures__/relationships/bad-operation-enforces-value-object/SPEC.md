# Relationship Fixture - bad Operation enforces Value Object

## Concept Registry

| Concept | Type |
| --- | --- |
| ProcessPayment | Operation |
| Money | Value Object |

## Feature Concept Graph

| From | Edge | To |
| --- | --- | --- |
| ProcessPayment | enforces | Money |
