# Red check — State Machine cannot enforce Operation

## Concept Registry

| Concept | Type |
| --- | --- |
| RunStateMachine | State Machine |
| ExecutePipelineRoute | Operation |

## Feature Concept Graph

| From | Edge | To |
| --- | --- | --- |
| RunStateMachine | enforces | ExecutePipelineRoute |

## RunStateMachine

| Attribute | Value |
| --- | --- |
| has_transitions | yes |

## ExecutePipelineRoute

| Attribute | Value |
| --- | --- |
| state_change | yes |
