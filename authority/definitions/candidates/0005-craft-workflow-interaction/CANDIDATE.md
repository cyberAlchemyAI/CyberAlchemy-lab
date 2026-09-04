<!-- GENERATED FILE: edit candidate.json and run render.py. -->

# Craft Workflow Interaction Definition Pack

> Machine-canonical candidate with no admission or authority effect.

- Candidate: `CAL-DEFINITION-CANDIDATE-SET-CRAFT-WORKFLOW-0005`
- Status: `candidate-authored-dependencies-open`
- Semantic owner: `role:craft-product-owner`
- Authority effect: `none`

## Definitions

| ID | Version | Disposition | Path |
| --- | --- | --- | --- |
| `DS-D1.9` | `1.0.0-candidate.1` | `migrate-preserving-stable-id` | `authority/definitions/candidates/0005-craft-workflow-interaction/definitions/workflow/v1/definition.json` |
| `craft.definition.workflow-decision-profile` | `1.0.0-candidate.1` | `reclassified-from-0003` | `authority/definitions/candidates/0005-craft-workflow-interaction/definitions/workflow-decision-profile/v1/definition.json` |
| `craft.definition.decision-checkpoint` | `1.0.0-candidate.1` | `reclassified-from-0003` | `authority/definitions/candidates/0005-craft-workflow-interaction/definitions/decision-checkpoint/v1/definition.json` |
| `craft.definition.user-decision-preference` | `1.0.0-candidate.1` | `workflow-resolution-specialization` | `authority/definitions/candidates/0005-craft-workflow-interaction/definitions/user-decision-preference/v1/definition.json` |
| `craft.definition.decision-request-set` | `1.0.0-candidate.1` | `presentation-only-successor-to-decision-bundle-proposal` | `authority/definitions/candidates/0005-craft-workflow-interaction/definitions/decision-request-set/v1/definition.json` |

## Ownership boundary

Craft owns workflow orchestration and human-interaction placement. CyberAlchemy Governance continues to own Authority and Gate semantics. No workflow profile, checkpoint, preference, or request set may create, merge, transfer, or widen authority.

## Promotion blockers

- Exact external source admissions are required for CAV2-D20, CAV2-D34, CAV2-D37, DS-D1.9, and the Craft Product identity.
- The selected craft-product-owner role has no admitted accountable-principal binding in the current Lab owner registry.
- Craft Product identity does not imply a Craft DDD Bounded Context; context selection remains separate.

## Claim ceiling

This candidate authors Craft workflow vocabulary only. It does not admit external sources, bind the Craft Product owner, select a Craft bounded context, configure a workflow, request a decision, or authorize any effect.
