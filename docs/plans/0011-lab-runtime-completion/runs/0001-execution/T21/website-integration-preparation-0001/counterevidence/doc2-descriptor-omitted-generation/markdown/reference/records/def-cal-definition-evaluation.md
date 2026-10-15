[Documentation home](../../README.md)

# Evaluation

<a id="def-cal-definition-evaluation"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Evaluation

# Evaluation

Executes stated checks against identified inputs and records each result, including checks that could not be evaluated.

**When it applies**

The application of one exact evaluation profile to one exact subject and input state, collecting every declared check outcome and causal dependency.

**Record formats**

[Evaluation · v1](type-cal-artifact-type-evaluation-v1.md#type-cal-artifact-type-evaluation-v1)

**A stated exclusion**

A claim that the subject conforms.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-evaluation-section-2"></a>

## Source explanatory wording

An Evaluation runs a declared set of checks against exact inputs and records every result, including the checks that could not yet be evaluated.

<a id="def-cal-definition-evaluation-section-3"></a>

## Exact governing statement

An Evaluation applies a version-exact profile P to a version-exact subject S and input state I, yielding a complete outcome set O with causal blockers preserved. Evaluation is an evidence-producing process; its outcomes do not exceed P's declared coverage or create authority.

````
evaluate(P@digest, S@digest, I@digest) -> O = {(check_id, PASS|FAIL|NOT_EVALUABLE, evidence_refs, blockers)}; O =/=> admitted(S).
````

- The profile, subject, and inputs are exact and current.
- Dependent checks are recorded as NOT_EVALUABLE rather than omitted.
- An evaluation result remains inside the profile's coverage.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Semantic foundation admission

**Original definition**

[Read the original record](../../assets/7ca1fc6de116-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.evaluation@1.0.0-candidate.1

**Content fingerprint · SHA-256**

7ca1fc6de116223f93d026856c7780320d600b79e454c0b4ef957bd03dd24a7b

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "authority_scope_ref": "scope:evaluation-definition",
  "applicability": "The application of one exact evaluation profile to one exact subject and input state, collecting every declared check outcome and causal dependency.",
  "exclusions": [
    "A claim that the subject conforms.",
    "A human admission or acceptance decision.",
    "An effectful execution not explicitly included in the profile."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
