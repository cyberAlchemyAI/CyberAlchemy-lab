<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Decision Policy

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `ea.decision-policy`
- Version: `0.1.0-candidate.1`
- Semantic owner: `role:ea-definitions-owner-unassigned`
- Authority scope: `scope:ea-project-candidate`
- Lifecycle posture reference: `candidate:ea-project-definition-review/v1`

## Scientific/formal voice

A Decision Policy is a frozen mapping from specified score inputs and uncertainty to a selection action at a stated capacity, with abstention, human review, accommodation and appeal rules.

### Notation

No notation is required.

### Boundary conditions

- A model score does not enact a hiring decision.
- A policy is not effective until the employer and applicable owners authorize that exact use.

### Testable conditions

None declared.

## Plain-language voice

The versioned rule that turns eligible evidence into an allowed recommendation or action under owner control.

## Domain-context voice

Workspace: `/home/vlad_/projects/engineer-assessment`

Candidate Decision Policy meaning for the Engineer Assessment product and research program. Its construct, implementation and use claims remain bounded by the source statement.

### Examples

None declared.

## Applicability

One role, population, employer, jurisdiction and claim tier.

### Exclusions

- Any other product or Lab-wide meaning without separate owner review and admission.

## Boundaries

- A model score does not enact a hiring decision.
- A policy is not effective until the employer and applicable owners authorize that exact use.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| model/definitions.json | /definitions/17 | `388fc306a48886a633bd22022713a7752040cab185fc1ece4d9e543e5a9ed5ac` | `candidate-unadmitted` |

## Primary consumers

- model/DEFINITIONS.md
- model/ontology.json
- research/full-protocol.md

## Lookup and drift

- Index: `model/definition-records/index.json` / `ea.decision-policy`
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
