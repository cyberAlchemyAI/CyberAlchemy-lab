## CAV2-D38: Claim-Proof Bound

Status: active
Term: claim <= proof
Aliases: claim-proof bound, claim proof invariant, evidence-bounded claim, proof-bounded claim

### Normative Definition

Claim <= proof is the CyberAlchemy v2 epistemic invariant that a claim's
asserted strength, authority effect, validation status, or publication posture
must not exceed the proof, evidence, witness, validation result, owner decision,
or accepted premise cited for it.

If support is absent, partial, private, indirect, disputed, or weaker than the
claim, the claim must be downgraded, marked as hypothesis or candidate,
flagged with residue, routed through a gate, or blocked from governing work.

### Formal Interpretation

For claim `c`, asserted strength `S(c)`, and support package `P(c)`:

```text
S(c) <= strength(P(c))
```

where `strength(P(c))` is interpreted by the relevant domain, validator,
research standard, owner decision, or constitution. If no support package is
declared, `S(c)` defaults to candidate or hypothesis.

### Operational Interpretation

Use claim <= proof when writing research findings, definitions, constitutions,
validation reports, ontology projections, public statements, or implementation
readiness notes. The invariant forces the project to ask: what exactly supports
this claim, and how strong may the wording be?

### Plain-Language Intuition

Do not say more than the evidence can carry.

### Domain-Context Voice

In CyberAlchemy v2, claim <= proof prevents research synthesis, inventory
cards, ontology projections, generated indexes, successful commands, or owner
intuition from hardening into stronger authority than they earned. It is the
epistemic companion to provenance and gates: provenance shows the support
trail, gates decide movement, and claim <= proof bounds what the project is
allowed to say.

### Boundary

Proof does not mean only formal mathematical proof. It can be a source citation,
validation run, witness, owner decision, accepted premise, or formal proof,
depending on the claim type. The invariant does not require maximal certainty;
it requires honest wording relative to declared support.

### Primary Consumers

- [DEFINITION-TOWERS.md](DEFINITION-TOWERS.md)
- [source-clusters/primordial.md](source-clusters/primordial.md)
- [../../CRAFT.md](../../CRAFT.md)
- [../../../projects/framework-unification/CONCEPT-MAP.md](../../../projects/framework-unification/CONCEPT-MAP.md)

