<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Experiment Run

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.experiment-run`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope.knowledge-development`
- Lifecycle posture reference: `candidate:artifact-reconstruction-l1/v1`

## Scientific/formal voice

Experiment Run is the normalized definition identified by semantic.experiment-run, owned within scope.knowledge-development, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D62 without silently merging it with another target.

Target-specific normative meaning:

An Experiment Run is one attributable execution of an Experiment Design that records the actual environment, inputs, interventions, deviations, observations, timestamps, stop condition, and evidence produced.

Bound source-semantic basis:

An experiment is a bounded, attributable empirical test that produces
observations by applying a declared protocol to a defined subject under named
conditions in order to test a question, hypothesis, Goal condition, or Research
question.

An Experiment artifact must preserve its Project and Goal links, Research
links when present, question or hypothesis, subject, protocol, conditions,
variables or interventions, measures, environment, prerequisites, stop rules,
run references, evidence references, findings references, limitations, owner
route, and challenge route. Missing run evidence means the experiment was not
shown to have run.

```text
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
```

### Notation

| Symbol | Meaning |
| --- | --- |
| semantic.experiment-run | Stable normalized identity for Experiment Run. |
| CAV2-D62 | Bound CyberAlchemy-v2 source-definition identity. |

### Boundary conditions

- An experiment is not Research (`CAV2-D61`), a Goal (`CAV2-D59`), a plan, a
runtime, a test suite, one command, findings, causal proof, or authority to run.
It is an ephemeral canonical Evidence artifact. A successful validator can show
that its record is well formed; it cannot show that the experiment ran or that
its hypothesis is true.
- This target remains distinct from the sibling targets semantic.experiment-design, semantic.observation reconstructed from CAV2-D62; shared source lineage does not merge their identities or validation purposes.

### Testable conditions

- The candidate identity remains cal.definition.experiment-run.
- Every selected source-section digest remains current.
- The machine record validates against Definition/v1.
- The human projection is regenerated exactly from the machine record.

## Plain-language voice

It records what happened in one execution of the planned experiment.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

In CyberAlchemy-lab migration work, Experiment Run is a prototype meaning reconstructed from CAL-NORMALIZE-01. It remains non-authoritative until the correct Lab owner admits a fully validated candidate.

Source context retained for reconstruction:

In CyberAlchemy v2, the PythonConstraint Experiment record narrows the prepared
Define downstream-utility protocol to the owner-selected benchmark. Until exact
run receipts exist, it remains a documented experiment design and cannot
support a claim that Define or DomainSpec improves engineering outcomes.

### Examples

- Resolve semantic.experiment-run by its machine identity rather than its directory name.
- Challenge source drift through the L1 drift audit before relying on Experiment Run.

## Applicability

Use an Experiment when a Project needs observations created by a repeatable
test rather than only existing sources or argument. Freeze the protocol inputs
and claim limits before treating run output as comparable evidence. Keep design,
run evidence, analysis, and owner decisions distinct.

### Exclusions

- Admission, activation, publication, release, deployment, and external effects.
- Meanings assigned to split or reclassified sibling targets unless explicitly referenced.

## Boundaries

- An experiment is not Research (`CAV2-D61`), a Goal (`CAV2-D59`), a plan, a
runtime, a test suite, one command, findings, causal proof, or authority to run.
It is an ephemeral canonical Evidence artifact. A successful validator can show
that its record is well formed; it cannot show that the experiment ran or that
its hypothesis is true.
- This target remains distinct from the sibling targets semantic.experiment-design, semantic.observation reconstructed from CAV2-D62; shared source lineage does not merge their identities or validation purposes.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cyberalchemy-v2:CAV2-D62 | ## CAV2-D62: Experiment | `f246fa1d41bfd244e512699f1aa5c57b86c269693be160bc75096c58d18af6d3` | `candidate-unadmitted` |

## Primary consumers

- semantic.evidence-set
- semantic.finding
- semantic.research-inquiry
- semantic.research-run

## Lookup and drift

- Index: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/registry.json` / `cal.definition.experiment-run@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/drift-audit.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.originates-from | cal.definition.experiment-run | cyberalchemy-v2:CAV2-D62 | role:definition-owner |

## Evidence

- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0003-review-led-reconstruction/target-candidates/semantic/semantic-experiment-run/v1/artifact.json
- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/receipts/validation.json
- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/receipts/validation.json

## Residue

- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/drift-audit.json

## Claim ceiling

Candidate Definition reconstructed from an accepted normalization scaffold and exact CyberAlchemy-v2 source sections. It is not admitted and grants no implementation, migration, registry, publication, release, deployment, or external-effect authority.
