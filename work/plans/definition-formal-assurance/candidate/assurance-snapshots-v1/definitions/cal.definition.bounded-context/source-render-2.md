<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Bounded Context

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.bounded-context`
- Version: `2.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:cyberalchemy-lab-context-metamodel`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

A Bounded Context is a versioned, owner-scoped semantic boundary inside which one declared domain model and one Ubiquitous Language are intended to remain internally consistent for an explicit scope and set of exclusions. It owns its identity, model, language, scope, contracts, semantic owner, lifecycle, evidence, and challenge route. A Bounded Context does not canonically own map membership or backreferences to Context Maps. Cross-context endpoint membership and directional relationships are owned only by separately governed Context Maps; reverse membership for a context is a generated projection derived from those maps.

```text
BoundedContext = (id, version, domain_model_ref, ubiquitous_language_ref, scope, exclusions, semantic_owner_ref, contract_refs, lifecycle, evidence_refs, challenge_route); Unique(id,version); ContextMapMembership(c) = {m | c in m.context_refs}; CanonicalOwner(ContextMapMembership) = ContextMap; ReverseMembershipIndex(c) = Generate(ContextMapRegistry,c).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| ContextMapMembership(c) | The set of Context Maps whose canonical endpoint set contains exact Bounded Context version c. |
| ReverseMembershipIndex(c) | A rebuildable lookup projection derived from canonical Context Maps, never a field owned by c. |

### Boundary conditions

- A folder name cannot establish context identity.
- Shared spelling across contexts does not imply shared meaning.
- A Bounded Context cannot carry a canonical Context Map backreference.
- Absence from a generated reverse-membership index does not amend any Context Map.

### Testable conditions

- Identity, version, owner, scope, exclusions, model, language, contracts, lifecycle, evidence, and challenge route are explicit.
- No canonical context_map_refs or equivalent map-membership field exists on the Bounded Context record.
- Every cross-context dependency resolves through a typed relationship in a Context Map whose context_refs contain both exact endpoint versions.
- Any reverse map-membership lookup is reproducible from canonical Context Map records.

## Plain-language voice

A named boundary within which words and domain rules have one deliberately consistent meaning. It describes itself; the separate Context Maps describe how it relates to other boundaries.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

Governance and Ontology Lifecycle remain distinct bounded contexts, but neither context should repeat a canonical reference to their shared Context Map. The map owns their exact membership and direction; a generated index can show the reverse lookup for people and tools.

### Examples

- contexts/governance and contexts/ontology-lifecycle each own context.json, while contexts/maps/governance-ontology-lifecycle owns their relationship.
- A generated context-map membership index may list cal.context.governance/v2 without changing the Governance context record.

## Applicability

Explicit owner-scoped semantic boundaries and their versioned models.

### Exclusions

- Repository folders or packages without context identity.
- Coordination frames, products, teams, deployment units, and databases.
- Canonical ownership of cross-context endpoint membership and directional relationships.

## Boundaries

- A Bounded Context is not a folder, module, package, Product, capability, Coordination Context, Project, Goal, team, deployment unit, database, or authority grant.
- Containment and imports do not imply a Context Map relationship.
- Map membership is not an independent canonical axis on a Bounded Context; it is a relation owned by a Context Map and may be exposed only as a generated projection.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| CAL-SOURCE-ADMISSION-CTX00-CAV2-D29 | CAV2-D29 | `f47b8ae8dcbfcc97d624871a5aab03cbf3ffdea2b341046a0bba1edbb59740be` | `admitted` |
| CAL-SOURCE-ADMISSION-CTX00-CAV2-D66 | CAV2-D66 | `93ed5c852579f7e84af9c3163f737f4f37c822d1a49063a3fa8b5af1d2ae7769` | `admitted` |
| CAL-SOURCE-ADMISSION-CTX00-LANGUAGE-CONCEPTS | whole-json | `e8cc7d26fffb69bc9b94eb8ecd70259c04b45f3683f52941084b7a07f37d436d` | `admitted` |
| CAL-SOURCE-ADMISSION-CTX00-GOVERNANCE-LANGUAGE | whole-json | `253530491c2555c75ce9fa6e5a90cb40ecbd6ca5b3e55e557c28360e6df02c13` | `admitted` |

## Primary consumers

- contexts
- product/capabilities
- authority/artifact-types/bounded-context

## Lookup and drift

- Index: `candidate:authority/definitions/registry.json` / `cal.definition.bounded-context`
- Drift owner: `role:definition-owner`
- Audit: `drift-audit-postimage.json`
- Challenge route: `route:definition-governance-challenge`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.governed-by | cal.definition.bounded-context@2.0.0-candidate.1 | role:definition-owner | role:definition-owner |
| relation.successor-of | cal.definition.bounded-context@2.0.0-candidate.1 | cal.definition.bounded-context@1.0.0-candidate.1 | role:definition-owner |

## Evidence

- cal.definition.definition@1.0.0-candidate.1
- cal.definition.bounded-context@1.0.0-candidate.1
- CAL-DECISION-0018-DEFINITION-AND-CTX00-PROMOTION
- CAL-DECISION-0024-GOVERNANCE-ONTOLOGY-LIFECYCLE-CONTEXT-MAP-PROMOTION
- CAL-DECISION-0025-GOVERNANCE-ONTOLOGY-LIFECYCLE-SUCCESSOR-PROMOTION

## Residue

- ctx06-definition-owner-admission-required
- ctx06-bounded-context-artifact-type-v2-required
- ctx06-generated-reverse-membership-index-required

## Claim ceiling

This candidate revises Bounded Context meaning to remove canonical Context Map backreferences. It does not supersede v1, admit this version, revise an artifact type or context instance, generate a live reverse index, authorize migration, or establish a stable release.
