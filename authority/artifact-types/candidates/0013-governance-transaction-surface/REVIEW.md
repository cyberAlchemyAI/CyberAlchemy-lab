<!-- GENERATED FILE: canonical data is carrier-manifest.json and integrated-example.json. -->

# Governance transaction surface review

- New candidate Artifact Types: `6`
- Required endpoint-role successors: `7`
- Required Typed Relation representation successor: `1`
- New candidate Definition: `Admission Transaction`
- Relation surface: `41` kinds
- Relation Kind successors: `3`
- New Relation Kind: `1`
- Human checkpoints in the example: `1`
- Independent Decisions in the bundle: `3`
- Admission Transactions: `1`
- Runtime activations: `0`
- Authority effect: `none`

## Candidate carriers

| Artifact Type | Definition posture | Relation roles | Fixture |
| --- | --- | ---: | --- |
| `cal.artifact-type.authority-boundary/v1` | `admitted` | 2 | `authority/artifact-types/authority-boundary/v1/fixtures/valid/record.json` |
| `cal.artifact-type.decision-bundle/v1` | `admitted` | 2 | `authority/artifact-types/decision-bundle/v1/fixtures/valid/record.json` |
| `cal.artifact-type.decision-checkpoint/v1` | `admitted` | 1 | `authority/artifact-types/decision-checkpoint/v1/fixtures/valid/record.json` |
| `cal.artifact-type.user-decision-preference/v1` | `admitted` | 1 | `authority/artifact-types/user-decision-preference/v1/fixtures/valid/record.json` |
| `cal.artifact-type.workflow-decision-profile/v1` | `admitted` | 1 | `authority/artifact-types/workflow-decision-profile/v1/fixtures/valid/record.json` |
| `cal.artifact-type.admission-transaction/v1` | `candidate-unadmitted` | 2 | `authority/artifact-types/admission-transaction/v1/fixtures/valid/record.json` |

## Required endpoint carrier successors

| Successor | Preserved predecessor |
| --- | --- |
| `cal.artifact-type.decision/v2` | `authority/artifact-types/decision/v1/artifact.json` |
| `cal.artifact-type.decision-scope/v2` | `authority/artifact-types/decision-scope/v1/artifact.json` |
| `cal.artifact-type.generated-output/v2` | `authority/artifact-types/generated-output/v1/artifact.json` |
| `cal.artifact-type.policy/v2` | `authority/artifact-types/policy/v1/artifact.json` |
| `cal.artifact-type.project-state/v2` | `authority/artifact-types/project-state/v1/artifact.json` |
| `cal.artifact-type.project-governance-event-history/v2` | `authority/artifact-types/project-governance-event-history/v1/artifact.json` |
| `cal.artifact-type.project-semantic-event-history/v2` | `authority/artifact-types/project-semantic-event-history/v1/artifact.json` |
| `cal.artifact-type.typed-relation/v3` | `authority/artifact-types/typed-relation/v2/artifact.json` |

## Admission preflight closure repair

- Reviewed thirteen-carrier target set digest: `9324030cacd0e1078129f8cbd3181a9af4b4046032bbd1d54413c97869c7f613`
- Corrected fourteen-carrier target set digest: `aa1795c50adffd94dcfee8f59683745f08f52d8b397e01f5dc91c342f89b5907`
- Added carrier: `cal.artifact-type.typed-relation/v3`
- Semantic scope changed: `false`

## Exact review bindings

- Review bundle digest: `1b44b08822178f1dff028a8ac3355b524d033ed41a5a393d7ba80ec8e3b0f594`
- Fourteen-carrier target set digest: `aa1795c50adffd94dcfee8f59683745f08f52d8b397e01f5dc91c342f89b5907`
- Selected outcomes: `null` until the owner decides
- Authorization evidence and application receipt: `null` while the transaction is planned

## Revised operational flow

1. prepare exact targets and digests
2. present one closed Decision Bundle at one final-review checkpoint
3. record each Decision.selected_outcome from one owner response
4. apply one all-or-nothing Admission Transaction
5. append events, refresh derived surfaces, bind receipt, and advance Project State inside the transaction

## Boundary conclusions

- Approval or rejection is the `selected_outcome` of each Decision; there is no Approval artifact type.
- A Decision is a member of a Decision Bundle. The bundle's checkpoint and the profile's allowed checkpoint remain closed contract references.
- One owner response may resolve all exact Decision members while preserving their identities, owners, scopes, effects, targets, and digests.
- The Admission Transaction applies the resolved bundle atomically and creates the declared state, event, receipt, registry, index, and projection consequences.
- The already materialized Decision 0073 Project State successor is a deterministic consequence and does not receive a separate Decision.
- A new checkpoint is required when a target or digest changes materially, authority changes, a new effect appears, or a challenge invalidates the bundle.

## Claim ceiling

This package materializes six candidate carrier contracts and one integrated example. It admits no Definition, Artifact Type, Relation Kind, instance, Typed Relation, or transaction.
