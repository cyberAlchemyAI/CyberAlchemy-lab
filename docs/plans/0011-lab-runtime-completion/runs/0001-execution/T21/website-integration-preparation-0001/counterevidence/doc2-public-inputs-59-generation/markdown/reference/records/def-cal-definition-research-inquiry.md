[Documentation home](../../README.md)

# Research Inquiry

<a id="def-cal-definition-research-inquiry"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Research Inquiry

# Research Inquiry

Defines a research question, scope, source rules, method and stopping conditions before the investigation runs.

**When it applies**

Use Research when a Project must inspect literature, repositories, benchmarks, past evidence, observations, or competing explanations before deciding what to believe or do. Keep the aggregate separate from findings so a later reader can see the source material without inheriting the synthesis as fact.

**Record formats**

[Research inquiry · v1](type-cal-artifact-type-research-inquiry-v1.md#type-cal-artifact-type-research-inquiry-v1)

**A stated exclusion**

Admission, activation, publication, release, deployment, and external effects.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-research-inquiry-section-2"></a>

## Source explanatory wording

It defines the question and rules for a piece of research before the research is run.

<a id="def-cal-definition-research-inquiry-section-3"></a>

## Exact governing statement

Research Inquiry is the normalized definition identified by semantic.research-inquiry, owned within scope.knowledge-development, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D61 without silently merging it with another target.

Target-specific normative meaning:

A Research Inquiry is the bounded question, scope, source policy, method, Project and Goal linkage, owner route, and stopping conditions that define what a research effort intends to investigate before evidence is gathered.

Bound source-semantic basis:

Research is a bounded, attributable investigation that gathers and organizes source material and observations to answer one declared question for a Project and one or more Goals.

A Research artifact must preserve its question, scope, sources, method, evidence aggregate, counterevidence, limitations, owner route, Goal and Project links, and references to any separate findings. Research records what was investigated and gathered. It does not silently turn its evidence aggregate into a conclusion, decision, definition, specification, or product claim.

````
```text
Research =
  (id, project_ref, goal_refs, question, scope, sources, method,
   evidence_aggregate, counterevidence, findings_refs, limitations,
   created, last_updated, owner_route, challenge_route)

Research.outcome is absent
Findings.question = Research.question
Findings derives_from Research
```
````

- Research is not a Goal (`CAV2-D59`), Project (`CAV2-D60`), experiment (`CAV2-D62`), findings, owner decision, canonical definition, proof, or execution authority. It is an ephemeral canonical Evidence artifact: it records an investigation at a time and cannot become authority by promotion.
- This target remains distinct from the sibling targets semantic.evidence-set, semantic.finding, semantic.research-run reconstructed from CAV2-D61; shared source lineage does not merge their identities or validation purposes.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../assets/0a5445e95404-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.research-inquiry@1.0.0-candidate.1

**Content fingerprint · SHA-256**

0a5445e954049cdd5abcee276fef085f97e409ebd325e571c489c4db92efafe7

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Use Research when a Project must inspect literature, repositories, benchmarks,\npast evidence, observations, or competing explanations before deciding what to\nbelieve or do. Keep the aggregate separate from findings so a later reader can\nsee the source material without inheriting the synthesis as fact.",
  "authority_scope_ref": "scope.knowledge-development",
  "exclusions": [
    "Admission, activation, publication, release, deployment, and external effects.",
    "Meanings assigned to split or reclassified sibling targets unless explicitly referenced."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
