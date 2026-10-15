<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Canonical Package Manifest

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.canonical-package-manifest`
- Version: `1.0.0-candidate.2`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:canonical-package-manifest`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

A Canonical Package Manifest M declares one canonical package home, aggregate, lifecycle owner, unit of change, every governed member's unique surface role, and every independent nested package relation. M must classify its own package.json exactly once as a canonical instance of Canonical Package Manifest/v1. Membership and nesting are explicit data, not directory inference.

```text
M=(home,aggregate,owner,unit,members,nested); members[package.json]=(I,CanonicalPackageManifest/v1,1); for all f in governed(home), exists exactly one members[f]; independent(n) => exists manifest(n) and relation(M,n).
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

- package.json occurs exactly once and is a canonical instance of Canonical Package Manifest/v1.
- Every canonical carrier has exactly one admitted type resolution.
- Every governed non-carrier has exactly one declared surface role.
- Every independent nested lifecycle has its own manifest and explicit parent relation.

## Plain-language voice

The manifest says what changes together and what every file does, including itself. Nested lifecycles are declared, never guessed from folders.

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
| cal.definition.canonical-package-manifest@1.0.0-candidate.1 | whole-json | `0b0ffa8eb2851bae34e2bf75070baab968a6f97816453b67b8bd7aa501b8359d` | `candidate-unadmitted` |

## Primary consumers

- cal.artifact-type.canonical-package-manifest/v1
- migration:registry-context

## Lookup and drift

- Index: `authority/definitions/candidates/0010-artifact-surface-foundation-revision/DEFINITIONS-INDEX.md` / `cal.definition.canonical-package-manifest@1.0.0-candidate.2`
- Drift owner: `role:definition-owner`
- Audit: `authority/definitions/candidates/0010-artifact-surface-foundation-revision/drift-audit-postimage.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.successor-of | cal.definition.canonical-package-manifest@1.0.0-candidate.2 | cal.definition.canonical-package-manifest@1.0.0-candidate.1 | role:definition-owner |

## Evidence

- ASF-REVISION-REVIEW-01

## Residue

- No existing package home is migrated by this Definition successor.

## Claim ceiling

This candidate defines package-manifest semantics only. It does not select a package home, move files, or confer lifecycle authority.
