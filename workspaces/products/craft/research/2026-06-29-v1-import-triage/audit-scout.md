---
node_type: research
subject: DomainSpec v1 → v2 import triage — AUDIT area
scout: van Lamsweerde (goal-oriented spec↔impl conformance)
dispatch_id: 2026-06-29-domainspec-v1-import-triage
area: audit
date: 2026-06-29
status: complete
---

# Audit Scout — DomainSpec v1 → v2 Import Triage

## Role & turf

van Lamsweerde, AUDIT scout. Home turf: goal-oriented requirements, specification
conformance, obligation tracing, and the gap between what a spec says and what an
implementation does. Verdict discipline: claim ≤ proof; found owner = REFORMULATE, never DROP.

## Sources read (read-only)

1. `projects/domainspec-v2/research/2026-06-29-v1-import-triage/SEED.md`
2. `implementation/domainspec/.claude/skills/domainspec-audit-alignment/SKILL.md`
3. `domainspec-lean-formalization/VLACHOPULOS-2026-AUDIT.md`
4. `domainspec-lean-formalization/SMITHE-2024-AUDIT.md`
5. `projects/domainspec-v2/research/2026-06-29-correctness-ownership-sweep/findings.md`
   (consulted to avoid re-deriving owned-vs-net-new already settled there)

---

## Capability inventory

### CAP-A1 — Alignment classify+remediate (domainspec-audit-alignment skill)

**What it does (cite):** The skill reads `domainspec/CHANGELOG.md` and feature docs,
inspects implementation evidence (code, tests, planning summaries, verification files),
classifies each spec item as `compliant | partial | missing | extra`, and emits a
prioritised remediation list into `docs/features/{feature}/ALIGNMENT-REPORT.md`
(SKILL.md §process steps 1–5).

**What it does NOT do (from reading):** It does not produce a machine-checkable
conformance predicate — output is a human-authored markdown report. The classification
is structural (file-presence + manual inspection), not computed from a formal relation.
No claim≤proof gate; the "extra" category catches overreach but does not block it.

**Candidate verdict:** IMPORT

**Why:** This is a load-bearing audit workflow that directly serves v2's mandate of
"govern + enforce Ontology A on evidence." The four-class schema (compliant / partial /
missing / extra) maps cleanly onto the correctness-ownership-sweep's
owned-vs-net-new split (findings.md §Verdict matrix). The remediation output wires
into the v2 enforcement loop. No collision with any net-new surface — it is exactly
the kind of spec↔impl gap-tracking that v2 needs at the feature level.

**Leverage (where it lands in v2):** Feature-level conformance gate. Import as-is with
one wiring addition: route the "missing" and "extra" rows to v2's claim-register so
the auto-computed claim≤proof verdict gate (correctness-sweep B6, currently net-new)
can consume them. The skill itself does not need to change; the consumer changes.

**Caveat (honest register):** The skill is designed-not-wired to a machine gate
(findings.md B6/B7 = net-new). IMPORT the skill as-is; the gate is a separate build
surface. Do not claim the import delivers the gate.

---

### CAP-A2 — Lean audit method (literature collision + ADJACENT verdict machinery)

**What it does (cite):** The two audit files (VLACHOPULOS-2026-AUDIT.md and
SMITHE-2024-AUDIT.md) embody a repeatable audit discipline: read the external paper's
core constructions, perform a side-by-side structural comparison on seven independent
axes, issue a collision verdict (PREEMPTS / PARTIAL / ADJACENT / CLEAR), prescribe
safe-to-claim / needs-reframing / positive-borrow split, and provide exact citation
formats and do-not-cite-as guards.

**Internal structure of the method (witnessed):**
- Seven-axis structural comparison table (VLACHOPULOS §Side-by-side)
- Correction-note / demote protocol (both files carry a 2026-05-22 correction
  that revised entropy labelling without reversing the verdict — the method survives
  partial proof-updates)
- Positive-borrow category (borrow Eilenberg–Moore reconstruction without claiming
  preemption is absent)
- Subset rule enforced: ADJACENT verdict in both cases; neither inflated to CLEAR

**What it does NOT do:** It is not a formal checker; verdicts are expert judgements
backed by detailed structural argument, not computed proofs. No Lean formalisation of
the collision predicate itself.

**Candidate verdict:** REFORMULATE

**Why:** This is build-from-owned. The method is a genuinely owned audit discipline
(two fully executed examples, correction-note discipline, do-not-cite-as guards).
However, these audit files are in `domainspec-lean-formalization/` and concern the
*physics/math framework*, not the DomainSpec language (Ontology A). The method is the
owner; re-authoring it for the v2 context means: (a) porting the seven-axis comparison
template as an audit harness for v2 spec↔literature conformance, (b) replacing the
content (physics adjunctions) with v2 concerns (ontology operators, governance
obligations), and (c) keeping the correction-note / demote protocol and subset-rule
enforcement. A direct re-import of the physics-domain audit files would be a layer
violation (out-of-context content in the wrong register).

**Leverage:** Re-author as a reusable `collision-audit.md` harness in v2. The side-by-side
table + verdict taxonomy + positive-borrow category are the importable primitives.

---

### CAP-A3 — Conformance obligations (spec→impl claim≤proof tracing)

**What it does (cite):** `findings.md` (correctness-ownership-sweep) establishes which
conformance obligations are witnessed vs. designed-not-wired vs. aspirational:
- **Witnessed at honest register:** honest-labeling discipline (five-label vocab B1),
  P8 necessary-not-sufficient fence (B2), definition cards with misuse warnings (B4),
  DCB validator-vs-freshness split (B5), σ-edge graph + edge-signature validation (A1/A5),
  content-hash freshness wiring (A3).
- **Designed-not-wired (net-new build surface):** auto-computed claim≤proof verdict gate
  (B6/B7), spec→test engine + AcceptSpecCodeCorrectnessClaim (A6/A7), contract/schema
  separation predicate (B9).
- **Aspirational/prose-only:** M6 grading beyond detector, behavioral saga witness (A2 two
  assertions tautological), formal model-check (A8).

**What this is as a v2 import candidate:** Not a single skill but a *triage map* — it tells
v2 exactly which conformance obligations it already owns and which are net-new build surfaces.
This is the "found owner" that the SEED says to treat as REFORMULATE, not DROP.

**Candidate verdict:** IMPORT (the witnessed/owned slice) + REFORMULATE (the
designed-not-wired slice — re-author as v2 build tasks, not as imports)

**Why:** The owned slice (B1/B2/B4/B5/A1/A5/A3-hash) is genuinely importable as the
conformance-obligation baseline: it gives v2 a claimed-and-witnessed vocabulary for labeling
spec items. The net-new slice (B6/B7/B9/A6/A7) cannot be imported because no artifact
exists yet — but the triage map itself is owned and should not be re-derived.

**Leverage:** Use findings.md as the conformance-obligation baseline for v2's audit loop.
When v2's audit-alignment skill classifies an item as "missing," it should first check
whether the finding is in the owned slice (→ wire it) or the net-new slice (→ build it).
This avoids the two failure modes: claiming the owned things are net-new (inflation) and
claiming the net-new things are owned (overshoot).

---

## Cross-cutting guards (carry on every row)

- **Adapter line:** CAP-A1's output (ALIGNMENT-REPORT.md) must not import app-runtime
  artifacts. The skill reads implementation code but writes to docs — that is the safe side
  of the adapter line.
- **Write-authority proviso:** none of these capabilities writes promotion-status. CAP-A1
  writes a report; a human or a gate (B6, net-new) decides promotion. Safe.
- **Free/moat boundary:** audit capabilities are governance-layer, not engine. They are
  freely describable. No moat concern.
- **Two-ontologies:** CAP-A2's Lean audit files concern Ontology B (math/physics framework).
  v2 governs Ontology A (DomainSpec language). The method ports; the content does not.

---

## Verdict table

| ID | Capability | Source | Verdict | Rationale (one line) |
|---|---|---|---|---|
| CAP-A1 | Alignment classify+remediate | `domainspec-audit-alignment/SKILL.md` | **IMPORT** | Direct v2 mandate fit; four-class schema owned + witnessed; wire output to B6 gate (net-new, separate) |
| CAP-A2 | Lean audit collision method | `VLACHOPULOS-2026-AUDIT.md`, `SMITHE-2024-AUDIT.md` | **REFORMULATE** | Method owned (two full examples, correction-note discipline); content is physics-domain, not Ontology A; re-author as v2 collision-audit harness |
| CAP-A3 | Conformance obligation triage (owned slice) | `correctness-ownership-sweep/findings.md` B1/B2/B4/B5/A1/A5/A3 | **IMPORT** | Witnessed at honest register; use as v2 conformance-obligation baseline, not re-derived |
| CAP-A4 | Conformance obligation triage (net-new slice) | `findings.md` B6/B7/B9/A6/A7 | **REFORMULATE** | Found owner = the triage map; re-author as v2 build tasks; do not claim as owned artifacts |

---

## What this scout does NOT claim

- That CAP-A1 delivers a machine-computed gate (it does not; B6 is net-new).
- That the Lean audit files (CAP-A2) are importable as v2 spec content (they are physics-domain).
- That the net-new conformance obligations (CAP-A4) are owned (they are not; the triage map is).
- That any of these verdicts resolves the free/moat contradiction in `test-engine/HANDOFF.md` —
  that is the synthesizer (Spivak)'s job; audit capabilities are governance-layer and do not
  touch the engine.

## Handoff note for synthesizer (Spivak)

The four rows above are ready for `findings.md`. CAP-A1 and CAP-A3(owned) are IMPORT-clean
with no moat concerns. CAP-A2 and CAP-A4 are REFORMULATE with explicit re-author instructions.
The audit area surfaces no DROP candidates — the honest-labeling discipline and the
collision-audit method are both owners that survived scrutiny. The net-new build surface
(B6/B7/B9/A6/A7) is not a gap in this triage — it is correctly labeled as build surface
in the correctness-ownership-sweep and should be imported as such (as tasks, not as artifacts).
