<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Identity Vault

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `ea.identity-vault`
- Version: `0.1.0-candidate.1`
- Semantic owner: `role:ea-definitions-owner-unassigned`
- Authority scope: `scope:ea-project-candidate`
- Lifecycle posture reference: `candidate:ea-project-definition-review/v1`

## Scientific/formal voice

An Identity Vault is the restricted mapping between a Challenge Participant's pseudonym and contact or reidentification data, with separate access, retention and deletion controls.

### Notation

No notation is required.

### Boundary conditions

- A vault is not a research extract or scorer input.
- Storing a key separately does not alone prevent reidentification.

### Testable conditions

None declared.

## Plain-language voice

It holds the information needed to contact a person or answer their data request away from their scored answer.

## Domain-context voice

Workspace: `/home/vlad_/projects/engineer-assessment`

Candidate Identity Vault meaning for the Engineer Assessment product and research program. Its construct, implementation and use claims remain bounded by the source statement.

### Examples

None declared.

## Applicability

One challenge deployment and its authorized identity operations.

### Exclusions

- Any other product or Lab-wide meaning without separate owner review and admission.

## Boundaries

- A vault is not a research extract or scorer input.
- Storing a key separately does not alone prevent reidentification.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| model/definitions.json | /definitions/59 | `01240396a11b626ef8f0302869e49cee2e60f3131f81ac5a80054fe1d988871b` | `candidate-unadmitted` |

## Primary consumers

- model/DEFINITIONS.md
- model/ontology.json
- software/DEFINITION-COVERAGE.md

## Lookup and drift

- Index: `model/definition-records/index.json` / `ea.identity-vault`
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
