<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Identity Relation

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.identity-relation`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:identity-relation-definition`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

An Identity Relation is a separately governed typed edge with relation identity, kind, source endpoint, target endpoint, owner, evidence, and lifecycle. It preserves endpoint identity and authority, and dependent classifications are expressed through such relations instead of inferred duplicate labels.

```text
R = (relation_id, kind, from_ref, to_ref, owner_ref, evidence_refs, lifecycle); R(a,b) does not imply a = b or authority(a) = authority(b).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| R(a,b) | One explicit typed relation from endpoint a to endpoint b. |

### Boundary conditions

- Both endpoints resolve independently.
- The relation kind has a declared interpretation and direction.
- Shared principal or directory placement cannot synthesize a relation.

### Testable conditions

- Relation ID, kind, endpoints, owner, evidence, and lifecycle are explicit.
- Removing the relation does not erase either endpoint.
- Validators reject endpoint collapse and inferred membership.

## Plain-language voice

An Identity Relation says exactly how two separate things are connected. The connection never turns them into the same thing and never gives one the other's authority.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

The Craft identity graph uses explicit relations such as coordinated_by, embodies_method, uses_method, and pursues_goal instead of repeating dependent labels on every artifact.

### Examples

- Craft coordinated_by Craft Project keeps Product and Project separate.
- Craft Project pursues_goal a Goal without absorbing the Goal's lifecycle.

## Applicability

An explicit, typed, owner-accountable statement connecting two independently identified endpoints for a declared purpose.

### Exclusions

- An inferred relation from names, paths, co-location, shared owners, or field resemblance.
- A mechanism that merges endpoints, transfers their authority, or silently creates a classification axis.

## Boundaries

- Identity Relation is not an endpoint identity.
- A relation is not authority transfer, identity equality, or context inference.
- Convenience labels derived from a relation are generated projections, not canonical axes.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.definition.definition@1.0.0-candidate.1 | whole-json | `eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575` | `admitted` |
| domainspec-core:CA2-DECISION-CRAFT-IDENTITY-003 | whole-file | `1f2d01026865e031adba063de0dc1dfa081c49a931223aa4bc9f726d3397bceb` | `candidate-unadmitted` |
| domainspec-core:CA2-PRODUCT-CRAFT | whole-file | `30ab8d1c7ac2b8f95a950a9cc7b83a2d6f3966e66635311a1e4083cec3be259e` | `candidate-unadmitted` |
| domainspec-core:CA2-PROJECT-CRAFT | whole-file | `a3c940af28ab9436549d35d5f93848c427695433704e8b6715d80b7b69f05485` | `candidate-unadmitted` |
| domainspec-core:CA2-GOAL-CRAFT-PRODUCT-FEATURE-FOUNDATION | whole-file | `075458bb50e508d00a1124cb43c5952a013657df2e6046b8674f25c44dd350a2` | `candidate-unadmitted` |

## Primary consumers

- authority/artifact-types/identity-graph/v1
- product/products/craft/v1/identity-graph.json

## Lookup and drift

- Index: `authority/definitions/candidates/0006-craft-identity/DEFINITIONS-INDEX.md` / `cal.definition.identity-relation`
- Drift owner: `role:definition-owner`
- Audit: `authority/definitions/candidates/0006-craft-identity/drift-audit-postimage.json`
- Challenge route: `route:definition-governance-challenge`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.governed-by | cal.definition.identity-relation@1.0.0-candidate.1 | role:definition-owner | role:definition-owner |
| relation.originates-from | cal.definition.identity-relation@1.0.0-candidate.1 | domainspec-core:CA2-DECISION-CRAFT-IDENTITY-003 | role:definition-owner |

## Evidence

- CAL-CML07-CRAFT-IDENTITY-CHAIN-0001
- CAL-SOURCE-ADMISSIONS-CRAFT-IDENTITY-V1
- CAL-OWNER-BINDINGS-CRAFT-IDENTITY-0004

## Residue

- identity-graph-artifact-type-required
- identity-graph-owner-activation-required

## Claim ceiling

This candidate defines explicit identity relations. It does not admit a relation vocabulary, instantiate graph edges, merge identities, transfer authority, or infer a Bounded Context.
