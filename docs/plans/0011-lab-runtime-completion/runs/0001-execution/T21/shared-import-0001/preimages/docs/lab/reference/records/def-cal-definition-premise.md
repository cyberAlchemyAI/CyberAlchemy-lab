[Documentation home](../../README.md)

# Premise

<a id="def-cal-definition-premise"></a>

[Reference catalog](../definitions.md#catalog-definitions) / Exact record

# Premise

An explicit assumption selected for the present work. It remains identified so conclusions can be revisited if it changes.

**When it applies**

Use "premise" for the load-bearing bets a project stands on *provisionally* — the things it commits to acting on before they are proven, and expects to test. The marker is a hedge: if a candidate axiom says "hypothesis", "we conjecture — not prove", or carries `veracidade: low`, it is a premise. A premise earns its way to axiom only through the evidence/promotion path (`CAV2-D48`), never by conviction alone.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**A stated exclusion**

Admission, activation, publication, release, deployment, and external effects.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

## Source explanatory wording

A premise is a declared assumption the project chooses to work with for now.

## Exact governing statement

Premise is the normalized definition identified by semantic.premise, owned within scope.shared-authority, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D55 without silently merging it with another target.

Target-specific normative meaning:

A Premise is a defeasible working proposition deliberately adopted so work may proceed without claiming that the proposition has been established as true; it carries its evidence posture, conviction, revision route, and retirement conditions.

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
- This target remains distinct from the sibling targets semantic.hypothesis reconstructed from CAV2-D55; shared source lineage does not merge their identities or validation purposes.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../../../evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/definitions/premise/v1/definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.premise@1.0.0-candidate.1

**Content fingerprint · SHA-256**

e4e87dfa32d8bd264caa3f40c5414e299a0808cbd4d29df0341f5b52d20f57d0

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

[Return to this catalog](../definitions.md#catalog-definitions)
