<!-- GENERATED FILE: edit decision.json and rerun render.py. -->

# Governance and Ontology Lifecycle context-language admission

> Machine-canonical decision; this Markdown is a generated projection.

- Decision: `CAL-DECISION-0023-GOVERNANCE-AND-ONTOLOGY-LIFECYCLE-CONTEXT-PROMOTION`
- Status: `owner-admitted`
- Selection: `approved`
- Principal: `person:<vrondelli>`
- Recorded: `2026-09-02T22:06:25Z`

## Admitted artifacts

| Artifact | Type | Version | Owner role | Effect |
| --- | --- | --- | --- | --- |
| `cal.context.governance` | `cal.artifact-type.bounded-context/v1` | `1.0.0-candidate.1` | `governance-context-owner` | `admitted` |
| `cal.language.governance` | `cal.artifact-type.ubiquitous-language/v1` | `1.0.0-candidate.1` | `governance-language-owner` | `admitted` |
| `cal.context.ontology-lifecycle` | `cal.artifact-type.bounded-context/v1` | `1.0.0-candidate.1` | `ontology-lifecycle-context-owner` | `admitted` |
| `cal.language.ontology-lifecycle` | `cal.artifact-type.ubiquitous-language/v1` | `1.0.0-candidate.1` | `ontology-lifecycle-language-owner` | `admitted` |

## Admission result

- Bounded Contexts admitted: `2`
- Ubiquitous Languages admitted: `2`
- Context Maps admitted: `0`
- Migration Manifests admitted: `0`

## Materialization

The four immutable machine-canonical candidate files remain unchanged. This decision overlays admitted status on their exact identities, versions, and SHA-256 digests.

Each admitted Bounded Context references exactly its own admitted Ubiquitous Language and each language references exactly its own context.

The two context-language pairs remain separate. Shared words and source relationships do not infer translation or integration.

## Excluded effects

- No Governance-to-Ontology-Lifecycle Context Map, relationship pattern, translation, or integration contract is selected or admitted.
- No source governance ontology or Ontology Lifecycle business ontology receives admission through proximity to these context artifacts.
- No capability instance, migration manifest, lineage record, DomainSpec source, system ontology, implementation binding, or conformance claim is admitted.
- No runtime enforcement, migration execution, destructive action, commit, push, publication, deployment, external effect, or stable release is authorized or performed.

## Successor obligations

- Re-enter routing before authoring a Context Map candidate.
- Select the exact directional relationship pattern and translation boundaries between the admitted context versions before recording any cross-context dependency.
- Keep Context Map admission separate from capability-instance binding, migration planning, migration execution, and implementation authority.

## Claim ceiling

This decision admits only the two exact Bounded Context candidates and their two exact Ubiquitous Language candidates. It does not select or admit a Context Map, admit either source ontology, authorize migration or implementation, publish, deploy, or establish a stable release.
