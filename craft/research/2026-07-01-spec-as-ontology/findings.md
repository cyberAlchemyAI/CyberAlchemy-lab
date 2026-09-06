---
node_type: research-findings
role: synthesizer (final, post-skeptic revision)
question: Should DomainSpec v2 treat its spec surface as a SYSTEM ONTOLOGY, and how does spec-as-ontology reshape the Batch-1 reformulation?
inputs: [A-ontology-substrate.md, B-derivation-substrate.md, skeptic.md]
build_from: research/spec-ontology-unification/SEED.md (2026-06-11, status: seed, tower NOT executed)
created: 2026-07-01
discipline: claim ≤ proof; cite by path; engine algorithm never asserted; residue = union of inputs
---

# Findings — Spec-as-ontology is a bounded, owned HYPOTHESIS; it changes the reformulation ~15%, all authoring-plane

## 1. Verdict

**Does spec-as-ontology change the Batch-1 reformulation? YES — bounded and additive (~15%),
never structural, and only under an already-owned promotion boundary.** The re-homing map
stays; no doc changes owner; no fourth governance is added. What changes is *authoring-plane*
support layered on top of the crisp contract, and even that is gated.

Critically: spec-as-ontology is **not a fresh finding** — it is an owned, still-unexecuted
**hypothesis**. `research/spec-ontology-unification/SEED.md` (2026-06-11, `Status: seed —
tower not yet executed`) already OWNS this exact question and *bounds* it. Explorer A's "the
spec **is** an ontology" must therefore be demoted from settled ambient fact to "SEED's Lane-Z
hypothesis, not yet witnessed." The two-plane boundary below is a **refinement of SEED**, not a
discovery.

## 2. Build-from-owned: SEED.md, and Lane Z vs Lane A weighed

SEED frames spec and ontology as "the **same object in two forms**" — a feature is a *tree* of
nodes, across features a *graph*; a **node → code pattern**, an **edge → composition rule**
(`SEED.md:14-27`) — with the explicit *purpose* of making implementation agents ephemeral,
bounded, cheaper, less drift-prone (`SEED.md:9-12,29-30`). It defines two lanes:

- **Lane Z (full unification, spec == ontology):** build the node→pattern / edge→composition
  model, attack where node↔pattern breaks 1:1 (`SEED.md:43-47`). This is A's position.
- **Lane A (keep spec + ontology SEPARATE, generated bidirectional mapping — codegen + drift
  check, "the v1 direction"; or a typed code-tag contract; or a queryable pattern catalog)
  (`SEED.md:48-53`).** **Lane A aligns with explorer B's derivation-centric view**: the spec
  stays the crisp derivation source, and any ontology structure is a *generated, separate,
  drift-checked* projection — never fused into the source.

**Weighing.** Neither lane is decidable here; SEED's own toy is unrun. But the two-plane
boundary (§3) is the honest *current* stance: it grants Lane A on the contract plane (the
engine-facing spec stays a separate crisp source, B/E-model) and grants Lane Z's intuition
*only* on the authoring plane as an unratified read-lens. This does not pre-empt SEED's
decision — Lane Z-vs-A stays open for the tower — it just refuses to fuse spec and ontology
before the toy proves agent gains, exactly as SEED's **Non-goals** demand (`SEED.md:60-64`).

**Promotion boundary (governs everything below):** "Local research only. No change to spec
schema, code-pattern catalog, agent constitutions, or runtime until a later approved
`task-session`" (`SEED.md:56-58`). Every recommendation in §5 is authoring-plane and
respects this — it proposes no spec-schema mutation.

## 3. The two-plane boundary rule (SURVIVES skeptic; refines SEED)

> **Ontology framing wins on the spec-AUTHORING plane; derivation stays primary on the
> engine-facing CONTRACT plane. Authority flows contract → authoring, never the reverse.**

- **CONTRACT plane (derivation-primary, = Lane A / B).** The *promoted, crisp* set the engine
  parses: 25 typed nodes + 29 typed edges + feature packs, total and machine-consumed
  (`AUTHORITY-MODEL.md:42-47`; `DESIGN.md:49-50`). What *bites* is `derive`/`lint`/`validate-*`
  (B-E5). Confidence, premise, and branch labels are **forbidden here** — softening a total
  input is the failure mode both A's own objection and B's E3 name.
- **AUTHORING plane (ontology-legitimate, = SEED Lane-Z intuition, held as hypothesis).**
  Whether a *newly proposed* concept/edge is ratified INTO the crisp set — an existing gate:
  `candidate` definitions + witness + owner decision (`AUTHORITY-MODEL.md:62,138-144`;
  `DESIGN.md:73`). This mirrors the ratified μF (crisp law) / νF (evolving observation) split
  (`AUTHORITY-MODEL.md:110-118`).

The seam holds because ontology-vault **by contract cannot cross it**: its outputs "are not ...
source authority, spec mutations, runtime conformance verdicts, or canonical source edits"
(`ontology-vault/SKILL.md:66-71`). B reads this as "cannot be spine"; A can read it as "safe as
an authoring lens." Both hold — that disclaimer is the *guarantee*, not a weakness.

## 4. Concrete Batch-1 impact (per doc/decision, with owners)

**The `DESIGN.md` §1 re-homing map stays; zero docs change owner** (skeptic KEEP; verified
`DESIGN.md:37-44`):

- **TAXONOMY (R2) / RELATIONSHIPS (R3):** owner stays **layering-governance**; framing stays
  "alphabet + edge-law" (`DESIGN.md:39-40`). Layering-governance already owns the RELATIONSHIPS
  Edge-Law (`AUTHORITY-MODEL.md:72`).
- **TEST-PIPELINE (R4):** unchanged — derivation contract, δ-rules private (`DESIGN.md:42`;
  Non-Collapse Rule 6). Never "the ontology's inference rules." (B wins flat.)
- **AXIOMS (R1):** A1/A2 stay mapped to validation/layering (`DESIGN.md:41`). A's "A1 = branch
  axis" is a *read-lens*, recorded as intuition, not law.
- **CONSTITUTION (R6a):** **no fourth "ontology governance"** — would violate the three-
  governance model (`AUTHORITY-MODEL.md:57-59`; skeptic KEEP).
- **§4 decisions D1–D4:** unchanged as written; the four dependent decisions in §6 bound them.

## 5. Recommendation for the reformulation DESIGN (all authoring-plane, within SEED's boundary)

1. **Cite SEED in DESIGN.** Add a note that TAXONOMY/RELATIONSHIPS-as-graph is SEED's owned
   Lane-Z hypothesis under a promotion boundary — not settled — so no §1 owner may be re-homed
   to "ontology" and no spec-schema field may be added by this reformulation.
2. **Ontology-view doc — route the owner or demote (CR-2).** If added, its authority is routed,
   not orphaned: **terms → `definitions-governance` (IDs), edges → `layering-governance` (the
   Edge-Law it already owns).** OTHERWISE demote it to a **generated, non-authoritative
   read-projection** (B §3) produced by `ontology-view`/`paired-views` over the crisp docs,
   needing no governance owner. Note: `ontology-view` is self-marked **seed / not promoted**
   (`ontology-view/SKILL.md:<status>`) — so this is a *seed-sigil* adoption, not a mature one.
3. **Confidence / premise / branch tags — authoring-plane-only, no verified consumer (CR-3).**
   A repo search finds **zero** engine/tool/spec consumers of confidence/premise/ontology-branch
   fields (the only `branch` hits in `test-derivation-engine/src` are domain-logic *ternary
   branch literals*, e.g. `emit/tests.ts:143`, not business/system/bridge labels). So: these
   tags MAY be captured by `ontology-vault --runtime inline` outputs (which are "not ... spec
   mutations", `ontology-vault/SKILL.md:66-71`) but **MUST NOT be written into the crisp
   TAXONOMY/RELATIONSHIPS docs the engine parses** until an owner (validation-governance, which
   owns what the engine consumes) ratifies a reader. UI-11 may then be described as
   "system-branch, low commitment-confidence" — but only as authoring metadata, never as a
   spec-schema field.
4. **Adopt ontology-vault — YES, bounded; NOT as spine.** As an authoring-plane lens on a
   runtime profile (`ontology-vault/SKILL.md:49-71`). It is owned (build-from-owned) and its own
   contract fences it to the authoring plane, structurally disarming the spine-capture failure
   mode. NB (CR-4): the "names the gate more precisely" good is *designed-for*, resting on
   **unrun** sigils (A-R2/R4) — assert capability as design, not delivered fact.

## 6. Residue + open owner decisions

**Residue (union of inputs; CR-5):**
- Engine treated as black-box; δ-rule coverage per type unverified (B-R1). Does not affect the
  boundary (drawn at the interface, not internals).
- Only the `features/sample` fixture was read, not real multi-aspect feature packs — the "aspect
  files = ontology fragments" pillar is unverified (A-R1).
- ontology-vault runtime-profile binding to the spec is unexercised (A-R2); ontology-vault /
  ontology-harness / paired-views are asserted from SKILL/spell text, not execution-verified
  (A-R4); ontology-view is seed-status (`ontology-view/SKILL.md:<status>`).
- Zero consumers of confidence/premise/branch fields is *verified-absent today* (§5.3 search),
  not proof none is planned (B-R2).

**Open owner decisions (DomainSpec v2 tower owner — SEED's `Owner:` line + this node):**
- **D-syn-1 (bounds `DESIGN.md:120` D2).** UI-11 is the softest seam: if UI is layering-only
  (not engine-derived), the authoring-plane overlay is *more* attractive there (B-R3).
- **D-syn-2 (bounds D1:116 / D4:127).** Does drift-governance absorb ontology-vault drift edges
  (`drifts_from`) or keep them overlay-only? Recommend overlay-only until a runnable consumer
  exists (B-R4).
- **D-syn-3.** Lane Z vs Lane A — deferred to the SEED tower, whose toy is unrun. This node does
  NOT decide it; the two-plane boundary is a safe interim that pre-empts neither.
- **D-syn-4.** Is the ontology-view doc a Batch-1 addition or a later authoring-support artifact?
  Changes no §1 owner either way; timing only. Constrained by SEED's promotion boundary
  (`SEED.md:56-58`).
