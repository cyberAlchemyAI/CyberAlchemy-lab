---
node_type: research
is_session: false
layer: research
nature: evidence
status: draft
dispatch_id: 2026-07-06-typed-artifacts-precedent
created_by: victorboscaro@gmail.com
last_updated: 2026-07-06
---

# Typed-Artifacts Precedent Sweep — Collected Returns (verbatim)

> Dispatch `2026-07-06-typed-artifacts-precedent` (dispatch_type: research). Four explorers,
> each sweeping one external lineage for owners of DomainSpec-v2's typed-artifact bet
> components: (a) node-envelope typed schema over ~15 stages; (b) typed provenance edges
> (derives-from/cites/implements/supersedes); (c) domain-concept typed edges with
> forbidden-edges-unconstructible; (d) tracked residue; (e) claim≤proof gate; (f) recursive
> self-application; all under LLM agents doing intent→code.
>
> These are the explorers' returns **verbatim**. The cited synthesis (verdict matrix) lives in
> `findings.md`; every load-bearing claim there cites the return it rests on. Half the
> formal-methods surface is already owned internally by the `alloy-tla-modeling` and
> `dcb-correctness` towers — this sweep is the EXTERNAL literature only.

---

## E1 — Curry (Type theory / proof-as-spec)

Discipline: every candidate carries a verifiable citation; where the lineage only *touches* a
component rather than owning it, it is demoted.

### (e) claim≤proof — natural owner
- **Curry-Howard correspondence** (propositions-as-types / proofs-as-programs). Cite: Wadler,
  "Propositions as Types," *CACM* 58(12), 2015. A well-typed program **IS** a proof; type =
  proposition (the claim), term = proof. Type-checker = the gate. **Use-mode: already-deployed**
  (type-checkers enforce claim≤proof mechanically).
- **Honest boundary:** owns claim≤proof cleanly only when the *artifact is code* and the *claim
  is a type* — there it is a theorem you cannot evade. **Stops at non-code artifacts** (~13 of
  ~15 v2 stages: design docs, session notes, ontology edges, residue registers — no term/type
  isomorphism for prose). **Stops harder at intent under LLM generation:** Curry-Howard verifies
  a proof is *valid*, never that the proposition is the *right* one or *faithfully translates
  intent*. Cite: Perrier, "Typed Chain-of-Thought: A Curry-Howard Framework for Verifying LLM
  Reasoning," arXiv:2510.01069, 2025 — applies C-H to LLM reasoning but concedes it reaches
  *syntactic* validity, not semantic truth/premise accuracy. **Demotion: for LLM intent→code the
  lineage owns proof-of-consequent, never proof-of-intent-fidelity.**
- Sharper owner for the "proof travels with the artifact" mechanic: **Proof-Carrying Code**
  (Necula, POPL 1997) — untrusted producer ships a machine-checkable proof of a stated policy;
  cheap consumer check. Ancestor of "grade carries a proof ref". **Use-mode: build-from-owned**
  (deployed for code+safety-policies; extending to non-code typed artifacts is a real port).

### (a) node-envelope — touches, does not own
- **Dependent sum / inductive families**: a Σ-type `(stage : Stage) × Body(stage)` is exactly
  "one schema, body varies per stage." Cite: Brady, "Idris," *JFP* 23(5), 2013. **Use-mode:
  build-from-owned** (formalism deployed; v2's envelope is a JSON-level discriminated union, not
  a checked Σ-type — informs, not owns).

### (c) forbidden-edges-unconstructible — strong secondary
- **"Make illegal states unrepresentable"** via no-constructor + refinement types. Cite: Rondon,
  Kawaguchi, Jhala, "Liquid Types," PLDI 2008. A refinement `{e : Edge | allowed(e)}` makes a
  forbidden edge *fail to type*. **Use-mode: build-from-owned** (refinement checking is deployed).

### (d) residue — names the gap, does not own tracking
- Type theory has the notion of the uncaptured remainder (spec-as-type vs full intent) but
  treats it as a *failure to eliminate*, not a *first-class tracked object*. Cite: Swamy et al.,
  "F*," POPL 2016. **Demotion — Use-mode: novel-attempt** for the tracking discipline.

### (b) provenance edges — does not own
- Gets `derives-from` for free (reduction/elaboration relation) and verified-compilation
  (CompCert-style) gives typed `implements`/`derives-from`; `cites`/`supersedes` are bookkeeping,
  not proof structure. **Use-mode: build-from-owned** for derives-from/implements only; **not
  owned** for cites/supersedes.

### (f) recursive self-application — owns the precedent
- Proof-assistant bootstrapping / self-verification (a system checking artifacts of its own
  kind). **Use-mode: build-from-owned** (deployed inside proof assistants; porting across typed
  artifacts generally is a port).

**E1 keystone (won't inflate):** Curry-Howard makes claim≤proof a *theorem* exactly where the
artifact is code and the claim is a type; for every other stage and for intent→spec fidelity
under LLM generation, the lineage proves the consequent, never the intent (Perrier 2510.01069 is
the citable ceiling).

---

## E2 — Spivak (Model-driven engineering + ontologies)

### Critical precision finding (the load-bearing distinction)
Two enforcement regimes exist and are NOT equivalent:
1. **Metamodel typing (MOF/Ecore/UML) = constructive.** If a metamodel declares no `EReference`
   A→B, an instance edge A→B is *not expressible* — the tooling has no slot for it. Genuine
   unconstructibility at the *structural* level.
2. **Constraint languages (OCL, SHACL) = validated-after-the-fact.** OCL invariants / SHACL
   shapes are *post-hoc validation* over an already-constructed model. Cite: Pavlyshyn, *Open
   World vs Closed World: Modeling OWL and SHACL Semantics*, 2024 ("SHACL … a post-hoc validation
   mechanism rather than a proactive constraint enforcement system"); spinrdf.org "SHACL and OWL
   Compared." The ill-typed edge *can be formed*, then flagged.

**Therefore:** v2's "a forbidden relation cannot be FORMED, not merely asserted" is achievable in
this lineage ONLY at the metamodel-typing layer, NOT at OCL/SHACL. Forbidden edges expressible as
*relational-property* rules (no cycle, author≠reviewer, stage-N can't cite N+2) fall to SHACL/OCL
= validate-after-the-fact. Only forbidden edges expressible as *absent type slots* are truly
unconstructible. True unconstructibility for relational constraints lives in
dependent-type/correct-by-construction encoding — a *different* lineage. Cite: "Ill-Typed
Programs Don't Evaluate," POPL/PACMPL 2024, arXiv:2307.06928.

### Construct → owner → component → use-mode
- **MOF four-layer stack (M3/M2/M1/M0)** — OMG MOF 2.5.1 (2019). → (a). node-envelope = an M2
  metamodel; 15 bodies = M1 instances. **build-from-owned.**
- **EMF/Ecore** — Steinberg et al., *EMF*, 2008. → (a). Executable realization of MOF's M3.
  **already-deployed** (infrastructure).
- **UML/OCL well-formedness** — OMG OCL 2.4 (2014). UML uses OCL to define its own metamodel's
  well-formedness. → (c) constraint half + (e) invariants-as-obligations. **build-from-owned**,
  but validate-after-the-fact (no unconstructibility).
- **SHACL** — W3C Rec, 2017. Node/property shapes validating a data graph; **validation reports =
  a structured residue ledger** (focus node + failing path). → (c) + (d). **build-from-owned**
  for constraint/residue; NOT an owner of unconstructibility.
- **OWL/RDFS + Open-World Assumption** — W3C OWL. **Cautionary negative precedent:** OWA means
  OWL *cannot* express integrity constraints / forbidden-edge prohibitions natively (why SHACL
  was created). Description-logic/inference is the WRONG owner for "forbidden edge."
- **Ologs** — Spivak & Kent, *PLoS ONE* 7(1):e24274, 2012 (arXiv:1102.1889). Category = types +
  typed arrows + commutative-diagram constraints. → (a)+(c). **build-from-owned** (a formalism,
  not a deployed enforcement engine).
- **PG-Schema / PG-Keys** — Angles et al., SIGMOD 2023 (arXiv:2211.10962). Typed nodes + typed
  edges + constraints, tractable validation; feeds ISO GQL. → (a)+(b)+(c). **build-from-owned**
  (enforcement validation-based, not constructive, for the constraint half).
- **Megamodels / Global Model Management** — Bézivin/Jouault/Favre; "On Metamodeling in
  Megamodels," MoDELS 2007; "Typing artifacts in megamodeling," *SoSyM* 11(2), 2011. **Direct
  precedent for "a metamodel over ~15 artifact stages"** — a macroscopic typed model whose
  elements are models/stages and whose edges are typed relations (incl. transformation/
  provenance). → (a)+(b). **build-from-owned.** Answers "does a metamodel-over-stages exist?" →
  YES, that's a megamodel.
- **MOF reflexivity / self-conformance** — MOF-defined-in-MOF. → (f). **build-from-owned**, with
  caution (AACS 2019: the self-describing claim "is hard to verify … no formal proofs").

**E2 summary:** v2 owns nothing here as pure novelty. **(c) is a SPLIT verdict** — structural
forbidden edges ARE unconstructible via MOF/Ecore (build-from-owned); relational forbidden edges
are only validated-after-the-fact in this whole lineage; true constructive relational prohibition
is a *different* (dependent-type) lineage and would be a novel-attempt. Sustainable claim:
"structurally-typed prohibitions are unconstructible; rule-based prohibitions are gated by
validation." Claiming v2 makes *all* forbidden edges unconstructible overshoots.

---

## E3 — Imieliński (Data provenance & lineage)

Verdict up front: PROV already owns three of four edge types outright; residue is not a
first-class provenance construct but its machinery is owned by data-exchange / schema-evolution
theory.

### (b) typed provenance edges
- **`prov:wasDerivedFrom`** — Lebo/Sahoo/McGuinness et al., "PROV-O," W3C Rec, 2013. = v2's
  `derives-from`, exactly. **already-deployed** (normative standard, production lineage systems).
- **`prov:wasQuotedFrom`** — PROV-O (subproperty of wasDerivedFrom) = v2's `cites` (the
  "reproduces source" reading). **already-deployed** as derivation-flavored citation. **Caveat:**
  PROV's cites is a *derivation* subproperty (content flows), NOT bibliographic; if v2's `cites`
  means "references without deriving," that's CiTO (Shotton, *J. Biomedical Semantics*, 2010), a
  different owner. **Pin which sense.**
- **`prov:wasRevisionOf`** (+ `prov:invalidatedAtTime`/`wasInvalidatedBy`) — PROV-O = v2's
  `supersedes`. **already-deployed.** YES, PROV owns supersedes-semantics for versioned artifacts.
- **`implements`** — **NONE in PROV.** Nearest neighbors (prov:used/wasGeneratedBy, P-Plan) don't
  mean "artifact X implements spec Y." Closer to formal-methods refines/satisfies (SysML
  `satisfy`, refinement calculus). **Use-mode: novel-attempt (justified)** — the one edge with no
  provenance-standard owner, and it's the intent→code arrow at the heart of v2's bet.

**Edge-set verdict:** 3 of 4 (derives-from, cites, supersedes) are **build-from-owned** over a
deployed W3C standard; `implements` is the one novel edge. Honest claim: "we re-type PROV's
derivation family and add one non-provenance edge (`implements`)," NOT "we invented typed
provenance edges."

### provenance-theory substrate
- **why/where/how-provenance** — Buneman/Khanna/Tan, ICDT 2001; Cheney/Chiticariu/Tan survey,
  FnT Databases 2009; Green/Karvounarakis/Tannen, "Provenance Semirings," PODS 2007. Fine-grained
  theory beneath a derives-from edge (tuple granularity; v2 is artifact granularity). **Reference-
  grade / already-deployed as theory.**

### (d) tracked residue
Provenance literature has NO construct literally named "residue = what a transformation dropped."
Semiring/how-provenance records what was USED, silent on what the input HAD that the output no
longer reflects. Residue is the *complement* of derivation; its owners live in data-exchange:
- **Lossy schema mappings / inverses / recovery** — Fagin, "Inverting Schema Mappings," PODS
  2006/TODS 2007; Fagin/Kolaitis/Popa/Tan, "Quasi-Inverses," PODS 2007; Arenas/Pérez/Riveros,
  "The Recovery of a Schema Mapping," PODS 2008/TODS 2009 (maximum recovery). A mapping is *lossy*
  exactly when it has no exact inverse; "maximum recovery" formalizes how much is recoverable =
  the loss. **build-from-owned** (specialize from relational instances to typed stage artifacts).
- **ProSA / Reverse Provenance Expansion** — Auge & Heuer, "ProSA," ADBIS 2019; "Combining
  Provenance Management and Schema Evolution," IPAW 2018; "Enhanced Inversion …," arXiv:2211.13810,
  2022. Where inversion is lossy, store *minimal extra provenance* (side tables) to reconstruct
  lost duplicates/values/dangling tuples — **residue made material.** **build-from-owned
  (strongest precedent for d).** v2's novelty is only the domain, not the mechanism.

**Residue verdict:** build-from-owned, not novel. Honest claim: "we adopt data-exchange's
loss/recovery accounting and materialize residue as a stored side-artifact per stage
translation," NOT "we introduce residue tracking."

---

## E4 — van Lamsweerde (LLM-era intent→code)

Legend: OWNED = clear prior art · PARTIAL = adjacent owner, a slice remains open · CLEAN = no
owner found = candidate novel.

1. **Type/grammar constrains generation (token level)** → (c). Mündler/He/Wang/Sen/Song/Vechev,
   "Type-Constrained Code Generation with LMs," PLDI 2025 (arXiv:2504.09246) — prefix automata +
   inhabitable-type search make ill-typed completions *provably unreachable*. Precursors:
   Synchromesh (NeurIPS 2022), Monitor-Guided Decoding (NeurIPS 2023). **OWNED at token/decoding
   granularity** — but constrains one program text, NOT a multi-stage typed DAG.
2. **Intent formalized into a typed artifact fed to a generator** → (a). Chivukula et al.,
   "Agint: Agentic Graph Compilation," NeurIPS 2025 wksp (arXiv:2511.19635) — explicit type
   floors text→data→spec→code, typed effect-aware code DAGs. Closest owner of v2's core.
   Spec-Driven Development corpus (GitHub Spec Kit; Spec Kit Agents arXiv:2604.05278) owns staged
   intermediate artifacts but weakly typed (NL/markdown). **OWNED (Agint) for typed staged
   artifacts.**
3. **Typed provenance across a composed pipeline** → (b). "Agentics 2.0," arXiv:2603.04241 (typed
   composable algebra, provenance+confidence preserved across composition); "From Agent Traces to
   Trust," arXiv:2606.04990 (survey of typed relations for verification/attribution/audit).
   **OWNED — established, surveyed category.**
4. **Requirements/goal formalization (KAOS-style) via LLM** → (a) upstream. "Agentic LLM
   Requirement Formalization," arXiv:2604.18228; LTLGuard arXiv:2603.05728; classic KAOS
   (van Lamsweerde/Dardenne). **OWNED** — mature, active lane.
5. **claim≤proof gate** → (e). Split ownership, **no unified owner**: NL granularity — PaperTrail
   (arXiv:2602.21045), MiniCheck (arXiv:2404.10774); formal-code granularity — SYNVER,
   SpecGen/SpecPylot (arXiv:2604.16560), VibeContract (arXiv:2603.15691). **PARTIAL** — "claim
   backed by proof" exists as NL fact-checking and as proof-carrying code, but *as a typed gate
   over a multi-stage artifact graph (claim node ≤ its proof edges, enforced before stage
   advance)* — **no owner found.** Defensible open slice.
6. **Tracked residue (first-class deferred/unresolved ledger)** → (d). Closest: HarnessBridge
   (arXiv:2606.12882) "unresolved coverage" (open issues not resolved by later turns); multi-agent
   -failure literature names "missing termination / skipped verification" as the dominant failure
   mode — but nobody models it as a typed artifact. **CLEAN (candidate novel)** — no source treats
   residue as a *typed, first-class, carried-forward ledger node*. Caveat: the *concept* "account
   for what you didn't resolve" is folklore; only the *typed-artifact instantiation* is unclaimed.
7. **Recursive self-application** → (f). Gödel Agent (ACL 2025), STOP, AlphaEvolve. **OWNED for
   self-improvement** — BUT these self-modify scaffolds/prompts/algorithms; none recursively apply
   *the same typed-artifact-graph machinery to construct the next version of that machinery*.
   **PARTIAL/CLEAN** — self-application of *this specific typed pipeline* not demonstrated.

**E4 GAP (honest framing):** every *individual* component (a,b,c) + formalization front-end has a
clear owner — do not claim them. The unclaimed territory is **the composition, not the parts**: a
single typed artifact graph carrying (a)+(b)+(c) **AND** (d) residue-as-typed-node **AND** (e)
claim≤proof enforced *at graph edges between stages*, the whole under LLM agents, (f) recursively
self-applied. (d) and (e) are the two thinnest-owned constructs — the honest novelty candidates.
The integrated stack (a–f as one substrate) has no owner in this sweep. **Skeptic's caution:**
"combining known constructs" is weak novelty unless the composition yields a property none of the
parts give; v2's defensible claim is narrow — *residue and claim≤proof as typed graph constructs*,
and *whether the composition is closed under self-application*.

**E4 caveat on its own sweep:** several cited arXiv IDs carry 2026 datestamps (2602–2606),
consistent with current-date context but not each venue-verified; the load-bearing owners (Agint,
Mündler PLDI'25, Agentics 2.0, the provenance survey) were fetched/confirmed.

---

# Reviewer returns (zig-zag with the synthesizer; robot_talks group, 2 waves)

Three skeptics, one gate each, `robot_talks: true`. Wave 1 = initial positions; Wave 2 = final
positions after confrontation (P14: synthesizer/approver receives initial AND final).

## S1 — Lakatos (precedent gate)

**Wave 1 (initial):** located the owner the four explorers all missed — the **assurance-case
lineage: SACM (OMG), GSN, Isabelle/SACM (arXiv:2009.12154)** — which owns typed claim-graphs,
residue nodes (GSN `undeveloped entity` = intentional incompleteness as a first-class typed
node), and claim-backed-by-proof edges. Demotions: b/`implements` → SysML `satisfy` / UML
Realization (build-from-owned, not novel); d/residue-node → GSN undeveloped-entity
(build-from-owned); e halved (SACM owns the claim≤proof edge; only the automated
**stage-advance enforcement interlock** survives). Composition relabeled "novel over
SACM-adjacent prior art", not whole-cloth.

**Wave 2 (final):** novelty survives narrowly and *only* on the enforced side. SACM owns the
static graph (human-argued, peer-reviewed; its `undeveloped` node is an annotation, nothing
*fires*). What clears SACM: (i) the automated per-stage interlock (SACM has no machine gate) —
corroborated by Sattler's (e) *firing*; (ii) the (d)×(e) conservation *wiring* (not SACM's
vocabulary). Final use-modes: (d) adopt-with-attribution (cite GSN/SACM, claim only the
lifecycle-obligation semantics); (e) claim-narrow-novelty ("machine-enforced per-stage
interlock", never "typed claim graph"); composition = conditional-novel iff the loop is wired,
else collapses to SACM.

## S2 — Sattler (non-vacuity gate)

**Wave 1 (initial):** built hand-witnesses on real v2 files. **5/6 WITNESSED**: (a) envelope →
Ecore EClass+inheritance + EEnum-state (`NODE-MODEL.md`, `TAXONOMY.md`); (c-structural) the
`(Event, Entity)` edge has no signature in `relationships.yml` → unconstructible; (d) residue
node instantiates on the real `deferred: depends-on` drop (`relationships.yml:527`); (e) the gate
**actually fired** — a TLA+ counterexample blocked stage-advance (`closure-gates.md:21-28`),
orthogonal to type-check (the AEO fixture passes `validate:rels` yet carries false endpoint
labels); composition witnessed at 3 components in one file. **One terminal NO-WITNESS KILL:**
(c-relational) as a refinement type — v2 types edges by intrinsic endpoint meta-type only, so the
cross-feature prohibition (graph-relational) *fails to type*; the surviving SHACL form is, per
v2's own R3 review, **not a live enforced gate**.

**Wave 2 (final):** (e)-automated-interlock = **WITNESSED (scoped)** — machine-produced
counterexample, mechanical block, wired into stage-advance; fired *once*, so WITNESSED not
PROVEN-SYSTEMIC. Conservation-loop wiring = **NO-WITNESS**: both endpoints exist (gate fires;
residue nodes exist) but the connecting edge — a specific gate failure reified as a residue
obligation then *consumed* at a later re-gate on the same trace — cannot be constructed on any
real artifact. "I have both nails; I do not have the plank between them." The composition is
vacuous as instantiated.

## S3 — Quine (definitional-soundness gate)

**Wave 1 (initial):** KILLed (a), (b/`implements`), (c-structural), (f) as null-residual
re-skins (owned, no surviving delta; his sharpest split with Lakatos on `implements` —
importance ≠ novelty). Kept (d) SOUND-thin [delta = forward-carried gate-consumed obligation,
≠ ProSA backward recovery, ≠ PROV death-marking] and (e) SOUND [delta = DAG stage-boundary
invariant over heterogeneous non-isomorphic nodes, ≠ Curry-Howard]. Composition CONDITIONAL — a
construct only if it wires conservation (unproven⇒residue⇒re-gated: "no claim advances unproven,
nothing dropped is silently lost"), else "combined known parts".

**Wave 2 (final):** conceded SACM co-locates claim-nodes + residue-nodes + claim≤evidence edges,
which collapses the *co-location* delta. **(d) → COLLAPSE**: SACM's typed residue node absorbs
the carried-obligation content; only machine-consumption automation is left, and per Sattler the
SHACL enforcement isn't live → unexecuted instance, not a definitional delta. **(e) → SURVIVES,
genuine construct**: a machine-enforced cross-type stage-boundary invariant is not reducible to
SACM's human-argued *argument decomposition*, and Sattler witnessed it firing → residual survives
*and* is executed. **Composition → SOUND-as-defined, unexecuted**: the forward conservation loop
is precisely what SACM structurally lacks (genuine construct-shape) but its enforcement rides on
the not-yet-live SHACL gate → a promissory note.

## Convergence (all three, Wave 2)

- **SACM/GSN/Isabelle-SACM owns everything representational** — typed claim graph, residue nodes,
  claim≤proof edges. All of (a), (b), (d-as-node) are build-from-owned; the sweep's original
  "novel" labels for b/`implements` and d were **corrected** by finding this lineage.
- **The one live, executed, defensible novelty is (e):** a *machine-enforced, per-stage
  claim≤proof interlock at DAG stage boundaries, orthogonal to type-checking* — witnessed firing
  once (`closure-gates.md`), not owned by SACM (human-argued), not Curry-Howard (unstatable for
  ~13/15 non-code stages). Scope caveat: WITNESSED, not PROVEN-SYSTEMIC.
- **The conservation loop is the real prize but is UNWIRED** — genuine construct-shape, NO-WITNESS
  as instantiated (Sattler), sound-as-defined-only (Quine). An **open item**, not a shippable
  claim.
- **"All forbidden edges unconstructible" is an overshoot** (terminal KILL on the relational
  half): only *structural* prohibition is unconstructible (MOF/Ecore); relational is
  validate-after-the-fact and not yet a live gate in v2.
