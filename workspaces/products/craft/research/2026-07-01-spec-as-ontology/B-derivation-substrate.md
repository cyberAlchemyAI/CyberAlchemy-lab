---
node_type: research
position: B · derivation-substrate
question: Should DomainSpec v2 treat its spec surface as a SYSTEM ONTOLOGY?
created: 2026-07-01
discipline: claim ≤ proof; cite by path; mark residue
---

# B · Derivation-Substrate — the spec is a derivation source, ontology is at most an overlay

## 1. Thesis

The spec surface (aspect files + TAXONOMY + RELATIONSHIPS) is fundamentally a
**derivation source**: a typed input the deterministic engine compiles into byte-stable
test obligations. Its identity is set by *what bites* — the engine's `derive` step and the
build-time validators — not by whether it also reads as a knowledge graph. "Spec-as-ontology"
is a true but *secondary* description: a read-lens / projection you can lay over the same
files. Making ontology the **backbone** of Batch-1 risks importing ceremony (roles, confidence
gates, branch bridges, premises) that no downstream compiler consumes — governance vocabulary
without enforcement. The reformulation should stay **derivation- and governance-centric**; the
owned `ontology-vault` sigil should enter, if at all, as an **optional projection**, never the spine.

## 2. Strongest evidence FOR the position

**E1 — The spec is literally a compiler input.** The engine README states the pipeline as
`parse (docs → G) → derive (δ: pure) → obligation_key (sha1) → emit_spec / emit_tests`
(`impl/test-derivation-engine/README.md` L14), with the parser producing a "typed concept
graph `G`" (L16) and δ carrying "exact cardinalities" (L18). TAXONOMY's 25 types and
RELATIONSHIPS' 29 edges are the *node/edge alphabet of G* — the grammar the compiler parses.
That is the definition of a derivation source, established by construction, not by analogy.

**E2 — The governances are derivation/validation shaped, not ontology shaped.**
`authority/AUTHORITY-MODEL.md` Core Rule: DomainSpec can "type … derive … validate … rule …
measure drift." Its Methods catalogue (L71–73) binds every governance to a *runnable method*:
validation → engine `derive`+`lint`, `TEST-PIPELINE.md`; layering → `audit-layering`, the
TAXONOMY layer-law, the RELATIONSHIPS Edge-Law; drift → the 5-surface ledger. None names an
ontology substrate. The spine already exists and it is derivation/governance, ratified 2026-06-29.

**E3 — `ontology-vault` disclaims spine authority in its own contract.** Its outputs "are not
promotion verdicts, source authority, spec mutations, runtime conformance verdicts, or canonical
source edits" (`.claude/skills/ontology-vault/SKILL.md` L67–71); it "block[s] profile outputs
that would mutate specs, canonical sources, runtime conformance, or promotion state without
owner approval" (L251–254). By design it *reports on* a governance surface; it cannot *be* one.
`paired-views` is the same shape — an explanation triad for "more than one audience"
(`.claude/skills/paired-views/SKILL.md` L28), whose single-owner invariant governs *documents*,
not derived obligations. These are lenses, and they say so.

**E4 — The spec's authority is "source of obligations," per Non-Collapse Rule 5.** "Expected
values come from the spec, never from running the implementation" (AUTHORITY-MODEL L158). The
spec's load-bearing role is to *dictate obligations a compiler derives and a test asserts* — an
active, checkable function. An ontology's role is to *name and relate concepts consistently* — a
passive, descriptive function. Rule 5 privileges the former.

**E5 — What bites is the engine + validators, not the graph.** DESIGN §1 (L49–50): "the engine
consumes TAXONOMY/RELATIONSHIPS + the feature packs; the validators (`validate-code-tags`,
`validate-relationships`, engine `lint`) enforce the layering + validation surfaces at build
time." Enforcement is deterministic and mechanical. Ontology consistency (one-home-per-term,
confidence) is *advisory* unless a compiler rejects on it — which nothing here does.

## 3. Concrete implications for the Batch-1 reformulation

The B-position **preserves** the existing DESIGN re-homing map (`development/reformulate-batch1/DESIGN.md`
§1) rather than replacing it — and hardens three doc bindings against ontology creep:

- **TEST-PIPELINE (R4) stays the spine's keystone.** Reformulate it as the deterministic
  *derivation contract* (spec construct → obligation class), δ-rules private (moat, Non-Collapse
  Rule 6). Do NOT reframe it as "the ontology's inference rules"; the contract is a compiler
  interface, not a semantic-web ruleset.
- **TAXONOMY (R2) + RELATIONSHIPS (R3) bind to LAYERING as an *alphabet + edge-law*, not a
  vocabulary.** Keep the framing "the type set `validate-code-tags` checks" / "edge-law … forbidden
  set unconstructible" (DESIGN §1). An ontology reading (concept graph, navigation paths — already
  in `RELATIONSHIPS.md` L327–390) can be noted as a *derived read-view*, explicitly non-normative.
- **CONSTITUTION (R6a) crosswalk keeps three governance owners, not a fourth "ontology governance."**
  Every v1 C-rule maps to validation/layering/drift or DROP (DESIGN R6a). Introducing an ontology
  owner would violate the ratified three-governance model (AUTHORITY-MODEL Authority Kinds) and add
  an owner with no runnable method.
- **Optional projection, gated.** IF a spec-as-ontology view is wanted, add it as a *Batch-3+*
  optional artifact produced by `ontology-vault --profile` / `paired-views` over the spec —
  read-only, non-authoritative, with the sigil's own "not source authority" contract (E3) enforced.
  It never re-homes a Batch-1 doc.

Net: the ontology framing changes **zero** of the six reformulation targets' owners; it earns at
most one optional appendix ("the spec as a read-graph") plus a Batch-3 projection route.

## 4. Strongest objection + rebuttal

**Objection.** RELATIONSHIPS is *already* a typed concept graph with roles, navigation paths, and
a registry (`RELATIONSHIPS.md` L327–420) — that IS an ontology. `ontology-vault`'s branch-aware
model (business/system/bridge, `SKILL.md` L37–47) maps almost one-to-one onto DomainSpec's
backend/UI/cross-layer split, and its drift edges (`drifts_from`, L151) mirror drift governance.
So ontology isn't foreign ceremony — it's the *native* shape, and making it the spine would unify
layering + drift under one owned, already-built governance instead of three bespoke ones. Refusing
it is reinventing what `ontology-vault` already provides.

**Rebuttal.** The structural resemblance is real but does not transfer *authority*. Two reasons.
(a) **Enforcement asymmetry.** The graph resemblance buys nothing the engine doesn't already
consume; `ontology-vault` explicitly cannot mutate specs or issue verdicts (E3), so adopting it as
spine would relabel the backbone while the *actual* bite stays with `derive`/`lint`/`validate-*`.
That is ceremony-over-enforcement — precisely the failure mode. (b) **The map is a lossy overlay,
not an isomorphism.** `ontology-vault` confidence/premise/promotion machinery has no counterpart
in a deterministic derivation (obligations are derived, not *promoted* by confidence); its bridge
edges are *evidence-gap trackers*, whereas DomainSpec's cross-layer edges are *derivation inputs*
that generate contract/E2E tests (`TEST-PIPELINE.md` L307–360, cross-layer → tests). Forcing the
spec under the vault contract would demote hard obligations to soft "claims." The correct move is
the converse: keep derivation as substrate, and let `ontology-vault` *read* it — which is exactly
what its `--profile … --runtime inline` projection mode is for (`SKILL.md` L49–71). Overlay, adopted
on its own terms; not spine.

## 5. Residue (unverified)

- **R1 — δ-rule / concept-type completeness.** Whether every TAXONOMY type + RELATIONSHIPS edge has
  a live δ-rule is unverifiable here: the engine README says parser and δ are "typed stubs"
  (`README.md` L25), and I did not (must not) read `src/rules`. If coverage is thin, the "engine is
  what bites" claim is *aspirational* for the uncovered types — a strength gap, not a position flaw.
- **R2 — Whether any planned consumer reads ontology metadata.** I found no compiler/validator that
  consumes confidence/premise/role fields; absence-of-evidence, not proof none is planned.
- **R3 — UI-11 derivation.** DESIGN D2 leaves open whether UI concepts derive obligations or are
  layering-only. If UI is layering-only, the "derivation substrate" claim is backend-scoped and the
  ontology overlay is comparatively *more* attractive for the UI surface — a bounded concession.
- **R4 — Drift-surface reconciliation (DESIGN D1).** Unresolved; if the drift model absorbs
  `ontology-vault` drift edges, the overlay boundary would need re-drawing. Owner decision pending.
