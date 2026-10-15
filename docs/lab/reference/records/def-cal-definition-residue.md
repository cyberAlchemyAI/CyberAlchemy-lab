[Documentation home](../../README.md)

# Residue

<a id="def-cal-definition-residue"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Residue

# Residue

Meaningful information, distinctions or obligations that remain unresolved or were not preserved by the current representation or work.

**When it applies**

Use residue when something meaningful remains after a local operation has done what it knows how to do. The remainder may be information loss, untyped noise, missing vocabulary, failed validation, a broken recomposition path, an authority gap, or an unresolved owner route.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**A stated exclusion**

Admission, activation, publication, release, deployment, and external effects.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-residue-section-2"></a>

## Source explanatory wording

Residue is the meaningful leftover: the part the current representation could not carry.

<a id="def-cal-definition-residue-section-3"></a>

## Exact governing statement

Residue is the normalized definition identified by semantic.residue, owned within scope.shared-authority, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D18 without silently merging it with another target.

Bound source-semantic basis:

Residue is the typed remainder exposed by a transformation, translation, promotion, validation, or governance operation when the target representation, layer, or decision path does not preserve, name, justify, validate, or carry all source structure required by the operation's intended use.

A residue becomes actionable in CyberAlchemy v2 only when it records:

- source operation or transformation - expected preservation or closure condition - observed remainder or failure-locus - residue type - evidence reference - owner route - treatment: repair, type, gate, climb, accept, or defer

````
For an operation `F : A -> B` with an intended preservation condition `P`, the
residue of `F` is the evidence-bearing part of `A` that `B` cannot preserve,
name, reconstruct, justify, or validate under `P`.

In DomainSpec formalization contexts, this umbrella has several non-identical
readings:

- schema residue: a schema-level unit failure or missing faithful shadow
- instance residue: an instance-level round-trip or migration failure
- `ResidueObject`: a finite probabilistic residue object with entropy
- `ResidueStructure`: a carrier/schema/signal/noise/refinement structure
- `ResidueCat`: a category of bundled residue structures and monotone morphisms
- `Carrier(mu_n)`: the reflection-tower carrier that turns level `n` residue
  into level `n+1` vocabulary

These readings may inform each other, but CyberAlchemy v2 must not treat them as
interchangeable without a typed coupling.
````

- Residue is not any bug, not any uncertainty, not proof of novelty, and not automatic promotion. Some residue is acceptable, some is repairable, some is a blocker, and some is the seed for a higher layer. The imported term `TranslationResidue` remains a source-specific candidate until a later pass decides whether it is a subtype, alias, or separate term.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../../../evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/definitions/residue/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.residue@1.0.0-candidate.1

**Content fingerprint · SHA-256**

637cc42f17a2d3505303cb04e43ec47b21c623e1adad36422c3b44ba241a52ff

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Use residue when something meaningful remains after a local operation has done\nwhat it knows how to do. The remainder may be information loss, untyped noise,\nmissing vocabulary, failed validation, a broken recomposition path, an authority\ngap, or an unresolved owner route.\n\nFirst type the residue. Then either repair it locally, record a typed coupling,\nroute it through a gate, promote it through the reflection tower method, accept\nit as tolerated residue, or defer it as an open question.",
  "authority_scope_ref": "scope.shared-authority",
  "exclusions": [
    "Admission, activation, publication, release, deployment, and external effects.",
    "Meanings assigned to split or reclassified sibling targets unless explicitly referenced."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
