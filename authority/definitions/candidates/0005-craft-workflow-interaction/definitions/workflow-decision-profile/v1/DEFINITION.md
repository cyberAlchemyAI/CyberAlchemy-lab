<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Workflow Decision Profile

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `craft.definition.workflow-decision-profile`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:craft-product-owner`
- Authority scope: `scope:craft-product-workflow`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

A Workflow Decision Profile is a versioned configuration owned by one Workflow type. It declares decision_mode as none or single, its allowed Decision Checkpoints, an optional explicit default, target-availability requirements, standing-authority requirements for none mode, invalidation conditions, and post-decision continuation limits. It constrains interaction resolution but does not perform a decision or grant authority.

```text
Profile(t)=(mode,allowed,default?,target_requirements,standing_basis,invalidation,continuation); mode in {none,single}; single => |allowed|>=1; none => allowed=empty and ExplicitNoNewDecisionBasis(Profile(t)).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| t | One exact Workflow type. |
| Profile(t) | The decision-interaction constraints owned by that Workflow type. |

### Boundary conditions

- None mode requires an explicit no-new-decision or standing-authority basis.
- A default is explicit configuration, not silent inference.
- A profile cannot widen Authority or preapprove unknown targets.

### Testable conditions

- decision_mode is exactly none or single.
- Single mode declares at least one allowed checkpoint.
- Every default belongs to the allowed set.
- None mode names its authority basis and declares no checkpoint.

## Plain-language voice

The Workflow type's rules for whether it asks a person, where it may ask, and what must already exist when it asks.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

Craft can define a single checkpoint after candidate validation for an admission Workflow, while a read-only audit can explicitly use none mode.

### Examples

- Definition admission: single, after exact candidate and postimage digests exist.
- Generated projection refresh: none, when canonical input and governed generator binding are unchanged.

## Applicability

Human-decision interaction constraints owned by one exact Craft Workflow type.

### Exclusions

- User-specific preferences.
- Authority-role assignments.
- A decision outcome or authorization to execute a Workflow.

## Boundaries

- Workflow Decision Profile is not User Decision Preference.
- Profile validity does not authorize Workflow execution.
- The profile owns interaction constraints, not authority semantics.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.definition.definition@1.0.0-candidate.1 | whole-json | `eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575` | `admitted` |
| domainspec-core:DS-D1.9 | lines:647-689 | `23835be6442b40136d19c747fdf2ea07f1eae996b33cf0997ace7d9b5f2e4228` | `candidate-unadmitted` |
| domainspec-core:CAV2-D20 | lines:1014-1185 | `ce8dd8633ff5df8fc76b71cf544327209f34a875ed9f93e262469f7c98d8b640` | `candidate-unadmitted` |
| domainspec-core:CAV2-D34 | lines:2252-2315 | `baa33a7047a1c1d512fce513c22134b377587d9acf77b2797412d2cd97118ef1` | `candidate-unadmitted` |

## Primary consumers

- candidate:product/products/craft
- candidate:craft-workflow-runtime
- tooling/validators

## Lookup and drift

- Index: `candidate:authority/definitions/registry.json` / `craft.definition.workflow-decision-profile`
- Drift owner: `role:craft-product-owner`
- Audit: `drift-audit-postimage.json`
- Challenge route: `route:definition-governance-challenge`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.governed-by | craft.definition.workflow-decision-profile@1.0.0-candidate.1 | role:craft-product-owner | role:craft-product-owner |
| relation.originates-from | craft.definition.workflow-decision-profile@1.0.0-candidate.1 | domainspec-core:CAV2-D20 | role:craft-product-owner |

## Evidence

- user-direction:single-configurable-decision-checkpoint
- domainspec-core:CAV2-D20

## Residue

- external-source-admission-required
- craft-product-owner-binding-required
- workflow-decision-profile-artifact-type-not-yet-authored

## Claim ceiling

This candidate defines Craft Workflow interaction constraints only. It does not create a profile instance, configure a user, or authorize a Workflow.
