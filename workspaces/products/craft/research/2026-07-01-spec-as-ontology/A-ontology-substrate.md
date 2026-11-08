---
node_type: research-position
position: A — ontology-substrate
question: Should DomainSpec v2 treat its spec surface as a SYSTEM ONTOLOGY, and how does spec-as-ontology reshape the Batch-1 reformulation?
created: 2026-07-01
discipline: claim ≤ proof; cite by path; residue marked
---

# Position A — The Spec Surface IS a System Ontology

## 1. Thesis

DomainSpec v2's spec surface — 25 typed concept classes (`impl/spec/TAXONOMY.md`) +
29 typed edges (`impl/spec/RELATIONSHIPS.md`) + per-feature aspect files — is not
"like" an ontology; it **is** one: a formal typed knowledge graph with a
single-type-per-node invariant and a typed edge signature per relation. The
Batch-1 reformulation should therefore stop treating TAXONOMY/RELATIONSHIPS as two
separate "layering" documents and instead **govern them as one ontology substrate**,
using the owned `ontology-vault` sigil (branch-aware business/system/bridge) as the
backbone, with `ontology-view` as the single canonical home for every concept term.
This is a *build-from-owned* move, not net-new machinery.

## 2. Strongest evidence FOR

**(a) The spec already declares itself a knowledge graph.**
`impl/spec/RELATIONSHIPS.md:3` — "The 29 typed edges that connect domain concepts
into a navigable **knowledge graph**." Line 7 — "these edges make the knowledge
graph navigable." This is the repo's own words, not my inference.

**(b) The single-type invariant = the ontology single-owner invariant.**
`impl/spec/TAXONOMY.md:3` — "Every concept in your system maps to **exactly one**
of these types." The owned `ontology-view` sigil enforces the identical rule:
"A term defined here must appear in **exactly one** lane row. A second definition
anywhere is a contract violation the `paired-views` spell will catch"
(`.claude/skills/ontology-view/SKILL.md:76`). The spec's typing discipline and the
ontology sigil's ownership discipline are the same invariant at different altitudes.

**(c) The cross-layer edges are already branch-bridge edges.**
`RELATIONSHIPS.md:42-50` defines 6 UI↔Backend edges: `fetches`, `mutates`,
`reflects`, `derives`, `contracts`, `mirrors`. `ontology-vault` defines starter
bridge edges `realized_by`, `depends_on`, `observed_by`, `tested_by`, `drifts_from`,
`traced_to` (`.claude/skills/ontology-vault/SKILL.md:145-152`). These are the same
construct: typed edges spanning a business/UI branch and a system/backend branch,
admissible only with evidence on both sides. The spec has *hand-rolled a subset of
what ontology-vault already governs generically.*

**(d) A1 is the ontology-vault business→system branch axis, verbatim.**
`impl/spec/AXIOMS.md:13-16` (A1) — "Domain semantics are authored in DomainSpec
artifacts first. Code … are downstream realizations." That is exactly
ontology-vault's business-branch-precedes-system-branch posture, with bridge edges
carrying `realized_by`/`traced_to`. A2 (`AXIOMS.md:26-29`, decisions belong to
domain not adapters) is the business/system branch *boundary*. The axioms are
already ontology-branch law.

**(e) Aspect files are ontology fragments.** The spec surface is per-feature
(`domain.md`, `operations.md`, `states.md`, `interfaces.md`, `events.md`,
`queries.md`, `mappings.md`, `workflows.md`, `UI-SPEC.md`), each populating typed
nodes/edges for one feature. Under ontology-vault these are exactly "vault-like
knowledge material" — session/source folders whose claims classify to
business/system/bridge branches (`SKILL.md:29,139-143`). The `ontology-harness`
spell (`.claude/skills/ontology-harness`) already composes `inventory` +
`ontology-vault` + `context-builder` to turn such material into a governance layer.

**(f) The governances already assume a graph.** `layering-governance` owns the
"Edge-Law / forbidden-edge" over the typed graph (`authority/AUTHORITY-MODEL.md:58,72`);
that is an ontology edge-rule, which `ontology-vault` names as a first-class mode
("validate relationship rules", `SKILL.md:34`). Layering governance = an ontology
edge-law dressed in architecture vocabulary.

## 3. Implications for the Batch-1 reformulation (the 6 docs)

The current `DESIGN.md` re-homes TAXONOMY and RELATIONSHIPS **separately** to
`layering` (`reformulate-batch1/DESIGN.md:37-40`). Spec-as-ontology changes this:

- **TAXONOMY + RELATIONSHIPS unify into ONE ontology substrate doc pair** governed
  as the ontology floor: TAXONOMY = the *class/role catalog* (nodes), RELATIONSHIPS
  = the *typed-relation graph* (edges). Both keep their layering binding, but layering
  becomes a **projection over the ontology**, not the ontology's owner. Concretely:
  add an `ontology-view` header owning `term:<concept>` for all 25 classes and
  `relation:<a>--<b>` for all 29 edges — the single canonical home
  (`ontology-view/SKILL.md:74`).
- **Adopt branch labels.** Tag each concept/edge `business` (domain/UI-intent),
  `system` (backend/runtime), or `bridge` (the 6 cross-layer edges) per
  `ontology-vault` branches. This makes A1/A2 (`AXIOMS.md`) *the branch law* instead
  of prose axioms — R1 (AXIOMS reformulation) binds A1/A2 to the bridge, not just
  "layering C6."
- **RELATIONSHIPS forbidden-edge law (DESIGN D4) becomes an ontology edge-rule.**
  Instead of inventing a bespoke "unconstructible" Markdown form, express it as an
  ontology-vault validate-mode edge rule with endpoint branch signatures — the sigil
  already owns "validate relationship rules" (`SKILL.md:34,216`). D4's open question
  gets an owned answer.
- **Add confidence + premise governance the current design lacks.** DESIGN routes
  surviving terms to `definitions-governance` for a tracked ID (`DESIGN.md:73`), but
  has **no confidence dimension** and **no premise ledger**. ontology-vault supplies
  evidence-confidence vs commitment-confidence separation and premise-review
  (`SKILL.md:31-34,196-200`). A UI-11 concept not yet engine-derived
  (DESIGN D2) becomes *system-branch, low commitment-confidence* — an honest state
  the current binary "kept/dropped" cannot express.
- **CONSTITUTION crosswalk gains an ontology-convention owner.** v1 C-rules about
  the graph (edge admissibility, concept typing) route to an ontology
  convention-update lane (`SKILL.md:33`) rather than being smeared across layering.

## 4. Strongest objection + rebuttal

**Objection.** ontology-vault is a *knowledge-governance* tool for evolving fuzzy
vaults with confidence gates and sessions; the spec is a *deterministic input
contract* to a proprietary engine. Bolting a confidence/premise ontology layer over
a surface whose whole value is that it is crisp and machine-consumed (`AUTHORITY-MODEL.md`
Core Rule) risks **softening a hard contract** — the engine needs a total function
over typed nodes, not "confidence 0.6 that Entity is an Entity."

**Rebuttal.** The objection conflates two planes. The *engine-facing contract* stays
crisp: TAXONOMY/RELATIONSHIPS remain the total, typed input the engine consumes
(`AUTHORITY-MODEL.md:71`); nothing about ontology governance changes what the engine
reads. Confidence/premise applies to the **spec-authoring plane** — whether a
*newly proposed* concept/edge is ratified into the crisp set — which the current
design *already gates* via `candidate` definitions (`DESIGN.md:73`) and the
AUTHORITY-MODEL's "candidate obligation → witness → owner decision" movement
(`AUTHORITY-MODEL.md:62,138-144`). ontology-vault names that existing gate more
precisely (evidence vs commitment confidence), it does not soften the delivered
contract. The crisp graph is the *promoted, high-confidence* projection of the
governed ontology — the same μF (crisp law) / νF (evolving observation) split the
AUTHORITY-MODEL already ratified (`AUTHORITY-MODEL.md:110-118`).

## 5. Residue (unverified)

- **R1** — I read only the `features/sample/SPEC.md` fixture, not real per-feature
  aspect files; the "aspect files = ontology fragments" claim is grounded in the
  TAXONOMY/RELATIONSHIPS aspect-source mapping (`TAXONOMY.md` "→ *.md" columns) and
  the FACTS list, not in inspected multi-aspect feature packs. Residual.
- **R2** — Whether `ontology-vault`'s runtime-profile mode can bind to the spec
  without a dedicated runtime is asserted from `SKILL.md:49-71`; not exercised here.
- **R3** — The engine's tolerance for a confidence-tagged input is **unverified by
  design** (engine treated as black-box); the rebuttal argues confidence lives on
  the authoring plane precisely to avoid needing to test this. If a future check
  shows the engine already ingests only the crisp set, R3 closes in my favor.
- **R4** — I did not confirm `ontology-harness`/`paired-views` are installed as
  runnable here beyond their SKILL/spell descriptions; composition claim is
  design-level, not execution-verified.
