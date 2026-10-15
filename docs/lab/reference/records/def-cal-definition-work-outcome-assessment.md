[Documentation home](../../README.md)

# Work Outcome Assessment

<a id="def-cal-definition-work-outcome-assessment"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Work Outcome Assessment

# Work Outcome Assessment

Compares the stated expected result of a work item or action with evidence of the observed result. It does not by itself establish lesson value or broader product benefit.

**When it applies**

A Work Outcome Assessment is an evidence-bounded comparison between one Work item or Agent Action’s declared expected result and its observed result.

**Record formats**

[Work outcome assessment · v1](type-cal-artifact-type-work-outcome-assessment-v1.md#type-cal-artifact-type-work-outcome-assessment-v1)

**A stated exclusion**

It does not by itself establish lesson value, causal attribution, Product value, acceptance, or authority effect.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-work-outcome-assessment-section-2"></a>

## Source explanatory wording

A Work Outcome Assessment is an evidence-bounded comparison between one Work item or Agent Action’s declared expected result and its observed result. It does not by itself establish lesson value, causal attribution, Product value, acceptance, or authority effect.

<a id="def-cal-definition-work-outcome-assessment-section-3"></a>

## Exact governing statement

A Work Outcome Assessment is an evidence-bounded comparison between one Work item or Agent Action’s declared expected result and its observed result. It does not by itself establish lesson value, causal attribution, Product value, acceptance, or authority effect.

````
WorkOutcomeAssessment(x) => governed_identity_or_record(x) and bounded_scope(x); WorkOutcomeAssessment(x) =/=> authority_effect(x).
````

- A Work Outcome Assessment is an evidence-bounded comparison between one Work item or Agent Action’s declared expected result and its observed result.
- It does not by itself establish lesson value, causal attribution, Product value, acceptance, or authority effect.
- Identity, lifecycle, evidence, authority, and relation effects remain separately governed.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Integrated definition model admission

**Original definition**

[Read the original record](../../../../authority/definitions/candidates/0013-integrated-lab-definition-model/definitions/work-outcome-assessment/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.work-outcome-assessment@1.0.0-candidate.1

**Content fingerprint · SHA-256**

9619d54051cc3aef3d98e4d7f3bfccc98f777ab3e39afe654ad8a7f50e71cdfc

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "A Work Outcome Assessment is an evidence-bounded comparison between one Work item or Agent Action’s declared expected result and its observed result.",
  "authority_scope_ref": "scope:work-outcome-assessment-definition",
  "exclusions": [
    "It does not by itself establish lesson value, causal attribution, Product value, acceptance, or authority effect.",
    "This Definition does not create or admit an Artifact Type, instance, relation, Policy, Decision, runtime, authority grant, or external effect."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
