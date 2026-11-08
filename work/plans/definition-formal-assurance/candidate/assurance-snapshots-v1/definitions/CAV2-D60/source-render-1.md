<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Project

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `CAV2-D60`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:project-definition`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

A Project is a durable coordination identity with purpose, scope, exclusions, owner routes, Goal references, evidence index, purpose or Product connections, lifecycle, and challenge route. Its identity survives changes to plans, tasks, folders, tools, and implementations.

```text
Project = (id, name, purpose, scope, exclusions, owner_routes, goal_refs, evidence_index, purpose_refs, lifecycle_state, challenge_route); |goal_refs| >= 1.
```

### Notation

| Symbol | Meaning |
| --- | --- |
| Project | One durable coordination identity. |

### Boundary conditions

- A proposed Project has at least one draft or active Goal.
- An active Project has at least one active Goal.
- Directory placement and membership do not create Project identity.

### Testable conditions

- Purpose, owner routes, Goal references, lifecycle, and challenge route are explicit.
- Project and Product IDs remain distinct.
- Project membership is represented by an explicit relation.

## Plain-language voice

A Project is the durable coordination identity that keeps related goals, decisions, evidence, and work together even when files and plans change.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

This candidate preserves CAV2-D60. CA2-PROJECT-CRAFT coordinates development of CA2-PRODUCT-CRAFT without becoming that Product.

### Examples

- The Craft Project pursues a Goal and uses the Craft Method through explicit relations.
- Moving a project directory does not change the Project identity.

## Applicability

A durable identity-bearing coordination boundary grouping related goals, owners, evidence, decisions, artifacts, work, and lifecycle toward a declared purpose.

### Exclusions

- A Product, Goal, Method, project space, repository, directory, plan, work pack, session, team, or authority envelope.

## Boundaries

- Project is not Product, Goal, Method, repository, directory, or authority.
- Coordination does not acquire the authority of coordinated artifacts.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.definition.definition@1.0.0-candidate.1 | whole-json | `eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575` | `admitted` |
| domainspec-core:CAV2-D60 | lines:4522-4602 | `3dc9faeecf91410b8b6a00aa8fd847d474031bd207e91743e72507dee6c526db` | `candidate-unadmitted` |
| domainspec-core:CA2-PROJECT-CRAFT | whole-file | `a3c940af28ab9436549d35d5f93848c427695433704e8b6715d80b7b69f05485` | `candidate-unadmitted` |
| domainspec-core:CA2-DECISION-CRAFT-IDENTITY-003 | whole-file | `1f2d01026865e031adba063de0dc1dfa081c49a931223aa4bc9f726d3397bceb` | `candidate-unadmitted` |

## Primary consumers

- authority/artifact-types/project-identity/v1
- coordination/projects/craft/v1/project.json

## Lookup and drift

- Index: `authority/definitions/candidates/0006-craft-identity/DEFINITIONS-INDEX.md` / `CAV2-D60`
- Drift owner: `role:definition-owner`
- Audit: `authority/definitions/candidates/0006-craft-identity/drift-audit-postimage.json`
- Challenge route: `route:definition-governance-challenge`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.governed-by | CAV2-D60@1.0.0-candidate.1 | role:definition-owner | role:definition-owner |
| relation.originates-from | CAV2-D60@1.0.0-candidate.1 | domainspec-core:CAV2-D60 | role:definition-owner |

## Evidence

- CAL-CML07-CRAFT-IDENTITY-CHAIN-0001
- CAL-SOURCE-ADMISSIONS-CRAFT-IDENTITY-V1
- CAL-OWNER-BINDINGS-CRAFT-IDENTITY-0004

## Residue

- project-identity-artifact-type-required
- craft-project-owner-activation-required

## Claim ceiling

This candidate migrates Project meaning while preserving CAV2-D60. It does not instantiate or activate the Craft Project or authorize coordinated work.
