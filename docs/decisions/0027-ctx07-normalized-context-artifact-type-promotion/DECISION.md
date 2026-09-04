<!-- GENERATED FILE: edit decision.json and rerun render.py. -->

# CTX07 normalized Bounded Context and Context Map artifact-type admission

> Machine-canonical decision; this Markdown is a generated projection.

- Decision: `CAL-DECISION-0027-CTX07-NORMALIZED-CONTEXT-ARTIFACT-TYPE-PROMOTION`
- Status: `owner-admitted`
- Authority effect: `two-normalized-context-artifact-type-versions-admitted-for-new-construction`
- Selection: `ADMIT-CTX07-NORMALIZED-CONTEXT-ARTIFACT-TYPES-V2`
- Principal: `person:<vrondelli>` as `artifact-type-owner`
- Recorded: `2026-09-03T04:08:12Z`

## Admitted artifact types

| Artifact type | Version | Predecessor | Digest |
| --- | --- | --- | --- |
| `cal.artifact-type.bounded-context/v2` | `2.0.0-candidate.1` | `cal.artifact-type.bounded-context/v1` | `c5d9d28582856759119761910b889b4d6e03eaac33622950b0049b3f24ab72bc` |
| `cal.artifact-type.context-map/v2` | `2.0.0-candidate.1` | `cal.artifact-type.context-map/v1` | `d0c8474eabefeea9a7b9cb18c8c0a80282a82eaae564d4f1c73ef4b60578626c` |

## Admission result

- Artifact types admitted: `2`
- Current for new normalized construction: `2`
- Predecessors withdrawn: `0`
- Predecessors superseded: `0`
- Context instances created: `0`
- Context Maps created: `0`
- Tooling runtimes admitted: `0`

## Materialization

Admission is an exact decision overlay over immutable candidate bytes. The two v2 records retain candidate version labels because lifecycle authority changes through this decision rather than by rewriting their machine-canonical sources.

Both v1 artifact types remain byte-preserved admitted history. This successor admission neither withdraws nor supersedes them and does not reinterpret historical instances.

New normalized Bounded Context and Context Map construction must cite the exact admitted v2 artifact-type refs. Historical artifacts continue resolving their exact v1 bindings.

Context Map membership is canonical only in exact map.json inputs. Any reverse context-to-map index is generated, disposable, noncanonical, and authority-free.

## Excluded effects

- No CTX07 candidate, schema, projection, fixture, validation receipt, v1 predecessor, Definition, registry, context, map, migration, or earlier decision byte is rewritten, withdrawn, superseded, or deleted.
- Shared schemas, generators, validators, fixtures, and receipts remain exact supporting evidence and local tooling; they are not admitted as runtime or enforcement authority.
- No Governance or Ontology Lifecycle Bounded Context or Ubiquitous Language epoch is authored, revised, admitted, withdrawn, or cut over.
- No successor Context Map, lineage record, migration amendment, source relocation, migration execution, implementation, commit, push, publication, deployment, external effect, or stable release is authorized or performed.

## Successor obligations

- Author new Governance and Ontology Lifecycle Bounded Context epochs against cal.artifact-type.bounded-context/v2 without canonical context_map_refs.
- Preserve their existing Ubiquitous Language ownership and explicit lineage while keeping CTX05 bytes as admitted history.
- Author a successor Context Map against cal.artifact-type.context-map/v2 with exact endpoint membership and typed directional relationships.
- Generate reverse membership only from exact admitted Context Map inputs, then author a source- and rollback-bound migration amendment before any cutover.

## Claim ceiling

This decision admits only the exact Bounded Context/v2 and Context Map/v2 artifact-type contracts for new normalized construction. It binds shared mechanics and validation as evidence but does not admit tooling as runtime authority, revise or create context or map instances, authorize migration, commit, publish, deploy, or establish stable-release state.
