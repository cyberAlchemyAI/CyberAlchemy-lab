---
node_type: research
role: skeptic
area: TWO OFFERS (test-engine free-vs-moat + scout candidates)
agent: "Gödel, Kurt — skeptic"
discipline: claim <= proof; found owner = REFORMULATE, never a kill; default-deny bad imports
date: 2026-06-29
---

# TWO OFFERS — Skeptic Memo

## Job 1 — Resolve the contradiction

### What the contradiction is

`test-engine/HANDOFF.md` (O4) calls the deterministic spec→test engine the **"free wedge" —
public-arcanum eligible**. `ASSIMILATION-TABLE.md` S3 and the inventory entries
(`machine-map-and-moat-synthesis`, `cav2-authority-and-determinism-synthesis`) call the
deterministic engine the **proprietary moat**, explicitly labeling an LLM-mediated test
generator a *downgrade* from it.

### Resolution — three distinct things, not two

The apparent contradiction dissolves once you distinguish three objects:

1. **Test-DERIVATION method** (the rule table + parsing pipeline — what `TEST-PIPELINE.md`
   specifies and what the `test-derivation-engine/` implements): this is the **free wedge**.
   HANDOFF.md is correct on its narrow claim: the *method* — "run deterministic rules over a
   feature's DFDS docs to derive test obligations" — is no-LLM, no-network, and carries no
   moat material. It is publishable into public arcanum. The engine's *algorithm* is proprietary
   per the `engine-algorithm-proprietary` memory note (cite+demonstrate results, never publish
   the algorithm), but the *method* (the what, not the how-exactly) is the publishable wedge.

2. **Attestation + governance-data lever** (the `attest(governance-act) → seal` + `verify`
   pipeline, the L1 MVP built 2026-06-29): this is the **moat**. `machine-map-and-moat-synthesis`
   is definitive: "attestation + governance-data + vertical" is the wall. `attestation-capability-moat-mvp-synthesis`
   confirms L1 is BUILT and marks the mechanism `cite-results-withhold-mechanism`. This is
   internal-only; mechanism never goes to public arcanum.

3. **Lean / formal-proof lever** (the `domainspec-lean-formalization/` AgentPermissionKernel,
   `decidePolicy_sound`): per `machine-map-and-moat-synthesis`, provability is a **conjectural
   amplifier, not the moat** — the framing the original session had *inverted*. It is an optional
   flag on top of the attestation wall, not the wall itself.

### One-line resolution

> The deterministic **test-derivation METHOD is the free wedge** (publishable, no moat
> material); the **attestation + governance-data LEVER is the moat** (L1 built, mechanism
> private); the Lean formal-proof lever is a conjectural amplifier on top, not the wall.

### Where the boundary sits

- Free (publish-ok): the test-derivation method (DFDS-doc → typed rule → obligation-key),
  the doc-schema surface syntax, `validate-*.ts` structural checks.
- Moat (internal): attestation mechanism (`attest.py`, canon rule, hash construction, L2
  scheme), governance-data corpus, vertical integration. Algorithm of the engine (cite
  results, withhold internals).
- Amplifier (conjectural, not moat): Lean/cat-theory formal proof of governance axioms.

HANDOFF.md's O4 is locally correct — it was scoped to the *test engine*, which truly is the
free wedge. ASSIMILATION-TABLE S3's "proprietary moat" label applies to the *engine as a
whole product capability* standing opposite an LLM-mediated generator — i.e., the
no-LLM/no-network construction guarantee is what makes the engine a moat *relative to
grain's `/propagate`*. The two statements are compatible: the method is the free wedge; the
algorithm + the attestation+governance lever together form the moat.

---

## Job 2 — Scout candidates: owner sweep + verdict

The v1 "TWO OFFERS" candidates visible from the SEED + HANDOFF materials are:

| # | Scout candidate | Found owner (cite) | Verdict | Rationale |
|---|----------------|---------------------|---------|-----------|
| T1 | Deterministic spec→test engine (the engine method itself) | `implementation/domainspec/tools/test-derivation-engine/` + `TEST-PIPELINE.md` | **REFORMULATE (BUILD-FROM-OWNED)** | Owner exists and is BUILT (L0 skeleton, pipeline wired). Not a kill. Re-import would duplicate it; wire the existing L0 stubs → SWU-ENG-001/003/005 as the v2 activation path. |
| T2 | LLM-mediated test generator (`domainspec-generate-tests` / `domainspec-test-designer`) | `tools/test-derivation-engine/README.md`: "Replaces the LLM-backed `domainspec-generate-tests` / `domainspec-test-designer` derivation" | **DROP** | Explicitly superseded by the deterministic engine; re-importing it is a downgrade (ASSIMILATION-TABLE S3 discipline). Out-of-layer for v2 moat. |
| T3 | Attestation capability / governance-data lever | `cyberAlchemy-v2/development/attestation-capability/` + `attestation-capability-moat-mvp-synthesis.md` (L1 BUILT) | **REFORMULATE (BUILD-FROM-OWNED)** | Owner exists; L1 MVP is live. v2's job is to activate it in the DomainSpec governance path (`attest(governance-act)` at spec-promotion events), not re-import. Mechanism stays private. |
| T4 | Lean/formal-proof lever (AgentPermissionKernel, `decidePolicy_sound`) | `domainspec-lean-formalization/` (main; sorry=0) per `lean-kernel-location-and-status` memory | **REFORMULATE (BUILD-FROM-OWNED)** | Owned in a separate repo, sorry-free. Conjectural amplifier on the attestation wall. v2 may *cite* it; it must not be assimilated as the moat itself (inverted framing risk). Import path: reference from governance-layer spec, never wholesale re-author. |
| T5 | Obligation-taxonomy as δ-coverage audit checklist (from grain's `/propagate`) | `TEST-PIPELINE.md` derivation tables (transition-row tests, state×event rejection, terminal no-outbound, invariant PBT) | **REFORMULATE (BUILD-FROM-OWNED)** | ASSIMILATION-TABLE S3 explicitly: "take only the obligation-taxonomy as a δ-coverage audit checklist." Owner is `TEST-PIPELINE.md`. Not a separate import; sharpen the existing taxonomy as a coverage-gap checklist for the engine's δ rules. |

### Denied imports (default-deny, no further discussion)

- **LLM test generator (T2):** downgrade from the moat, explicitly superseded.
- **Lean as the moat (T4 reframe):** provability is amplifier, not wall — importing it as the
  moat inverts the machine-map correction and overclaims (claim > proof; Lean→cav2 links zero).
- **Attestation mechanism into public arcanum:** `attestation-capability-moat-mvp-synthesis`
  is `cite-results-withhold-mechanism`. L1 mechanism stays in `attest.py`, private.

---

## Guardrail check

- **claim ≤ proof:** engine L0 is a skeleton (parser + δ rules are typed stubs — README is
  explicit). Do not claim "the engine is built" for v2 activation; claim "L0 pipeline wired,
  stubs present, SWU-ENG-001/003/005 are the remaining units."
- **write-authority proviso:** no modeling surface in v2 should write promotion-status. The
  attestation lever (T3) must be invoked at owner-cleared gates, not auto-applied.
- **adapter line:** test-derivation engine is spec-layer; do not import any grain runtime
  (event store, CQRS append) into the engine path (ASSIMILATION-TABLE S4–S9 discipline).
- **free/moat boundary:** the engine's derivation method is publishable to arcanum; the
  algorithm and the attestation mechanism are not. Keep them in separate surfaces.

---

## Residue

- G1 (from HANDOFF.md, still open): spec→code/test mapping seam overlaps
  `spec-ontology-unification` tower. Resolve before claiming full test-engine coverage.
- G2 (from HANDOFF.md, still open): correctness coupling with `dcb-correctness` — generated
  test read-set invalidation on source-spec change. Must be resolved before "coverage-checkable"
  claim is sound.
- T3 activation path (open): where exactly does `attest(governance-act)` fire in the DomainSpec
  v2 promotion lifecycle? Owner-routed decision before implementation.
