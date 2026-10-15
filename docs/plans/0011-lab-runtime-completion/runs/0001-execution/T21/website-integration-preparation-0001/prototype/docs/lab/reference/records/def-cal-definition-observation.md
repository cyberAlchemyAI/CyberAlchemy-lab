[Documentation home](../../README.md)

# Observation

<a id="def-cal-definition-observation"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Observation

# Observation

Records what was seen or measured during a Research or Experiment Run, with conditions and uncertainty, before interpreting its meaning.

**When it applies**

Use an Experiment when a Project needs observations created by a repeatable test rather than only existing sources or argument. Freeze the protocol inputs and claim limits before treating run output as comparable evidence. Keep design, run evidence, analysis, and owner decisions distinct.

**Record formats**

[Observation · v1](type-cal-artifact-type-observation-v1.md#type-cal-artifact-type-observation-v1)

**A stated exclusion**

Admission, activation, publication, release, deployment, and external effects.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-observation-section-2"></a>

## Source explanatory wording

An observation records what was seen or measured, before interpreting what it means.

<a id="def-cal-definition-observation-section-3"></a>

## Exact governing statement

Observation is the normalized definition identified by semantic.observation, owned within scope.knowledge-development, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D62 without silently merging it with another target.

Target-specific normative meaning:

An Observation is an attributable record of something measured, perceived, or recorded during a Research or Experiment Run, together with its method, conditions, provenance, and uncertainty; it is not yet an explanatory finding.

Bound source-semantic basis:

An experiment is a bounded, attributable empirical test that produces observations by applying a declared protocol to a defined subject under named conditions in order to test a question, hypothesis, Goal condition, or Research question.

An Experiment artifact must preserve its Project and Goal links, Research links when present, question or hypothesis, subject, protocol, conditions, variables or interventions, measures, environment, prerequisites, stop rules, run references, evidence references, findings references, limitations, owner route, and challenge route. Missing run evidence means the experiment was not shown to have run.

````
```text
Experiment =
  (id, project_ref, goal_refs, research_refs, question_or_hypothesis,
   subject, protocol_ref, conditions, variables_or_interventions,
   measures, environment, prerequisites, stop_rules, run_refs,
   evidence_refs, findings_refs, limitations, created, last_updated,
   owner_route, challenge_route)

ran(Experiment) only if valid_run_refs_exist
concluded(Experiment) only through separate Findings or owner decision
```
````

- An experiment is not Research (`CAV2-D61`), a Goal (`CAV2-D59`), a plan, a runtime, a test suite, one command, findings, causal proof, or authority to run. It is an ephemeral canonical Evidence artifact. A successful validator can show that its record is well formed; it cannot show that the experiment ran or that its hypothesis is true.
- This target remains distinct from the sibling targets semantic.experiment-design, semantic.experiment-run reconstructed from CAV2-D62; shared source lineage does not merge their identities or validation purposes.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../assets/ecdb79cc3cc5-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.observation@1.0.0-candidate.1

**Content fingerprint · SHA-256**

ecdb79cc3cc5ba8030bee0bd4a80e577944828221c4849866b04e8ad90d83183

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Use an Experiment when a Project needs observations created by a repeatable\ntest rather than only existing sources or argument. Freeze the protocol inputs\nand claim limits before treating run output as comparable evidence. Keep design,\nrun evidence, analysis, and owner decisions distinct.",
  "authority_scope_ref": "scope.knowledge-development",
  "exclusions": [
    "Admission, activation, publication, release, deployment, and external effects.",
    "Meanings assigned to split or reclassified sibling targets unless explicitly referenced."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
