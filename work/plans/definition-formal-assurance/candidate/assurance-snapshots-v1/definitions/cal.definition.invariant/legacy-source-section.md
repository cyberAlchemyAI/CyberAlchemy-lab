## CAV2-D54: Invariant

Status: active
Term: invariant
Aliases: must-hold constraint, system invariant
Promoted: 2026-07-08 (design session; generic parent of CAV2-D16/D29/D38/D49; subject-test boundary against axiom)

### Normative Definition

An invariant is a **condition on the system's own behavior or artifacts that must
remain true** across a declared scope of decisions, transformations, or states —
such that a violation is **drift or a defect**. Its defining subject is the
**system**: unlike an axiom (`CAV2-D53`), which the system is built around, an
invariant is something the system **must satisfy** and can fail to. An invariant is
the checkable *what-must-stay-true* that a constitution rule (`CAV2-D58`)
operationalizes and a validator or gate (`CAV2-D37`) enforces.

### Formal Interpretation

```text
invariant I:  ∀ state/transition s in scope(I):  must-hold(I, s)
subject(I) = the system            (its behavior / artifacts)
system can violate I?  Yes — a violation is drift/defect (a bug)
grounded-by:        an axiom (CAV2-D53) answering "why must I hold?"
operationalized-by: constitution rule (CAV2-D58)
enforced-by:        validator / gate (CAV2-D37)
```

CyberAlchemy v2 already carries specific invariants — `CAV2-D16` typed coupling,
`CAV2-D29` axis orthogonality, `CAV2-D38` claim ≤ proof, `CAV2-D49` closed
authority-kind enumeration; this definition is their generic parent.

### Operational Interpretation

Use "invariant" for a single must-hold truth about the system that is, in
principle, checkable and whose breach is a defect. Two tests: (1) can the system
violate it (is a breach a bug)? If yes, it is an invariant; if the system cannot
make it false, it is an axiom. (2) Is it one condition (invariant) or a bundle of
authoritative rules with selectors and modes (a constitution, `CAV2-D58`)? Each
invariant should trace *up* to an axiom (its "why") and *down* to a validation
mode.

### Plain-Language Intuition

A condition the system must keep true — "same input, same output." Break it and
you have a bug. It is the *what must stay true*, sitting below the axiom that
says *why* and above the rulebook that says *how*.

### Domain-Context Voice

In CyberAlchemy v2, invariant is the middle of the `axiom → invariant →
constitution → validator` chain: the checkable anchor that a constitution may
operationalize and a selected validator or gate may enforce, and the parent
genus of the already-promoted invariant instances
(`CAV2-D16`/`D29`/`D38`/`D49`). An invariant with no axiom under it is unjustified;
an invariant with no validation mode is un-enforceable (`none-yet`, per
constitution-governance).

### Boundary

An invariant is **not** an axiom (`CAV2-D53`): same-input-same-output is a system
must-hold; "unreproducible results cannot be trusted" is the world-truth behind it.
It is **not** a constitution (`CAV2-D58`): the invariant is one must-hold
proposition, the constitution is the scoped, composable rulebook that
operationalizes many invariants with selectors, examples, validation modes, and
precedence. It is **not** a validator or gate (`CAV2-D37`): the invariant states
what must be true, the validator is the check that enforces it. It is **not**
automatically authority — an invariant governs only through its owner route.

### Open Questions

#### IN-OQ-1. Generic parent vs. the specific instances.

Does a generic `invariant` parent add a real distinction over the specific
instances (`CAV2-D16`/`D29`/`D38`/`D49`), or risk over-abstraction? Promoted as the
parent genus; watch that it does not absorb or blur their specific boundaries.
Status: OPEN (monitor).

#### IN-OQ-2. Own authority-kind, or governs as `Definition`?

Should `invariant` be a first-class authority kind, or continue governing as the
`Definition` kind (as `CAV2-D16`/`D29`/`D38`/`D49` currently do)? Mirrors
[AUTHORITY-MODEL OQ-2](../AUTHORITY-MODEL.md). Status: OPEN (tracked upstream).

#### IN-OQ-3. Is the trace obligation a constitution rule or a soft expectation?

Should the expectation that every invariant traces *up* to an axiom (`CAV2-D53`)
and *down* to a validation mode (`deterministic`/`review`/`hybrid`/`none-yet`) be a
**constitution rule** (authoritatively adopted and scoped), or a soft documentary
expectation? Ties to the
enforcement thread and [AUTHORITY-MODEL OQ-1](../AUTHORITY-MODEL.md). Status: OPEN.

### Primary Consumers

- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- [DEFINITION-DRIFT-AUDIT.md](DEFINITION-DRIFT-AUDIT.md)
- [#cav2-d53-axiom](#cav2-d53-axiom)
- [#cav2-d58-constitution](#cav2-d58-constitution)
- [#cav2-d37-gate](#cav2-d37-gate)
- [../AUTHORITY-MODEL.md](../AUTHORITY-MODEL.md) (Invariant, Axiom, Constitution)
- [../../ontology/governance/README.md](../../ontology/governance/README.md)
