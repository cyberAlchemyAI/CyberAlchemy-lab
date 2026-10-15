[Documentation home](../../README.md)

# Semantic Primitive

<a id="def-cal-definition-semantic-primitive"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Semantic Primitive

# Semantic Primitive

A base semantic kind available for building more specialized kinds under the declared model.

**When it applies**

Use this term when deciding whether a candidate belongs in the primordial basis rather than a lower tower. A primitive type should be small enough for multiple towers to reuse, but strict enough that lower artifacts cannot stretch it by vibe, proximity, or repeated use.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**A stated exclusion**

Admission, activation, publication, release, deployment, and external effects.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-semantic-primitive-section-2"></a>

## Source explanatory wording

A primitive type is a base kind the project is allowed to build with before it builds narrower things.

<a id="def-cal-definition-semantic-primitive-section-3"></a>

## Exact governing statement

Semantic Primitive is the normalized definition identified by semantic.semantic-primitive, owned within scope.shared-authority, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D31 without silently merging it with another target.

Bound source-semantic basis:

A primitive type is a CyberAlchemy v2 base semantic kind that lower definitions, methods, constitutions, disciplines, schemas, ontology records, or execution artifacts may reference without deriving its meaning from a narrower source space, implementation layer, project glossary, or generated representation.

To count as a primitive type, the term must declare its stable name, authority scope, allowed consumers, source-evidence boundary, relation to any external authority term, and the condition under which lower layers may specialize it. Lower layers may instantiate, specialize, or compose a primitive type, but they must not silently redefine it.

````
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
````

- Primitive type is not a programming-language primitive, not a database field type, not a schema class, not a DomainSpec `DS-D1` meta-type, not a source glossary label, and not automatic authority for any term called "primitive" in another folder.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../../../evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/definitions/semantic-primitive/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.semantic-primitive@1.0.0-candidate.1

**Content fingerprint · SHA-256**

6ebbd2daae345dc75d363b7848ecd14ccc8d5fe4bef97f49b08f070efef631d4

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Use this term when deciding whether a candidate belongs in the primordial basis\nrather than a lower tower. A primitive type should be small enough for multiple\ntowers to reuse, but strict enough that lower artifacts cannot stretch it by\nvibe, proximity, or repeated use.",
  "authority_scope_ref": "scope.shared-authority",
  "exclusions": [
    "Admission, activation, publication, release, deployment, and external effects.",
    "Meanings assigned to split or reclassified sibling targets unless explicitly referenced."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
