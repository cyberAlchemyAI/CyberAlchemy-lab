## CAV2-D37: Gate

Status: active
Term: gate
Aliases: governance gate, review gate, decision gate, admission gate

### Normative Definition

A gate is an explicit checkpoint that decides or routes whether a candidate
term, rule, artifact, relation, method, claim, mutation, or execution may
continue, must continue with named risk, must stop, or must defer to another
owner.

Every CyberAlchemy v2 gate must declare its owner route, scope, inputs,
criteria, possible verdicts, required evidence, residue handling, record
location, and downstream effect. Unless a narrower gate defines otherwise, the
minimum verdict vocabulary is `pass`, `flag`, `block`, and `defer`.

### Formal Interpretation

A gate `G` is a decision function:

```text
G(scope, input, evidence, criteria) -> verdict
verdict in {pass, flag, block, defer}
```

The verdict is admissible only if it records owner route, evidence basis,
residue or risk when present, and downstream effect.

### Operational Interpretation

Use gate for any controlled transition: promotion, schema amendment,
implementation mutation, validation acceptance, source import, extraction,
public/private boundary movement, or recursive method step. A gate is the place
where ambiguity either receives permission, receives risk, stops, or changes
owner.

### Plain-Language Intuition

A gate is the checkpoint that says "go", "go with this named risk", "stop", or
"send this to the right owner first."

### Domain-Context Voice

In CyberAlchemy v2, gate is the generic primitive under `CAV2-D5` promotion
gate, schema amendment checks, Craft blockers, decision-gate routes, validation
checks, and the pass/flag/block behavior used across research and handoff
surfaces. It keeps consequential movement explicit instead of implied by a file
edit or successful generation.

### Boundary

Gate is not bureaucracy, not a checklist item by itself, not permission without
a record, and not proof of correctness. A gate may use validators or human
decisions, but the gate is the recorded transition logic and effect.

### Primary Consumers

- [DEFINITION-TOWERS.md](DEFINITION-TOWERS.md)
- [source-clusters/primordial.md](source-clusters/primordial.md)
- [../promotion-policy.md](../promotion-policy.md)
- [../../CRAFT.md](../../CRAFT.md)
