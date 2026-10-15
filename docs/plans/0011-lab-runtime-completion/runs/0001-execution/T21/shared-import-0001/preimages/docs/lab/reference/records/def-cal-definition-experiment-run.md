[Documentation home](../../README.md)

# Experiment Run

<a id="def-cal-definition-experiment-run"></a>

[Reference catalog](../definitions.md#catalog-definitions) / Exact record

# Experiment Run

A record of one execution of an experiment design, including conditions, deviations and observations.

**When it applies**

Use an Experiment when a Project needs observations created by a repeatable test rather than only existing sources or argument. Freeze the protocol inputs and claim limits before treating run output as comparable evidence. Keep design, run evidence, analysis, and owner decisions distinct.

**Record formats**

[Experiment run · v1](type-cal-artifact-type-experiment-run-v1.md#type-cal-artifact-type-experiment-run-v1)

**A stated exclusion**

Admission, activation, publication, release, deployment, and external effects.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

## Source explanatory wording

It records what happened in one execution of the planned experiment.

## Exact governing statement

Experiment Run is the normalized definition identified by semantic.experiment-run, owned within scope.knowledge-development, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D62 without silently merging it with another target.

Target-specific normative meaning:

An Experiment Run is one attributable execution of an Experiment Design that records the actual environment, inputs, interventions, deviations, observations, timestamps, stop condition, and evidence produced.

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
- This target remains distinct from the sibling targets semantic.experiment-design, semantic.observation reconstructed from CAV2-D62; shared source lineage does not merge their identities or validation purposes.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../../../evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/definitions/experiment-run/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.experiment-run@1.0.0-candidate.1

**Content fingerprint · SHA-256**

70997d63ff433df6fa0588a8a441a6a82219fc7f37d1d4e12a83aee35b045533

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

[Return to this catalog](../definitions.md#catalog-definitions)
