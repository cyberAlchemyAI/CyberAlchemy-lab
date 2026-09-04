<!-- GENERATED FILE: edit decision.json and rerun render.py. -->

# CTX05 successor context, lineage, and migration-plan admission

> Machine-canonical decision; this Markdown is a generated projection.

- Decision: `CAL-DECISION-0025-GOVERNANCE-ONTOLOGY-LIFECYCLE-SUCCESSOR-PROMOTION`
- Status: `owner-admitted`
- Selection: `ADMIT-CTX05-SUCCESSORS-AND-MIGRATION-V1`
- Principal: `person:<vrondelli>`
- Recorded: `2026-09-03T03:20:43Z`

## Admitted artifacts

| Artifact | Type | Owner | Overlay | Digest |
| --- | --- | --- | --- | --- |
| `cal.context.governance/v2` | `cal.artifact-type.bounded-context/v1` | `governance-context-owner` | `admitted` | `5c59ae8dc12807ad8996749a82e1f9b0c1f624b3ef87aaebf4442e957d90d88f` |
| `cal.language.governance/v2` | `cal.artifact-type.ubiquitous-language/v1` | `governance-language-owner` | `admitted` | `ba84484be3f0d793e935ba4bbf960885ce1adcd2d2763aee940396ff290918d7` |
| `cal.context.ontology-lifecycle/v2` | `cal.artifact-type.bounded-context/v1` | `ontology-lifecycle-context-owner` | `admitted` | `4a8ef8f3441a055aeed10e368db4bcec7bf6c098e15e2356cfd25d659df3a4b8` |
| `cal.language.ontology-lifecycle/v2` | `cal.artifact-type.ubiquitous-language/v1` | `ontology-lifecycle-language-owner` | `admitted` | `8d01b878d93fa1b502d57348b8c5cad3c25968504de0ef7df37b17e63dda2e55` |
| `cal.context-lineage.governance.v1-to-v2` | `cal.artifact-type.context-lineage-record/v1` | `context-lineage-owner` | `admitted` | `6e09af319953649599c081ea029c3827b639e7282a224eeeeeb795032dc56c98` |
| `cal.context-lineage.ontology-lifecycle.v1-to-v2` | `cal.artifact-type.context-lineage-record/v1` | `context-lineage-owner` | `admitted` | `95298b5e68d963d9a2e4f2cb55d5b825defe96783310dcbea6832bf8a12d48bc` |
| `cal.context-migration.governance-ontology-lifecycle-v1-to-v2` | `cal.artifact-type.context-migration-manifest/v1` | `context-migration-owner` | `admitted-plan-only` | `0ff95bc63c12ed5e3640086d7609223bbbda1e0b46af28e9e9c0bbf602c7a973` |

## Admission result

- Bounded Context successors: `2`
- Ubiquitous Language successors: `2`
- Lineage records: `2`
- Migration plans: `1`
- Migration execution authorizations: `0`
- Predecessors superseded: `0`

## Boundaries

All seven immutable machine-canonical candidates and their generated projections remain unchanged. This decision overlays admitted status on their exact identities and SHA-256 digests.
The v2 context-language pairs are admitted as additive successors. Their v1 predecessors remain admitted, byte-preserved, and not superseded or withdrawn by this decision.
The two lineage records are admitted as identity-history evidence only; equivalence_inferred and admission_inferred remain false, and the records do not themselves supersede either predecessor.
The v1 Context Map remains unchanged and continues to name v1 endpoints. A successor map epoch is required before v2 endpoints can be represented as exact map endpoints.
The migration manifest is admitted as an immutable plan only. execution_authority remains false, no cutover occurs, and physical source-package relocation remains excluded.

## Excluded effects

- No v1 context, language, Context Map, or candidate-pack bytes are rewritten, withdrawn, superseded, or deleted.
- No semantic equivalence, automatic admission, or migration completion is inferred from either lineage record.
- No successor Context Map epoch, reverse relationship, or reusable global relationship-kind artifact is selected or admitted.
- No source-domain package under cyberAlchemy-v2/ontology/governance or ontology-lifecycle is selected, admitted, copied, moved, renamed, rewritten, or deleted.
- No payload schema, Anti-Corruption Layer adapter, capability instance, DomainSpec source, system ontology, runtime, implementation binding, or implementation conformance is admitted.
- No migration execution, cutover, destructive action, commit, push, publication, deployment, external effect, or stable release is authorized or performed.

## Successor obligations

- Author and separately admit a successor Context Map epoch whose exact endpoints are the admitted v2 contexts before any consumer cutover.
- Keep the current migration manifest execution_authority false; any cutover requires a separate immutable execution decision after all owner gates are current.
- Author a separate source-admission and migration manifest before relocating either physical domain package.
- Preserve all five declared preimages and exercise the recorded rollback boundary in a non-effectful rehearsal before execution authorization.

## Claim ceiling

This decision admits only the exact four CTX05 successor context-language artifacts, two non-inferential lineage records, and one immutable migration plan. It does not infer equivalence or supersession, revise Context Map endpoints, authorize migration execution or physical source relocation, admit implementation, commit, publish, deploy, or establish a stable release.
