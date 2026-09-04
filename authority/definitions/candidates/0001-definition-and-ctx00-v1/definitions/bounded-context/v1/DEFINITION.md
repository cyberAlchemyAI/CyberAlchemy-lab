<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Bounded Context

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.bounded-context`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:cyberalchemy-lab-context-metamodel`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

A Bounded Context is a versioned, owner-scoped semantic boundary inside which one declared domain model and one Ubiquitous Language are intended to remain internally consistent for an explicit scope and set of exclusions. Relationships to other Bounded Contexts exist only through separately owned directional Context Maps and contracts.

```text
BoundedContext = (id, version, domain_model_ref, ubiquitous_language_ref, scope, exclusions, semantic_owner_ref, contract_refs, context_map_refs, lifecycle, evidence_refs, challenge_route); Unique(id,version); CrossContextDependency => Exists(ExactDirectionalContextMap).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| Unique(id,version) | One stable context identity at one exact version. |

### Boundary conditions

- A folder name cannot establish context identity.
- Shared spelling across contexts does not imply shared meaning.
- Cross-context dependencies require explicit directional maps.

### Testable conditions

- Identity, version, owner, scope, exclusions, model, and language are explicit.
- Every cross-context dependency resolves to a typed Context Map relation.

## Plain-language voice

A named boundary within which words and domain rules have one deliberately consistent meaning.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

Governance and Ontology Lifecycle are distinct bounded-context candidates because authority decisions and ontology event history have related but non-identical models and ownership.

### Examples

- contexts/governance and contexts/ontology-lifecycle would each need their own context.json; their directory names alone establish nothing.

## Applicability

Explicit owner-scoped semantic boundaries and their versioned models.

### Exclusions

- Repository folders or packages without context identity.
- Coordination frames, products, teams, deployment units, and databases.

## Boundaries

- A Bounded Context is not a folder, module, package, Product, capability, Coordination Context, Project, Goal, team, deployment unit, database, or authority grant.
- Containment and imports do not imply a Context Map relationship.

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
- authority/artifact-types/context-map

## Lookup and drift

- Index: `candidate:authority/definitions/registry.json` / `cal.definition.bounded-context`
- Drift owner: `role:definition-owner`
- Audit: `drift-audit-postimage.json`
- Challenge route: `route:definition-governance-challenge`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.governed-by | cal.definition.bounded-context@1.0.0-candidate.1 | role:definition-owner | role:definition-owner |

## Evidence

- CAL-DECISION-0016-ONTOLOGY-LIFECYCLE-CONTEXT-PLACEMENT
- CAL-DECISION-0017-CTX00-SOURCE-ADMISSION

## Residue

- bounded-context-artifact-type-required
- bounded-context-owner-bindings-required

## Claim ceiling

This candidate defines Bounded Context meaning only; it does not admit Governance or Ontology Lifecycle as contexts or select their integration pattern.
