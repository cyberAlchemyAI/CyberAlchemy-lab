[Documentation home](../../README.md)

# Workflow Decision Profile · Craft workflow

<a id="def-craft-definition-workflow-decision-profile"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Workflow Decision Profile · Craft workflow

# Workflow Decision Profile · Craft workflow

Defines whether a workflow requires a person’s decision, the allowed review positions and conditions for continuation. Configuring it does not perform a decision or grant authority.

**When it applies**

Human-decision interaction constraints owned by one exact Craft Workflow type.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**A stated exclusion**

User-specific preferences.

This name is used in both Lab and Craft workflow scopes. This entry has its own identity and source; matching names do not merge the definitions.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-craft-definition-workflow-decision-profile-section-2"></a>

## Source explanatory wording

The Workflow type's rules for whether it asks a person, where it may ask, and what must already exist when it asks.

<a id="def-craft-definition-workflow-decision-profile-section-3"></a>

## Exact governing statement

A Workflow Decision Profile is a versioned configuration owned by one Workflow type. It declares decision_mode as none or single, its allowed Decision Checkpoints, an optional explicit default, target-availability requirements, standing-authority requirements for none mode, invalidation conditions, and post-decision continuation limits. It constrains interaction resolution but does not perform a decision or grant authority.

````
Profile(t)=(mode,allowed,default?,target_requirements,standing_basis,invalidation,continuation); mode in {none,single}; single => |allowed|>=1; none => allowed=empty and ExplicitNoNewDecisionBasis(Profile(t)).
````

- None mode requires an explicit no-new-decision or standing-authority basis.
- A default is explicit configuration, not silent inference.
- A profile cannot widen Authority or preapprove unknown targets.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Craft foundation admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0005-craft-workflow-interaction/definitions/workflow-decision-profile/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

craft.definition.workflow-decision-profile@1.0.0-candidate.1

**Content fingerprint · SHA-256**

52c6843ee540bcd056e51d163b725f84474097f76785a8cb0d9f974a314039e8

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "authority_scope_ref": "scope:craft-product-workflow",
  "applicability": "Human-decision interaction constraints owned by one exact Craft Workflow type.",
  "exclusions": [
    "User-specific preferences.",
    "Authority-role assignments.",
    "A decision outcome or authorization to execute a Workflow."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
