<!-- Scout: Hoare, Tony | Repo: juxt/allium (v3.6.0) | Date: 2026-06-29 -->

# Allium Scout Memo — Tony Hoare
**Repo:** juxt/allium (v3.6.0, read from clone at assimilate/allium)
**Vector:** maximize assimilable surface — mechanisms allium has that DomainSpec LACKS

---

## Framing: what I'm comparing against

DomainSpec currently has:
- A **25-concept taxonomy** (TAXONOMY.md) covering Entity, Value Object, State Machine, Operation, Rule, Workflow, Saga, etc.
- Markdown-based spec artifacts per feature (SPEC.md, states.md, operations.md, events.md, interfaces.md)
- A **deterministic test-derivation engine** (CLI) that reads those artifacts and emits backend test obligations
- Skills for spec-first development (domainspec-spec-feature), alignment audit (domainspec-audit-alignment), and test generation (domainspec-generate-tests)
- Discovery-first gating: spec-writing is blocked without a prior discovery artifact

What DomainSpec does NOT yet have (from observable evidence):
- A formal behavioural language with machine-checkable grammar
- Transition graph declarations embedded in entity specs (lifecycle is described in Markdown state-machine tables, not a formal graph)
- Structural CLI analysis across rules (missing-producer detection, deadlock detection, unreachable-transition detection)
- Bidirectional spec↔code reconciliation as a named, automated skill
- Library/module spec composition and cross-module references
- Formal surface/boundary contracts with typed signatures

---

## Candidates (ranked by leverage)

---

### 1. Bidirectional spec↔code reconciliation (`/weed`)

**What it is:** A named, autonomous skill that compares `.allium` specs against implementation code, classifies every divergence (spec bug / code bug / aspirational / intentional gap), and can fix in either direction on request.

**Source cite:** `skills/weed/SKILL.md` — entire file; see especially the "Modes" section (lines 19–26) and "Process-level checks" (lines 33–42): transition reachability in code, surface-trigger coverage, invariant enforcement, bottom-up process reconstruction.

**Gap in DomainSpec:** `domainspec-audit-alignment` exists but is one-way and report-only (classifies items as compliant/partial/missing/extra, emits a remediation list). It does not reconstruct the lifecycle from code, propose which direction to fix, or write back to specs. There is no "update code to match spec" direction at all.

**Why it's leverage:** Saturn's loop is "intent↔reality with evidence." Weed is the mechanism that closes that loop at the implementation boundary. DomainSpec can emit test obligations but cannot currently detect that the running code has drifted from the spec in ways that don't show up as failing tests (e.g. a new state transition added to the code that the spec never declared).

**Leverage: H | Adoption cost: M** — The skill protocol (modes, divergence classification, process-level checks) is the hard part; the actual code-reading is already done in audit-alignment. Port the classification taxonomy and add the code→spec reconstruction direction.

---

### 2. Formal transition graph with CLI-enforced completeness obligations

**What it is:** An inline declaration on entity status fields that lists valid edges, terminal states, and forces two completeness checks: (a) every non-terminal state has at least one outbound edge, (b) every declared edge is witnessed by at least one rule. The CLI enforces both automatically.

**Source cite:** `skills/allium/SKILL.md` lines 268–302 (Transition graph syntax); `skills/allium/references/language-reference.md` lines 542–581 (full spec: edges, terminal states, completeness obligations, drift-as-error). The `allium check` hook (`hooks/allium-check.mjs` lines 166–168) runs `allium check <file>` automatically post-write.

**Gap in DomainSpec:** DomainSpec's `states.md` artifacts describe state machines in Markdown tables. There is no machine-checkable graph, no CLI validation that every declared transition has a witnessing operation, and no terminal-state obligation. The test-derivation engine can derive test obligations from states.md, but cannot detect that a declared state transition has no witnessing operation in the spec itself.

**Why it's leverage:** DomainSpec's correctness moat depends on the spec being authoritative. A state machine declared in Markdown with no graph validator is an unverified claim. The allium transition graph pattern — declare edges inline on the entity, let the CLI prove completeness — makes the lifecycle a checkable artefact, not just documentation.

**Leverage: H | Adoption cost: M** — Requires extending the spec language (states.md or a new entity section) with a formal edge list and hooking the test-derivation engine to validate witnessing. Does not require a new tool from scratch; the existing engine could absorb this.

---

### 3. `open question` declarations as first-class spec citizens

**What it is:** A named syntactic slot in the spec for unresolved design decisions. `open question "Admin ownership - should admins be assigned to specific roles?"` — recorded formally, surfaced by `allium check`, treated as a convergence invariant: the loop is not done until the open questions section is empty.

**Source cite:** `skills/allium/SKILL.md` lines 306–308 (syntax); `skills/allium/references/recommended-loops.md` lines 26–29 (convergence invariant — "no open questions remain" is an explicit exit condition alongside tests-pass and weed-clean); `skills/elicit/SKILL.md` lines 284–291 (surface ambiguity explicitly, record as open question rather than guessing).

**Gap in DomainSpec:** DomainSpec has discovery as the upstream mechanism for resolving ambiguity before spec-writing. But within an active spec, there is no formal slot for "I know this is unresolved." Unresolved questions either block spec-writing entirely (the discovery gate) or get silently assumed in the spec. There is no convergence condition that checks "are there known unknowns still open?"

**Why it's leverage:** The instruction "escalate genuine ambiguity to the human rather than guessing" is a standing rule in multiple DomainSpec skills. But there is no structural enforcement. Adopting `open question` as a first-class field in SPEC.md (with a CI/lint gate that fails if any are present at ship time) makes the rule enforceable, not just advisory.

**Leverage: H | Adoption cost: S** — Pure documentation/schema extension to SPEC.md. No new tooling needed. The test-derivation engine could emit a warning when open questions are present. Very low friction adoption path.

---

### 4. `surface` + `contract` as boundary specification primitives

**What it is:** `surface` declares what an external party (actor) can see (`exposes`) and do (`provides`) at a named boundary, scoped to an entity context. `contract` declares typed obligation interfaces (`serialize: (value: Any) -> ByteArray`) referenced by surfaces with `demands`/`fulfils` direction. Together they give every boundary a machine-readable contract, not just a prose description.

**Source cite:** `skills/allium/SKILL.md` lines 179–222 (surface syntax, contract syntax, surface-to-implementation contract); `skills/allium/references/language-reference.md` lines 130–198 (contracts full spec); `skills/allium/references/patterns.md` Pattern 9 (framework integration contract with expression-bearing invariants and `demands`/`fulfils`).

**Gap in DomainSpec:** DomainSpec has `interfaces.md` per feature, which describes REST/GraphQL/module contracts in Markdown. The `domainspec-audit-alignment` skill checks whether implementation matches the interface description, but the interface description itself has no formal type or direction constraint (demands vs fulfils). There is no concept of an actor-facing boundary scope.

**Why it's leverage:** DomainSpec's implementation pillar needs to produce boundaries, not just domain logic. The current `interfaces.md` is a documentation layer; allium's `surface` is a checkable contract layer. Adopting surface-style scoping would let the test-derivation engine generate actor-restriction tests and context-scoping tests automatically, which today require manual specification.

**Leverage: H | Adoption cost: L** — Requires a significant spec language extension (new artifact type or new section in SPEC.md for surfaces + contracts, new test-derivation engine rules). Worth planning for DomainSpec v2; not a quick add.

---

### 5. Post-write CLI hook for automated structural validation

**What it is:** A multi-editor-compatible post-write hook that runs `allium check <file>` automatically whenever a `.allium` file is written, surfaces diagnostics inline to the model, and shows a one-time install notice if the CLI is absent (then stays quiet). The hook handles Claude Code, Cursor, Windsurf, and Aider from one script.

**Source cite:** `hooks/allium-check.mjs` — full file (185 lines); especially the multi-IDE input normalization (lines 131–135: handles `tool_input.file_path`, `file_path`, `tool_info.file_path`), the per-machine install-notice marker logic (lines 11–39), and the `CLAUDE_PROJECT_ROOT` / `workspace_roots` project-root resolution (lines 148–163).

**Gap in DomainSpec:** The test-derivation engine (`node tools/test-derivation-engine/dist/cli.js derive {feature}`) is invoked manually inside skills, not as a hook. There is no automatic post-write validation of spec artifacts. The `domainspec-generate-tests` skill documents that you MUST NOT edit inside the ENGINE-REGION fence, but there is no automated drift check running on every write.

**Why it's leverage:** The allium hook pattern shows exactly how to wire a deterministic checker into the LLM's write loop without requiring the LLM to remember to run it. The per-machine "show once" notice is a production-quality UX detail that prevents hook noise from degrading the session. DomainSpec's engine drift check (`cli.js check {feature}`) is the natural candidate for this pattern.

**Leverage: M | Adoption cost: S** — The hook script pattern is essentially copy-adaptable. Replace `.allium` extension detection with DomainSpec's artifact types (e.g. `SPEC.md`, `states.md`, `TEST-SPEC.engine.md`), replace `allium check` with `cli.js check {feature}`. Wire into `.claude/settings.json` hooks.

---

### 6. Code-first distillation as a named, structured skill (`/distill`)

**What it is:** A skill that works backward from implementation code to produce a behavioural spec — filtering out implementation detail (DB schemas, API paths, ORM calls, tokens) through three discipline tests ("Why test", "Could it be different? test", "Template vs Instance test") and producing a spec that captures intended behaviour, not accidental behaviour.

**Source cite:** `skills/distill/SKILL.md` — full file (816 lines); especially the seven-step process (lines 319–586): map the territory, extract entity states, identify candidate processes, extract transitions, find temporal triggers, identify external boundaries, abstract away implementation. Also the worked translation table at lines 428–437 (code pattern → spec pattern).

**Gap in DomainSpec:** `domainspec-brownfield-translation` exists and is the closest equivalent, but it translates "as-is" artifacts from code + docs. It does not have an explicit discipline for separating intended from accidental behaviour, nor the three abstraction tests allium's distill skill applies systematically. The distinction between "code bug" (don't bless as spec) and "intentional behaviour" (include in spec) is not structurally enforced.

**Why it's leverage:** DomainSpec's brownfield translation skill is a high-value entry point (existing codebases → DomainSpec). The allium distill discipline directly improves its correctness: the "Would we rebuild this?" test, the "could it be different?" test, and the step-2.5 "identify candidate processes from state machines before assigning transitions" are not in the current brownfield skill.

**Leverage: M | Adoption cost: S** — Pure skill-layer addition. Enrich `domainspec-brownfield-translation/SKILL.md` with the three abstraction tests and the process-identification step. No new tooling.

---

### 7. Spec maturity assessment as a routing gate

**What it is:** Before doing any analysis, check what constructs are present in the spec and route to the appropriate action — "coarse spec" (entities + transition graphs, no rules) → fill in rules; "detailed spec with rules" → gap analysis; "spec with surfaces" → validation. The checker only runs `allium analyse` (process-level) when the spec has both witnessing rules and surfaces defined.

**Source cite:** `skills/allium/references/assessing-specs.md` — full file (67 lines); especially the per-entity assessment checklist (lines 25–33) and the `check` vs `analyse` routing (lines 35–43).

**Gap in DomainSpec:** DomainSpec skills (generate-tests, audit-alignment) run their full process regardless of spec maturity. If `states.md` has no witnessing operations yet, the test-derivation engine still runs and produces thin output without flagging that the spec isn't ready for meaningful test derivation. There is no explicit maturity gate.

**Why it's leverage:** The maturity gate prevents a well-known failure mode: the LLM produces a test spec from a coarse feature spec, the developer believes coverage is good, but the tests are vacuous because the spec never captured the rules. The allium pattern (check maturity → route to the right phase) is directly adoptable as a pre-condition in `domainspec-generate-tests` and `domainspec-audit-alignment`.

**Leverage: M | Adoption cost: S** — Add a maturity-check step at the top of both skills. Map DomainSpec's artifact inventory (which files exist, which sections are populated) to maturity levels. No new tooling.

---

## What NOT to import (discipline)

- **The `.allium` language itself** — DomainSpec already has a 25-concept taxonomy and Markdown-based artifacts. Replacing the spec language wholesale is not an import, it's a rewrite. The value is in the mechanisms, not the syntax.
- **The Allium governance panel** (nine-member design review) — DomainSpec has its own authority-promotion governance in cyberAlchemy-v2. No parallel.
- **Library spec composition (`use "github.com/..."`)** — the module system is valuable but depends on allium's immutable coordinate system (git SHAs). Worth researching separately once DomainSpec's spec language is more formalized. Not ready to import now.

---

## Priority ranking summary

| # | Candidate | Leverage | Cost | DomainSpec gap severity |
|---|-----------|----------|------|------------------------|
| 1 | Bidirectional spec↔code reconciliation (`/weed`) | H | M | High — Saturn loop is incomplete without it |
| 2 | Formal transition graph with CLI completeness | H | M | High — lifecycle specs are unverified claims |
| 3 | `open question` declarations as convergence gate | H | S | Medium — discovery gate helps but doesn't cover in-flight ambiguity |
| 4 | Surface + contract boundary primitives | H | L | Medium — interfaces.md exists but is unchecked |
| 5 | Post-write CLI hook for automated validation | M | S | Medium — engine drift check exists but is not auto-wired |
| 6 | Code-first distillation discipline (3 abstraction tests) | M | S | Low-medium — brownfield skill exists, needs sharpening |
| 7 | Spec maturity assessment as routing gate | M | S | Low-medium — skills run regardless of spec completeness |

---

## One sentence per candidate for rapid triage

1. **Weed:** Import the divergence-classification taxonomy and the bidirectional reconciliation protocol into `domainspec-audit-alignment`; add the "update code" mode DomainSpec currently lacks entirely.
2. **Transition graph:** Add a formal edge-list declaration to `states.md` and wire it into the test-derivation engine to check witnessing + completeness; this makes lifecycle specs checkable, not just descriptive.
3. **Open question:** Add `open_questions: []` as a required field in SPEC.md frontmatter and make the test-derivation engine fail (with advisory) if any are populated at derivation time.
4. **Surface/contract:** Plan for DomainSpec v2 spec language: a `surfaces:` section per feature that formalizes actor-boundary contracts with typed signatures, replacing/extending interfaces.md.
5. **Post-write hook:** Adapt `allium-check.mjs` to run `cli.js check {feature}` on every write to DomainSpec spec artifacts; wire via `.claude/settings.json` PostToolUse hook.
6. **Distillation discipline:** Enrich `domainspec-brownfield-translation/SKILL.md` with allium's three abstraction tests and the "separate intended from accidental behaviour" step.
7. **Maturity gate:** Add a spec-maturity pre-check to `domainspec-generate-tests` and `domainspec-audit-alignment` that routes to the appropriate phase rather than running the full process on a coarse spec.
