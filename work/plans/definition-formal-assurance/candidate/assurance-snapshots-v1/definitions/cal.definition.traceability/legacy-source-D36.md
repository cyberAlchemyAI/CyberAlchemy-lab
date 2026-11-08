## CAV2-D36: Traceability

Status: active
Term: traceability
Aliases: traceable chain, traceable linkage, lifecycle traceability

### Normative Definition

Traceability is the ability to follow explicit, typed links across intent,
source evidence, provenance, definitions, rules, methods, artifacts, gates,
validation, decisions, residue, and next routes so that a later human or agent
can answer why something exists, what it depends on, what it affects, and where
to continue.

Traceability is satisfied only when the relevant chain has enough link targets,
relation types, authority postures, and residue markers to be traversed without
hidden conversation context.

### Formal Interpretation

For a work object `x` and a review question `q`, traceability holds when there
is a declared path:

```text
trace_q(x) = x -> link_1 -> link_2 -> ... -> answer_or_residue
```

Each `link_i` must have a target, relation type, and authority posture. If the
path breaks, the break must be recorded as typed residue or a named gap.

### Operational Interpretation

Use traceability when deciding whether CyberAlchemy v2 is navigable enough to
resume, validate, publish, extract, or hand off. It is the check that source
receipts, definitions, Craft state, decisions, and validation evidence are
connected rather than merely present.

### Plain-Language Intuition

Traceability means you can follow the thread from "why are we doing this?" to
"what changed?" to "what happens next?"

### Domain-Context Voice

In CyberAlchemy v2, traceability turns the stable repository objective into a
navigation requirement. It binds CAV2 definitions, source clusters, import
manifests, Craft contexts, inventory cards, ontology projections, handoffs, and
validation evidence into routes that future work can traverse without replaying
the original conversation.

### Boundary

Traceability is not the same as provenance. Provenance records origin and
transformation history; traceability tests whether the project can navigate the
relevant links for a question. Traceability is also not proof, completeness, or
approval.

### Primary Consumers

- [DEFINITION-TOWERS.md](DEFINITION-TOWERS.md)
- [source-clusters/primordial.md](source-clusters/primordial.md)
- [../../CRAFT.md](../../CRAFT.md)
- [../../TO-VLAD/SESSION-HANDOFF-cav2-primordial-basis.md](../../TO-VLAD/SESSION-HANDOFF-cav2-primordial-basis.md)
