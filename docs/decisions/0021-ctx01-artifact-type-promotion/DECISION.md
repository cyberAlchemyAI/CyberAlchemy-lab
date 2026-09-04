<!-- GENERATED FILE: edit decision.json and rerun render-decision.py. -->

# CTX01 artifact-type admission decision

> Machine-canonical decision; this Markdown is a generated projection.

- Status: `owner-admitted`
- Selection: `ADMIT-CTX01-ARTIFACT-TYPES-V1`
- Owner: `artifact-type-owner -> person:<vrondelli>`
- Recorded: `2026-09-02T18:57:01Z`

## Admitted artifact types

| Artifact type | Artifact | Schema |
| --- | --- | --- |
| `cal.artifact-type.bounded-context/v1` | `authority/artifact-types/bounded-context/v1/artifact.json` | `authority/artifact-types/bounded-context/v1/schema.json` |
| `cal.artifact-type.ubiquitous-language/v1` | `authority/artifact-types/ubiquitous-language/v1/artifact.json` | `authority/artifact-types/ubiquitous-language/v1/schema.json` |
| `cal.artifact-type.capability-instance/v1` | `authority/artifact-types/capability-instance/v1/artifact.json` | `authority/artifact-types/capability-instance/v1/schema.json` |
| `cal.artifact-type.coordination-context/v1` | `authority/artifact-types/coordination-context/v1/artifact.json` | `authority/artifact-types/coordination-context/v1/schema.json` |
| `cal.artifact-type.context-map/v1` | `authority/artifact-types/context-map/v1/artifact.json` | `authority/artifact-types/context-map/v1/schema.json` |
| `cal.artifact-type.context-migration-manifest/v1` | `authority/artifact-types/context-migration-manifest/v1/artifact.json` | `authority/artifact-types/context-migration-manifest/v1/schema.json` |
| `cal.artifact-type.context-lineage-record/v1` | `authority/artifact-types/context-lineage-record/v1/artifact.json` | `authority/artifact-types/context-lineage-record/v1/schema.json` |

## Admission result

Artifact Type/v1 successor current: `True`

Artifact types admitted: `7`

## Excluded effects

- Shared schema mechanics, generators, validators, fixtures, and receipts remain evidence and local tooling; they are not admitted runtimes or implementation bindings.
- No operational context, language, map, migration, lineage, or capability-instance owner is bound.
- No Bounded Context, Coordination Context, Ubiquitous Language, Context Map, Capability Instance, Context Migration Manifest, or Context Lineage Record instance is created or admitted.
- No migration execution, implementation authority, publication, deployment, external effect, or stable release is authorized or performed.

## Successor obligations

- Re-enter routing before preparing operational owner-role bindings.
- Admit exact operational owner identities and role scopes before authoring any context-metamodel instance.
- Author Governance and Ontology Lifecycle context instances only after those owner bindings validate.
- Keep Context Map relationship selection and physical migration as separate later decisions.

## Claim ceiling

This decision makes Artifact Type/v1 candidate.2 the current registration overlay and admits only the seven exact CTX01 artifact-type contracts. It does not admit tooling as runtime authority, bind operational owners, create context-metamodel instances, authorize migration or implementation, publish, deploy, or establish a stable release.
