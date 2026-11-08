# Agent Execution Orchestrator — normalized v2 feature pack

> Build-from-owned projection of
> `impl/test-derivation-engine/__fixtures__/agent-execution-orchestrator/`.
> Root DS-D8 remains authoritative. This pack re-emits only nine authored rows
> whose endpoint types are currently admissible; it does not repair or replace
> the source fixture's three invalid rows.

## What This Feature Owns

Composition and execution of explicit lifecycle routes, governed branch and
cancellation choices, boundary exposure, and governance signal emission.

## Concept Registry

| Concept | Type |
| --- | --- |
| FeatureLifecyclePipelineWorkflow | Workflow |
| PipelineRouteTemplate | Entity |
| StageContract | Value Object |
| AssemblePipelineRoute | Operation |
| ExecutePipelineRoute | Operation |
| CancelSupersededRun | Operation |
| EmitGovernanceSignals | Operation |
| BranchStrategyPolicy | Policy |
| CancellationPolicy | Policy |
| RouteArtifactInterface | Interface |
| SandboxProviderInterface | Interface |
| DelegationTelemetryLedgerInterface | Interface |
| GovernanceSignalEmission | Event |

## Feature Concept Graph

| From | Edge | To | Source Evidence |
| --- | --- | --- | --- |
| FeatureLifecyclePipelineWorkflow | orchestrates | ExecutePipelineRoute | source `workflows.md#featurelifecyclepipelineworkflow` |
| FeatureLifecyclePipelineWorkflow | orchestrates | EmitGovernanceSignals | source `workflows.md#featurelifecyclepipelineworkflow` |
| PipelineRouteTemplate | contains | StageContract | source `domain.md#pipelineroutetemplate` |
| BranchStrategyPolicy | applies | ExecutePipelineRoute | source `rules.md#branchstrategypolicy` |
| CancellationPolicy | applies | CancelSupersededRun | source `rules.md#cancellationpolicy` |
| RouteArtifactInterface | exposes | AssemblePipelineRoute | source `interfaces.md#internal-routeartifactinterface` |
| SandboxProviderInterface | exposes | ExecutePipelineRoute | source `interfaces.md#internal-sandboxproviderinterface` |
| DelegationTelemetryLedgerInterface | exposes | EmitGovernanceSignals | source `interfaces.md#internal-delegationtelemetryledgerinterface` |
| EmitGovernanceSignals | produces | GovernanceSignalEmission | source `operations.md#emitgovernancesignals` and `observability.md#governancesignalemission` |

## FeatureLifecyclePipelineWorkflow

Coordinates route execution and governance-signal emission in one feature.

| Attribute | Value |
| --- | --- |
| scope | intra-feature |

## PipelineRouteTemplate

Identity-bearing explicit route template containing ordered stage contracts.

| Field | Type | Required | Identity | Description |
| --- | --- | --- | --- | --- |
| templateId | string | yes | yes | stable route-template identity |
| stageContracts | StageContract[] | yes |  | ordered stage contracts from the source domain |
| selectedStages | string[] | yes |  | selected lifecycle stages |

## StageContract

Immutable stage obligation embedded in a route template.

| Field | Type | Required | Identity | Description |
| --- | --- | --- | --- | --- |
| stage | string | yes |  | selected lifecycle stage |
| operationRef | string | yes |  | operation executed for the stage |
| terminalOutcomes | string[] | yes |  | allowed terminal outcomes |

**Equality:** two StageContract values are equal when stage, operationRef, and
terminalOutcomes are equal.

## AssemblePipelineRoute

Publishes an explicit route artifact from a selected lifecycle chain.

| Attribute | Value |
| --- | --- |
| state_change | yes |

## ExecutePipelineRoute

Executes an authored route template and records run state.

| Attribute | Value |
| --- | --- |
| state_change | yes |

## CancelSupersededRun

Cancels an older active run under latest-run-wins policy.

| Attribute | Value |
| --- | --- |
| state_change | yes |

## EmitGovernanceSignals

Appends governance signals after terminal outcomes and recovery branches.

| Attribute | Value |
| --- | --- |
| state_change | yes |

## BranchStrategyPolicy

Selects the execution branch strategy for a route.

| Attribute | Value |
| --- | --- |
| formal_return_type | strategy |

## CancellationPolicy

Selects cancellation behavior when a newer run supersedes an active run.

| Attribute | Value |
| --- | --- |
| formal_return_type | strategy |

## RouteArtifactInterface

Internal boundary for publishing route artifacts.

| Attribute | Value |
| --- | --- |
| interface_kind | internal |

## SandboxProviderInterface

Internal boundary for sandbox-backed route execution.

| Attribute | Value |
| --- | --- |
| interface_kind | internal |

## DelegationTelemetryLedgerInterface

Internal boundary for append-only governance telemetry.

| Attribute | Value |
| --- | --- |
| interface_kind | internal |

## GovernanceSignalEmission

Past-tense notification that governance signal rows were emitted.

| Attribute | Value |
| --- | --- |
| temporal | past |

## Omitted Source Rows

The following source-fixture rows are intentionally absent and have no
replacement edge:

- `AssemblePipelineRoute --enforces--> StageContract`
- `RunStateMachine --enforces--> ExecutePipelineRoute`
- `RunArtifactMapping --maps--> TelemetryEnvelope`

Absent-sibling cross-feature declarations are also excluded.
