## CAV2-D55: Premise

Status: active
Term: premise
Aliases: working premise, working hypothesis, hypothesis, conviction bet
Promoted: 2026-07-08 (design session; the `veracidade: low`/`convicção: high` bet layer completing the axiom/invariant/premise trio)

### Normative Definition

A premise is a **working proposition the project adopts in order to proceed
without having established it as true** — a defeasible bet or commitment,
characteristically held at **low veracity but often high conviction**
(`veracidade: low`, `convicção: high`) — that is expected to be revised, promoted,
or retired as evidence accumulates. A premise may complement axioms (a working
elaboration built on the bedrock) or stand alone as a conjecture the project is
betting on. It can provisionally ground invariants and rules, but it does **not**
carry the settled truth of an axiom (`CAV2-D53`).

### Formal Interpretation

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

### Operational Interpretation

Use "premise" for the load-bearing bets a project stands on *provisionally* — the
things it commits to acting on before they are proven, and expects to test. The
marker is a hedge: if a candidate axiom says "hypothesis", "we conjecture — not
prove", or carries `veracidade: low`, it is a premise. A premise earns its way to
axiom only through the evidence/promotion path (`CAV2-D48`), never by conviction
alone.

### Plain-Language Intuition

A bet you are willing to build on for now. You act as if it is true, but you know
it is not proven — and you are watching for the evidence that confirms it, revises
it, or kills it.

### Domain-Context Voice

In the vault corpora, premises live beside axioms (`business-premises`,
`ontology-premises`, `system-premises`) and "sit on top of" them; `veracidade: low
/ convicção: high` is the premise signature. ZefraHub `AX-ONT-7` ("we conjecture —
not prove") and `AX-SYS-3` ("the folder structure is a hypothesis") are premises
mislabeled as axioms. Demotion is normal and healthy: a vault moved an
"adaptive-system axiom" to the `P-ONT-9` premise because it was "an engineering
commitment about maintenance, not a foundational truth."

### Boundary

A premise is **not** an axiom (`CAV2-D53`): the axiom is held true (high veracity),
the premise is a bet (low veracity) even when conviction is high — `CAV2-D23` keeps
veracity and commitment separate, and the premise is exactly where they diverge. It
is **not** an invariant (`CAV2-D54`): the invariant is a must-hold on the system, a
premise is a proposition to reason from. It is **not** a disposable hypothesis: a
premise is *load-bearing* (things are built on it) while still unproven — which is
what makes its defeasibility worth tracking rather than ignoring. Promotion premise
→ axiom is an evidence-gated lifecycle move (`CAV2-D48`), never automatic.

### Open Questions

#### PR-OQ-1. Premise vs. hypothesis — one term or two?

Do we need both `premise` and `hypothesis`, or is `premise` the CAV2 term and
`hypothesis` a source-local alias (the vaults use "hypothesis" in `AX-SYS-3`)?
Current lean: one term, `premise`, with `hypothesis` an alias. Status: OPEN.

#### PR-OQ-2. Where is the premise → axiom threshold?

Where exactly does a premise become an axiom (veracity crosses a line) or get
retired? Ties to `AX-OQ-3` and the `CAV2-D23` evidence/commitment axes; the
promotion move itself is `CAV2-D48`. Status: OPEN.

#### PR-OQ-3. May a premise ground an invariant or constitution rule?

If a rule is built on a premise (a bet) rather than an axiom (a truth), how is that
provisional footing marked so the rule is visibly a bet — a residue flag, a
validation-mode caveat, or a blocked promotion? Status: OPEN.

### Primary Consumers

- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- [DEFINITION-DRIFT-AUDIT.md](DEFINITION-DRIFT-AUDIT.md)
- [#cav2-d53-axiom](#cav2-d53-axiom)
- [#cav2-d23-authority-lifecycle-axis](#cav2-d23-authority-lifecycle-axis)
- [#cav2-d48-authority-promotion-lifecycle](#cav2-d48-authority-promotion-lifecycle)
