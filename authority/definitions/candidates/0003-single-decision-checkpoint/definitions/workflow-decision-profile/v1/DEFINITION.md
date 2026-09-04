<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Workflow Decision Profile

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.workflow-decision-profile`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:cyberalchemy-lab-workflow-interaction`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

A Workflow Decision Profile is a versioned configuration owned by one workflow type that declares decision_mode as none or single, the allowed Decision Checkpoints, an optional explicit default, required decision-target availability, standing-authority requirements for none mode, invalidation conditions, and post-decision continuation limits. It constrains checkpoint resolution but never performs a Governance Decision or grants authority.

```text
Profile(t) = (decision_mode, allowed_checkpoints, default_checkpoint?, target_requirements, standing_authority_requirements, invalidation_conditions, continuation_limits). decision_mode in {none,single}. single => |allowed_checkpoints| >= 1. none => allowed_checkpoints = empty and ExplicitNoNewDecisionBasis(profile).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| t | One exact workflow type. |
| Profile(t) | The decision-interaction constraints owned by workflow type t. |

### Boundary conditions

- None mode requires an explicit no-new-decision or standing-authority basis.
- A profile default is explicit configuration, not silent inference.
- A profile cannot widen an Authority Boundary or preapprove unknown future targets.

### Testable conditions

- decision_mode is exactly none or single.
- Single mode declares at least one allowed checkpoint.
- Every default belongs to the allowed set.
- None mode declares no checkpoint and names its authority basis.

## Plain-language voice

The workflow type's rules for whether it asks a person, where it is allowed to ask, and what must already exist when it asks.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

A definition-admission workflow can allow one checkpoint after candidate validation, while a read-only audit can use none mode. Both choices are explicit and type-owned.

### Examples

- Definition admission: single, after exact candidate and postimage digests exist.
- Generated projection refresh: none, when canonical input is unchanged and the generator binding is already governed.

## Applicability

Configuration constraints for human decisions in one workflow type.

### Exclusions

- User-specific preferences.
- Owner-role assignments and Authority Boundaries.
- A decision or authorization to execute the workflow.

## Boundaries

- Workflow Decision Profile is not User Decision Preference.
- Profile validity does not authorize workflow execution.
- The profile owns allowed interaction structure, not semantic or effect authority.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.definition.definition@1.0.0-candidate.1 | whole-json | `eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575` | `admitted` |
| cal.language.governance/v2 | whole-json | `ba84484be3f0d793e935ba4bbf960885ce1adcd2d2763aee940396ff290918d7` | `admitted` |

## Primary consumers

- authority/profiles
- tooling/validators
- contexts/governance

## Lookup and drift

- Index: `candidate:authority/definitions/registry.json` / `cal.definition.workflow-decision-profile`
- Drift owner: `role:definition-owner`
- Audit: `drift-audit-postimage.json`
- Challenge route: `route:definition-governance-challenge`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.governed-by | cal.definition.workflow-decision-profile@1.0.0-candidate.1 | role:definition-owner | role:definition-owner |

## Evidence

- user-direction:single-configurable-approval-boundary

## Residue

- definition-owner-admission-required
- workflow-definition-import-from-craft-required
- workflow-profile-artifact-type-not-yet-authored

## Claim ceiling

This candidate defines a workflow-type configuration contract only. It does not create a profile instance, configure a user, or authorize a workflow.
