<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Canonical Package Home

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.canonical-package-home`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:canonical-package-home-definition`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

A Canonical Package Home is the unique governed artifact tree H selected for an owner-local aggregate A by an explicit lifecycle-owner binding and unit-of-change declaration. H carries A's canonical machine sources. Capability, bounded-context, product, DomainSpec, implementation, evidence, and projection facets may be colocated in H when they share A's lifecycle, but their identities and authorities remain distinct and are connected by explicit typed relations. Indexes and global views may reference or generate projections of H; they must not duplicate its canonical carriers.

```text
CPH(A)=H iff declared_owner(A)=lifecycle_owner(H) and unit_of_change(A)=unit_of_change(H); exists exactly one H for each canonical carrier c in A such that canonical_at(c,H); colocated(x,y,H) =/=> identity(x)=identity(y); classified_as(x,k) =/=> CPH(x)=root(k); indexes(i,c) =/=> canonical_at(c,i).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| A | One owner-local aggregate whose canonical sources change and recover as a declared unit. |
| H | The single governed artifact tree selected as A's canonical package home. |
| CPH(A) | The explicit mapping from aggregate A to canonical package home H. |

### Boundary conditions

- The lifecycle owner and unit of change select the home; the directory does not select the owner, identity, or context.
- Semantic orthogonality requires distinct identities and typed relations, not separate physical roots.
- A bounded context may be a facet of an aggregate without being the aggregate's directory or owning every colocated artifact.
- Artifacts with different lifecycle owners or independent recovery boundaries require separate canonical homes even when one global index presents them together.

### Testable conditions

- Every canonical machine carrier in scope resolves to exactly one canonical package home.
- The package manifest names the owner-local aggregate, lifecycle owner, and unit of change explicitly.
- Colocated capability, context, product, DomainSpec, implementation, evidence, and projection facets keep distinct identifiers and explicit typed relations.
- Global registries, catalogs, and indexes contain references or generated projections rather than duplicate canonical machine carriers.
- Moving a package without an explicit semantic or authority decision cannot change any artifact identity, context membership, or authority.

## Plain-language voice

Keep one thing that changes together in one canonical workshop. The workshop can contain separately labelled capability, context, product, runtime, and evidence benches; putting them together does not make them the same thing. Catalogs elsewhere point to the workshop instead of keeping rival master copies.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

Registry Context is a capability-owned aggregate, so its proposed canonical package home is capabilities/registry-context/v1/. Its bounded-context definition, capability instance, product and DomainSpec projections, runtime bindings, schemas, evidence, and tests may live below that root when they share the same lifecycle. Global context, product, ontology, and capability indexes reference those carriers; they do not own duplicate copies.

### Examples

- capabilities/registry-context/v1/context/ carries the bounded-context identity while capabilities/registry-context/v1/capability/ carries the capability-instance identity.
- capabilities/registry-context/v1/runtime/ and evidence/ remain distinct facets even though they are physically cohesive with the same owner-local aggregate.
- A global contexts index points to the Registry Context carrier rather than becoming its second canonical home.

## Applicability

Selecting the single governed artifact tree that carries the canonical machine sources of one explicitly declared owner-local aggregate and keeps its related semantic facets cohesive without collapsing their identities.

### Exclusions

- Inferring semantic identity, context membership, or authority from a directory path.
- Requiring every semantic axis or bounded context to have a separate top-level directory.
- Colocating artifacts that have different lifecycle owners or independent units of change.

## Boundaries

- Canonical Package Home is not Bounded Context.
- Canonical Package Home is not Product Capability or Capability Instance.
- Canonical Package Home is not ownership by directory placement.
- Canonical Package Home is not a universal monorepo layout or deployment unit.
- Colocation is not semantic collapse, shared authority, or implicit context membership.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.definition.definition@1.0.0-candidate.1 | whole-json | `eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575` | `admitted` |
| cal.definition.bounded-context@2.0.0-candidate.1 | whole-json | `6ee155d2e7427e33357e55e56bc5228c2b584ea435bb9dc516ddb66385f590c0` | `admitted` |
| cal.definition.capability-instance@1.0.0-candidate.1 | whole-json | `d1e0140d47887b3f8c49334e81c33bd105edaecaf02f3df3df841885340505a5` | `admitted` |
| domainspec-core:CAV2-D22 | lines:1305-1395 | `48bdcc5934896dff19434e12947c040f9c0a591962b11682de6437e18e2742ef` | `candidate-unadmitted` |
| domainspec-core:CAV2-D42 | lines:2790-2872 | `1d12194518e5b55ba9d8da8ebdb5a77700f84c462589c4757e8fec4c9ee366c9` | `candidate-unadmitted` |
| domainspec-core:CAV2-D64 | lines:4842-5091 | `891c6b66c578bc0b8f763ad15e250fea255aed36274b9799436f6ab9544dd080` | `candidate-unadmitted` |
| domainspec-core:CAV2-D66 | lines:5358-5483 | `93ed5c852579f7e84af9c3163f737f4f37c822d1a49063a3fa8b5af1d2ae7769` | `candidate-unadmitted` |
| domainspec-core:CAV2-D67 | lines:5484-5611 | `bf8f3cb9b7d22aaa3c54b7c1eb177b85100be9bc421142bb3ead7e2456431d13` | `candidate-unadmitted` |

## Primary consumers

- migration:registry-context
- cal.artifact-type.capability-instance/successor

## Lookup and drift

- Index: `authority/definitions/candidates/0008-canonical-package-home/DEFINITIONS-INDEX.md` / `cal.definition.canonical-package-home@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `authority/definitions/candidates/0008-canonical-package-home/drift-audit-postimage.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

No typed relations declared.

## Evidence

- CPH-01
- CPH-02
- CPH-03
- CPH-04

## Residue

- External CAV2 source selections require Lab source admission before this Definition can be admitted.
- Capability Instance Artifact Type enforcement remains successor work.

## Claim ceiling

This candidate defines package-home selection and cohesion semantics only. It does not select a home for Registry Context, admit the Definition, move files, confer authority, or establish conformance.
