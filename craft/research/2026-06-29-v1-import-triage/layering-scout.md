---
node_type: research
subject: DomainSpec v1 → v2 import triage — layering alignment
dispatch_id: 2026-06-29-domainspec-v1-import-triage
area: layering
role: scout
agent: "Simon, Herbert — SCOUT / LAYERING ALIGNMENT"
discipline: claim <= proof; one verdict per capability; found owner = build-from-owned, never a kill
date: 2026-06-29
---

# Layering Scout Memo — Simon, Herbert

> Maximize importable surface for v2. Area: architecture of complexity / near-decomposability.
> READ-ONLY pass over v1. Sources: `domainspec-audit-layering/SKILL.md`, `ADLC-ALIGNMENT.md`,
> `TAXONOMY.md`. Verdict vocabulary per SEED.md.

---

## Framing — what "layering" means in v1

v1 operates a **four-layer dependency law** (TAXONOMY.md Architecture Mapping Appendix):

- Domain → depends on nothing external
- Application → depends on domain only
- Infrastructure → depends on domain/application contracts
- Interface → depends on application only

The `domainspec-audit-layering` skill enforces the same law at the *feature* level:
business/domain behavior must live in domain layers, not use-case orchestration code.
`ADLC-ALIGNMENT.md` extends this into a seven-layer meta-model (L0–L7) and names all
gaps where enforcement is still manual or absent.

The four distinct layering capabilities I catalogued, and how they fare under
build-from-owned scrutiny, follow.

---

## Candidate rows

### C1 — Layer drift detection (misplaced domain logic in use-cases)

**What it does (cite):** `domainspec-audit-layering/SKILL.md` §process step 3:
"Identify misplaced domain behavior in use-cases." It reads `SPEC.md`, the
`domain/` tree, and `use-cases/` to surface domain logic that leaked upward. Output is
a `LAYERING-ALIGNMENT-REPORT.md` with CRITICAL/HIGH/MEDIUM/LOW classification and
explicit file targets.

**Candidate verdict:** IMPORT

**Why:** v2's core mission is "govern + enforce Ontology A on evidence." Layer drift is
exactly a violation of Ontology A's layer law (domain concepts must stay in the domain
layer). This skill's detection logic — concept-to-code map, misplacement classification,
priority triage — is directly load-bearing for v2's enforcement surface. The
classification rubric (critical→high→medium→low) and the explicit file-target format
are actionable for automated enforcement; there is no owned v2 equivalent yet.

**Leverage:** HIGH — every governed feature needs drift detection; the rubric is
reusable across all domain classes.

**Guardrails on import:** Skill references `CHANGELOG.md` for framework constraints;
v2 must re-anchor this to v2's own constitution/axioms chain (ADLC-ALIGNMENT.md G13/G16)
rather than v1's changelog. The write-authority proviso holds: the skill produces a
*report*, not a promotion-status mutation.

---

### C2 — Dependency-ordered migration plan

**What it does (cite):** `domainspec-audit-layering/SKILL.md` §process step 5:
"Produce dependency-ordered migration tasks with explicit file targets." Outputs
`LAYERING-ALIGNMENT-PLAN.md`. The ordering respects transitive dependencies so that
migrating A before B does not break A.

**Candidate verdict:** IMPORT

**Why:** A drift *detector* without a remediation plan is an audit, not governance.
v2's enforcement loop (the gap ADLC-ALIGNMENT.md calls G4 / L6-enforcement) requires a
plan artifact that can be executed deterministically. The dependency-ordering logic is
a near-decomposability property — the plan is decomposable because it respects the same
layer law used to detect the drift. No owned equivalent exists in v2 yet.

**Leverage:** MEDIUM — needed once per governed feature; most valuable when layer debt
is high at spec-time.

**Guardrails:** Migration tasks must reference concept IDs from SPEC.md (stated
authority rule in the skill). In v2, the authoritative ID source is Ontology A; wire to
that rather than feature-local SPEC.md IDs.

---

### C3 — ADLC alignment tracking (the L0–L7 meta-layer map + gap registry)

**What it does (cite):** `ADLC-ALIGNMENT.md` maps DomainSpec's artefacts onto the
seven Meta-Track layers (L0–L7), declares 16 gaps (G1–G16), and maintains a roadmap
to closure. The layer map is the most complete description of *where* v1 sits relative
to a full governance stack.

**Candidate verdict:** REFORMULATE

**Why:** The layer map is a v1-scoped self-assessment — it describes what v1 has,
what it lacks, and what v1 planned to build. Importing it wholesale into v2 would
carry v1's framing of gaps as the ground truth for v2. Instead, the right move is to
re-author the L0–L7 map from v2's perspective (govern + enforce Ontology A on evidence),
using the gap IDs (G1–G16) only as a checklist to verify coverage, not as v2's own
structure. The owner is the map itself — build-from-owned is to re-derive, not import.
Specifically, G13 (formal constitution) and G16 (derivation chain L4→L3→L6) are the
most directly load-bearing for v2 and should be v2 first-class artefacts, not inherited
pointers.

**Leverage:** HIGH as a checklist reference; DROP as a wholesale import.

**Guardrails:** The two-ontologies guardrail (language A vs cav2 authority B) is
relevant here — the ADLC layer map is v1's operational framing, not a definition in
Ontology A; keep it in the evidence tier.

---

### C4 — Taxonomy layers (the 25-concept + layer-law Architecture Mapping Appendix)

**What it does (cite):** `TAXONOMY.md` Architecture Mapping Appendix defines:
(a) which layer each of the 14 backend meta-concepts belongs to (Domain / Application /
Infrastructure / Interface), (b) the layer dependency rule (Domain → nothing,
Application → domain, Infrastructure → domain+application, Interface → application),
(c) the encapsulation rule (public API = exported functions/types, private =
unexported). This is the canonical layer-membership oracle: given any meta-concept, it
tells you which layer owns it.

**Candidate verdict:** IMPORT

**Why:** This is v1's most foundational layering artefact. v2 governs Ontology A;
Ontology A's language includes these 25 meta-concepts; their layer assignments are not
arbitrary, they are the formal definition of what "domain purity" means. Importing this
table as a first-class v2 axiom (not just a reference) gives the drift detector (C1)
and the migration planner (C2) their ground truth. Without this table, neither C1 nor
C2 can classify a violation. The UI layer table (11 UI meta-concepts + UI layer
assignments) carries the same importance for the UI enforcement lane.

**Leverage:** HIGH — foundational; every enforcement rule in v2 traces to this table.

**Guardrails:** The table is v1-owned; import its *content*, not its v1 file
structure. In v2, this becomes an Ontology A axiom (layer-membership law), citeable
from the formal constitution (ADLC G13). Do not re-format in a way that loses the
"Maps To" counterpart columns — those are the cross-layer traceability links that make
the table machine-checkable.

---

## Verdict summary

| # | Capability | Verdict | Leverage |
|---|-----------|---------|---------|
| C1 | Layer drift detection (misplaced-logic audit) | **IMPORT** | HIGH |
| C2 | Dependency-ordered migration plan | **IMPORT** | MEDIUM |
| C3 | ADLC alignment layer map + gap registry (G1–G16) | **REFORMULATE** | HIGH (as checklist reference only) |
| C4 | Taxonomy layer-membership table + layer dependency rule | **IMPORT** | HIGH |

---

## Highest-leverage single move

**Import C4 first.** The 25-concept layer-membership table is the axiom every other
layering capability depends on. Without it, drift detection has no ground truth,
migration plans have no target layer to migrate *to*, and the ADLC gap registry
references undefined terms. Import it as a v2 Ontology A axiom, anchor it to the
formal constitution (G13), and derive the layer-dependency rule from it. C1 and C2
import immediately follows because their process steps reference the same table by
name.

---

## Guardrails carried forward to every row

- **claim ≤ proof:** No row claims v2 will have automated enforcement; the skill
  produces reports and plans — enforcement wiring is a separate gap (ADLC G4/A1 from
  ASSIMILATION-TABLE.md).
- **write-authority proviso:** All imported artefacts produce reports or plans; none
  mutate promotion-status.
- **adapter line:** The migration plan produces file-target tasks; it does not import
  app-runtime logic.
- **free/moat boundary:** Drift detection is structurally deterministic (file-parse +
  layer-law comparison) — it does not depend on LLM reasoning and is therefore free to
  publish.
