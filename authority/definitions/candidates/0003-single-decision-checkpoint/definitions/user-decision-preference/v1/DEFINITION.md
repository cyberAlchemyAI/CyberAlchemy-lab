<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# User Decision Preference

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.user-decision-preference`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:cyberalchemy-lab-workflow-interaction`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

A User Decision Preference is a versioned user-owned interaction configuration that selects one preferred Decision Checkpoint for an exact workflow type or workflow instance scope. It is applied only when the selected checkpoint is allowed by the applicable Workflow Decision Profile. An invalid preference blocks resolution and must not silently fall back. A preference has no authority effect and cannot waive a required decision, create standing authority, or alter an owner, target, effect, or scope.

```text
Preference(u,s) = preferred_checkpoint. Applicable(p,w) iff Scope(p) matches w and preferred_checkpoint in Allowed(Profile(Type(w))). ExplicitInvalid(p,w) => BLOCK; no fallback.
```

### Notation

| Symbol | Meaning |
| --- | --- |
| u | The user who owns the interaction preference. |
| s | An exact workflow-type or workflow-instance scope. |

### Boundary conditions

- A preference changes interaction placement only.
- An explicit invalid preference blocks instead of falling back.
- Absence of a preference may use only an explicit valid profile default.

### Testable conditions

- The preference names its user and exact scope.
- The preferred checkpoint is validated against the applicable profile.
- No preference field grants authority or changes decision requirements.

## Plain-language voice

The user's saved choice for where a particular kind of workflow should ask them. It can move the question only among places the workflow already permits.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

CyberAlchemy Lab may let the user prefer review after validation or immediately before cutover, depending on the workflow profile. An unsupported choice stops and explains the conflict.

### Examples

- Prefer the post-validation checkpoint for definition admission.
- A preference for pre-authorship cannot apply when the decision must bind exact candidate bytes.

## Applicability

User-owned selection of an interaction checkpoint for an exact workflow type or instance scope.

### Exclusions

- Authority-role assignment.
- Workflow-type safety constraints.
- Decision outcome, standing authorization, or effect scope.

## Boundaries

- User Decision Preference is not a Governance Decision.
- Preference is not authority and cannot remove a mandatory checkpoint.
- Preference resolution must not silently infer or substitute another value.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.definition.definition@1.0.0-candidate.1 | whole-json | `eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575` | `admitted` |
| CAL-OWNERS-FOUNDATION-01 | whole-json | `bb20cdc8ed61decba43977fafc4d04052cb59bb8e4402d6419a3d85776a3422d` | `admitted` |

## Primary consumers

- authority/preferences
- authority/profiles
- tooling/validators

## Lookup and drift

- Index: `candidate:authority/definitions/registry.json` / `cal.definition.user-decision-preference`
- Drift owner: `role:definition-owner`
- Audit: `drift-audit-postimage.json`
- Challenge route: `route:definition-governance-challenge`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.governed-by | cal.definition.user-decision-preference@1.0.0-candidate.1 | role:definition-owner | role:definition-owner |

## Evidence

- user-direction:boundary-configurable-by-user-preferences-and-workflow-type

## Residue

- definition-owner-admission-required
- preference-artifact-type-not-yet-authored

## Claim ceiling

This candidate defines preference semantics only. It does not create a preference, identify a current user's settings, or grant authority.
