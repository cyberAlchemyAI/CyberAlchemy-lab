---
node_type: research
role: skeptic
subject: glyph (external repo)
agent: "Wadler, Philip — precedent/ownership skeptic"
repo: domainspec-core
vector: minimize imports to genuine gaps; flag overshoot; build-from-owned over net-new
date: 2026-06-29
discipline: claim <= proof; skeptical in BOTH directions
---

# Glyph — Ownership Skeptic Verdict

**Me:** Wadler, Philip — the precedent/ownership skeptic for the **glyph** repo, working the `domainspec-core` corpus.
**Vector:** minimize imports to genuine gaps. A found owner = **build-from-owned, never a kill** (memory: precedent-sweep-owned-in-repo). I attack in both directions — I refuse to import what DomainSpec already owns, AND I refuse to inflate a glyph claim past its proof.

## What glyph actually offers (skim of README/USAGE/AGENT_WALKTHROUGH + examples)

Glyph is two things bolted together:
1. **A compact typed-intent DSL → multi-target codegen.** ~40-line `.glyph` file → lexer → recursive-descent parser → AST → conventions (smart defaults) → 7 generators emitting TS interfaces, Zod schemas, Postgres DDL (RLS + audit triggers), Express routers, guard JSON, rules middleware, pipelines. 8 block types: `type`, `model`, `transition`, `service`, `rules`, `guard`, `pipeline`, `task`. Opinionated invariants: every `service` needs a co-located `guard`; transitions must end `_ -> _: deny`; fields required by default.
2. **An agent-orchestration protocol.** `.glyph` as the inter-agent wire format (claimed ~92% token reduction vs. passing generated code); tier-specific system prompts (strategist/architect/executor/reviewer/utility) with per-tier model routing; `context_profiles.json` (scoped per-model context windows); `task` blocks → dependency DAG for orchestration.

DomainSpec's whole thesis is **typed-intent → reality with a defensible chain of custody**, and it already ships a subagents-strategy, a context-builder, and a distill. So my prior is: most of glyph is already owned. The sweep confirms that strongly.

---

## Verdicts by mechanism

### 1. Compact typed-intent DSL → multi-target codegen — **ALREADY-OWNED (build-from-owned)**

**Owner:** `implementation/domainspec/TAXONOMY.md` (25 meta-concepts) + `implementation/domainspec/development/deterministic-test-derivation-engine/{SPEC.md,ARCHITECTURE.md}` (the `parse → typed-graph G → pure δ → obligation_key → emit` deterministic pipeline) + the pipeline skills (`domainspec-pipeline`, `domainspec-spec-feature`, `domainspec-generate-tests`, `domainspec-implement`).

Glyph's 8 blocks are a **strict subset** of DomainSpec's 25-concept taxonomy, near 1:1:

| Glyph block | DomainSpec meta-concept (TAXONOMY.md) |
|---|---|
| `type` | Enum / Type, Value Object |
| `model` | Entity (+ classification annotations) |
| `transition` | **State Machine** (states + transitions + guards + effects + invariants) |
| `service` | Interface |
| `rules` | Rule / Policy |
| `guard` | Rule (backend) / Guard (UI) |
| `pipeline` | Workflow / Saga |
| `task` | (orchestration — owned by subagents-strategy, see §4) |

DomainSpec also owns the codegen-from-typed-source claim more rigorously than glyph: glyph's pipeline is a one-shot AST→string emit; DomainSpec's engine is **deterministic by construction** (same docs → byte-identical obligations), which is its load-bearing paper claim C2. Glyph makes no determinism claim.

**This is the heart of glyph and DomainSpec already owns it.** Importing glyph's DSL wholesale would be re-skinning the taxonomy with a terser surface syntax. **Not a kill** — the only *build-from-owned* seed here is the **concrete-syntax ergonomics** (see §6 / Gap-1), not the concept set.

### 2. Deny-by-default / classification-in-the-language — **ALREADY-OWNED (build-from-owned)**

**Owners (two, complementary):**
- **Forbidden-by-construction:** `implementation/domainspec/.claude/skills/ontology-view/` — the **forbidden-edge guard**: "make forbidden relationships *unconstructible by type* FIRST (no catalog edge admits the endpoint pair)" rather than asserted at runtime.
- **Exhaustive negative coverage:** `implementation/domainspec/TEST-PIPELINE.md` §"Invalid Transitions" — *"for every state × event combination NOT in the Transition Table, generate a rejection test."* That is deny-by-default, derived and tested, not merely declared.
- **Classification / ownership vocabulary:** `cyberAlchemy-v2/` ontology + mint authority-model (`classification`, `internal/confidential/restricted`, `owned by`/owner-route) and `arcanum/definitions/DEFINITIONS.md` (ownership/authority as first-class).

Glyph's `_ -> _: deny` wildcard and `[confidential, owned by customer]` annotations are a **weaker, runtime-only** version of what DomainSpec already encodes at the type/ontology layer and turns into exhaustive negative tests. DomainSpec's version is strictly stronger (unconstructible-by-type + derived rejection tests vs. a runtime guard string). **Build-from-owned at most**, never a kill.

### 3. Token-compression-as-protocol / scoped context profiles — **ALREADY-OWNED (build-from-owned), with OVERSHOOT on the number**

**Owner:** `implementation/domainspec/.claude/skills/domainspec-context-builder/SKILL.md` and arcanum `context-builder` (sigil) — *"minimal deterministic task context pack using selector-level retrieval, interested-data subsets, and strict relevance gates,"* with `lean|standard|deep` excerpt budgets, obligation-linked excerpts, `--strict` (every selected item must map to an obligation), and `--emit json|both` handoff packs. This is precisely glyph's `context_profiles.json` "each agent only loads what it needs" claim — and DomainSpec's version is **obligation-gated** (provably relevant), where glyph's is block-membership-gated (heuristic).

So the *mechanism* (scope each agent to only the slice it needs, emit a structured context pack) is **owned**. See OVERSHOOT-1 for why the headline number does not transfer.

### 4. Tier-specific agent prompts + per-role model routing + task-graph → DAG — **ALREADY-OWNED (build-from-owned)**

**Owner:** `domainspec-subagents-strategy` skill + `register-dispatch` + the live ledger `telemetry/agents/subagents-dispatch.yaml`. The ledger already records, per dispatch, groups with **roles as epistemic functions** (explorer/auditor/skeptic/writer), **per-agent `model:`** (`claude-opus-4-8`/`claude-sonnet-4-6`/`claude-haiku-4-5`), **`token_budget:`**, **`angle:`**, and an **`anti_bias:`** axis — i.e., tier-specific routing to the cheapest capable model is already operational practice, and richer than glyph's fixed 5-tier `TIER_MODELS` map (glyph has no anti-bias/tension layer at all).

Glyph's `task` block → dependency DAG (parent/depends/route/budget) maps onto: the **Workflow/Saga** meta-concept (orchestration with compensation) for the dependency graph, and the subagents-strategy dispatch sheet for routing+budget. DomainSpec additionally owns an **anti-bias / pairwise-tension** discipline (`anti-bias-vector-composition`, `check-tension`) that glyph's task graph entirely lacks. **Build-from-owned, not a kill.**

---

## Genuine gaps (honestly conceded)

### GAP-1 — A terse, parseable *concrete syntax* for the typed-intent layer — **GENUINE-GAP (narrow)**
DomainSpec's intent substrate is **Markdown spec artifacts** (`domain.md`, `operations.md`, `states.md`, …) consumed by the deterministic engine's parser. It owns the *concept model* and a *canonical machine-parseable doc schema*, but it has **no compact single-file PEG/EBNF surface syntax** like glyph's 6-lines-per-model. Glyph ships a **formal PEG grammar** (`grammar/`). DomainSpec's owners are the concept layer; a glyph-style terse front-end that *desugars into* the existing taxonomy + engine schema is a genuine ergonomic gap — *but it is a syntax skin over an owned engine, not a new capability.* Import as **seed for an alternate concrete syntax**, explicitly desugaring to TAXONOMY concepts, never as a parallel concept set.

### GAP-2 — Direct emit to a running Express/Postgres app from the typed source — **GENUINE-GAP, but see OVERSHOOT-2**
DomainSpec's deterministic engine's first emit target is **test obligations** (`emit_spec`/`emit_tests`, vitest), and code is generated by the LLM `domainspec-implement` path against contracts. Glyph emits **runnable RLS-bearing Postgres DDL + Express routers** directly from source. A *deterministic* runtime-code emitter (not just test emitter) is something DomainSpec has scoped but not shipped in the engine. Concede the gap — with the overshoot caveat below.

---

## Overshoot risks (import-as-described would exceed proof)

### OVERSHOOT-1 — "92% token reduction" is glyph's own measurement of glyph, not a DomainSpec result
The 92% / 12.3x figure in AGENT_WALKTHROUGH.md is glyph measuring `.glyph` source vs. *its own* generated TS/SQL/Express output, for *one* example. It is **not** a measured property of DomainSpec's context-builder, and it is not independently reproduced. Importing the *number* (or the framing "agents save ~350k tokens") would violate claim ≤ proof. Import the **mechanism** (already owned, §3); do **not** import the headline metric without DomainSpec running its own measurement.

### OVERSHOOT-2 — glyph's emit targets (Express/Postgres/Zod) may not match DomainSpec's engine target
DomainSpec's deterministic engine deliberately targets **TypeScript test artifacts** (Stryker/vitest) so determinism is provable against a mutation oracle; its architecture is functional/clean-layered (TAXONOMY appendix), not Express-router-shaped. Glyph's generators hard-code Express + raw `pg` + a specific RLS/audit idiom. Importing glyph's *generators* as-is would bind DomainSpec to a stack its engine doesn't target and would smuggle un-determinism-checked emit into a pipeline whose whole value is determinism-by-construction. The **gap (GAP-2) is real**, but the **import path is not glyph's generators** — it's "add a deterministic runtime-emit stage to the *owned* engine," targeting DomainSpec's own architecture.

### OVERSHOOT-3 — "one .glyph file replaces 8-12 handwritten files / writes a whole backend" framing
This is a productivity claim with no evidence beyond glyph's 4 examples. DomainSpec's discipline (CLAUDE.md: claim ≤ proof; Saturn/DomainSpec framed as *intended, not shipped*) forbids importing this rhetoric. Strip it; keep only the mechanism.

---

## Tally

- **ALREADY-OWNED (build-from-owned):** 4 — (1) typed-intent DSL→codegen [TAXONOMY + deterministic engine + pipeline skills]; (2) deny-by-default + classification [ontology-view forbidden-edge guard, TEST-PIPELINE negative derivation, cav2/arcanum ownership vocab]; (3) scoped context profiles / token-compression-as-protocol [domainspec-context-builder / arcanum context-builder]; (4) tier prompts + per-role model routing + task DAG [subagents-strategy + register-dispatch + dispatch ledger + Workflow/Saga].
- **GENUINE-GAP:** 2 — (G1) terse single-file concrete PEG syntax that desugars into the owned taxonomy; (G2) deterministic runtime-code emit (vs. test-only emit) — narrow, and bounded by OVERSHOOT-2.
- **OVERSHOOT-RISK:** 3 — (O1) the 92% number is glyph-on-glyph, not a DomainSpec measurement; (O2) glyph's Express/Postgres generators don't match DomainSpec's TS-test engine target; (O3) "writes a whole backend" productivity rhetoric is unproven.

**Skeptic's bottom line:** glyph is ~85% already owned. The defensible imports are two narrow *seeds* — a terse concrete syntax that desugars to the 25-concept taxonomy (G1) and a deterministic runtime-emit stage on the owned engine (G2) — and both must be built *into the existing owners*, not imported as glyph's grammar+generators wholesale. Every other glyph mechanism has a named DomainSpec owner. No KILL verdicts (none warranted; every candidate has an owner or a build-from-owned seed). Import the metrics at your peril.
