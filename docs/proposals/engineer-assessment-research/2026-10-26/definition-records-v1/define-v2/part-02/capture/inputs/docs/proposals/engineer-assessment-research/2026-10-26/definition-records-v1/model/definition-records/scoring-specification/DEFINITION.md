<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Scoring Specification

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `ea.scoring-specification`
- Version: `0.1.0-candidate.1`
- Semantic owner: `role:ea-definitions-owner-unassigned`
- Authority scope: `scope:ea-project-candidate`
- Lifecycle posture reference: `candidate:ea-project-definition-review/v1`

## Scientific/formal voice

A Scoring Specification is a versioned rule set mapping elicited Criterion Ratings and declared missingness to session and optional composite scores, uncertainty and permitted interpretations for one declared formative or role-linked purpose.

```text
S_v = f_v(ratings, missingness, case, role, mode)
```

### Notation

| Symbol | Meaning |
| --- | --- |
| S_v | score under version v |
| f_v | frozen version-specific scoring rule |

### Boundary conditions

- A formula alone does not validate what a score means.
- Changing weights, transformations or missingness rules creates a new score version.

### Testable conditions

None declared.

## Plain-language voice

It is the recipe that turns evidence-based ratings into a reportable number and states when that number should not be used.

## Domain-context voice

Workspace: `/home/vlad_/projects/engineer-assessment`

Candidate Scoring Specification meaning for the Engineer Assessment product and research program. Its construct, implementation and use claims remain bounded by the source statement.

### Examples

None declared.

## Applicability

One score version and compatible role, cases, rubrics and modes.

### Exclusions

- Any other product or Lab-wide meaning without separate owner review and admission.

## Boundaries

- A formula alone does not validate what a score means.
- Changing weights, transformations or missingness rules creates a new score version.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| model/definitions.json | /definitions/22 | `388fc306a48886a633bd22022713a7752040cab185fc1ece4d9e543e5a9ed5ac` | `candidate-unadmitted` |

## Primary consumers

- model/DEFINITIONS.md
- model/ontology.json
- research/full-protocol.md

## Lookup and drift

- Index: `model/definition-records/index.json` / `ea.scoring-specification`
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
