<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Integration Boundary

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `ea.integration-boundary`
- Version: `0.1.0-candidate.1`
- Semantic owner: `role:ea-definitions-owner-unassigned`
- Authority scope: `scope:ea-project-candidate`
- Lifecycle posture reference: `candidate:ea-project-definition-review/v1`

## Scientific/formal voice

An Integration Boundary is a versioned, owner-scoped point where product components, external services or trust zones exchange data or responsibility under a stable behavioral contract. It identifies the producer and consumer, inputs and outputs, data sensitivity and purpose, required invariants, failure and recovery behavior, and the interface that candidate implementations must satisfy independent of vendor choice.

### Notation

No notation is required.

### Boundary conditions

- A boundary is not a vendor, library, implementation, option review, test result or deployed binding.
- A diagram arrow or boundary name alone does not specify the contract, custody or owner; changing its behavioral obligation requires a new version and review.

### Testable conditions

None declared.

## Plain-language voice

The stable seam in the product: what crosses it and what must remain true even if the library or provider changes.

## Domain-context voice

Workspace: `/home/vlad_/projects/engineer-assessment`

Candidate Integration Boundary meaning for the Engineer Assessment product and research program. Its construct, implementation and use claims remain bounded by the source statement.

### Examples

None declared.

## Applicability

One named product capability crossing or replaceable subsystem interface across option and release cycles.

### Exclusions

- Any other product or Lab-wide meaning without separate owner review and admission.

## Boundaries

- A boundary is not a vendor, library, implementation, option review, test result or deployed binding.
- A diagram arrow or boundary name alone does not specify the contract, custody or owner; changing its behavioral obligation requires a new version and review.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| model/definitions.json | /definitions/85 | `872f620092ad78fde583f97c710f94a0e17e8152032ab900965a26d1c97532b7` | `candidate-unadmitted` |

## Primary consumers

- model/DEFINITIONS.md
- model/ontology.json
- software/DEFINITION-COVERAGE.md

## Lookup and drift

- Index: `model/definition-records/index.json` / `ea.integration-boundary`
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
