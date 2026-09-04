<!-- GENERATED FILE: edit decision.json and rerun render-decision.py. -->

# Context-operational owner admission decision

> Machine-canonical decision; this Markdown is a generated projection.

- Status: `owner-admitted`
- Selection: `ADMIT-CTX02-OPERATIONAL-OWNERS-V1`
- Principal: `person:<vrondelli>`
- Recorded: `2026-09-02T20:15:47Z`

## Admitted operational roles

| Role | Principal | Effect |
| --- | --- | --- |
| `lab-architecture-owner` | `person:<vrondelli>` | Own cross-context architecture, independent identity axes, recursion boundaries, and repository placement policy. |
| `governance-context-owner` | `person:<vrondelli>` | Own the Governance Bounded Context identity, semantic boundary, model scope, contracts, and challenge route. |
| `ontology-lifecycle-context-owner` | `person:<vrondelli>` | Own the Ontology Lifecycle Bounded Context identity, semantic boundary, event-history and replay model, contracts, and challenge route. |
| `governance-language-owner` | `person:<vrondelli>` | Own Governance context-local terminology, expressions, relations, interpretations, and ambiguity handling. |
| `ontology-lifecycle-language-owner` | `person:<vrondelli>` | Own Ontology Lifecycle context-local terminology, expressions, relations, interpretations, and ambiguity handling. |
| `coordination-context-owner` | `person:<vrondelli>` | Own recursive coordination-context identity, purpose, subject scope, consumers, and bounded-context membership. |
| `context-map-owner` | `person:<vrondelli>` | Own Context Map membership and explicit directional relationship contracts between exact context versions. |
| `capability-instance-owner` | `person:<vrondelli>` | Own exact capability-instance identity, extension scope, recursion stop, and instance-local authority claim. |
| `context-migration-owner` | `person:<vrondelli>` | Own context migration intent, dispositions, dependency order, expected postimages, rollback boundary, and required gates. |
| `context-lineage-owner` | `person:<vrondelli>` | Own historical predecessor-successor context identity evidence, preserved and changed scope, and challenge route. |

## Admission result

- Foundation roles preserved: `5`
- Operational roles admitted: `10`
- Current role count: `15`
- Context instances created: `0`

## Excluded effects

- No Bounded Context, Coordination Context, Ubiquitous Language, Context Map, Capability Instance, Context Migration Manifest, or Context Lineage Record instance is authored or admitted.
- No Governance to Ontology Lifecycle relationship pattern is selected.
- No source selector, Product Capability, DomainSpec source, system ontology, implementation binding, or conformance claim is admitted by this owner decision.
- No migration execution, destructive action, publication, deployment, external effect, or stable release is authorized or performed.

## Successor obligations

- Re-enter routing before authoring context or language candidates.
- Author Governance and Ontology Lifecycle Bounded Context candidates with their separate context-owner roles.
- Author one Ubiquitous Language candidate for each context under its context-local language owner.
- Keep context and language admission, Context Map pattern selection, capability-instance binding, and migration execution as separate later gates.

## Claim ceiling

This decision activates only ten exact operational role bindings through the immutable owner-registry successor while preserving five Foundation roles. It does not create or admit context-metamodel instances, select their relationships, authorize migration or implementation, publish, deploy, or establish a stable release.
