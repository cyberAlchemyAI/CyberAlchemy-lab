---
node_type: research
is_session: false
status: skeptic-critique
created: 2026-07-02
authored_by: research skeptic (Feyerabend — anti-method, anti-ceremony)
dispatch: 2026-07-02-spec-comprehension-model
tension_partner: skeptic-gigerenzer (completeness side)
promotion_boundary: local research only — attacks the candidate, promotes nothing.
attacks: ./candidate-model.md
claim_discipline: claim ≤ proof. Disk facts cited file:line; anything unmeasured is labelled HYPOTHESIS.
---

# Skeptic — Feyerabend: the merged model smuggles ceremony back in

> *"The only principle that does not inhibit progress is: anything goes."* The candidate
> spent three lenses proving that comprehension is bought by **subtraction**, then wrote a
> four-move **model** — a tier declaration, a 4-part unit, a two-form allowance, a narrative
> carve-out. That is method re-growing over the cut. Four moves is three moves too many.

---

## (1) Verdict

**STILL TOO MUCH.** The comprehension asset is already 100% on disk as pure projections of
the 14 backend schemas; the merged candidate re-wraps what exists in three new authoring
rituals (M1 lens-declaration, M2 4-part unit, M3 two-form allowance) and re-imports the very
narrative vocabulary it killed (M4). The honest floor is **author nothing, relocate three
things, delete one** — not a "comprehension model."

---

## (2) Per-move critique

### M1 — the "per-domain author-declarable CORE/GENERIC lens" is a new ritual, not a distillation

The distilled *reading order* (CORE ~6 / SUPPORTING / GENERIC) costs nothing — it is just a
suggested path through docs that already exist. But M1 does not stop there. It makes the split
**"a per-domain author-declarable lens"** (`candidate-model.md:57`). That is a fresh authoring
obligation bolted in front of the taxonomy: before a novice can read a type they must first
*declare their core subdomain*. That is strictly **harder** than "here are the 6 types most
specs use," and it re-introduces exactly the up-front complexity distillation was meant to
remove.

Sharpest cut: the candidate's own source refutes it. `lens-distillation.md:188` calls the
distilled order **"a learning *order*, not a new artifact."** M1 promotes it to a declarable
artifact — cargo-culting Evans/Vernon's *strategic-design* investment call ("same subdomain,
different category by org," `lens-distillation.md:250-256`) into the *comprehension* layer,
where it does not belong. **Kill the declaration.** Ship one fixed default order — the six the
lens already names (Entity, VO, Operation, Rule, State Machine, Event). A default is a reading
hint at zero cost; a declarable lens is a ceremony. If a domain disagrees with the order, it
reads in a different order — no declaration required.

### M2 — the 4-part "comprehension unit" is OCM-009 wearing a smaller hat

M2 mandates, *per CORE type*: positive + discriminating negative + named axis + thin definition
(`candidate-model.md:60-64`). Count them: **four required forms per type.** That is structurally
OCM-009 ("all seven sentence forms are required → reject deliverable,"
`OPTIMIZATION-CHAIN-METHOD.md:134`) with the number filed from 7 to 4 — the same "one idea, N
mandatory renderings" ritual the candidate spent lens-distillation §5 condemning. Minimalism
banner, ceremony underneath.

And the four parts **already exist authored** in the card the repo ships. `entity.md` already
carries the *named axis + thin definition* ("Distinguisher vs Value Object,"
`entity.md:32-35`) and the *positive + negative* ("Fixtures — the discriminating pair,"
`entity.md:37-40`). The **only** real delta M2 proposes over disk is **reordering** (examples
before definition — the card is definition-first, fixtures 5th of 6, `entity.md:18-40`,
confirmed by `lens-example.md:98-99`). So M2's honest content is one instruction — "reorder the
existing card, examples-first" — not a new named unit.

Sharpest cut (this is what the dispatch asked): **collapse M2 to the crossed fixture pair + a
one-line axis label, author NOTHING.** The axis label is not authored either — it is already
the schema's `distinguisher.rule` string (`entity.schema.yml:26-28`: *"an Entity HAS an
identity field; a Value Object has none…"*). So M2 reduces to: co-locate the ok/bad pair beside
the schema and surface `distinguisher.rule` as the caption. Defining a 4-part "unit" over that
is inventing a ritual to describe a relocation.

### M3 — "at most two authored human forms" — the honest floor is ZERO (for backend)

M3 permits "at most two authored human forms" (`candidate-model.md:69-72`). Even one is one too
many. **`entity.md` is a total projection of `entity.schema.yml`** — every section maps to a
structured schema field, nothing in the card is absent from the schema:

| entity.md section | source field in entity.schema.yml |
| --- | --- |
| Formal criterion (`:18-22`) | `criterion:` (`:16-23`) |
| Required structure (`:24-26`) | `required_structure:` (`:12-13`) |
| Edge participation (`:28-30`) | `edge_participation:` (`:31-33`) |
| Distinguisher (`:32-35`) | `distinguisher:` (`:26-28`) |
| Fixtures (`:37-40`) | `fixtures:` (`:35-37`) |
| Boundary (`:42-45`) | shape-only header comment (`:3-5`) |

The card is a `render(schema)`, not an authored form. Every one of the **14 backend schemas**
carries a single-valued `distinguisher.vs` (verified on disk: entity→ValueObject,
value-object→Entity, workflow→Saga, saga→Workflow, rule→Policy, policy→Rule, operation→Query,
query→Operation, calculation→Rule, event→Operation, interface→Mapping, mapping→Interface,
enum→Entity, state-machine→Enum). So the projection source exists for **all 14 backend types**.

Sharpest cut: **the floor is zero authored per-spec forms — project the card from the schema.**
If plain-language genuinely helps, that is *one optional `plain:` field added once at the
meta-type level* and projected — not "two authored forms per comprehension unit." M3's "two"
adds 2×6 = 12 hand-maintained sentences whose only guaranteed product is drift surface — a risk
the candidate itself flags at R3 (`candidate-model.md:89-90`) and then declines to follow to its
floor.

### M4 — "narrative survives for target-state" re-imports the word the model just buried

M4 (`candidate-model.md:74-78`) grants a narrative a home in the target-state doc, paired with a
"checkable oracle." But the candidate's own example lens already showed the target-state oracle
is **the same crossed-pair device as M2** — a DONE positive plus a near-miss NOT-DONE negative
(`lens-example.md:166-184`), not a narrative layer. So M4 is not a fourth move; it is M2's
device pointed at a feature instead of a meta-type.

Sharpest cut: **drop the word "narrative" entirely and fold M4 into M2's rule** — "author intent
as a DONE / NOT-DONE example pair." Keeping "narrative" as a surviving category re-seats the OCM
"add a dialect" instinct the three lenses converged to reject; it is the smuggler's residue. The
device is a pair of examples; call it that.

### Whole-dispatch cut — is a "comprehension model" artifact itself the ceremony? Mostly yes.

The maximally-Feyerabend answer to the owner's goal ("understand the proposed abstractions of a
new spec") is three mechanical moves and no new model:

1. **RELOCATE** the `__fixtures__/mt/*-ok.md` / `*-bad.md` pairs next to their `.schema.yml` +
   card (they sit in a separate `__fixtures__/` dir today) and reorder each card examples-first.
   Author nothing; the fixtures already exist and already run in CI, so the comprehension asset
   fails when it rots.
2. **PROJECT** the card from the schema (`distinguisher` = the axis caption). Zero authored
   forms for the 14 backend types.
3. **DELETE** the redundant discriminations: the `Common Confusion` rows that merely restate a
   schema `distinguisher` (`TAXONOMY.md:579-602`) — lens-distillation itself named these tables
   the *tell of bloat* (`lens-distillation.md:112-119`).

No tier declaration, no 4-part unit, no "comprehension-narrative-model" node. That artifact —
the thing this very dispatch is producing — is, in the strict Feyerabend reading, the ceremony.

---

## (3) Counter-proposal — the minimal version (author / relocate / delete)

**AUTHOR (net-new): nothing required.** *Optional, once, at meta-type level (not per spec):* a
single `plain:` line per backend schema **iff** a reader study later shows plain-language earns
its keep — HYPOTHESIS, unmeasured (`lens-distillation.md:277`), so not authored now.

**RELOCATE (author nothing new):**
- Move each `*-ok.md`/`*-bad.md` pair adjacent to its schema+card; reorder cards examples-first
  (invert `entity.md:18-40`).
- Surface each schema's existing `distinguisher.rule` string as the pair's one-line caption
  (`entity.schema.yml:26-28`).
- Replace M1's declarable lens with one fixed default reading order (the 6 CORE names).

**DELETE:**
- The `Common Confusion` rows already covered by a schema `distinguisher`
  (`TAXONOMY.md:579-588` backend) — redundant with data the validator already holds.

That is the whole thing. It achieves "understand the proposed abstractions" by leading with the
crossed pair the repo already ships, captioned by the axis the schema already carries — and it
authors **zero** new prose.

---

## (4) Residue I concede to the completeness side (Gigerenzer is right here)

**My "delete the confusion tables" and "project from schema, author zero" cuts assume every
discrimination lives in a schema `distinguisher`. On disk, it does not — for a large minority.**

- Each backend schema's `distinguisher.vs` is **single-valued** (verified: operation→Query
  only, workflow→Saga only, etc.). The `Common Confusion` table encodes *multiple* pairwise
  discriminations per type. At least **"Operation vs Workflow"** (`TAXONOMY.md:583`) has **no**
  schema counterpart — operation distinguishes only vs Query, workflow only vs Saga. Deleting
  that row loses its only authored home.
- **The 11 UI meta-types have NO `.schema.yml` at all** (verified: only `structural/`,
  `behavioral/`, `connective/`, `lifecycle/` dirs exist — all backend; no `ui/`). So for 44% of
  the taxonomy there is **nothing to project from**, and the 9 UI `Common Confusion` rows
  (`TAXONOMY.md:592-602`) — of which the 4 non-shadow pairs (Page vs Layout, Component vs Page,
  Hook vs Binding, Form vs Component, Action vs Hook) are not even in the Backend-Counterpart
  column — are the **only** place those discriminations are authored.

Concession: my "author zero, project everything, delete the tables" floor is honest for the
**14 backend types**, but for the **UI half** and for the cross-pairs the single-valued
distinguisher cannot hold, cutting to relocation genuinely **loses discrimination information**.
There, Gigerenzer's completeness worry is not ceremony — it is a real gap, and the confusion
table (or, better, adding UI schemas + multi-valued distinguishers) is doing load-bearing work
my maximal cut would destroy. I hold the line that the *backend* comprehension asset needs zero
new authoring; I concede the *UI* half is not yet projectable and cannot be cut to relocation
without loss.

---

### Claim ≤ proof ledger
| Claim | Proof | Strength |
| --- | --- | --- |
| `entity.md` is a total projection of `entity.schema.yml` | section→field table above, both read 2026-07-02 | Strong (on disk) |
| All 14 backend schemas carry a single-valued `distinguisher.vs` | grep over `meta-types/**/*.schema.yml` | Strong (on disk) |
| No UI schemas exist (11 types unprojectable) | only 4 backend category dirs present | Strong (on disk) |
| "Operation vs Workflow" + 5 UI pairs have no schema distinguisher | cross-check confusion table vs `distinguisher.vs` set | Strong (on disk) |
| M2's 4-part unit = OCM-009's "N required forms" ritual, smaller N | `candidate-model.md:60-64` vs `OPTIMIZATION-CHAIN-METHOD.md:134` | Medium (structural analogy) |
| Reordering examples-first improves comprehension | — | HYPOTHESIS (unmeasured; `lens-example.md:246`) |
