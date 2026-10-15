<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Typed Connection Extension Rule

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.typed-connection-extension-rule`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:typed-connection-extension-rule-definition`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

The Typed Connection Extension Rule requires every global Relation Kind to expose a finite closed set of exact ordered source-kind to target-kind connections. A proposed extension must bind one effective predecessor Relation Kind version, one source endpoint contract, one target endpoint contract, direction, global scope, an exact qualifier schema with pair-specific values and constraints, canonical relation authority, contestability, owner, evidence, lifecycle effect, validation effect, and the exact successor contract version. It may reuse the Relation Kind only when the same unique semantic question remains intact; otherwise it must propose a distinct Relation Kind. Ontology-local connections must remain scoped to their exact Ontology contract. No global connection is created by endpoint registration, separate source and target lists, wildcard matching, historical observation, local graph use, shared naming, candidate validation, endpoint admission, or a second writable projection.

```text
For each global Relation Kind r, Conn(r) is a finite closed set of ordered pairs (s,t) in K x K. ValidExtend(r@v,s,t,r@v_prime) requires Effective(r@v), Resolved(s), Resolved(t), SameQuestion(r@v,r@v_prime), PairQualifierSchema(r@v_prime,s,t), CanonicalAuthority(r@v_prime,s,t) in {TypedRelation, SpecializedCarrier}, Contestable(r@v_prime,s,t), and exact owner, evidence, lifecycle, validation, and successor bindings. A relation instance e conforms only when (kind(source(e)),kind(target(e))) is in Conn(r@v_prime), direction and qualifiers validate, and the exact contract is admitted and effective. Local(o,s,t) does not imply (s,t) in Conn(r). Register(k) does not imply any (k,x) or (x,k) in Conn(r).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| K | The governed set of endpoint kinds. |
| r | One Relation Kind contract. |
| Conn(r) | The finite closed set of exact ordered endpoint-kind pairs declared by r. |
| Extend(r,s,t) | One proposed addition of the ordered pair source kind s to target kind t under r. |

### Boundary conditions

- Conn(r) contains ordered endpoint-kind pairs, so (s,t) and (t,s) are distinct unless both are explicitly declared.
- SourceKinds(r) and TargetKinds(r) are generated projections of Conn(r); they do not authorize SourceKinds(r) x TargetKinds(r).
- The effective predecessor version must be resolved through exact decision and succession overlays before a successor pair set is computed.
- Both endpoint kinds must resolve to admitted carriers or explicitly permitted governed internal record contracts.
- Each pair binds a qualifier schema, allowed values, and cross-qualifier constraints; open qualifier strings do not close the connection contract.
- One canonical relation authority is selected. A specialized carrier projection and generic Typed Relation cannot both accept independent writes.
- Global and ontology-local scope are distinct. Local(o,s,t) supplies no global pair.
- Every effective contract supplies contestability, owner, evidence, lifecycle, and authority-effect boundaries.
- Only an exact admitted successor Relation Kind contract makes a proposed global pair available.

### Testable conditions

- Every allowed global connection resolves to one exact ordered pair in Conn(r).
- No admitted Relation Kind contract contains wildcard or catch-all endpoint kinds.
- No validator infers allowed pairs from the Cartesian product of source-kind and target-kind projections.
- Every extension resolves the effective predecessor and names the exact successor contract version.
- Every global endpoint kind resolves to an admitted carrier or an explicitly permitted governed internal record contract.
- Every exact pair binds a closed qualifier schema, pair-specific value domain, and cross-qualifier constraints.
- Every proposal declares global or ontology-local scope; ontology-local edges fail global validation.
- Every global connection selects Typed Relation or specialized carrier as canonical authority, never both.
- Every extension binds contestability, owner, evidence, lifecycle effect, validation effect, and authority-effect rules.
- Registering an endpoint kind without an explicit pair leaves it unconnected.
- A proposed pair that changes the Relation Kind unique question is rejected or routed to a distinct Relation Kind proposal.
- A candidate or validated extension remains ineffective until exact admission.

## Plain-language voice

A new kind of wire must name its two plug types, purpose, labels, owner, challenge route, and one authoritative record. Both plug contracts must exist. A wire drawn only inside one Ontology stays local. Adding a plug, copying a local wire, or validating a draft does not connect anything globally.

## Domain-context voice

Workspace: `/home/vlad_/projects/CyberAlchemy-lab`

CyberAlchemy Lab keeps global Relation Kind contracts closed as exact ordered endpoint pairs. A proposal resolves the effective predecessor, proves endpoint carrier or internal-record contracts, preserves one semantic question, binds pair-specific qualifier rules and contestability, selects canonical relation authority, passes orthogonality and no-collapse validation, and submits the exact successor contract for admission. Ontology-local edges remain local unless an independently admitted global contract exists. The proposal has no effect while candidate-only.

### Examples

- Adding decision -> intent to relation.declares-effect-on preserves that Relation Kind question only when a closed effect_kind domain such as satisfies, rejects, or supersedes is bound to the exact pair.
- Challenge Event -> Operational Lesson asks which subject is challenged. It requires a challenges Relation Kind proposal rather than being compressed into evidence-bears-on or declares-effect-on.
- Ontology Node -> governed subject through represents may remain ontology-local. It cannot be published as a global identity assertion.
- A Capability Realization Binding may remain the canonical lifecycle record and project one digest-bound implementation -> product-capability Typed Relation. The projection cannot become a second writable authority.
- The undeclared pair experiment-run -> product remains rejected even when both endpoints exist and another membership pair is admitted.

## Applicability

Proposing one additional global ordered source endpoint kind to target endpoint kind connection under an existing Relation Kind, proposing a distinct Relation Kind when the semantic question differs, or proving that an ontology-local connection remains bounded to one exact Ontology contract.

### Exclusions

- Creating relation instances or admitting endpoint carriers.
- Inferring connections from separate source and target indexes.
- Changing Relation Kind meaning through an endpoint extension.
- Using wildcard or catch-all endpoint kinds.
- Publishing ontology-local edges as global connections without a separate admitted global contract.
- Treating a specialized binding and its Typed Relation projection as two writable authorities.
- Treating candidate validation, structural conformance, or endpoint admission as connection admission.

## Boundaries

- A connection is an allowed ordered pair of endpoint kinds in one exact Relation Kind contract; it is not a relation instance between two identified objects.
- A source-kind list and target-kind list are discovery projections only; their Cartesian product is not a connection contract.
- Registering or admitting an endpoint kind creates no connection.
- A global connection cannot become effective until both endpoint kinds resolve to admitted carriers or to explicitly governed internal record contracts permitted by the Relation Kind.
- Every global connection binds an exact qualifier schema and the allowed qualifier values and constraints for that ordered pair.
- Every proposal declares global or ontology-local scope. An ontology-local connection remains inside its exact Ontology contract and does not enter the global Relation Kind registry by implication.
- A specialized relation carrier declares one canonical-authority mapping: projects-as when the specialized carrier is canonical, or represented-by when the generic Typed Relation is canonical. Dual writable authority is forbidden.
- Every effective connection binds an exact contestability contract and owner route for the Relation Kind, pair, qualifiers, endpoints, and relation instance.
- The successor proposal resolves the effective predecessor Relation Kind version through decision and succession overlays before computing the new closed pair set.
- Admitting a connection neither admits its endpoint carriers nor creates, validates, admits, activates, or proves a relation instance.
- Reusing an existing Relation Kind is permitted only when its unique semantic question and qualifier contract express the proposed connection without collapse; otherwise a distinct Relation Kind must be proposed.
- A wildcard, catch-all endpoint, directory convention, observed historical use, shared label, or local ontology edge is not a declared global connection.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.definition.definition@1.0.0-candidate.1 | whole-json | `eac40dc90ad32383cf8d6724858bf1f4d80c105ed06c8168996a861b43a09575` | `admitted` |
| cal.definition.typed-coupling-invariant@1.0.0-candidate.1 | whole-json | `2358180b511b4297dfd53c8942125c811b3495c6fd73ce0b59ea7f68309aaaf1` | `admitted` |
| cal.definition.classification-orthogonality-invariant@1.0.0-candidate.1 | whole-json | `503e6a2575194be2b24d363578b8ab4a92590c88cf1bbeac53065ac4ad16be4a` | `admitted` |
| cal.definition.identity-relation@1.0.0-candidate.1 | whole-json | `cf6a40999ffab4e25f8766d1cd3f6085b7b3ab9468828539521c18e9ca30f28e` | `admitted` |

## Primary consumers

- CAL-AXIS-ORTHOGONAL-RELATION-MODEL-0002
- cal.artifact-type.relation-kind/successor

## Lookup and drift

- Index: `authority/definitions/candidates/0012-typed-connection-extension-rule/DEFINITIONS-INDEX.md` / `cal.definition.typed-connection-extension-rule@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `authority/definitions/candidates/0012-typed-connection-extension-rule/drift-audit-postimage.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

No typed relations declared.

## Evidence

- authority/relation-kinds/candidates/0002-axis-orthogonal-model/model.json
- authority/relation-kinds/candidates/0002-axis-orthogonal-model/endpoint-inventory.json
- authority/relation-kinds/candidates/0002-axis-orthogonal-model/receipts/no-collapse.json
- .arcanum/ontology-vault/2026-10-05-lab-integrated-model.md
- .arcanum/ontology-vault/2026-10-06-lab-semantic-gap-audit.md

## Residue

- Definition-owner admission remains required.
- Relation Kind owner review remains required for every existing and proposed endpoint pair.
- No canonical Relation Kind Artifact Type or general Typed Relation carrier currently exists.
- Qualifier schemas and pair-specific value domains remain unmaterialized.
- Twenty-two current endpoint kinds still lack canonical carriers.
- Global versus ontology-local scope and specialized-carrier authority must be selected per connection contract.

## Claim ceiling

This candidate defines how a closed global Relation Kind endpoint contract may be extended and how ontology-local scope remains bounded. It does not admit this Definition, admit or modify a Relation Kind, authorize any endpoint pair, resolve endpoint carriers, admit qualifier schemas or relation instances, select runtime behavior, or grant authority.
