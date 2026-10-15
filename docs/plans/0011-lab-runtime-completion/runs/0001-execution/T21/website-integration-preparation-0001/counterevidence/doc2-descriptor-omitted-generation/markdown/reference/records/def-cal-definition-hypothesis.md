[Documentation home](../../README.md)

# Hypothesis

<a id="def-cal-definition-hypothesis"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Hypothesis

# Hypothesis

A proposition framed so evidence can test it. It remains distinct from an assumption already chosen as a premise.

**When it applies**

Use "premise" for the load-bearing bets a project stands on *provisionally* — the things it commits to acting on before they are proven, and expects to test. The marker is a hedge: if a candidate axiom says "hypothesis", "we conjecture — not prove", or carries `veracidade: low`, it is a premise. A premise earns its way to axiom only through the evidence/promotion path (`CAV2-D48`), never by conviction alone.

**Record formats**

[Hypothesis · v1](type-cal-artifact-type-hypothesis-v1.md#type-cal-artifact-type-hypothesis-v1)

**A stated exclusion**

Admission, activation, publication, release, deployment, and external effects.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-hypothesis-section-2"></a>

## Source explanatory wording

A hypothesis is an idea framed so evidence can test it, not an assumption the project has already chosen to rely on.

<a id="def-cal-definition-hypothesis-section-3"></a>

## Exact governing statement

Hypothesis is the normalized definition identified by semantic.hypothesis, owned within scope.shared-authority, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D55 without silently merging it with another target.

Target-specific normative meaning:

A Hypothesis is a falsifiable provisional proposition posed for investigation or experiment, with declared observations or outcomes that could support, refine, or reject it; it is not adopted as a working basis merely by being stated.

Bound source-semantic basis:

A premise is a **working proposition the project adopts in order to proceed without having established it as true** — a defeasible bet or commitment, characteristically held at **low veracity but often high conviction** (`veracidade: low`, `convicção: high`) — that is expected to be revised, promoted, or retired as evidence accumulates. A premise may complement axioms (a working elaboration built on the bedrock) or stand alone as a conjecture the project is betting on. It can provisionally ground invariants and rules, but it does **not** carry the settled truth of an axiom (`CAV2-D53`).

````
```text
premise P:  adopted-to-proceed(P) ∧ ¬established-true(P) ∧ defeasible(P)
            typically veracity(P) = low, conviction(P) = high   (CAV2-D23: the two axes diverge)
lifecycle:  P --evidence--> { promote → axiom (CAV2-D48) | revise | retire }
distinguished-from:
  axiom (CAV2-D53):      veracity high, held true     → a premise is a bet
  invariant (CAV2-D54):  a must-hold on the system    → a premise is a proposition to reason from
```

The premise is exactly the case where **veracity and conviction diverge**
(`CAV2-D23`): the project may be highly committed to acting on `P` while `P`
remains unproven.
````

- A premise is **not** an axiom (`CAV2-D53`): the axiom is held true (high veracity), the premise is a bet (low veracity) even when conviction is high — `CAV2-D23` keeps veracity and commitment separate, and the premise is exactly where they diverge. It is **not** an invariant (`CAV2-D54`): the invariant is a must-hold on the system, a premise is a proposition to reason from. It is **not** a disposable hypothesis: a premise is *load-bearing* (things are built on it) while still unproven — which is what makes its defeasibility worth tracking rather than ignoring. Promotion premise → axiom is an evidence-gated lifecycle move (`CAV2-D48`), never automatic.
- This target remains distinct from the sibling targets semantic.premise reconstructed from CAV2-D55; shared source lineage does not merge their identities or validation purposes.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../assets/73ff2afa18f6-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.hypothesis@1.0.0-candidate.1

**Content fingerprint · SHA-256**

73ff2afa18f644175bab998fc4b0372d1d9e556d725fec968d6a8bec24817a9f

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Use \"premise\" for the load-bearing bets a project stands on *provisionally* — the\nthings it commits to acting on before they are proven, and expects to test. The\nmarker is a hedge: if a candidate axiom says \"hypothesis\", \"we conjecture — not\nprove\", or carries `veracidade: low`, it is a premise. A premise earns its way to\naxiom only through the evidence/promotion path (`CAV2-D48`), never by conviction\nalone.",
  "authority_scope_ref": "scope.shared-authority",
  "exclusions": [
    "Admission, activation, publication, release, deployment, and external effects.",
    "Meanings assigned to split or reclassified sibling targets unless explicitly referenced."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
