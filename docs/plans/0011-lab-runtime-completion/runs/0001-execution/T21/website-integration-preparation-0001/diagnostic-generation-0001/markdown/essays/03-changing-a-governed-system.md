[Documentation home](../README.md)

<a id="essay-3"></a>

Part I · Governance Essay 03 · 4 minute read

<a id="essay-3-title"></a>

## Changing a governed system

The investigation suggests revised code, a different record format and new success criteria. Reviewing them together is convenient, provided the owner can distinguish their effects. Code changes behavior. A format changes stored representation. Criteria might change completion’s meaning. The Lab records the intended effects before acceptance.

Lifecycle gives each subject its states and permitted changes over time. A record format can be accepted while a particular record is still a draft. Selected software can await activation. A graph can represent a proposal as proposed. A session ends while its project continues. We need each subject’s state to understand those facts.

The Lab separates three changes. A Semantic Epoch is an owner-selected accepted meaning version; a material owner-determined change to export inclusion rules needs a successor. A Representation Revision changes machine encoding while preserving meaning, with equivalence evidence, validation and owner selection. A Derived Refresh regenerates and validates a view from unchanged canonical input under an exact generator binding. It adds no meaning, representation revision, decision or authority effect. A generator change follows its tooling route.

A proposal identifies exact subjects, versions and relevant file bytes, requested effects, authority limits and invalidating conditions. A Decision chooses an outcome within those limits. A Decision Bundle puts separate decisions at one review checkpoint. Their owners, targets and effects stay separate, so accepting one supplies no automatic acceptance for the rest.

An Admission Transaction applies an already authorized bundle. It checks authorization, targets and starting state, then applies the declared consequences together. Accepted records, receipts, histories, Project State and generated indexes can be part of that result. Project State is saved knowledge outside any agent. The transaction has only the permission supplied by its decisions.

The inspected records show a governance approval covering record contracts, the Admission Transaction definition and connection rules, with consequences applied together. A later approval accepted the local runtime and declared operational records. Each approval identifies its scope. Deployment and publication still have their own authorization requirements.

Two histories let us recover the result. Project Semantic Event History records complete resulting states and predecessors. Project Governance Event History records decisions, authorization, policies, challenges and evidence for those changes. Both identify the same change events, letting a reader connect what changed with why it was accepted.

Event sourcing retains an ordered change history and reconstructs state from it. Replay performs that reconstruction from recorded inputs. The Lab also links a separate authority history. Reconstructing a state leaves the acceptance of its inputs to the applicable governance records. [Martin Fowler, Event Sourcing](https://martinfowler.com/eaaDev/EventSourcing.html)

The local implementation supplies bounded evidence. A signed proposal identifies changes and expected starting state. An exclusive writer lock prevents competing local writes. Prepared transaction records precede the accepted-state reference update, and recovery recognizes completed history and unfinished work. The recorded tests concern local process interruption on the selected filesystem, without establishing power-loss durability or coordination across machines.

A Challenge Contract sets eligible participants, reasons, evidence, responsibility, timing and resolution requirements. A Challenge Event records one eligible challenge. Missing-row evidence could challenge a completeness finding. Filing it creates a matter requiring resolution. Suspension, withdrawal or revised meaning still needs the applicable rule and authorized decision.

An accepted change can leave an earlier Context View stale. The view identifies task information, source versions and use conditions. The runtime can require a fresh checked selection tied to accepted state. The next agent recovers the change and authority from project records, with no need to inherit a private conversation.

### Definitions and sources

[Semantic Epoch](../reference/records/def-cal-definition-semantic-epoch.md#def-cal-definition-semantic-epoch) · [Representation Revision](../reference/records/def-cal-definition-representation-revision.md#def-cal-definition-representation-revision) · [Derived Refresh](../reference/records/def-cal-definition-derived-refresh.md#def-cal-definition-derived-refresh) · [Decision](../reference/records/def-cal-definition-decision.md#def-cal-definition-decision) · [Decision Bundle](../reference/records/def-cal-definition-decision-bundle.md#def-cal-definition-decision-bundle) · [Admission Transaction](../reference/records/def-cal-definition-admission-transaction.md#def-cal-definition-admission-transaction) · [Project Semantic Event History](../reference/records/def-cal-definition-project-semantic-event-history.md#def-cal-definition-project-semantic-event-history) · [Project Governance Event History](../reference/records/def-cal-definition-project-governance-event-history.md#def-cal-definition-project-governance-event-history) · [Challenge Contract](../reference/records/def-cal-definition-challenge-contract.md#def-cal-definition-challenge-contract) · [Challenge Event](../reference/records/def-cal-definition-challenge-event.md#def-cal-definition-challenge-event)

- [Governance transaction approval](../assets/17c191453d8d-DECISION.md)
- [Committed Project State](../assets/8ba8ee25ccbf-current.json)
- Local runtime: storage, approvals and replay
- Local runtime: governed consequences

Follow these links to the exact sources used by the essay. An older draft label leaves standing to the acceptance recorded for that version.

[Continue to essay 04 **What the Lab organizes →**](04-what-the-lab-organizes.md#essay-4)
