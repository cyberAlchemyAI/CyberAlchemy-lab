# CyberAlchemy ontology runtime integration graph — version 1

Status: admitted versioned read model  
Decision: `CAL-D65SYS-0020` / `D65SYS-1`  
Canonical replay source: no

This is the complete readable projection of the 43 direct edges in the
byte-identical versioned `graph.json`. It is a view, not an independently
authored ontology or canonical event history.

```text
OntologyProjectionAccess -exposes-> ResolveContextProjectionBinding
OntologyProjectionAccess -exposes-> VerifyCanonicalEventCut
OntologyProjectionAccess -exposes-> EvaluateGovernanceJoin
OntologyProjectionAccess -exposes-> MaterializeEventCalculatedProjection
OntologyProjectionAccess -exposes-> DeliverProjection
OntologyProjectionAccess -exposes-> ResolveProjectionChallenge
ResolveContextProjectionBinding -produces-> IntegrationEpochWasRecorded
BusinessSystemBridge -contains-> ContextSelector
BusinessSystemBridge -contains-> CanonicalEventCut
BusinessSystemBridge -contains-> IntegrationEpoch
BusinessSystemBridge -contains-> ChallengeRoute
BusinessSystemBridge -contains-> GovernanceJoinPolicy
BusinessSystemBridge -contains-> ProjectionProfile
BusinessSystemBridge -owns-> ContextProjectionBinding
BusinessSystemBridge -owns-> EventCalculatedProjection
IntegrationBusinessOntologyOwner -performs-> ResolveProjectionChallenge
CanonicalEventTruthRule -enforces-> MaterializeEventCalculatedProjection
ChallengeBlockingPolicy -applies-> ResolveProjectionChallenge
ResolveProjectionChallenge -produces-> ProjectionChallengeWasRaised
ResolveProjectionChallengeWorkflow -orchestrates-> ResolveProjectionChallenge
ContextConsumerOnlyRule -enforces-> DeliverProjection
ContextProductOwner -performs-> ResolveContextProjectionBinding
GovernedContext -performs-> ResolveContextProjectionBinding
GovernedContext -performs-> DeliverProjection
ProjectionDeliveryPolicy -applies-> DeliverProjection
DeterministicProjectionRule -enforces-> MaterializeEventCalculatedProjection
CalculateEventProjection -calculates-> MaterializeEventCalculatedProjection
ExactCutRequiredRule -enforces-> VerifyCanonicalEventCut
FulfillProjectionRequest -orchestrates-> ResolveContextProjectionBinding
FulfillProjectionRequest -orchestrates-> VerifyCanonicalEventCut
FulfillProjectionRequest -orchestrates-> EvaluateGovernanceJoin
FulfillProjectionRequest -orchestrates-> MaterializeEventCalculatedProjection
FulfillProjectionRequest -orchestrates-> DeliverProjection
EndpointIdentitySeparationRule -enforces-> ResolveContextProjectionBinding
MaterializeEventCalculatedProjection -produces-> ProjectionBecameAvailable
MaterializeEventCalculatedProjection -produces-> ExactCutBecameTraceable
CalculateLatestNodeSnapshot -calculates-> MaterializeEventCalculatedProjection
EventCalculatedProjection -emits-> ProjectionBecameAvailable
EventCalculatedProjection -emits-> InvalidCutWasRejected
EventCalculatedProjection -emits-> ExactCutBecameTraceable
CalculateLatestRelationSnapshot -calculates-> MaterializeEventCalculatedProjection
SelectorAdmissionPolicy -applies-> ResolveContextProjectionBinding
VerifyCanonicalEventCut -produces-> InvalidCutWasRejected
```
