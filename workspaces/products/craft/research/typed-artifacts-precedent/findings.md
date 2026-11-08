---
node_type: research
is_session: false
layer: research
nature: findings
status: draft
dispatch_id: 2026-07-06-typed-artifacts-precedent
final_approver: parent
created_by: victorboscaro@gmail.com
last_updated: 2026-07-06
---

# Typed-Artifacts Precedent Sweep — Findings (Verdict Matrix)

> Dispatch `2026-07-06-typed-artifacts-precedent`. Question: for each component of DomainSpec-v2's
> typed-artifact bet, who in the *external* literature already owns it, and where (if anywhere) is
> the precedent genuinely clean? Evidence: four explorer returns (E1 Curry / E2 Spivak / E3
> Imieliński / E4 van Lamsweerde) + a three-skeptic robot_talks review over two waves (S1 Lakatos
> precedent · S2 Sattler non-vacuity · S3 Quine definitional-soundness), verbatim in
> [`research.md`](research.md). Every load-bearing claim below cites the return it rests on (P9).
> Research rule: **a found owner is a GO under `build-from-owned`, never a KILL** — only no-witness
> or definitional-collapse are terminal KILLs.

## 1. Headline

The sweep set out expecting several novelty candidates and found that **almost the entire bet is
already owned** — and by a lineage the four explorers all missed until the precedent skeptic named
it: the **assurance-case stack — SACM (OMG), GSN, Isabelle/SACM** [S1-W1]. SACM owns, in one
metamodel, exactly the three things v2 treated as its own: typed claim-graphs, first-class residue
nodes (GSN `undeveloped entity`), and claim-backed-by-proof edges. That discovery corrected two of
the sweep's draft novelty labels to `build-from-owned` and halved a third.

**One live, executed, defensible novelty survives all three gates:** component **(e) — a
machine-enforced, per-stage claim≤proof interlock at DAG stage boundaries, orthogonal to
type-checking**. It is not owned by SACM (which is human-argued and peer-reviewed, never
machine-gated per stage) [S1-W2], not Curry-Howard (which is unstatable for the ~13/15 non-code
stages) [E1], and it was **witnessed firing** on a real v2 counterexample [S2-W1,W2]. Its scope is
honest and small: witnessed once, **not proven-systemic** [S2-W2].

**The bigger prize — the conservation loop — is real in shape but currently UNWIRED.** No witness
exists on any v2 artifact that a gate failure is reified as a residue obligation and *re-consumed*
at a later stage [S2-W2]; it is sound-as-defined only [S3-W2]. It is an **open item**, not a
shippable claim.

## 2. Verdict matrix

| component | best owner(s) + citation | witnessed? | sound? | verdict | use-mode |
|---|---|---|---|---|---|
| **(a) node-envelope** | MOF M2 metamodel / **megamodel** = metamodel-over-stages [E2]; Ecore/EMF deployed [E2]; Agint typed floors [E4]; Σ-types [E1] | yes [S2-W1: fits Ecore EClass+inheritance] | yes | **GO** | **build-from-owned** (Ecore already-deployed). v2's JSON discriminated union is a *weaker* realization than a checked Σ-type/M2 — no standalone delta [S3-W1] |
| **(b) provenance — 3 edges** (derives-from, cites, supersedes) | PROV-O `wasDerivedFrom`/`wasQuotedFrom`/`wasRevisionOf`, W3C Rec 2013 [E3] | yes | yes | **GO** | **already-deployed** — re-typing a W3C standard. *Pin the sense:* if `cites` = bibliographic (not derivational), owner shifts to CiTO (Shotton 2010) [E3] |
| **(b) `implements`** | **SysML `satisfy` / UML Realization** [S1-W1]; refinement calculus / CompCert semantics-preservation [E1] | yes | yes | **GO** | **build-from-owned** — *corrected from novel-attempt.* The draft's "NONE in PROV" [E3] was novelty-of-absence; the edge is a standard traceability link [S1-W1]. "Heart of the bet" is importance, not novelty [S3-W1] |
| **(c) forbidden edges — structural** | MOF/Ecore constructive typing (absent `EReference` ⇒ edge inexpressible) [E2]; token-level type-constrained decoding [E4, Mündler PLDI 2025] | yes [S2-W1: `(Event,Entity)` has no signature in `relationships.yml`] | yes | **GO** | **build-from-owned** — genuine unconstructibility at the structural layer |
| **(c) forbidden edges — relational** | dependent/refinement types could make it constructive [E1]; SHACL/OCL only *validate-after-the-fact* [E2] | **NO [S2-W1]** | claim overshoots | **KILL (the unconstructibility claim)** | v2 types edges by intrinsic endpoint only; the cross-feature prohibition is graph-relational and *fails to type*; the SHACL form is **not a live gate** per v2's own R3 review [S2-W1]. "*All* forbidden edges unconstructible" is an overshoot [E2, S3-W1] |
| **(d) residue** | **GSN `undeveloped entity` / SACM** [S1-W1]; materialization mechanism = data-exchange recovery + ProSA side tables [E3] | yes [S2-W1] | collapses post-SACM | **GO (owned)** | **build-from-owned** — *corrected from novel-attempt.* SACM's typed residue node absorbs the carried-obligation content; only machine-consumption automation is left, and SHACL isn't live → unexecuted instance, not a delta [S3-W2] |
| **(e) claim≤proof — as a machine-enforced per-stage interlock** | SACM/Isabelle-SACM own the static claim≤proof *edge* [S1-W1]; **but the automated per-stage stage-advance interlock is unowned** [S1-W2, E4] | **YES — fired on a real counterexample** [S2-W1,W2, `closure-gates.md`] | yes [S3-W2: not reducible to SACM's argument-decomposition] | **GO** | **novel-attempt (narrow, witnessed-once)** — the one live novelty. Orthogonal to type-check (AEO passes `validate:rels` yet is false) [S2]. Ceiling: proves the consequent, never intent-fidelity under LLM [E1, Perrier 2510.01069] |
| **(f) recursive self-application** | proof-assistant bootstrapping [E1]; MOF reflexivity [E2]; Gödel-Agent/STOP/AlphaEvolve [E4] | precedent only | yes | **GO** | **build-from-owned** — "this substrate applied to its own next version" is an *unexecuted instance* of reflexivity, not a construct [S3-W1] |
| **integrated composition a–f (conservation loop)** | no owner binds all six; nearest = SACM co-location, but SACM is a static snapshot [S1-W2] | **NO-WITNESS** [S2-W2] | sound-as-defined only [S3-W2] | **OPEN ITEM** (not GO, not KILL) | genuine construct-*shape* (the loop unproven⇒residue⇒re-gated is not SACM's) but **unwired** on every real artifact — a promissory note until the connecting edge is built |

## 3. The novelty question — resolved

**Owned; v2 may NOT claim as novel** (cite and inherit): (a) node-envelope = megamodel/Ecore
[E2]; (b) three provenance edges = PROV [E3]; (b) `implements` = SysML `satisfy` [S1-W1]; (c)
structural prohibition = MOF/Ecore [E2]; (d) residue-as-typed-node = GSN/SACM [S1-W1]; the static
claim≤proof *edge* = SACM/Isabelle-SACM [S1-W1]; (f) reflexivity precedent [E1,E2,E4]; and the
whole intent→typed-artifact front-end [E4].

**The single defensible novelty claim v2 may ship, stated at exactly its proof width:**

> *We make the assurance-case claim≤proof gate a **machine-enforced, per-stage advance-blocker**
> over a heterogeneous DAG of typed artifacts — orthogonal to type-checking — where SACM/GSN own
> the static claim/residue/evidence graph but nothing that fires.* [S1-W2, S2-W2, S3-W2]

Anything broader overshoots. In particular: do **not** claim the typed claim-graph, the residue
node, the provenance edges, or "residue tracking" as invented — all are owned. Do **not** claim
"all forbidden edges unconstructible" — only structural ones are.

**Cross-lineage reconciliation (E1 vs E2 on forbidden-edges-unconstructibility):** the apparent
disagreement dissolves — they own different halves. *Structural* prohibition (absent type slot) is
MDE-constructive [E2]; *relational* prohibition is dependent-type-constructive [E1] — a different
lineage — and is otherwise only SHACL/OCL validate-after-the-fact [E2]. v2's current design does
neither for the relational case, and its own R3 review confirms the SHACL gate isn't live [S2-W1].

## 4. Open items surfaced (feed the tower's open-question section)

1. **Wire the conservation loop or drop the composition claim.** The prize — gate-failure ⇒
   residue obligation ⇒ re-consumed at a later re-gate — has NO witness on any artifact [S2-W2].
   Until built, the "integrated a–f substrate" is a promissory note, not a novelty.
2. **Relational-prohibition enforcement is not live.** v2 types edges by intrinsic endpoint only;
   cross-feature/relational prohibitions are `obligations`+`feature_scope` metadata that the R3
   review says pass `validate:rels` while carrying false labels [S2-W1]. Either adopt dependent-
   type encoding (constructive) [E1] or make the SHACL gate actually fire.
3. **Pin `cites` semantics** — derivational (PROV `wasQuotedFrom`) vs bibliographic (CiTO) [E3].
4. **Prove (e) systemic, not one-shot.** The interlock was witnessed firing *once* [S2-W2]; the
   claim's strength is bounded to that single live counterexample until recurrence is shown.
5. **Adopt-with-attribution, everywhere.** The action item from the SACM discovery is a citation
   sweep: every v2 doc touching claim-graphs / residue nodes / provenance edges must cite
   SACM/GSN / PROV / MOF as prior art, not present them as original.

## 5. One-line answer to the dispatch goal

**a = build-from-owned (Ecore) · b/3-edges = already-deployed (PROV) · b/implements =
build-from-owned (SysML satisfy) · c-structural = build-from-owned (MOF) · c-relational = overshoot
KILL (validate-after-fact, not live) · d = build-from-owned (GSN/SACM + ProSA) · e = novel-attempt,
narrow & witnessed-once (machine-enforced per-stage claim≤proof interlock) · f = build-from-owned ·
integrated composition = OPEN (genuine shape, unwired).** The sweep's net: v2's only live novelty
over the literature — including the SACM/assurance-case lineage it initially missed — is the
*automated per-stage enforcement* of a claim≤proof gate; the conservation loop that would make the
whole substrate novel is real in design but not yet instantiated.
