# Glyph Scout Report
**Scout**: Hejlsberg, Anders (forward-extraction, SCOUT vector)
**Repo**: glyph (read-only clone at `/tmp/.../scratchpad/assimilate/glyph`)
**Date**: 2026-06-29
**Mission**: Identify highest-leverage mechanisms glyph has that DomainSpec LACKS. Ranked. Claim <= proof.

---

## Ranked Import Candidates

### #1 — Homoiconic Task Blocks as Agent-Readable Work Items

**What it is**: The `task` block in glyph source compiles bidirectionally: `.glyph` → `work_items` SQL rows (D1), and `work_items` JSON → `.glyph` source (decompiler). Agents read and write tasks in the same language as the domain spec — zero translation layer. The orchestrator loads task graph state as Glyph, not prose or JSON.

**Source cite**:
- `compiler/src/codegen_taskgraph.js` — `generateTaskGraph()`, `compileTaskToWorkItem()`, `generateWorkItemsSQL()`
- `compiler/src/decompiler.js` — `decompileWorkItems()`, `decompileFullState()`
- `grammar/glyph.peg` — §9 `TaskDef` production

**Why it's leverage**: DomainSpec has a subagent-dispatch strategy (YAML telemetry, `subagents-dispatch.yaml`). What it lacks is a machine-readable, spec-level language for expressing work items that agents can read back verbatim. Today handoffs are prose + YAML. Glyph's homoiconic loop means an agent can receive its task as a Glyph block (typed, structured, budget-bounded), emit a modified block, and the orchestrator re-parses it — no ambiguity, no NL serialization cost.

**Adoption cost**: M (conceptual port — the `task` block grammar is ~20 lines of PEG, but wiring into DomainSpec's dispatch schema and telemetry layer takes thought)
**Leverage**: H
**Type**: IDEA-to-port (the mechanism is clean; the JS compiler is not the artifact to lift)

---

### #2 — Compiler-Enforced Guard Co-location (Guardrails as First-Class Language Construct)

**What it is**: Every `service` block requires a co-located `guard` block to compile. The compiler enforces this — no guard, no output. Guard blocks carry: `budget` ($/task), `classify` (data sensitivity tier), `escalate` (cost threshold → tier escalation), `sanitize`, `timeout`, `retry`, `audit`. These compile to `guards.json` — runtime configs consumed by the orchestration layer.

**Source cite**:
- `compiler/src/codegen_guards.js` — `generateGuardConfigs()`, full directive-to-JSON mapping
- `grammar/glyph.peg` — §7 `GuardDef` production
- `CLAUDE.md` — "A service CANNOT compile without a matching guard block"
- `examples/invoice_service.glyph` — canonical example

**Why it's leverage**: DomainSpec's sigil/spell system describes agent behavior but does not enforce co-located budget/classification/escalation constraints at the spec level. The glyph pattern is: constraints are not documentation — they are enforced by the compiler and emitted as machine-consumable config. Applying this to DomainSpec's sigil authoring (a sigil that touches `confidential` data must declare a `guard` block or fail validation) would close a correctness gap.

**Adoption cost**: S (the pattern is conceptual; enforcement is a validator rule, not a full compiler)
**Leverage**: H
**Type**: IDEA-to-port

---

### #3 — Compiler-Generated Scoped Context Profiles (Per-Task Agent Context Minimization)

**What it is**: For every task, service, and model block in the AST, the compiler generates a `context_profile_json` that lists exactly which types, models, services, transitions, rules, guards, and pipelines the assigned agent needs — and nothing more. The profile includes a token-budget estimate. Agents receive only the Glyph blocks listed in their profile, not the full codebase.

**Source cite**:
- `compiler/src/codegen_taskgraph.js` — `generateContextProfile()`, `generateAllContextProfiles()`, `generateServiceContextProfile()`, `estimateContextTokens()`
- `AGENT_WALKTHROUGH.md` — Phase 4 "Scope context per task" wiring example, token economics table

**Why it's leverage**: DomainSpec already uses scoped context discipline (sigils load minimal context), but the scoping is manually maintained in skill/sigil files. Glyph derives it deterministically from the AST — which models does this service reference? Which transitions apply to those models? Which guards match? The result is a machine-generated `required_context` map that an orchestrator can use to slice context without human curation. DomainSpec's subagent strategy would benefit from this being derived from the spec graph, not maintained by hand.

**Adoption cost**: M (requires a spec graph that can be traversed — depends on whether DomainSpec has a parseable AST or spec store; if spec definitions are in structured YAML/TOML this is a week's work)
**Leverage**: H
**Type**: IDEA-to-port

---

### #4 — Tier-Specific Agent System Prompts with Role-Appropriate Few-Shot Examples

**What it is**: Five distinct system prompt templates — `strategist`, `architect`, `executor`, `reviewer`, `utility` — each with role-appropriate few-shot Glyph examples rather than generic instructions. The strategist prompt shows task DAG decomposition. The reviewer prompt shows a flagging-and-correction cycle. The utility prompt shows compact context summarization. Model selection is mapped to tier: `strategist→claude-opus`, `utility→claude-haiku`.

**Source cite**:
- `compiler/src/agent_prompts.js` — full `TIER_PROMPTS` map, `getAgentPrompt()`, `BASE_PROMPT`
- `AGENT_WALKTHROUGH.md` — "How to Wire It Up", `TIER_MODELS` constant

**Why it's leverage**: DomainSpec's current subagent strategy (`domainspec-subagents-strategy` skill) routes tasks but does not enforce tier-differentiated system prompts with role-appropriate examples. The glyph pattern encodes what each tier *does* and what good output looks like, reducing off-rail behavior. Particularly valuable: the reviewer prompt's explicit checklist + flagging pattern is a direct import for DomainSpec's `review` skill.

**Adoption cost**: S (the prompts are prose/examples, portable immediately as Arcanum skill content)
**Leverage**: M-H (high for reviewer/utility tiers; the strategist/executor distinction DomainSpec may already cover partially)
**Type**: IDEA-to-port (the content pattern is the import, not the JS module)

---

### #5 — Deny-by-Default as a Grammar-Level Principle (Not a Convention)

**What it is**: Three language-level mechanisms enforce deny-by-default: (a) `transition` blocks must end with `_ -> _: deny` — the wildcard catch-all that blocks any unlisted state transition; (b) the conventions engine (`conventions.js` T1) auto-inserts this rule if absent; (c) model classification defaults to `internal` (not `public`), and service actions default to `auth` (not `public`). These are not docs or guidelines — the compiler applies them and reports every convention applied via `ConventionReport`.

**Source cite**:
- `compiler/src/conventions.js` — `applyTransitionConventions()` (T1), `applyModelConventions()` (M1), `applyServiceConventions()` (S2), `ConventionReport` class
- `grammar/glyph.peg` — `TransitionRule` with `_ -> _: deny` wildcard
- `CLAUDE.md` — "Key Rules: Every transition block should end with `_ -> _: deny`"

**Why it's leverage**: DomainSpec's constitution and governance layer has deny-by-default as a stated principle (CAV2-C13 governs-cycle). What glyph demonstrates is that this principle can be compiler-enforced and auditable — `ConventionReport` produces a record of every default applied, making the "what was implicit" surface explicit and reviewable. Porting this means DomainSpec's spec validation layer can emit a convention report alongside compiled artifacts.

**Adoption cost**: S (conceptual; the ConventionReport pattern is ~50 lines of audit bookkeeping)
**Leverage**: M
**Type**: IDEA-to-port

---

### #6 — Signal-Based Routing Class Inference (Keyword Scoring Over AST)

**What it is**: When a `task` block omits `route:`, the compiler infers the routing tier by scoring the task's `do:`, `accept:`, and `context:` fields against four signal wordlists (`STRATEGIST_SIGNALS`, `ARCHITECT_SIGNALS`, `REVIEWER_SIGNALS`, `UTILITY_SIGNALS`) plus structural signals (budget threshold, number of referenced services/models, `critical` priority). Returns `{ routingClass, confidence, reason }` with the reason string encoding which signals fired.

**Source cite**:
- `compiler/src/codegen_taskgraph.js` — `inferRoutingClass()`, signal constant arrays, `scoreSignals()`, `buildReason()`

**Why it's leverage**: DomainSpec's dispatch strategy (`domainspec-subagents-strategy`) routes tasks, but routing decisions are made by the LLM reading the task description. Glyph's pattern is deterministic: keyword scoring + structural heuristics → routing class + confidence score + human-readable reason string. This is auditable, repeatable, and cheap. The confidence score enables the orchestrator to escalate low-confidence inferences for human review. DomainSpec could apply this to its `telemetry/agents/subagents-dispatch.yaml` dispatch records.

**Adoption cost**: S (the scoring logic is ~100 lines; the signal wordlists are the real artifact to port and tune)
**Leverage**: M
**Type**: IDEA-to-port (the JS is trivially portable to any language)

---

### #7 — Bidirectional Decompiler (AST → Glyph Source, work_items → task blocks)

**What it is**: A decompiler (`decompiler.js`) that round-trips: any AST node can be serialized back to valid, compilable Glyph source. The `decompileWorkItems()` function converts live `work_items` database rows back to Glyph `task` blocks, and `decompileFullState()` reconstructs a complete `.glyph` file from AST + live work item state.

**Source cite**:
- `compiler/src/decompiler.js` — `decompile()`, `decompileWorkItems()`, `decompileFullState()`
- `AGENT_WALKTHROUGH.md` — Phase D4 "Bidirectional Mapping" commentary in codegen_taskgraph.js header

**Why it's leverage**: This closes the intent↔reality loop that Saturn is designed to close. If DomainSpec's spec layer can serialize current system state back to the intent DSL, an agent can compare the decompiled state against the authored spec and surface drift without human mediation. The decompiler is the mechanism that makes "is the implementation still consistent with the spec?" a computable question rather than a review task.

**Adoption cost**: L (requires a spec language with a parseable AST and a live state store to decompile from — this is a larger investment, but the pattern is proven here)
**Leverage**: H (architectural, aligns directly with Saturn's intent↔reality closure mission)
**Type**: IDEA-to-port

---

### #8 — Utility Agent as Compression Layer (Structured Context Summarization Protocol)

**What it is**: The `utility` agent tier has a defined role: after implementation and review, it generates compact context summaries (~150 tokens) that replace full generated code (~7,000+ tokens) for any future agent that needs registry context. The format is Glyph comment syntax — structured, not prose. The `AGENT_WALKTHROUGH.md` documents the exact summary format and the token economics.

**Source cite**:
- `compiler/src/agent_prompts.js` — `TIER_PROMPTS.utility` (full prompt with examples)
- `AGENT_WALKTHROUGH.md` — Phase 6 "Utility Compresses Context", the 150-token summary example, token economics table

**Why it's leverage**: DomainSpec's `distill` skill and inventory system (`arcanum/inventory`) serve a similar compression purpose, but without a defined agent tier or a canonical output format that downstream agents consume directly. Glyph's pattern makes compression a first-class phase in the build cycle with a typed output format. The ~150-token summary is the inter-session handoff artifact. DomainSpec's `close-session` skill could mandate utility-tier summarization output in a canonical format rather than free-form session notes.

**Adoption cost**: S (the prompt pattern and output format are immediately portable as a convention for `close-session` / inventory synthesis)
**Leverage**: M
**Type**: IDEA-to-port

---

## Priority Summary Table

| # | Candidate | Leverage | Cost | Type |
|---|-----------|----------|------|------|
| 1 | Homoiconic task blocks (bidirectional spec↔work-item) | H | M | Idea |
| 2 | Compiler-enforced guard co-location | H | S | Idea |
| 3 | Compiler-derived scoped context profiles | H | M | Idea |
| 4 | Tier-specific prompts + few-shot examples | M-H | S | Idea |
| 5 | Deny-by-default as compiler convention + audit report | M | S | Idea |
| 6 | Signal-based routing class inference (deterministic) | M | S | Idea |
| 7 | Bidirectional decompiler (state → spec source) | H | L | Idea |
| 8 | Utility agent as typed compression layer | M | S | Idea |

## Scout Notes

All candidates are IDEA-to-port. The glyph codebase is JavaScript and targets a specific TS/Postgres/Express stack — no literal code should be lifted. The mechanisms are the import: the grammar designs, compiler enforcement patterns, agent protocol conventions, and token-economics thinking.

The two highest-impact imports are **#1** (homoiconic task blocks closing the dispatch↔spec gap) and **#3** (compiler-derived context profiles replacing hand-curated agent context loading). Both require DomainSpec to have a spec graph that can be traversed — which is the precondition check for the skeptic audit to verify.

**#7** (bidirectional decompiler) is the Saturn alignment candidate — highest architectural leverage but highest adoption cost. Flag for Saturn roadmap, not near-term sprint.
