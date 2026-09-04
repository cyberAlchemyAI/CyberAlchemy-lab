<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# User Decision Preference

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `craft.definition.user-decision-preference`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:craft-product-owner`
- Authority scope: `scope:craft-product-workflow`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

A User Decision Preference is a versioned user-owned interaction configuration selecting one preferred Decision Checkpoint for an exact Workflow type or instance scope. It applies only when allowed by the Workflow Decision Profile. An explicit invalid preference blocks resolution and never silently falls back. A preference has no authority effect and cannot waive a required decision, create standing authority, or alter an owner, target, effect, or scope.

```text
Preference(u,s)=preferred_checkpoint; Applicable(p,w) iff Scope(p) matches w and preferred_checkpoint in Allowed(Profile(Type(w))); ExplicitInvalid(p,w)=>BLOCK.
```

### Notation

| Symbol | Meaning |
| --- | --- |
| u | The user who owns the interaction preference. |
| s | An exact Workflow-type or Workflow-instance scope. |

### Boundary conditions

- A preference changes interaction placement only.
- An explicit invalid preference blocks instead of falling back.
- Absence may use only an explicit valid profile default.

### Testable conditions

- The preference names its user and exact scope.
- The selected checkpoint is validated against the applicable profile.
- No preference field changes authority or decision requirements.

## Plain-language voice

The user's saved choice for where a kind of Workflow should ask them, limited to positions that Workflow already permits.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

Craft may let a user prefer review after validation or immediately before cutover when the Workflow profile permits it; an unsupported choice blocks visibly.

### Examples

- Prefer post-validation for definition admission.
- A pre-authorship preference is invalid when the decision must bind exact candidate bytes.

## Applicability

User-owned selection of an allowed interaction checkpoint for an exact Craft Workflow type or instance scope.

### Exclusions

- Authority-role assignment.
- Workflow-type safety constraints.
- Decision outcome, standing authorization, or effect scope.

## Boundaries

- User Decision Preference is not an authority-bearing decision.
- Preference cannot remove a mandatory checkpoint.
- Preference resolution must not silently infer a substitute value.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.definition.definition@1.0.0-candidate.1 | whole-json | `eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575` | `admitted` |
| domainspec-core:CAV2-D34 | lines:2252-2315 | `baa33a7047a1c1d512fce513c22134b377587d9acf77b2797412d2cd97118ef1` | `candidate-unadmitted` |
| domainspec-core:CAV2-D20 | lines:1014-1185 | `ce8dd8633ff5df8fc76b71cf544327209f34a875ed9f93e262469f7c98d8b640` | `candidate-unadmitted` |

## Primary consumers

- candidate:product/products/craft
- candidate:craft-user-profile
- tooling/validators

## Lookup and drift

- Index: `candidate:authority/definitions/registry.json` / `craft.definition.user-decision-preference`
- Drift owner: `role:craft-product-owner`
- Audit: `drift-audit-postimage.json`
- Challenge route: `route:definition-governance-challenge`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.governed-by | craft.definition.user-decision-preference@1.0.0-candidate.1 | role:craft-product-owner | role:craft-product-owner |
| relation.originates-from | craft.definition.user-decision-preference@1.0.0-candidate.1 | domainspec-core:CAV2-D20 | role:craft-product-owner |

## Evidence

- user-direction:boundary-configurable-by-user-preferences-and-workflow-type

## Residue

- external-source-admission-required
- craft-product-owner-binding-required
- preference-artifact-type-not-yet-authored

## Claim ceiling

This candidate defines Craft preference resolution only. It does not create a preference, identify current settings, or grant authority.
