# Relationship Fixture - bad authored creation projection

## Concept Registry

| Concept | Type |
| --- | --- |
| CreatePlayer | Operation |
| Player | Entity |

## Feature Concept Graph

| From | Edge | To |
| --- | --- | --- |
| CreatePlayer | creates | Player |

## CreatePlayer

| Attribute | Value |
| --- | --- |
| state_change | yes |
| creation_targets | Player |
