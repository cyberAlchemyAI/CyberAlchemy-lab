[Documentation home](../../README.md)

# Claim-Support Compatibility Invariant

<a id="def-cal-definition-claim-support-compatibility-invariant"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Claim-Support Compatibility Invariant

# Claim-Support Compatibility Invariant

A claim’s strength, status or authority effect must stay within the proof, evidence, owner decision or accepted premise offered to support it. Partial or missing support must remain explicit.

**When it applies**

Use claim <= proof when writing research findings, definitions, constitutions, validation reports, ontology projections, public statements, or implementation readiness notes. The invariant forces the project to ask: what exactly supports this claim, and how strong may the wording be?

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**A stated exclusion**

Admission, activation, publication, release, deployment, and external effects.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-claim-support-compatibility-invariant-section-2"></a>

## Source explanatory wording

Do not say more than the evidence can carry.

<a id="def-cal-definition-claim-support-compatibility-invariant-section-3"></a>

## Exact governing statement

Claim-Support Compatibility Invariant is the normalized invariant identified by semantic.claim-support-compatibility-invariant, owned within scope.shared-authority, and carried by type.invariant. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D38 without silently merging it with another target.

Bound source-semantic basis:

Claim <= proof is the CyberAlchemy v2 epistemic invariant that a claim's asserted strength, authority effect, validation status, or publication posture must not exceed the proof, evidence, witness, validation result, owner decision, or accepted premise cited for it.

If support is absent, partial, private, indirect, disputed, or weaker than the claim, the claim must be downgraded, marked as hypothesis or candidate, flagged with residue, routed through a gate, or blocked from governing work.

````
For claim `c`, asserted strength `S(c)`, and support package `P(c)`:

```text
S(c) <= strength(P(c))
```

where `strength(P(c))` is interpreted by the relevant domain, validator,
research standard, owner decision, or constitution. If no support package is
declared, `S(c)` defaults to candidate or hypothesis.
````

- Proof does not mean only formal mathematical proof. It can be a source citation, validation run, witness, owner decision, accepted premise, or formal proof, depending on the claim type. The invariant does not require maximal certainty; it requires honest wording relative to declared support.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../assets/73e97225d896-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.claim-support-compatibility-invariant@1.0.0-candidate.1

**Content fingerprint · SHA-256**

73e97225d896fa5ba9157ec860b3ef7b9c36da01b3089943f9d2b5f87558f2f1

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Use claim <= proof when writing research findings, definitions, constitutions,\nvalidation reports, ontology projections, public statements, or implementation\nreadiness notes. The invariant forces the project to ask: what exactly supports\nthis claim, and how strong may the wording be?",
  "authority_scope_ref": "scope.shared-authority",
  "exclusions": [
    "Admission, activation, publication, release, deployment, and external effects.",
    "Meanings assigned to split or reclassified sibling targets unless explicitly referenced."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
