[Documentation home](../../README.md)

# Residue Measurement

<a id="def-cal-definition-residue-measurement"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Residue Measurement

# Residue Measurement

Measures distinctions, uncertainty or information loss exposed by a declared operation. The mathematical interpretation, measure, scope and status must be stated before it influences governance.

**When it applies**

Use residue entropy when a CyberAlchemy v2 artifact needs to compare, rank, route, or validate typed residue by a quantitative or categorical observable. Valid examples include finite Shannon entropy on a `ResidueObject`, Boltzmann `log |fiber|` in a finite coarse-graining bridge, KL or entropy-gap evidence in a declared finite-support setting, retrieval entropy as evidence for classification uniqueness, or an entropy profile over a declared residue chain.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**A stated exclusion**

Admission, activation, publication, release, deployment, and external effects.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-residue-measurement-section-2"></a>

## Source explanatory wording

Residue entropy is how much meaningful distinction the current layer collapsed or left unnamed.

<a id="def-cal-definition-residue-measurement-section-3"></a>

## Exact governing statement

Residue Measurement is the normalized definition identified by semantic.residue-measurement, owned within scope.knowledge-development, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D27 without silently merging it with another target.

Bound source-semantic basis:

Residue entropy is a CyberAlchemy v2 primitive observable for typed residue: it measures the distinguishability, uncertainty, or information loss exposed by a transformation, translation, coarse-graining, classification, validation, or governance operation after the residue type and source operation have been declared.

Residue entropy may influence authority, routing, validation, ontology, or implementation only when the entropy claim declares:

- entropy register or mathematical reading - source operation or transformation - typed residue source - measure or observable used - finite, weighted, retrieval, probabilistic, or categorical scope - theorem, conjecture, analogy, or review status - authority effect or non-governing residue treatment

````
For a finite probabilistic residue object `R` with finite carrier `F_R` and
probability mass function `rho`, the residue entropy observable is:

```text
H(R) = sum_{x in F_R} negMulLog(rho(x))
```

In the finite microcanonical macrostate bridge, for a coarse-graining
`f : M -> M'`:

```text
S_f(m') = log |fiber_f(m')|
```

and positive entropy marks fully-faithful residue:

```text
S_f(m') > 0  <->  m' in ffNoise(f)
```

This makes finite Boltzmann entropy a readout of `Residue_FF(Macro)`, not a
replacement for the broader `CAV2-D18` residue primitive.
````

- Residue entropy is not generic disorder, not uncertainty by itself, not proof of novelty, and not automatic promotion. Non-numeric residue may still be valid and actionable. Weighted, Gibbs, continuous, Markov-category, free-energy, RG, or physical second-law claims require their own typed bridge before they may govern CyberAlchemy v2 authority.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../assets/6baa9a3c04b8-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.residue-measurement@1.0.0-candidate.1

**Content fingerprint · SHA-256**

6baa9a3c04b875a7237d1bf70f423c1f2d51c4192d2efa0cef40e70210fcdadd

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Use residue entropy when a CyberAlchemy v2 artifact needs to compare, rank,\nroute, or validate typed residue by a quantitative or categorical observable.\nValid examples include finite Shannon entropy on a `ResidueObject`, Boltzmann\n`log |fiber|` in a finite coarse-graining bridge, KL or entropy-gap evidence in\na declared finite-support setting, retrieval entropy as evidence for\nclassification uniqueness, or an entropy profile over a declared residue chain.\n\nBefore using the observable as evidence, the artifact must name what residue is\nbeing measured and which register supplies the measure. If the register cannot\nbe named, the claim remains analogy, research pressure, or typed residue.",
  "authority_scope_ref": "scope.knowledge-development",
  "exclusions": [
    "Admission, activation, publication, release, deployment, and external effects.",
    "Meanings assigned to split or reclassified sibling targets unless explicitly referenced."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
