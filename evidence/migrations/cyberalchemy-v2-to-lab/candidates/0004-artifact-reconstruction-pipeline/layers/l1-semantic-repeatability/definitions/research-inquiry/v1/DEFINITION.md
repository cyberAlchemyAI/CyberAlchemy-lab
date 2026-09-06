<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Research Inquiry

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.research-inquiry`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope.knowledge-development`
- Lifecycle posture reference: `candidate:artifact-reconstruction-l1/v1`

## Scientific/formal voice

Research Inquiry is the normalized definition identified by semantic.research-inquiry, owned within scope.knowledge-development, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D61 without silently merging it with another target.

Target-specific normative meaning:

A Research Inquiry is the bounded question, scope, source policy, method, Project and Goal linkage, owner route, and stopping conditions that define what a research effort intends to investigate before evidence is gathered.

Bound source-semantic basis:

Research is a bounded, attributable investigation that gathers and organizes
source material and observations to answer one declared question for a Project
and one or more Goals.

A Research artifact must preserve its question, scope, sources, method,
evidence aggregate, counterevidence, limitations, owner route, Goal and Project
links, and references to any separate findings. Research records what was
investigated and gathered. It does not silently turn its evidence aggregate
into a conclusion, decision, definition, specification, or product claim.

```text
```text
Research =
  (id, project_ref, goal_refs, question, scope, sources, method,
   evidence_aggregate, counterevidence, findings_refs, limitations,
   created, last_updated, owner_route, challenge_route)

Research.outcome is absent
Findings.question = Research.question
Findings derives_from Research
```
```

### Notation

| Symbol | Meaning |
| --- | --- |
| semantic.research-inquiry | Stable normalized identity for Research Inquiry. |
| CAV2-D61 | Bound CyberAlchemy-v2 source-definition identity. |

### Boundary conditions

- Research is not a Goal (`CAV2-D59`), Project (`CAV2-D60`), experiment
(`CAV2-D62`), findings, owner decision, canonical definition, proof, or
execution authority. It is an ephemeral canonical Evidence artifact: it records
an investigation at a time and cannot become authority by promotion.
- This target remains distinct from the sibling targets semantic.evidence-set, semantic.finding, semantic.research-run reconstructed from CAV2-D61; shared source lineage does not merge their identities or validation purposes.

### Testable conditions

- The candidate identity remains cal.definition.research-inquiry.
- Every selected source-section digest remains current.
- The machine record validates against Definition/v1.
- The human projection is regenerated exactly from the machine record.

## Plain-language voice

It defines the question and rules for a piece of research before the research is run.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

In CyberAlchemy-lab migration work, Research Inquiry is a prototype meaning reconstructed from CAL-NORMALIZE-01. It remains non-authoritative until the correct Lab owner admits a fully validated candidate.

Source context retained for reconstruction:

In CyberAlchemy v2, the PythonConstraint Research record explains why that
benchmark was selected, which exact sources support the selection, and which
questions about DomainSpec-v2 fit remain open. It informs the Project and Goal
without claiming that the experiment has run.

### Examples

- Resolve semantic.research-inquiry by its machine identity rather than its directory name.
- Challenge source drift through the L1 drift audit before relying on Research Inquiry.

## Applicability

Use Research when a Project must inspect literature, repositories, benchmarks,
past evidence, observations, or competing explanations before deciding what to
believe or do. Keep the aggregate separate from findings so a later reader can
see the source material without inheriting the synthesis as fact.

### Exclusions

- Admission, activation, publication, release, deployment, and external effects.
- Meanings assigned to split or reclassified sibling targets unless explicitly referenced.

## Boundaries

- Research is not a Goal (`CAV2-D59`), Project (`CAV2-D60`), experiment
(`CAV2-D62`), findings, owner decision, canonical definition, proof, or
execution authority. It is an ephemeral canonical Evidence artifact: it records
an investigation at a time and cannot become authority by promotion.
- This target remains distinct from the sibling targets semantic.evidence-set, semantic.finding, semantic.research-run reconstructed from CAV2-D61; shared source lineage does not merge their identities or validation purposes.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cyberalchemy-v2:CAV2-D61 | ## CAV2-D61: Research | `ace1c0c50ec2ecf0e2a6df9d9a855cb30f6ad4f763ae2a4589da4ea586e5b4fb` | `candidate-unadmitted` |

## Primary consumers

- semantic.experiment-design
- semantic.experiment-run
- semantic.observation

## Lookup and drift

- Index: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/registry.json` / `cal.definition.research-inquiry@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/drift-audit.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.originates-from | cal.definition.research-inquiry | cyberalchemy-v2:CAV2-D61 | role:definition-owner |

## Evidence

- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0003-review-led-reconstruction/target-candidates/semantic/semantic-research-inquiry/v1/artifact.json
- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/receipts/validation.json
- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/receipts/validation.json

## Residue

- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/drift-audit.json

## Claim ceiling

Candidate Definition reconstructed from an accepted normalization scaffold and exact CyberAlchemy-v2 source sections. It is not admitted and grants no implementation, migration, registry, publication, release, deployment, or external-effect authority.
