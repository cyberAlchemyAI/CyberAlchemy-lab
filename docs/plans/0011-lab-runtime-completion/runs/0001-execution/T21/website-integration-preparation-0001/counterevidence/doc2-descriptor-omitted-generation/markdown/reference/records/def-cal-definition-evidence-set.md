[Documentation home](../../README.md)

# Evidence Set

<a id="def-cal-definition-evidence-set"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Evidence Set

# Evidence Set

Organizes evidence for a stated question, including material against the conclusion and gaps in support.

**When it applies**

When assembling provenance-preserving support, counterevidence and limitations for one declared question or claim.

**Record formats**

[Evidence set · v1](type-cal-artifact-type-evidence-set-v1.md#type-cal-artifact-type-evidence-set-v1)

**[In the Northstar incident](../../tutorials/incident-walkthrough.md)**

Group the selected inputs, method and result that bear on the omission assessment.

**Common mistake**

Assuming that assembling the set accepts its claims.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-evidence-set-section-2"></a>

## Source explanatory wording

It is the organized body of evidence for a question, including what pushes against the answer and where the evidence is weak.

<a id="def-cal-definition-evidence-set-section-3"></a>

## Exact governing statement

Evidence Set is the normalized definition identified by semantic.evidence-set, owned within scope.knowledge-development, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D61 without silently merging it with another target.

Target-specific normative meaning:

An Evidence Set is a bounded, provenance-preserving aggregate of supporting evidence, counterevidence, limitations, freshness, and applicability assembled for one declared question or claim without itself becoming a finding or decision.

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
- This target remains distinct from the sibling targets semantic.finding, semantic.research-inquiry, semantic.research-run reconstructed from CAV2-D61; shared source lineage does not merge their identities or validation purposes.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../assets/26f072c0292c-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.evidence-set@1.0.0-candidate.1

**Content fingerprint · SHA-256**

26f072c0292c4b7349726061f7df218ef1ce883c08888d33e375d4cbe1dd7148

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
