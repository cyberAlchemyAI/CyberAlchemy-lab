<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Case Generation Run

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `ea.generation-run`
- Version: `0.1.0-candidate.1`
- Semantic owner: `role:ea-definitions-owner-unassigned`
- Authority scope: `scope:ea-project-candidate`
- Lifecycle posture reference: `candidate:ea-project-definition-review/v1`

## Scientific/formal voice

A Case Generation Run is one reproducible execution of a pinned Case Generator against one Generation Brief, retaining model or human author, prompt/configuration, seed where applicable, inputs, all outputs, cost and failure receipts.

### Notation

No notation is required.

### Boundary conditions

- Reproducible inputs do not guarantee identical stochastic output.
- A run cannot approve or publish its own candidates.

### Testable conditions

None declared.

## Plain-language voice

It records exactly how a batch of draft questions was produced, including rejected drafts.

## Domain-context voice

Workspace: `/home/vlad_/projects/engineer-assessment`

Candidate Case Generation Run meaning for the Engineer Assessment product and research program. Its construct, implementation and use claims remain bounded by the source statement.

### Examples

None declared.

## Applicability

One candidate-producing execution; no live administration.

### Exclusions

- Any other product or Lab-wide meaning without separate owner review and admission.

## Boundaries

- Reproducible inputs do not guarantee identical stochastic output.
- A run cannot approve or publish its own candidates.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| model/definitions.json | /definitions/63 | `ee71e3997b38376b76da25a94a1bc4d9cc41a7b5470242f68e4aa7b5b02926dc` | `candidate-unadmitted` |

## Primary consumers

- model/DEFINITIONS.md
- model/ontology.json
- software/QUESTION-LIFECYCLE.md

## Lookup and drift

- Index: `model/definition-records/index.json` / `ea.generation-run`
- Drift owner: `role:ea-definitions-owner-unassigned`
- Audit: `tools/validate_definition_records.py`
- Challenge route: `role:ea-independent-reviewer-unassigned`

## Typed relations

No typed relations declared.

## Evidence

None declared.

## Residue

None declared.

## Claim ceiling

Generated project-scoped candidate Definition record only. Shape and projection checks grant no Lab admission, semantic truth, implementation, collection or employment-use authority.
