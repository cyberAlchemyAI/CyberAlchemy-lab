---
node_type: research
role: skeptic
area: code-tag-drift
persona: "Rittel, Horst — wicked-problems skeptic"
subject: DomainSpec v1 → v2 import triage — CODE-TAG DRIFT surface
dispatch_id: 2026-06-29-domainspec-v1-import-triage
date: 2026-06-29
discipline: default-deny; found owner = REFORMULATE, never kill; claim <= proof
guardrails:
  - write-authority-proviso (no modeling surface writes promotion-status)
  - two-ontologies (Ontology A = DomainSpec language; Ontology B = cav2 authority — align, not merge)
  - adapter line (no app-runtime imports)
---

# Skeptic Memo — CODE-TAG DRIFT
## Rittel, Horst — owner-sweep + default-deny

Scope: every v1 capability clustered under code↔spec tag tracking, drift detection,
composability enforcement, and writeback signaling. Rittel's method: name the candidate,
find the existing owner, render exactly one verdict (REFORMULATE / IMPORT / DROP), flag
any write-authority or two-ontologies conflict.

---

## Owner sweep

### C1 — Code-tag extract / annotate

**Scout candidate:** import the annotation schema + extract tooling as a net-new v2 surface.

**Owner found:** `implementation/domainspec/governance/tags/` — fully operational cluster:
`CODE-TAG-SCHEMA.md` / `CODE-TAG-SCHEMA.json` (versioned schema), `extract-code-tags.ts`
(CLI extractor), `code-tags.json` (live output), `code-tags.agent-execution-orchestrator.json` /
`code-tags.kg.json` / `code-tags.ui-*.json` (feature-scoped datasets). Skill:
`implementation/domainspec/.claude/skills/domainspec-tag-code/SKILL.md` — fully parameterised
agent that runs extract → validate → drift in one call. Commands exposed: `pnpm run
code-tags:extract` / `check:code-tags`.

**Verdict: REFORMULATE.** The extract+annotate surface is owned and running. v2 sharpening:
endpoint-type the schema against `TAXONOMY.md`'s 25 meta-types (so the validator can reject
unknown concept types structurally, not just by string-match). Zero net-new capability needed.

---

### C2 — Code-tag validate (schema + edge rules)

**Scout candidate:** import validation logic that checks code tags against spec concept
tables and edge rules.

**Owner found:** `governance/tags/tools/validate-code-tags.ts` (~770 lines, live). Checks
concept-id presence in the concept catalog, edge admissibility via `code-tag-rules.ts`
(`parseRelationshipRules` from TAXONOMY.md/RELATIONSHIPS.md), waiver bypass via
`code-tag-waivers.yaml`, `spec_ref.path` + line resolution, PASS/FLAG/BLOCK verdict. The
`CODE-TAG-REMEDIATION.md` catalog maps every failure code to a remediation action.
CI integration: `check:code-tags` in `package.json`.

**Verdict: REFORMULATE.** Owned and wired into CI. The real v2 sharpening (from correctness-
ownership-sweep `findings.md` A5 + B1) is: replace string-match edge admissibility with
endpoint-pair type-checking — so a `Rule --mutates--> Operation` is *unconstructible-by-type*,
not merely string-rejected. That is a precision upgrade of the existing gate, not a new one.

---

### C3 — Drift detection (code→spec direction)

**Scout candidate:** import code→spec writeback — detecting when code declares concepts that
are absent from spec (the "orphan anchor" problem, ADLC-ALIGNMENT L2→L1 gap).

**Owner found (partial):** `governance/tags/tools/compare-code-tag-drift.ts` (~470 lines)
compares extracted code-tag triples against parsed doc-triples from `docs/features/` spec
files and emits `CODE-TAG-DRIFT-REPORT.md`. This IS the code→spec direction. What is present:
a structural diff of declared edges vs spec-documented edges. What the scout correctly flags
as missing (confirmed): the *writeback* direction where a detected drift auto-updates or
proposes a spec amendment rather than only flagging it.

**Verdict: REFORMULATE.** The drift detect surface is owned. The code→spec *writeback*
direction is exactly ASSIMILATION-TABLE B1's verdict ("the code→spec write-back direction is
a real sharpening, not a missing capability — build into the owned skill"). v2 wires the
divergence taxonomy (spec-bug / code-bug / aspirational / intentional-gap) from allium's
`/weed` into the existing `compare-code-tag-drift.ts` report, closes the audit-alignment
loop. No new tool needed — extend the owned emitter.

**Write-authority proviso check:** the drift reporter produces a report artifact, it does NOT
write `promotion-status` to any concept node. Sound as long as "auto-propose spec amendment"
is advisory output, not a promotion write. **Flag:** if any v2 writeback path were to mutate
a concept's status in the concept catalog, it would violate the proviso. Keep writeback as
flag-only / proposed-patch output — never as a live catalog mutation. This is a hard
architectural constraint, not a soft preference.

---

### C4 — Composability enforcement (edge→implementation obligation)

**Scout candidate:** import edge-composition obligation checking — `Rule --enforces--> Operation`
implies the operation must call the rule in code.

**Owner found:** `governance/tags/tools/check-code-tag-composability.ts` + `CODE-TAG-COMPOSABILITY-PATTERNS.md`
+ `check-code-tag-composability.test.ts`. The matrix (Rule→enforces→Operation, Calculation→calculates→
Operation, Policy→applies→Operation, Interface→exposes→Operation/Query, Binding→mutates/fetches→
Operation/Query, Workflow→orchestrates→Operation) is fully specified and the checker runs per
feature. `pnpm run code-tags:composability`.

**Verdict: REFORMULATE.** Owned and executable. v2 sharpening: wire the composability check
into the PostToolUse hook chain (ASSIMILATION-TABLE A1's wiring gap applies here too) so a
spec-doc write that would break a composability obligation fails-closed at write time rather
than at next manual run.

---

### C5 — Waiver registry

**Scout candidate:** import a formal waiver mechanism so acknowledged-gaps don't pollute
drift reports.

**Owner found:** `governance/tags/CODE-TAG-WAIVERS.md` + `governance/tags/code-tag-waivers.yaml` —
a governed waiver registry with a policy document. Already consumed by `validate-code-tags.ts`
(waiver-bypass path on BLOCK failures).

**Verdict: REFORMULATE.** Owned. v2 sharpening: time-bound waivers (auto-expire after N days)
and waiver-reviewed-by field to close the audit trail. No net-new mechanism.

---

### C6 — Promotion-status write (the proviso violation candidate)

**Scout candidate (hypothetical / flag):** a code-tag tool that, upon detecting full drift
resolution, writes `status: promoted` or similar to a concept entry in the catalog.

**Owner found:** none — and correctly so.

**Verdict: DROP.** Any modeling surface that auto-writes promotion-status violates the
write-authority proviso from `ontology-operationalization-in-the-machine-synthesis.md`
(§ decision spine: "no modeling operation may acquire a write-edge to authority/promotion-status").
The code-tag layer is Ontology A (DomainSpec language governance); promotion lives in
Ontology B (cav2 authority). Merging the two by granting code-tag tooling a write-edge to
promotion-status would re-fuse the regulator with the regulated (Conant-Ashby collapse).
Reject unconditionally. The drift layer may *surface* a "drift resolved" signal; the
promotion act is a separate, cav2-owned gate.

---

### C7 — Two-ontologies alignment check

**Scout candidate:** import a mechanism that validates DomainSpec language tags (Ontology A)
against cav2 authority kinds (Ontology B) — e.g., checking that a tagged concept's `type`
field maps to a known authority kind.

**Owner found (partial):** `ADLC-ALIGNMENT.md` (the @biz/@sys binding concept is described);
`validate-code-tags.ts` checks concept-id membership in the doc-derived catalog but does NOT
cross-validate against cav2 kind definitions.

**Two-ontologies flag:** any import that lets code-tag validation emit verdicts *about*
cav2 authority kinds — rather than about TAXONOMY.md meta-types — would begin merging
Ontology A and B. Alignment means: TAXONOMY.md types (Rule, Operation, Binding, …) map
to @biz/@sys annotation tiers at the code surface; cav2 kinds (D1–D* authority categories)
remain separately governed. A v2 alignment check is sound only if it validates that
`concept.type` belongs to TAXONOMY.md's 25 meta-types — it must NOT validate that `concept.type`
maps to a cav2 kind (that is cav2's gate, not the code-tag gate).

**Verdict: REFORMULATE.** The v2 sharpening is to make `validate-code-tags.ts` check
endpoint-pair type admissibility against TAXONOMY.md types only (Ontology A). Any cross-check
into cav2 kinds is a two-ontologies violation; route that to cav2's authority gate instead.

---

## Summary verdict table

| Candidate | Owner (cited) | Verdict | v2 sharpening |
|---|---|:---:|---|
| C1 extract / annotate | `governance/tags/`, `domainspec-tag-code` skill | REFORMULATE | endpoint-type schema against TAXONOMY.md 25 types |
| C2 validate (schema + edge) | `validate-code-tags.ts` + `CODE-TAG-REMEDIATION.md` | REFORMULATE | endpoint-pair type-check (not string-match); owned by correctness-sweep A5 |
| C3 drift detect (code→spec) | `compare-code-tag-drift.ts` + `CODE-TAG-DRIFT-REPORT.md` | REFORMULATE | add divergence taxonomy (allium B1 sharpening); writeback = flag-only (proviso) |
| C4 composability enforcement | `check-code-tag-composability.ts` + `CODE-TAG-COMPOSABILITY-PATTERNS.md` | REFORMULATE | wire into PostToolUse hook (ASSIMILATION-TABLE A1 wiring gap) |
| C5 waiver registry | `CODE-TAG-WAIVERS.md` + `code-tag-waivers.yaml` | REFORMULATE | time-bound waivers + reviewed-by field |
| C6 promotion-status write | no owner (correctly absent) | DROP | write-authority proviso violation; hard reject |
| C7 two-ontologies alignment | `validate-code-tags.ts` (partial) | REFORMULATE | Ontology A only; no cav2-kind cross-check |

---

## Cross-cutting flags (carry into synthesis)

1. **Write-authority proviso (hard):** C3's writeback path and C6 are the live risk. Any v2
   wiring that auto-mutates a concept's promotion-status or authority-kind through the code-tag
   layer collapses Ontology A into B. Enforce: drift reporter = advisory output only; promotion
   = cav2 gate only.

2. **Two-ontologies (hard):** C7 names the boundary. Code-tag validation checks TAXONOMY.md
   membership (Ontology A). cav2 authority kind membership is Ontology B. Never merge the
   validators. Any "does this concept belong to a cav2 kind?" check must be routed to cav2's
   gate — not wired into `validate-code-tags.ts`.

3. **Adapter line:** The `compare-code-tag-drift.ts` CLI and the composability checker are
   spec-layer tools. No v2 port should import app-runtime state (live service introspection,
   running event stores) to compute drift — drift is derived from static code tags vs spec
   docs. (cf. ASSIMILATION-TABLE S6, S4: live-runtime introspection is below the adapter line.)

4. **ASSIMILATION-TABLE B1 already resolved code→spec direction.** The divergence taxonomy
   (spec-bug / code-bug / aspirational / intentional-gap) is the precise sharpening to import
   into `compare-code-tag-drift.ts`. Rittel concurs: do not re-derive this — cite the table
   and execute against the owned tool.

5. **PostToolUse hook gap (from ASSIMILATION-TABLE A1):** The spec-semantic validator hook is
   missing. The composability checker and the validate-code-tags gate exist but are manually
   triggered. Wiring them into a fail-closed PostToolUse hook on `docs/features/**` writes is
   the single highest-ROI gap in this surface — and it is a wiring gap, not a capability gap
   (every part exists).

---

## Rittel's bottom line

The code-tag drift surface is the **most owned cluster in all of v1**: schema, extractor,
validator, composability checker, drift reporter, waiver registry, skill — all exist and run.
Zero candidates warrant IMPORT. Every candidate is REFORMULATE (sharpen the owned tool) except
the promotion-status writer, which is DROP on hard architectural grounds (write-authority
proviso). The scout's real work is: (a) wire the existing gate into a PostToolUse hook, (b)
add endpoint-pair type-checking to the validator, (c) add the allium divergence taxonomy to
the drift reporter. Default-deny upheld across all seven candidates.
