<!--
  MINT-ACT OUTPUT (L1 authority-spine seed) for the `domainspec-v2` domain.
  Cast from cyberAlchemy-v2/development/mint/templates/authority-model.md via the EMIT-PROCEDURE,
  grounded in DomainSpec's own AUTHORITY-MAP.md + DRIFT-CONVERGENCE.md. INTERNAL / private —
  never publish to arcanum/. INHERITS cav2 meta-machinery (table FORMAT, source-movement shape,
  non-collapse rule structure, gate vocab); LOCALIZES the object content (the three governances).
  Obs-B baked in: cav2 NEVER on a resolution path — harvested precedent / citation only.
  Domain-originated kinds are PROPOSED; the domainspec-v2 owner RATIFIES (D49 owner-gate). An L1
  integrity receipt exists; external L2 actor-identity signing remains BLOCKED.
-->

# Authority Model

Status: active local authority model (three kinds RATIFIED; L1 integrity receipt present; external L2 signature pending)
Owner: DomainSpec v2 owner

## Purpose

This model decides what this repository is allowed to claim while it **governs and enforces
the DomainSpec language (Ontology A) on evidence** — typing intent into spec concepts and
holding their derived obligations, structural layering, and convergence.

It deliberately separates:

- the **spec primary source** — the feature pack (`docs/features/<f>/` DFDS aspect docs) and the
  normative research definitions (`research/.../DEFINITIONS.md`) — what the domain says about itself;
- **repository-local method authority** — owned by *this repo's own* constitution
  (`constitutions/domainspec-v2-CONSTITUTION.md`), NOT by any external framework;
- external evidence (other methodology corpora; **v1 `implementation/domainspec/` as harvested precedent**);
- local synthesis (a repo-authored reading);
- policy / implementation authority, which this repo does not own (the implementation contract, deploy, org policy).

> **Localization invariant (Obs-B).** Method authority (source posture, promotion discipline,
> non-collapse, layering law, convergence judgement) is owned **locally** by this repo's
> constitution + this model. **No external framework (including CyberAlchemy v2) is named as the
> method authority.** cav2 and DomainSpec v1 appear ONLY as **harvested precedent (supporting
> source)** in `source-spine.md` — cited for provenance, never on a resolution path. This is the
> emit-time state; it needs no later decision to become true.

## Core Rule

DomainSpec can **type** a spec node, **derive** its obligations, **validate** them, **rule** on
its layer, and **measure** drift toward convergence. DomainSpec **cannot** mark an obligation
*satisfied in production*, declare *convergence*, or promote a spec into the **implementation
contract** without (a) a witness (the derived check actually passes) and (b) an **external owner
decision** (the impl conforms / the release is made). Expected values are read **from the spec**,
never by running the implementation.

## Authority Kinds

<!-- INHERITED: the 4-column FORMAT. LOCALIZED: the rows. The 3 bold rows are domain-originated
     (F3(c): lexical AND owner-route new vs every cav2 D49 row); each carries a default-deny cell. -->

| Kind | Counts as | Owner route | Blocked use |
| --- | --- | --- | --- |
| Primary source | What the spec/domain says about itself: the DFDS feature pack + normative research `DEFINITIONS.md`. | The feature pack + research-definitions route (AUTHORITY-MAP rules 1,4). | Treating a reviewer's reading (local synthesis) as the spec's own declaration. |
| **Validation governance** ⟵ *domain-originated (RATIFIED — owner 2026-06-29; L1 integrity receipt; external L2 pending)* | Authority over **build-time fidelity**: which obligations a typed spec must derive into and what counts as pass/fail. A function mapping a typed spec → its required, deterministically-derived obligations — *neither a definition nor a (cav2) gate*. | **`validation-governance`** *(owns the derive/lint/audit validation surface; NOT `constitution-governance`, NOT cav2's `gate`/SMT meta-validation)*. | **Default-deny:** may NOT declare runtime conformance, waive an obligation it binds, or treat a passing derived test as correctness (passing is necessary, not sufficient). |
| **Layering governance** ⟵ *domain-originated (RATIFIED — owner 2026-06-29; L1 integrity receipt; external L2 pending)* | Authority over **structural fidelity**: each concept's architectural layer + the layer-law / Edge-Law **admissibility** of dependencies (a forbidden edge is *unconstructible*, not merely flagged). | **`layering-governance`** *(owns the layer-law + Edge-Law admissibility; a new governance function cav2 has no row for)*. | **Default-deny:** may NOT approve a cross-layer edge the law forbids, cross the adapter line, or treat a layer *assignment* as a dependency-law *verdict*. |
| **Drift governance** ⟵ *domain-originated (RATIFIED — owner 2026-06-29; L1 integrity receipt; external L2 pending)* | Authority over **temporal fidelity / convergence**: across the 5 drift surfaces (semantic / contract / runtime / governance / coordination), whether divergence is being reduced **with evidence**. | **`drift-governance`** *(owns the drift/convergence ledger; new route; Saturn is its actuator, not its definition)*. | **Default-deny:** may NOT write a node's promotion-status (write-authority proviso), declare convergence from a single signal, or be conflated with Saturn (the control loop). |
| Related evidence | Other spec/methodology corpora; **v1 `implementation/domainspec/` and cav2 as harvested precedent**. | Relevant evidence route. | Treating analogy / harvested precedent as proof or as authority. |
| Local synthesis | A repo-authored reading or hypothesis. | DomainSpec v2 tower / lane owner review. | Becoming policy by proximity; standing in for a governance ruling. |
| Candidate obligation | A proposed obligation, layer-rule, or convergence-criterion that should hold. | Closure plan + validation (witness on a real feature) route. | Becoming a bound rule before witness and owner ratification. |
| Workflow witness | A concrete feature/scenario that can test a candidate. | Evidence harness / validation route. | Being treated as general proof from one example. |
| External policy / implementation authority | The implementation contract, deploy tooling, and org policy this repo does NOT own. | External owner route (impl + platform). | This repo proposes; the external owner decides. |

### Methods catalogue (each governance → the already-built methods that exercise it)

<!-- LOCALIZED. "Each already-created capability is a method to do a governance" — cited to
     IMPORT-MANIFEST.md (the REFORMULATE rows). Methods are instruments OF a governance, not kinds. -->

- **Validation governance** → engine `derive` + `lint` (`impl/test-derivation-engine`), `TEST-PIPELINE.md` (the derived-obligation rules the engine runs), `generate-tests`, `audit-alignment`, `tools/validate-*.ts`.
- **Layering governance** → `audit-layering`, `ADLC-ALIGNMENT.md`, the `TAXONOMY.md` layer-membership + layer-law, the `RELATIONSHIPS.md` Edge-Law / forbidden-edge guard, `ARCHITECTURE.md`.
- **Drift governance** → `DRIFT-CONVERGENCE.md` (the 5 surfaces + convergence criteria), `tag-code` + `compare-code-tag-drift.ts`, `sync-registry`, `OBSERVABILITY.md` (runtime drift), `GOVERNANCE-SIGNALS`, `TUNING-LOOP.md`; **Saturn** is the actuator that acts on the signals (not the authority over them).

> **D49 owner-gate.** The three bold rows were **proposed** by the mint and are now **RATIFIED** by the
> domainspec-v2 owner (2026-06-29; see `decisions/2026-06-29-ratify-governance-kinds.md`). A
> [2026-07-12 L1 integrity receipt](attestations/2026-07-12-governance-kinds-l1/RESULT.md) binds the
> mint proposal to that owner-ratification record and passes exact/content-tampered verification.
> It does not authenticate an external actor; the L2 cryptographic signature remains pending. They
> are this repo's OWN domain-local kinds table —
> **not** a change to cav2's closed D49 enumeration. Seeded from cav2's table FORMAT, owner-authored thereafter.

## Governance Chain (recursive — CAV2-D30 bounded recursive self-application)

> **Build-from-owned, NOT a discovery.** This is the *application* of owned mathematics — μF/νF
> (initial-algebra / final-coalgebra) duality (Hagino 1987; Jacobs 2016; Turi-Rutten 1998),
> catamorphism-as-fold (Meijer-Fokkinga-Paterson 1991) — to the governance triad, instantiating
> **CAV2-D30** (bounded recursive self-application), **D17** (reflection tower), **D29** (axis
> orthogonality). D30 owns the *process-discipline*; the schema below is the application, not D30
> restated. Resolved by dispatch `2026-06-29-recursive-governance-model`
> ([findings](../research/2026-06-29-recursive-governance-model/findings.md)).

The three governances form a recursive **what / how / when** chain over the spec↔reality relation:

- **layering = the LAW (what)** — the admissible typed structure (edge-law + layer-direction);
- **validation = the CHECK (how)** — confirms a typed spec/impl conforms to the law;
- **drift = the TREND (when)** — whether conformance holds over time.

Chain (an explicit typed coupling): `layering (law) → validation (checks the law) → drift
(aggregates checks over time)`, with **Saturn** as the return edge (drift → correction → law/spec) —
a chain that closes into a loop, not a pure pipeline.

### The recursive schema (one node, applied at every level)

```text
GovernanceNode = {
  law:   Norm,                                    -- what
  check: AtomicLeaf | Governed(GovernanceNode),   -- how   (μF: recurses; base = AtomicLeaf)
  trend: Stream<CheckResult>,                     -- when  (νF: coinductive observation dual)
  sub:   GovernanceNode[]                         -- the recursion
}
```

- **`law`/`check` = μF** (initial algebra, inductive). Bounded **decidability-rooted**: the base case
  is a one-step decidable leaf (`classifyFormal`/δ, `sub=[]`). **Witnessed at depth 1**; depth-2 is
  *asserted, not witnessed* (residue R-leaf-inhabitation).
- **`trend`/drift = νF** (final coalgebra, coinductive observation stream). Its bound is
  guardedness/productivity — **a design commitment, NOT a present-tense fact**: the engine has no
  `Stream<CheckResult>` type or guardedness check yet (residue R-trend-type). Do not claim it is
  statically checkable today. (This is why edge-law is the layering *law*, validated by a method, not
  a drift concern — the μF/νF split, not a broken triad.)
- **Model A (distributed norms)** follows as a **corollary of D30's authority-boundary clause** (a
  central law-node would collapse the functor's recursive position) — not a top-level discovery.

### Net-new vs owned (claim ≤ proof)

- **OWNED (cite, don't claim):** μF/νF duality + catamorphism + guardedness-as-νF-bound + Beer VSM +
  CAV2-D30/D17/D29.
- **NET-NEW (exactly three, at correct altitude):** (a) *applying* μF/νF to the law/check/trend triad
  (application, not theory); (b) the decidable-leaf base case engine-witnessed via `classifyFormal`/δ
  (depth-1 only); (c) the `trend`-type gap (engineering residue).
- **Residue (owners):** R-leaf-inhabitation (depth-2 leaf) → validation/drift governance + experiment
  lane (survivable); R-trend-type (`Stream<CheckResult>` + guardedness absent) → engine lane (fatal to
  the νF *phrasing*, not the architecture).

## Source Movement

<!-- INHERITED: the no-automatic-arrow pipeline. LOCALIZED: the node labels. -->

```text
spec evidence (DFDS feature pack + research definitions)
  -> source record (captured, dated, kind-labeled)
  -> typed spec node (TAXONOMY concept) + its Formal cell
  -> candidate obligation / layer-rule / convergence-criterion
  -> validation request (does the derived check fire and pass on a witness?)
  -> external owner decision (impl conforms / release / promote into the contract)
```

No arrow is automatic. A candidate can be blocked, demoted, split, or sent back to spec work
(e.g. an unparseable Formal cell re-routes to `coverage_gap`, never a guessed obligation).

## Non-Collapse Rules

<!-- INHERITED: the "X is not Y" structure. LOCALIZED: DomainSpec's real conflations (grounded in
     DRIFT-CONVERGENCE.md + the free/moat resolution). Last rule = the Obs-B precedent rule. -->

1. A **passing derived test is not runtime correctness.** (Build-time fidelity is necessary, not sufficient — runtime conformance is a separate surface + an external decision.)
2. A **drift signal is not a correction**, and **detecting drift is not converging.** (Convergence is an evidence-backed trend, not one passing check.)
3. **Saturn (the control loop) is not drift (the signal).** (The actuator that acts on drift is not the authority that defines it.)
4. A **layer assignment is not a dependency-law verdict**, and a **misplacement is not automatically a violation** (severity is ruled, not assumed).
5. **Expected values come from the spec, never from running the implementation.** (No circular self-validation.)
6. The **deterministic engine's results are free/citable; its `src/rules` algorithm is withheld** — demonstration is not disclosure (the open-core boundary; the algorithm is an optimization edge, not the moat wall).
N. **Harvested external method precedent (DomainSpec v1, CyberAlchemy v2) supports domainspec-v2
   credibility — it is NOT final domainspec-v2 correctness, and holds NO authority over its
   decisions.** *(Obs-B non-collapse rule — forbids the precedent's leak at the rule level.)*

## Gate Vocabulary

<!-- INHERITED verbatim in shape. -->

- `pass`: evidence, source kind, owner route, and validation surface are adequate for the next move.
- `flag`: work may continue with a named risk and follow-up.
- `block`: stop until a source, authority, witness, or boundary gap closes.
- `defer`: not rejected, but the route or timing is not ready.
