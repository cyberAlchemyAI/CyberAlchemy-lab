# Relationship Fixture - bad reversed enforces

## Concept Registry

| Concept | Type |
| --- | --- |
| MaxAmountRule | Rule |
| ProcessPayment | Operation |

## Feature Concept Graph

| From | Edge | To |
| --- | --- | --- |
| ProcessPayment | enforces | MaxAmountRule |
