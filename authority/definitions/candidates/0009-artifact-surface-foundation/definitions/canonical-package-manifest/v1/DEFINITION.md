<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Canonical Package Manifest

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.canonical-package-manifest`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:canonical-package-manifest`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

A Canonical Package Manifest M is the machine-canonical declaration of CPH(A)=H. M names aggregate A, lifecycle owner, unit of change, root H, each governed file role, explicit canonical carriers, and any nested package home with its independent lifecycle and typed parent relation. M describes cohesion but grants no semantic or operational authority.

```text
M=(A,H,owner,unit,carriers,components,projections,evidence,fixtures,transients,nested); nested(n,H) and independent(n) => exists manifest(n) and typed_relation(n,H).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| M | One Canonical Package Manifest. |
| H | The declared canonical package-home root. |

### Boundary conditions

- Files with different lifecycle owners or recovery boundaries require separate package homes.
- A directory without its own manifest remains a facet of the nearest declared package.
- Manifest membership cannot change Artifact identity or type.

### Testable conditions

- Every canonical carrier has exactly one package home and one admitted type resolution.
- Every governed non-carrier has exactly one declared surface role.
- Every independent nested lifecycle has its own manifest and explicit parent relation.

## Plain-language voice

The package manifest says what changes together, who owns that lifecycle, which files are canonical, and what every supporting folder is for. It makes nesting explicit without turning folders into meaning.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

product/products/ontology/v1 can declare product.json as a canonical carrier and contracts, runtime, tests, fixtures, and projections as distinct facets. source-package becomes a nested package only if it owns an independent lifecycle and recovery boundary.

### Examples

- implementation/bindings/ontology-product-lifecycle/v1 likely needs its own manifest because it has a distinct runtime-binding owner.
- Rust target directories are declared transient rather than scanned as canonical carriers.

## Applicability

Declaring one Canonical Package Home, its owner-local aggregate, lifecycle owner, unit of change, governed carriers, facets, and nested package relations.

### Exclusions

- Making directory placement authoritative.
- Collapsing colocated semantic identities.
- Treating every nested directory as a package home.

## Boundaries

- Canonical Package Manifest is not Canonical Package Home.
- Manifest membership is not context membership.
- Manifest validation is not product approval or migration authority.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.definition.definition@1.0.0-candidate.1 | whole-json | `eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575` | `admitted` |
| cal.definition.canonical-package-home@1.0.0-candidate.1 | whole-json | `c810597968723991449fe78458254679cc6dc87b2b81e54e16a9aa599c59f8ca` | `admitted` |
| cal.definition.artifact-type@1.0.0-candidate.1 | whole-json | `90c61c2fa5a5f1d5d0a96d8e6c1f4b1f902e8ad57d85ef1e315e549470abb69f` | `admitted` |

## Primary consumers

- cal.artifact-type.canonical-package-manifest/v1
- migration:registry-context

## Lookup and drift

- Index: `authority/definitions/candidates/0009-artifact-surface-foundation/DEFINITIONS-INDEX.md` / `cal.definition.canonical-package-manifest@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `authority/definitions/candidates/0009-artifact-surface-foundation/drift-audit-postimage.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

No typed relations declared.

## Evidence

- ASF-RESEARCH-05

## Residue

- No existing package home is migrated by this Definition candidate.

## Claim ceiling

This candidate defines package-manifest semantics only. It does not select a package home, move files, or confer lifecycle authority.
