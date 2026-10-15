[Documentation home](../../README.md)

# Axiom

<a id="def-cal-definition-axiom"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Axiom

# Axiom

A foundational proposition about the world or domain that the model takes as given and builds around. It is not a requirement on the system’s behavior; revising it requires reviewing what depends on it.

**When it applies**

Use "axiom" for the load-bearing truths a project stands on and reasons *from* — the ones that justify why a whole area, method, or rule family exists. Three tests: (1) can the system make it false? If yes, it is an invariant, not an axiom. (2) Is it actually believed true, or is it a bet? A bet (`veracidade: low`) is a **premise**, not an axiom. (3) Does a family derive from it? If nothing does, it is inert.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**A stated exclusion**

Admission, activation, publication, release, deployment, and external effects.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-axiom-section-2"></a>

## Source explanatory wording

A truth you build on, not a rule you obey. "Creatives are fat-tailed" is true about the world; you design around it. If it turned out false, your plan was wrong — not your code.

<a id="def-cal-definition-axiom-section-3"></a>

## Exact governing statement

Axiom is the normalized definition identified by semantic.axiom, owned within scope.shared-authority, and carried by type.definition. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D53 without silently merging it with another target.

Bound source-semantic basis:

An axiom is a **foundational proposition taken as given** — bedrock the system does not derive further within itself and holds as true (high commitment/veracity) — **from which a family of premises, invariants, and constitution rules derives**, such that revising it forces rethinking everything built on it. Its defining subject is the **world or domain** the system operates in: an axiom states *why* the system is shaped as it is, and the system is **built around** it rather than made to satisfy it. It is **not** a constraint on the system's own behavior — that is an invariant (`CAV2-D54`).

````
```text
axiom A:  taken-as-given(A) ∧ ¬derives-within-system(A) ∧ veracity(A) = high
          ∧ fan_out(A) = { premises, invariants, constitution-rules derived from A }
subject(A) = world/domain          (not the system's own behavior)
system can violate A?  No — if A is false, the premise was wrong, not the code buggy
genesis:       invariant → "why must this hold?" → A     (discovery order)
justification: A → invariant → constitution rule          (top-down order)
```

The **fan-out** is the axiom's signature: a proposition that grounds only one
downstream item, and nothing else, is not an axiom but the restatement of a single
invariant.
````

- An axiom is **not** an invariant (`CAV2-D54`): the invariant is a must-hold on the *system*; the axiom is a given truth about the *world* the system is built around. It is **not** a premise: a premise is a working bet held at low veracity (`veracidade: low`), an axiom is held true. It is **not** a constitution (`CAV2-D58`): the constitution is the authoritative scoped rulebook; the axiom is the reason behind it. It is **not** a definition (`CAV2-D33`): a definition assigns meaning to a term, an axiom asserts a foundational truth. An axiom and the invariants it grounds enforce nothing by themselves. A constitution authorizes and scopes constraints; a selected validator or gate checks or performs enforcement.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../assets/fdafe8a39a52-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.axiom@1.0.0-candidate.1

**Content fingerprint · SHA-256**

fdafe8a39a52749278574bcdc570f41c8a282e7a6e44071fd595fcfcd181a0c4

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Use \"axiom\" for the load-bearing truths a project stands on and reasons *from* —\nthe ones that justify why a whole area, method, or rule family exists. Three tests:\n(1) can the system make it false? If yes, it is an invariant, not an axiom. (2) Is\nit actually believed true, or is it a bet? A bet (`veracidade: low`) is a\n**premise**, not an axiom. (3) Does a family derive from it? If nothing does, it is\ninert.",
  "authority_scope_ref": "scope.shared-authority",
  "exclusions": [
    "Admission, activation, publication, release, deployment, and external effects.",
    "Meanings assigned to split or reclassified sibling targets unless explicitly referenced."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
