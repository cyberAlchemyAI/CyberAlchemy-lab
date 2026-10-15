## CAV2-D35: Provenance

Status: active
Term: provenance
Aliases: source provenance, origin chain, provenance chain, source chain

### Normative Definition

Provenance is the declared origin and transformation chain for a term, artifact,
claim, rule, decision, relation, validation result, or residue. It records where
the object came from, which sources or prior objects it depends on, which
operations changed it, which owners or processes handled it, and which
authority posture it held at each relevant step.

Provenance must identify source references and relation types with enough
precision that a later reviewer can distinguish source evidence, local
adaptation, promotion, demotion, translation, derivation, validation, and
generated projection.

### Formal Interpretation

For object `x`, provenance is a typed path:

```text
Prov(x) = [(source_i, relation_i, operation_i, owner_i, posture_i)]*
```

The path may be incomplete only if the missing segment is explicitly recorded
as residue with an owner route. Untyped "came from" language is not sufficient
for authority-bearing use.

### Operational Interpretation

Use provenance before promoting, adapting, importing, validating, or publishing
anything. Provenance answers what source material is being used, what happened
to it, and where the current object should be audited if it drifts.

### Plain-Language Intuition

Provenance is the receipt trail for where something came from and how it got
here.

### Domain-Context Voice

In CyberAlchemy v2, provenance is the lower-level basis for
`CAV2-D24` provenance-first navigation, authority imports, source clusters,
inventory evidence cards, Craft links, handoffs, and future extraction review.
It lets v2 import scattered work without flattening source ownership or
pretending that source evidence has already become local authority.

### Boundary

Provenance is not proof, not authority, not trust, not validation, and not
credit assignment by itself. A perfect source trail can still point to a false,
unpromoted, private, or unusable claim. It only tells the project where meaning
and transformations came from.

### Primary Consumers

- [DEFINITION-TOWERS.md](DEFINITION-TOWERS.md)
- [source-clusters/primordial.md](source-clusters/primordial.md)
- [../imports/definitions/MANIFEST.md](../imports/definitions/MANIFEST.md)
- [../../SOURCE-MAP.md](../../SOURCE-MAP.md)
- [../../CRAFT.md](../../CRAFT.md)
