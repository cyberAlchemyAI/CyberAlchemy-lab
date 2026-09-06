# Relationship Fixture - bad creates with multiple targets

## Concept Registry

| Concept | Type |
| --- | --- |
| CreatePlayer | Operation |
| Player | Entity |
| Team | Entity |

## Feature Concept Graph

| From | Edge | To |
| --- | --- | --- |
| CreatePlayer | creates | Player |
| CreatePlayer | creates | Team |

## CreatePlayer

| Attribute | Value |
| --- | --- |
| state_change | yes |
