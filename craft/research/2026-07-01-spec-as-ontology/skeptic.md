---
node_type: research-skeptic
role: skeptic (red-team the synthesis)
question: Should DomainSpec v2 treat its spec surface as a SYSTEM ONTOLOGY, and how does spec-as-ontology reshape the Batch-1 reformulation?
target: synthesis.md
created: 2026-07-01
discipline: claim ≤ proof; cite by path; owned-precedent sweep; owner-route check; engine algorithm never asserted
---

# Skeptic — red-team of the spec-as-ontology synthesis

Verdict up front: the synthesis **SURVIVES its core boundary claim** (the two-plane seam is
sound and every load-bearing citation checks out), but the synthesizer **MUST REVISE** on two
counts before the verdict is safe to act on: (1) an **uncited owned precedent** exists
(`spec-ontology-unification/SEED.md`) that already frames "spec == ontology" as an *open
hypothesis under a promotion boundary*, which the synthesis silently treats as settled ambient
fact; (2) two proposed additions (the ontology-view doc; branch/confidence tagging) inherit an
**owner-route gap** — they name owning *sigils* but no owning *governance*, and the AUTHORITY-MODEL
recognizes exactly three governances as the owners of spec-surface authority.

## Method

- Verified every load-bearing citation in synthesis.md against source (paths + lines below).
- Owned-precedent sweep: `arcanum/`, `.claude/skills/`, `projects/domainspec-v2/`, `research/`.
- Claim ≤ proof: flagged claims exceeding cited evidence, engine-algorithm leaks, asserted
  consumers of confidence/premise/branch fields.
- Owner-route: every proposed change must name a real owner (a ratified governance OR an owned sigil).

Citations confirmed accurate: `RELATIONSHIPS.md:3` (self-declares "knowledge graph");
`TAXONOMY.md:3` ("exactly one of these types"); `AXIOMS.md` A1/A2 (semantic-first / decisions-in-domain);
`RELATIONSHIPS.md` cross-layer 6 edges (`fetches`/`mutates`/`reflects`/`derives`/`contracts`/`mirrors`);
`ontology-vault/SKILL.md:66-71` (outputs "are not ... source authority, spec mutations ...");
`ontology-vault/SKILL.md:49-71` (`--profile`/`--runtime inline`); `AUTHORITY-MODEL.md:57-59` (3 governances,
Authority Kinds); `AUTHORITY-MODEL.md:110-118` (μF/νF split); engine `README.md` pipeline + "typed stubs".
**No engine-algorithm leak** in A, B, or synthesis — the engine is treated as a black-box interface throughout. Good.

---

## CHANGE REQUESTS

### CR-1 — Uncited owned precedent: `spec-ontology-unification/SEED.md` (BLOCKING for the sweep)
- **Claim.** Synthesis §intro treats "the spec reads-as / bites-as a knowledge graph" as a fresh
  two-position finding, and A §1 asserts spec "**is** one" as ambient truth.
- **Problem.** An owned precedent already OWNS this exact question:
  `projects/domainspec-v2/research/spec-ontology-unification/SEED.md` (2026-06-11) — "Treat the spec
  and the ontology as the **same object in two forms**" (SEED L14-16), and explicitly holds it as a
  *hypothesis under test* with a hard **promotion boundary**: "Local research only. No change to spec
  schema, code-pattern catalog, agent constitutions, or runtime until a later approved `task-session`"
  (SEED L56-58). It even lists a Lane-A alternative (keep spec/ontology separate + generated mapping,
  the v1 direction) that neither A nor the synthesis weighs. Per the owned-in-repo rule, a found owner
  makes this **build-from-owned**, never a net-new finding — and here the owner also *bounds* the claim
  the synthesis assumes.
- **Required fix.** Cite `spec-ontology-unification/SEED.md`; re-state A's "the spec **is** an ontology"
  as "an owned, still-unexecuted hypothesis (SEED, promotion boundary L56-58)", not settled fact; note
  that the seed's promotion boundary already forbids the spec-schema mutations A §3 flirts with.
- **Owner.** DomainSpec v2 tower owner (the seed's `Owner:` line) + this research node.

### CR-2 — Ontology-view doc names a sigil but no governance owner (owner-route orphan)
- **Claim.** Synthesis §3: "**Ontology-view doc:** ADD one, but **as authoring documentation, not a
  governance owner** ... It is the definitions-governance surface given graph shape."
- **Problem.** The AUTHORITY-MODEL recognizes exactly three governances as spec-surface authority owners
  (`AUTHORITY-MODEL.md:57-59`, Authority Kinds). A new *document* with no governance owner is an orphan:
  the synthesis says it "does not sit in the §1 re-homing map" yet it would live in `impl/spec/` and carry
  `term:`/`relation:` handles (`ontology-view/SKILL.md:74`). Who ratifies its content, who is default-deny
  on it? The phrase "definitions-governance surface given graph shape" is the closest to an owner but is
  asserted, not routed — and `definitions-governance` owns *terms/IDs*, not a graph view.
- **Required fix.** Either (a) route the ontology-view doc's authority to a *named* existing owner —
  `definitions-governance` for terms, `layering-governance` for the edge graph (it already owns the
  RELATIONSHIPS Edge-Law, `AUTHORITY-MODEL.md:72`) — stated explicitly; or (b) demote it to a *generated
  read-projection* (B's framing, B §3 "optional projection, gated") produced by `ontology-view`/`paired-views`
  over the crisp docs, non-authoritative, so it needs no governance owner. Do not leave it as an authored
  doc with no ratifier.
- **Owner.** definitions-governance (terms) + layering-governance (edges), OR the ontology-view/paired-views sigils (if projection-only).

### CR-3 — Confidence + branch tagging asserts consumers that do not exist (claim ≤ proof)
- **Claim.** Synthesis §3 recommends adopting ontology-vault for "evidence-vs-commitment confidence" and a
  "premise ledger", and carries A §3's branch-labeling ("tag each concept/edge business/system/bridge").
  D-syn-4 concedes "no compiler/validator is confirmed to read confidence/premise/role fields."
- **Problem.** This is *stronger* than "not confirmed": a repo search (`test-derivation-engine/src`, `spec`,
  `tools`) finds **zero** consumers of confidence / premise / branch fields anywhere. So the recommendation
  proposes writing fields with no reader. That is fine on the authoring plane ONLY if fenced — but §3's
  language ("**Adopt** branch labels", A §3 "**Tag each** concept") reads as a live surface change, which
  crosses into the crisp contract the synthesis's own §1 forbids softening.
- **Required fix.** Restate as: confidence/premise/branch tags are **authoring-plane-only annotations with
  no engine or validator consumer today (verified absent)**; they may be recorded by `ontology-vault --runtime
  inline` outputs (which are "not ... spec mutations", `ontology-vault/SKILL.md:66-71`) but MUST NOT be written
  into the crisp TAXONOMY/RELATIONSHIPS docs the engine parses until an owner ratifies a consumer. Fold the
  D-syn-4 fence into §3 itself, not as an afterthought.
- **Owner.** validation-governance (owns what the engine consumes) gates any promotion of a field to a read
  surface; ontology-vault sigil for the authoring-plane capture.

### CR-4 — "ontology-vault names this existing gate more precisely" overstates verified capability (claim ≤ proof, minor)
- **Claim.** Synthesis §1: ontology-vault "names this existing gate more precisely (evidence-vs-commitment
  confidence, premise ledger) without adding enforcement the engine must honor."
- **Problem.** A's own residue R4 flags that `ontology-harness`/`paired-views`/ontology-vault are asserted
  from SKILL/spell descriptions, "not execution-verified"; R2 flags the runtime-profile-binds-to-spec claim
  as unexercised. The sweep confirms the sigils *exist* as packages (`.claude/skills/ontology-vault`,
  `ontology-harness`, `paired-views`, and canonical `arcanum/arcana/ontology-vault/`) but `ontology-view` is
  self-marked **seed / not promoted** (`ontology-view/SKILL.md:25-27`, `<status>Seed ... Not promoted`).
  "Names more precisely" is a *capability* claim resting on unrun sigils; the seed status of ontology-view in
  particular undercuts "single canonical home ... it does not consume engine authority" being a delivered good.
- **Required fix.** Qualify: "ontology-vault *is designed to* name this gate more precisely" and carry A's R2/R4
  residue forward into the synthesis residue (currently synthesis residue only carries B-R1). Note ontology-view
  is seed-status, so the "ADD an ontology-view doc" recommendation is a *seed-sigil* adoption, not a mature one.
- **Owner.** research node residue; ontology-view sigil promotion-gate (`ontology-view/SKILL.md:145-153`).

### CR-5 — Synthesis residue is thinner than its inputs' residue (completeness)
- **Claim.** Synthesis §Residue carries only "engine black-box; δ-rule coverage per type unverified (B-R1)."
- **Problem.** A contributed R1 (only the sample fixture read, not real multi-aspect feature packs — the
  "aspect files = ontology fragments" pillar is unverified), R2 (runtime-profile binding unexercised), R4
  (sigils not execution-verified). These are load-bearing to the "adopt ontology-vault, bounded" verdict and
  are dropped. Claim ≤ proof requires the synthesis residue to be the *union*, not a subset.
- **Required fix.** Add A-R1/R2/R4 to the synthesis residue block.
- **Owner.** research node.

---

## What SURVIVES (do not touch)

- The **two-plane boundary** (contract-primary / authoring-legitimate, authority flows
  contract→authoring) — sound, every cite verified, no engine leak. This is the synthesis's real contribution.
- **No fourth governance** (§2, R6a) — correctly enforced against `AUTHORITY-MODEL.md:57-59`.
- **Re-homing map unchanged** (§2) — B wins §1; verified against `DESIGN.md:37-44`. TAXONOMY/RELATIONSHIPS
  stay layering; TEST-PIPELINE stays validation with δ-rules private (`DESIGN.md:42`); the "~15% additive"
  framing is defensible *given CR-1..CR-5 applied*.
- **ontology-vault fenced by its own contract** (§1, §3) — `SKILL.md:66-71` genuinely disarms the
  spine-capture failure mode. Correct.
