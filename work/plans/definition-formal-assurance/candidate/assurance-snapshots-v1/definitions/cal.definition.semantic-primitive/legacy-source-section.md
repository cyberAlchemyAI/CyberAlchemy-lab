## CAV2-D31: Primitive Type

Status: active
Term: primitive type
Aliases: semantic primitive type, primitive semantic type, base semantic object, semantic primitive

### Normative Definition

A primitive type is a CyberAlchemy v2 base semantic kind that lower definitions,
methods, constitutions, disciplines, schemas, ontology records, or execution
artifacts may reference without deriving its meaning from a narrower source
space, implementation layer, project glossary, or generated representation.

To count as a primitive type, the term must declare its stable name, authority
scope, allowed consumers, source-evidence boundary, relation to any external
authority term, and the condition under which lower layers may specialize it.
Lower layers may instantiate, specialize, or compose a primitive type, but they
must not silently redefine it.

### Formal Interpretation

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

### Operational Interpretation

Use this term when deciding whether a candidate belongs in the primordial basis
rather than a lower tower. A primitive type should be small enough for multiple
towers to reuse, but strict enough that lower artifacts cannot stretch it by
vibe, proximity, or repeated use.

### Plain-Language Intuition

A primitive type is a base kind the project is allowed to build with before it
builds narrower things.

### Domain-Context Voice

In CyberAlchemy v2, primitive type names the role played by local bases such as
axis orthogonality, bounded recursive self-application, residue, method, and
definition. It also keeps CAV2 local primitives separate from DomainSpec
meta-types, Arcanum schema/contract terms, programming types, and ontology node
types. Those may be evidence or external references, but they become CAV2
primitive types only when this file re-authors the local semantic role.

### Boundary

Primitive type is not a programming-language primitive, not a database field
type, not a schema class, not a DomainSpec `DS-D1` meta-type, not a source
glossary label, and not automatic authority for any term called "primitive" in
another folder.

### Primary Consumers

- [source-clusters/primordial.md](source-clusters/primordial.md)
- [DEFINITION-TOWERS.md](DEFINITION-TOWERS.md)
- [DEFINITION-LOCALIZATION-ROUTE.md](DEFINITION-LOCALIZATION-ROUTE.md)
- [../../CRAFT.md](../../CRAFT.md)
