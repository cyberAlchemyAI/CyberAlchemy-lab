# Relationship Fixture - bad creates with multiple sources

## Concept Registry

| Concept | Type |
| --- | --- |
| CreatePlayer | Operation |
| RegisterPlayer | Operation |
| Player | Entity |

## Feature Concept Graph

| From | Edge | To |
| --- | --- | --- |
| CreatePlayer | creates | Player |
| RegisterPlayer | creates | Player |

## CreatePlayer

| Attribute | Value |
| --- | --- |
| state_change | yes |

## RegisterPlayer

| Attribute | Value |
| --- | --- |
| state_change | yes |
