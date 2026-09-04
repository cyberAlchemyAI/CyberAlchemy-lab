<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Context Map

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.context-map`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:cyberalchemy-lab-context-metamodel`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

A Context Map is a versioned, owner-approved set of typed directional relationships between exact Bounded Context versions. Each relationship declares upstream and downstream roles, integration or translation contracts, information and authority limits, owners, evidence, drift handling, and change coordination.

```text
ContextMap = (id, version, context_refs, relationships, owner_refs, lifecycle, evidence_refs, drift_route); Relationship = (source_context_version, target_context_version, direction, relationship_kind, contract_refs, translation_refs, information_boundary, authority_boundary, owners); Proximity does not imply Relationship.
```

### Notation

| Symbol | Meaning |
| --- | --- |
| Relationship | One owned directional mapping between two exact context versions. |

### Boundary conditions

- Both endpoint identities and versions are explicit.
- Direction and authority limits cannot be inferred from imports.
- One mapping pattern is selected by its owners, not by this generic definition.

### Testable conditions

- Every relationship has two exact endpoints, direction, kind, owners, and boundaries.
- No context dependency is derived from filesystem proximity.

## Plain-language voice

The explicit map showing how bounded contexts depend on or translate for one another and who owns each side.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

The first candidate map will place Ontology Lifecycle downstream of Governance while leaving the exact DDD integration pattern for a separate owner decision.

### Examples

- Governance may publish authority outcomes that Ontology Lifecycle records through an explicit translation contract.

## Applicability

Directional semantic and integration relationships between exact Bounded Context versions.

### Exclusions

- Directory trees, import graphs, runtime topology, and authority transfer.

## Boundaries

- A Context Map is not a directory tree, dependency scan, import graph, ontology relation set, runtime topology, authority transfer, or evidence that two contexts agree.
- A map records dependent classifications through relations; it does not add redundant canonical axes.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| CAL-SOURCE-ADMISSION-CTX00-CAV2-D29 | CAV2-D29 | `f47b8ae8dcbfcc97d624871a5aab03cbf3ffdea2b341046a0bba1edbb59740be` | `admitted` |

## Primary consumers

- contexts/*/maps
- contexts/*/context.json

## Lookup and drift

- Index: `candidate:authority/definitions/registry.json` / `cal.definition.context-map`
- Drift owner: `role:definition-owner`
- Audit: `drift-audit-postimage.json`
- Challenge route: `route:definition-governance-challenge`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.governed-by | cal.definition.context-map@1.0.0-candidate.1 | role:definition-owner | role:definition-owner |

## Evidence

- CAL-DECISION-0016-ONTOLOGY-LIFECYCLE-CONTEXT-PLACEMENT
- CAL-DECISION-0017-CTX00-SOURCE-ADMISSION

## Residue

- context-map-artifact-type-required
- governance-to-ontology-lifecycle-pattern-decision-required

## Claim ceiling

This candidate defines Context Map meaning only; it does not select the Governance to Ontology Lifecycle relationship pattern or create a map.
