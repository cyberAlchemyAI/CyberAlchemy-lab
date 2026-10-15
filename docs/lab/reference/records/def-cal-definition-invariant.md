[Documentation home](../../README.md)

# Invariant

<a id="def-cal-definition-invariant"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Invariant

# Invariant

A condition the system must preserve. It constrains system behavior, separately from an axiom about the world and the rules used to enforce it.

**When it applies**

Use "invariant" for a single must-hold truth about the system that is, in principle, checkable and whose breach is a defect. Two tests: (1) can the system violate it (is a breach a bug)? If yes, it is an invariant; if the system cannot make it false, it is an axiom. (2) Is it one condition (invariant) or a bundle of authoritative rules with selectors and modes (a constitution, `CAV2-D58`)? Each invariant should trace *up* to an axiom (its "why") and *down* to a validation mode.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**A stated exclusion**

Admission, activation, publication, release, deployment, and external effects.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-invariant-section-2"></a>

## Source explanatory wording

A condition the system must keep true — "same input, same output." Break it and you have a bug. It is the *what must stay true*, sitting below the axiom that says *why* and above the rulebook that says *how*.

<a id="def-cal-definition-invariant-section-3"></a>

## Exact governing statement

Invariant is the normalized definition identified by semantic.invariant, owned within scope.shared-authority, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D54 without silently merging it with another target.

Bound source-semantic basis:

An invariant is a **condition on the system's own behavior or artifacts that must remain true** across a declared scope of decisions, transformations, or states — such that a violation is **drift or a defect**. Its defining subject is the **system**: unlike an axiom (`CAV2-D53`), which the system is built around, an invariant is something the system **must satisfy** and can fail to. An invariant is the checkable *what-must-stay-true* that a constitution rule (`CAV2-D58`) operationalizes and a validator or gate (`CAV2-D37`) enforces.

````
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
````

- An invariant is **not** an axiom (`CAV2-D53`): same-input-same-output is a system must-hold; "unreproducible results cannot be trusted" is the world-truth behind it. It is **not** a constitution (`CAV2-D58`): the invariant is one must-hold proposition, the constitution is the scoped, composable rulebook that operationalizes many invariants with selectors, examples, validation modes, and precedence. It is **not** a validator or gate (`CAV2-D37`): the invariant states what must be true, the validator is the check that enforces it. It is **not** automatically authority — an invariant governs only through its owner route.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../../../evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/definitions/invariant/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.invariant@1.0.0-candidate.1

**Content fingerprint · SHA-256**

cf04f6e6e5adadc778059b0227248eff2c63130b73b84955507512f421eb3654

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Use \"invariant\" for a single must-hold truth about the system that is, in\nprinciple, checkable and whose breach is a defect. Two tests: (1) can the system\nviolate it (is a breach a bug)? If yes, it is an invariant; if the system cannot\nmake it false, it is an axiom. (2) Is it one condition (invariant) or a bundle of\nauthoritative rules with selectors and modes (a constitution, `CAV2-D58`)? Each\ninvariant should trace *up* to an axiom (its \"why\") and *down* to a validation\nmode.",
  "authority_scope_ref": "scope.shared-authority",
  "exclusions": [
    "Admission, activation, publication, release, deployment, and external effects.",
    "Meanings assigned to split or reclassified sibling targets unless explicitly referenced."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
