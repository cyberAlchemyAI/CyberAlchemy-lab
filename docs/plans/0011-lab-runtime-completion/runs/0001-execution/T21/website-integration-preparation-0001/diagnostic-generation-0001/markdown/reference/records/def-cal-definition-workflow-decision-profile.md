[Documentation home](../../README.md)

# Workflow Decision Profile · Lab workflow

<a id="def-cal-definition-workflow-decision-profile"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Workflow Decision Profile · Lab workflow

# Workflow Decision Profile · Lab workflow

Defines whether a workflow requires a person’s decision, the allowed review positions and conditions for continuation. Configuring it does not perform a decision or grant authority.

**When it applies**

Configuration constraints for human decisions in one workflow type.

**Record formats**

[Workflow decision profile · v1](type-cal-artifact-type-workflow-decision-profile-v1.md#type-cal-artifact-type-workflow-decision-profile-v1)

**A stated exclusion**

User-specific preferences.

This name is used in both Lab and Craft workflow scopes. This entry has its own identity and source; matching names do not merge the definitions.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-workflow-decision-profile-section-2"></a>

## Source explanatory wording

The workflow type's rules for whether it asks a person, where it is allowed to ask, and what must already exist when it asks.

<a id="def-cal-definition-workflow-decision-profile-section-3"></a>

## Exact governing statement

A Workflow Decision Profile is a versioned configuration owned by one workflow type that declares decision_mode as none or single, the allowed Decision Checkpoints, an optional explicit default, required decision-target availability, standing-authority requirements for none mode, invalidation conditions, and post-decision continuation limits. It constrains checkpoint resolution but never performs a Governance Decision or grants authority.

````
Profile(t) = (decision_mode, allowed_checkpoints, default_checkpoint?, target_requirements, standing_authority_requirements, invalidation_conditions, continuation_limits). decision_mode in {none,single}. single => |allowed_checkpoints| >= 1. none => allowed_checkpoints = empty and ExplicitNoNewDecisionBasis(profile).
````

- None mode requires an explicit no-new-decision or standing-authority basis.
- A profile default is explicit configuration, not silent inference.
- A profile cannot widen an Authority Boundary or preapprove unknown future targets.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../assets/8146ff31bf5e-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.workflow-decision-profile@1.0.0-candidate.1

**Content fingerprint · SHA-256**

8146ff31bf5e48acb3e2026d41bafee1217ede50c7a7ccdb292600337a064f22

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "authority_scope_ref": "scope:cyberalchemy-lab-workflow-interaction",
  "applicability": "Configuration constraints for human decisions in one workflow type.",
  "exclusions": [
    "User-specific preferences.",
    "Owner-role assignments and Authority Boundaries.",
    "A decision or authorization to execute the workflow."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
