<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Estimand

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `ea.estimand`
- Version: `0.1.0-candidate.1`
- Semantic owner: `role:ea-definitions-owner-unassigned`
- Authority scope: `scope:ea-project-candidate`
- Lifecycle posture reference: `candidate:ea-project-definition-review/v1`

## Scientific/formal voice

An Estimand is the exact population-level quantity a study intends to learn, specifying population, outcome, policies or conditions compared, capacity, time horizon and treatment of missing outcomes before estimating it.

```text
Delta_U = U(pi_A; P,C,T,Y) - U(pi_B; P,C,T,Y)
```

### Notation

| Symbol | Meaning |
| --- | --- |
| U | selection utility defined for the target population and outcome |
| pi_A | candidate decision policy |
| pi_B | comparator policy |
| P | target pool |
| C | selection capacity |
| T | outcome horizon |
| Y | independent outcome |

### Boundary conditions

- An observed sample statistic is an estimate, not the estimand itself.
- Top-capacity utility for all applicants is not identified from hired-only outcomes without additional design and assumptions.

### Testable conditions

None declared.

## Plain-language voice

It states precisely what difference the experiment is trying to estimate before the data arrive.

## Domain-context voice

Workspace: `/home/vlad_/projects/engineer-assessment`

Candidate Estimand meaning for the Engineer Assessment product and research program. Its construct, implementation and use claims remain bounded by the source statement.

### Examples

None declared.

## Applicability

One registered hypothesis or decision comparison.

### Exclusions

- Any other product or Lab-wide meaning without separate owner review and admission.

## Boundaries

- An observed sample statistic is an estimate, not the estimand itself.
- Top-capacity utility for all applicants is not identified from hired-only outcomes without additional design and assumptions.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| model/definitions.json | /definitions/26 | `9b4acc6f96f4cf70495aaabdba3ad6da6642f93890c7515c57248765a6272649` | `candidate-unadmitted` |

## Primary consumers

- model/DEFINITIONS.md
- model/ontology.json
- research/full-protocol.md

## Lookup and drift

- Index: `model/definition-records/index.json` / `ea.estimand`
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
