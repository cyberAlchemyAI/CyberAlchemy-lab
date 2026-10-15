[Documentation home](../../README.md)

# Decision Checkpoint · Craft workflow

<a id="def-craft-definition-decision-checkpoint"></a>

[Reference catalog](../definitions.md#catalog-definitions) / Exact record

# Decision Checkpoint · Craft workflow

A position in a workflow where required decisions or requests can be presented together. It determines where the question appears, not what the reviewer may authorize.

**When it applies**

Human-decision placement within one exact Craft Workflow instance.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**A stated exclusion**

The Authority governing a decision.

This name is used in both Lab and Craft workflow scopes. This entry has its own identity and source; matching names do not merge the definitions.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

## Source explanatory wording

The one place in a Workflow where the person is asked to decide; it says where the question appears, not what the person may authorize.

## Exact governing statement

A Decision Checkpoint is one Workflow-local position at which a closed Decision Request Set may be presented as one human interaction. It carries no authority. Its placement is resolved from the applicable Workflow Decision Profile and User Decision Preference, while every request retains its independently governed owner, scope, exact target, and effect.

````
Checkpoint(w,c) iff c in Allowed(Profile(Type(w))) and Resolve(Profile(Type(w)),Preference(User(w),Type(w)))=c; Authority(c)=none.
````

- Approval is a possible decision outcome, not the checkpoint.
- Grouping requests does not merge authority.
- A checkpoint cannot bind unknown future bytes when an exact-byte decision is required.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Craft foundation admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0005-craft-workflow-interaction/definitions/decision-checkpoint/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

craft.definition.decision-checkpoint@1.0.0-candidate.1

**Content fingerprint · SHA-256**

631292bd1683c319ee296088f717fd3ac7631ad68f540c77e656c993943e0437

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "authority_scope_ref": "scope:craft-product-workflow",
  "applicability": "Human-decision placement within one exact Craft Workflow instance.",
  "exclusions": [
    "The Authority governing a decision.",
    "The decision outcome.",
    "Automated validation or generated projection refreshes."
  ]
}
````

[Return to this catalog](../definitions.md#catalog-definitions)
