<!-- GENERATED FILE: edit decision.json and rerun render.py. -->

# CTX06 Context Map reference-normalization Definition admission

> Machine-canonical decision; this Markdown is a generated projection.

- Decision: `CAL-DECISION-0026-CTX06-REFERENCE-NORMALIZATION-DEFINITION-PROMOTION`
- Status: `owner-admitted`
- Authority effect: `two-successor-definition-versions-admitted-and-current-lookup-selected`
- Selection: `ADMIT-CTX06-REFERENCE-NORMALIZATION-DEFINITIONS-V2`
- Principal: `person:<vrondelli>` as `definition-owner`
- Recorded: `2026-09-03T03:41:57Z`

## Admitted Definition successors

| Definition | Version | Predecessor | Digest |
| --- | --- | --- | --- |
| `cal.definition.bounded-context` | `2.0.0-candidate.1` | `cal.definition.bounded-context@1.0.0-candidate.1` | `6ee155d2e7427e33357e55e56bc5228c2b584ea435bb9dc516ddb66385f590c0` |
| `cal.definition.context-map` | `2.0.0-candidate.1` | `cal.definition.context-map@1.0.0-candidate.1` | `677ff95db15b30a80e2d59673286142337c3a513e52fd27dd033fe710f8de050` |

## Admission result

- Successor Definitions admitted: `2`
- Canonical Definition versions: `10`
- Current Definition terms: `8`
- Predecessors withdrawn: `0`
- Artifact types revised: `0`

## Materialization

The exact owner token admits the two immutable Definition candidates and deterministically materializes their decision-bound live registry, current lookup, generated index, and current drift audit.

Both v1 Definition versions remain byte-preserved and admitted historical authority. The successor-of relations and this decision do not withdraw or supersede them.

New work resolves Bounded Context and Context Map through the explicit v2 current_lookup entries. Historical artifacts continue resolving their exact v1 Definition bindings.

## Excluded effects

- No v1 Definition, artifact type, context, map, decision, migration plan, candidate pack, or receipt byte is rewritten, withdrawn, superseded, or deleted.
- No Bounded Context/v2 or Context Map/v2 artifact type, schema, generator, validator, fixture, or generated reverse-membership index is authored or admitted.
- No Governance or Ontology Lifecycle context or language epoch is authored, revised, admitted, withdrawn, or cut over.
- No successor Context Map, lineage record, migration amendment, source relocation, migration execution, implementation, commit, push, publication, deployment, external effect, or stable release is authorized or performed.

## Successor obligations

- Author and separately admit normalized Bounded Context/v2 and Context Map/v2 artifact types before constructing new context or map instances.
- Provide a deterministic generated reverse-membership index whose canonical inputs are admitted Context Maps only.
- Author new Governance and Ontology Lifecycle context epochs without map backreferences, preserve CTX05 bytes, and record explicit lineage.
- Then author a successor Context Map with those exact endpoints and a source- and rollback-bound migration amendment before any cutover.

## Claim ceiling

This decision admits only the exact Bounded Context/v2 and Context Map/v2 Definition versions and their synchronized live registry/index/drift surfaces. It does not revise or admit artifact types, contexts, maps, migrations, implementations, publications, deployments, or stable-release state.
