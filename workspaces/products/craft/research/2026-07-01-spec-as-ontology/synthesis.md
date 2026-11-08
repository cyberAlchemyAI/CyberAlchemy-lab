---
node_type: research-synthesis
role: synthesizer (writer)
question: Should DomainSpec v2 treat its spec surface as a SYSTEM ONTOLOGY, and how does spec-as-ontology reshape the Batch-1 reformulation?
inputs: [A-ontology-substrate.md, B-derivation-substrate.md]
created: 2026-07-01
discipline: claim ≤ proof; cite by path; engine algorithm never asserted; residue marked
---

# Synthesis — Bounded BOTH/AND on a two-plane seam

Both explorers cite accurately, and both are right about *different planes* of the same
files. A proves the spec **reads as** a knowledge graph — the repo says so verbatim
(`impl/spec/RELATIONSHIPS.md:3`, `TAXONOMY.md:3`). B proves that same graph **bites as**
a compiler alphabet — the engine parses it into `G` and derives obligations
(`impl/test-derivation-engine/README.md` per B-E1), and every ratified governance binds a
*runnable method*, none named "ontology" (`authority/AUTHORITY-MODEL.md:66-73`). The
disagreement is not about the facts; it is about which plane owns authority.

## 1. The boundary (the crisp rule)

> **Ontology framing wins on the spec-AUTHORING plane; derivation stays primary on the
> engine-facing CONTRACT plane. Authority flows contract → authoring, never the reverse.**

- **CONTRACT plane (derivation-primary).** The *promoted, crisp* set the engine consumes:
  25 typed nodes + 29 typed edges + feature packs, total and machine-consumed
  (`AUTHORITY-MODEL.md:42-47`, Core Rule; `DESIGN.md:49-50`). What *bites* here is
  `derive`/`lint`/`validate-*` (B-E5). Confidence, premises, roles, and branch labels are
  **forbidden** on this plane — nothing downstream reads them, and softening a total input
  into "confidence 0.6 that Entity is an Entity" is the failure mode both A's objection and
  B's E3 name. B owns this plane outright.
- **AUTHORING plane (ontology-legitimate).** Whether a *newly proposed* concept/edge is
  ratified INTO the crisp set. This gate already exists — `candidate` definitions +
  witness + owner decision (`AUTHORITY-MODEL.md:62,138-144`; `DESIGN.md:73`). A's
  contribution is that ontology-vault *names this existing gate more precisely* (evidence-
  vs-commitment confidence, premise ledger) without adding enforcement the engine must
  honor. This is exactly the μF (crisp law) / νF (evolving observation) split the
  AUTHORITY-MODEL already ratified (`AUTHORITY-MODEL.md:110-118`).

The seam is real because ontology-vault **by contract cannot cross it**: its outputs
"are not ... source authority, spec mutations, runtime conformance verdicts, or canonical
source edits" (`.claude/skills/ontology-vault/SKILL.md:66-71`). That disclaimer is not a
weakness A must overcome — it is the *guarantee* that lets ontology framing sit on the
authoring plane without threatening the contract. B reads it as "cannot be spine"; A can
read it as "safe to adopt as authoring lens." Both readings hold because the boundary holds.

## 2. Concrete Batch-1 impact per affected doc

Verdict: **the re-homing map (`DESIGN.md` §1) stays; ownership of zero doc changes.** B
wins §1. What A wins is *added authoring-plane machinery*, not re-homing.

- **TAXONOMY (R2) / RELATIONSHIPS (R3):** owner stays **layering**; framing stays
  "alphabet + edge-law" (`DESIGN.md:39-40`, B's point). ADD: a non-normative
  ontology read-view note is *permitted* (the graph is self-declared, `RELATIONSHIPS.md:3`),
  but it re-homes nothing.
- **TEST-PIPELINE (R4):** unchanged, derivation contract, δ-rules private
  (`DESIGN.md:42`; Non-Collapse Rule 6). Never "the ontology's inference rules." B wins flat.
- **AXIOMS (R1):** A1/A2 stay mapped to validation/layering (`DESIGN.md:41,80-81`). A's
  "A1 = branch axis" is a *true read-lens*, not a re-home — record it as intuition, not law.
- **CONSTITUTION (R6a):** **no fourth "ontology governance" owner** — that would violate the
  ratified three-governance model (`AUTHORITY-MODEL.md:57-59`; B-E2). Every v1 C-rule maps
  to validation/layering/drift or DROP, as designed.

## 3. Adopt ontology-vault? — YES, bounded; NOT as spine

Adopt it as an **authoring-plane lens on a runtime profile** (`SKILL.md:49-71`,
`--runtime inline`), NOT as the Batch-1 spine. Rationale:

- It is *owned* and *build-from-owned* (A) — no net-new machinery.
- Its own contract fences it to the authoring plane (`SKILL.md:66-71`) — so adopting it
  cannot demote a hard obligation to a soft claim (B's fatal objection is structurally
  disarmed, not merely argued away).
- It earns two authoring-plane goods the current design lacks: (i) **evidence-vs-commitment
  confidence** for a proposed-but-not-yet-derived concept (UI-11 becomes *system-branch, low
  commitment-confidence* instead of binary kept/dropped — A §3); (ii) a **premise ledger**
  for the branch axioms.

**Ontology-view doc:** ADD one, but **as authoring documentation, not a governance owner** —
a single canonical home for `term:<concept>` / `relation:<a>--<b>` (`ontology-view/SKILL.md`).
It is the definitions-governance surface given graph shape; it does not sit in the §1
re-homing map and does not consume engine authority.

## 4. Open decisions for the owner

- **D-syn-1 (bounds D2, DESIGN.md:120).** UI-11 is the softest seam: if UI is
  layering-only (not engine-derived), the ontology overlay is *more* attractive there
  (B-R3). Owner: adopt confidence-tagging for UI concepts specifically?
- **D-syn-2 (bounds D1, DESIGN.md:116; D4, :127).** Does drift governance *absorb*
  ontology-vault drift edges (`drifts_from`), or keep them overlay-only? If absorbed, the
  contract/authoring boundary needs a redraw (B-R4). Recommend: overlay-only until a
  runnable consumer exists.
- **D-syn-3.** Is the ontology-view doc a Batch-1 addition or a Batch-2 authoring-support
  artifact? It changes no §1 owner either way; timing is the only question.
- **D-syn-4 (residue).** No compiler/validator is confirmed to read confidence/premise/role
  fields (A-R3, B-R2). Keep those fields strictly authoring-plane until an owner ratifies a
  consumer — the boundary rule (§1) makes this safe by default, not by inspection.

## Residue

Engine treated as black-box throughout; δ-rule coverage per type unverified (B-R1) — does
not affect the boundary, which is drawn at the contract *interface*, not its internals.
