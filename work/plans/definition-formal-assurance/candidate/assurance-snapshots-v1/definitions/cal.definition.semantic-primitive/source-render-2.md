<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Semantic Primitive

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.semantic-primitive`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope.shared-authority`
- Lifecycle posture reference: `candidate:artifact-reconstruction-l1/v1`

## Scientific/formal voice

Semantic Primitive is the normalized definition identified by semantic.semantic-primitive, owned within scope.shared-authority, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D31 without silently merging it with another target.

Bound source-semantic basis:

A primitive type is a CyberAlchemy v2 base semantic kind that lower definitions,
methods, constitutions, disciplines, schemas, ontology records, or execution
artifacts may reference without deriving its meaning from a narrower source
space, implementation layer, project glossary, or generated representation.

To count as a primitive type, the term must declare its stable name, authority
scope, allowed consumers, source-evidence boundary, relation to any external
authority term, and the condition under which lower layers may specialize it.
Lower layers may instantiate, specialize, or compose a primitive type, but they
must not silently redefine it.

```text
For a CyberAlchemy v2 term `t`, `primitive_type(t)` is admissible only when:

```text
authority_scope(t) = CAV2
owner(t) = definitions-governance
derived_from_narrower_source_space(t) = false
boundary(t) is declared
consumer_surface(t) is declared
specialization_rule(t) is declared
```

If `t` is borrowed from an external authority, the primitive claim applies only
to CyberAlchemy v2's local role for `t`, not to the external authority's whole
meaning.
```

### Notation

| Symbol | Meaning |
| --- | --- |
| semantic.semantic-primitive | Stable normalized identity for Semantic Primitive. |
| CAV2-D31 | Bound CyberAlchemy-v2 source-definition identity. |

### Boundary conditions

- Primitive type is not a programming-language primitive, not a database field
type, not a schema class, not a DomainSpec `DS-D1` meta-type, not a source
glossary label, and not automatic authority for any term called "primitive" in
another folder.

### Testable conditions

- The candidate identity remains cal.definition.semantic-primitive.
- Every selected source-section digest remains current.
- The machine record validates against Definition/v1.
- The human projection is regenerated exactly from the machine record.

## Plain-language voice

A primitive type is a base kind the project is allowed to build with before it
builds narrower things.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

In CyberAlchemy-lab migration work, Semantic Primitive is a prototype meaning reconstructed from CAL-NORMALIZE-01. It remains non-authoritative until the correct Lab owner admits a fully validated candidate.

Source context retained for reconstruction:

In CyberAlchemy v2, primitive type names the role played by local bases such as
axis orthogonality, bounded recursive self-application, residue, method, and
definition. It also keeps CAV2 local primitives separate from DomainSpec
meta-types, Arcanum schema/contract terms, programming types, and ontology node
types. Those may be evidence or external references, but they become CAV2
primitive types only when this file re-authors the local semantic role.

### Examples

- Resolve semantic.semantic-primitive by its machine identity rather than its directory name.
- Challenge source drift through the L1 drift audit before relying on Semantic Primitive.

## Applicability

Use this term when deciding whether a candidate belongs in the primordial basis
rather than a lower tower. A primitive type should be small enough for multiple
towers to reuse, but strict enough that lower artifacts cannot stretch it by
vibe, proximity, or repeated use.

### Exclusions

- Admission, activation, publication, release, deployment, and external effects.
- Meanings assigned to split or reclassified sibling targets unless explicitly referenced.

## Boundaries

- Primitive type is not a programming-language primitive, not a database field
type, not a schema class, not a DomainSpec `DS-D1` meta-type, not a source
glossary label, and not automatic authority for any term called "primitive" in
another folder.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cyberalchemy-v2:CAV2-D31 | ## CAV2-D31: Primitive Type | `fddeaca1c06e48637bb26cc8b0184eebed7ac5791feaea1d765fdfa83309bf1e` | `candidate-unadmitted` |

## Primary consumers

- semantic.schema

## Lookup and drift

- Index: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/registry.json` / `cal.definition.semantic-primitive@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/drift-audit.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.originates-from | cal.definition.semantic-primitive | cyberalchemy-v2:CAV2-D31 | role:definition-owner |

## Evidence

- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0003-review-led-reconstruction/target-candidates/semantic/semantic-semantic-primitive/v1/artifact.json
- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/receipts/validation.json
- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/receipts/validation.json

## Residue

- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/drift-audit.json

## Claim ceiling

Candidate Definition reconstructed from an accepted normalization scaffold and exact CyberAlchemy-v2 source sections. It is not admitted and grants no implementation, migration, registry, publication, release, deployment, or external-effect authority.
