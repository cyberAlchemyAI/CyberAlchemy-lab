# Relationship Fixture - Calculation cannot read an Entity directly

## Concept Registry

| Concept | Type |
| --- | --- |
| DealSplitCalculation | Calculation |
| SettlementTransaction | Entity |

## Feature Concept Graph

| From | Edge | To |
| --- | --- | --- |
| DealSplitCalculation | reads | SettlementTransaction |
