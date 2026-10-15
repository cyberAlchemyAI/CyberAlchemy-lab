[Documentation home](../../README.md)

# Decision Checkpoint · Lab workflow

<a id="def-cal-definition-decision-checkpoint"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Decision Checkpoint · Lab workflow

# Decision Checkpoint · Lab workflow

A position in a workflow where required decisions or requests can be presented together. It determines where the question appears, not what the reviewer may authorize.

**When it applies**

Human decision placement within one exact workflow instance.

**Record formats**

[Decision checkpoint · v1](type-cal-artifact-type-decision-checkpoint-v1.md#type-cal-artifact-type-decision-checkpoint-v1)

**A stated exclusion**

The Authority Boundary governing a decision.

This name is used in both Lab and Craft workflow scopes. This entry has its own identity and source; matching names do not merge the definitions.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-decision-checkpoint-section-2"></a>

## Source explanatory wording

The one place in a workflow where the person is asked to decide. Calling it a checkpoint avoids confusing where the question appears with what the person is allowed to authorize.

<a id="def-cal-definition-decision-checkpoint-section-3"></a>

## Exact governing statement

A Decision Checkpoint is one workflow-local position at which a closed set of required Governance Decisions may be presented as one human interaction. It carries no authority by itself. Its placement is resolved from a Workflow Decision Profile and an applicable User Decision Preference, while every decision presented there retains its own Authority Boundary, accountable owner, exact target, and effect.

````
DecisionCheckpoint(w,c) iff c in Allowed(Profile(Type(w))) and Resolved(Profile(Type(w)),Preference(User(w),Type(w))) = c. Authority(c) = none.
````

- Approval is one possible decision outcome, not the checkpoint itself.
- Grouping decisions at one checkpoint does not merge their Authority Boundaries.
- A checkpoint cannot bind unknown future bytes when the required decision targets exact output bytes.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../assets/dce0f44b9efd-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.decision-checkpoint@1.0.0-candidate.1

**Content fingerprint · SHA-256**

dce0f44b9efd159f7135672847ce0c8082b5b983f8ac7150f5db1564613cc06f

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "authority_scope_ref": "scope:cyberalchemy-lab-workflow-interaction",
  "applicability": "Human decision placement within one exact workflow instance.",
  "exclusions": [
    "The Authority Boundary governing a decision.",
    "The decision outcome.",
    "Automated validation or generated projection refreshes."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
