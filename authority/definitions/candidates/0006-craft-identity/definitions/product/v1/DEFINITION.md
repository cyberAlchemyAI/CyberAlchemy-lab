<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Product

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.product`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:product-definition`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

A Product is a durable identity-bearing boundary for a coherent purpose and promise of value. It may be coordinated by Projects, embody Methods, contain Product Features and Capabilities, and have many realizations, but none of those relations merges their identities or transfers their authority.

```text
Product(p) = (identity, purpose, value_promise, lineage, owner_route); related(p,x) does not imply p = x.
```

### Notation

| Symbol | Meaning |
| --- | --- |
| p | One Product identity. |
| x | A separately identified Project, Method, Feature, Capability, context, or realization. |

### Boundary conditions

- A shared name, owner, path, or relation does not collapse Product with another identity.
- Product placement does not create a Bounded Context.

### Testable conditions

- The Product has a stable ID and owner route.
- Every related identity has its own ID and typed relation.
- No Product identity is inferred from a directory name.

## Plain-language voice

A Product is the enduring thing that promises value. Projects organize work around it, and methods help build it, but neither is the Product itself.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

Craft is the current name of the same Product lineage formerly called DomainSpec v2. This Definition gives Product a new Lab semantic ID because the source corpus has no exact Product Definition ID to preserve.

### Examples

- CA2-PRODUCT-CRAFT is coordinated by CA2-PROJECT-CRAFT.
- Craft embodies CAV2-D20 without becoming the Craft Method.

## Applicability

A durable identity that owns a coherent promise of value, purpose, and product meaning across the projects and realizations used to develop it.

### Exclusions

- A Project that coordinates work.
- A Method used to build systems.
- A Product Feature, Product Capability, repository, package, directory, Bounded Context, or implementation.

## Boundaries

- Product is not Project.
- Product is not Method or Goal.
- Product is not Product Feature, Product Capability, Bounded Context, repository, directory, or implementation.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.definition.definition@1.0.0-candidate.1 | whole-json | `eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575` | `admitted` |
| domainspec-core:CA2-PRODUCT-CRAFT | whole-file | `30ab8d1c7ac2b8f95a950a9cc7b83a2d6f3966e66635311a1e4083cec3be259e` | `candidate-unadmitted` |
| domainspec-core:CA2-DECISION-CRAFT-IDENTITY-003 | whole-file | `1f2d01026865e031adba063de0dc1dfa081c49a931223aa4bc9f726d3397bceb` | `candidate-unadmitted` |

## Primary consumers

- authority/artifact-types/product-identity/v1
- product/products/craft/v1/product.json

## Lookup and drift

- Index: `authority/definitions/candidates/0006-craft-identity/DEFINITIONS-INDEX.md` / `cal.definition.product`
- Drift owner: `role:definition-owner`
- Audit: `authority/definitions/candidates/0006-craft-identity/drift-audit-postimage.json`
- Challenge route: `route:definition-governance-challenge`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.governed-by | cal.definition.product@1.0.0-candidate.1 | role:definition-owner | role:definition-owner |
| relation.originates-from | cal.definition.product@1.0.0-candidate.1 | domainspec-core:CA2-PRODUCT-CRAFT | role:definition-owner |

## Evidence

- CAL-CML07-CRAFT-IDENTITY-CHAIN-0001
- CAL-SOURCE-ADMISSIONS-CRAFT-IDENTITY-V1
- CAL-OWNER-BINDINGS-CRAFT-IDENTITY-0004

## Residue

- product-identity-artifact-type-required
- source-admission-required

## Claim ceiling

This candidate defines Product meaning only. It does not admit or instantiate Craft, select a Bounded Context, or authorize migration or implementation.
