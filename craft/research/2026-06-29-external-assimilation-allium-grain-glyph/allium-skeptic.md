# Allium Skeptic Memo — Dijkstra, Edsger (repo: allium)

Role: precedent/ownership SKEPTIC. Vector: minimize imports to genuine gaps. Counter scout
enthusiasm by naming what DomainSpec ALREADY owns; flag any candidate whose import would
overshoot claim ≤ proof. Assessed independently of the scout's list (not read).

Discipline applied: the precedent-sweep rule (`MEMORY: precedent-sweep-owned-in-repo`) — a
found owner in-repo is **build-from-owned**, NEVER a kill. I am also skeptical the *other*
way: I refuse to manufacture an owner that isn't really there, and I name the two real seams.

---

## What allium actually is (so we judge the mechanism, not the marketing)

A behavioural-spec language (`.allium`: entities + value/sum types + `when/requires/ensures`
rules + transition graphs (v3) + surfaces/contracts + invariants + `open question`), a
six-skill loop (`/elicit /distill /tend /weed /propagate` + `/allium` router), and an
optional Rust CLI (`allium check / analyse / plan / model`) doing semantic inference, gap
findings, and test-obligation generation, plus an editor post-write validation hook.
Crucially: "Allium has no compiler and no runtime… purely descriptive… LLMs already function
as pseudocode compilers" (README) — and the CLI's test generation is **LLM-mediated at the
implementation bridge** (propagate SKILL: "The implementation bridge is LLM-mediated").

That last fact is the load-bearing one for several verdicts below.

---

## Verdict table

| # | Mechanism (as allium offers it) | Verdict | DomainSpec owner |
|---|---|---|---|
| 1 | Behavioural spec substrate (entities/rules/states/events/boundaries) as primary artifact | ALREADY-OWNED | `implementation/domainspec/TAXONOMY.md` (25 meta-concepts) |
| 2 | Code-first distillation discipline (`/distill`) | ALREADY-OWNED | `domainspec-brownfield-translation` skill |
| 3 | Bidirectional spec↔code reconciliation (`/weed`) | ALREADY-OWNED | `domainspec-audit-alignment` + `DRIFT-CONVERGENCE.md` |
| 4 | Test generation from spec (`/propagate`) | ALREADY-OWNED (and DomainSpec's is *stronger*) | `tools/test-derivation-engine/` + `TEST-PIPELINE.md` + `domainspec-generate-tests` |
| 5 | Formal transition graph + completeness/reachability | ALREADY-OWNED | `TAXONOMY.md` (State Machine) + `TEST-PIPELINE.md` |
| 6 | Open-question convergence gate / spec-maturity routing | ALREADY-OWNED | `domainspec-spec-feature` discovery gate + `readiness-gate`/`decision-gate`/`verify-feature` |
| 7 | Surface/contract boundary primitives | ALREADY-OWNED | `TAXONOMY.md` (Interface, Mapping, Event) |
| 8 | Forced contradiction surfacing *by structure of a constrained grammar* | OVERSHOOT-RISK | (see below) |
| 9 | Harness-enforced post-write **spec validator** hook on the spec artifact | GENUINE-GAP (narrow) | partial: PreToolUse Write\|Edit hook exists but validates frontmatter, not spec semantics |

---

## ALREADY-OWNED (build-from-owned) — with citations

### 1 — Behavioural spec substrate → `TAXONOMY.md`
Allium's `entity / value / enum / rule / state-transition / event / surface` set is a near
one-to-one subset of DomainSpec's 25 meta-concepts: Entity, Value Object, Enum/Type, **Rule**
("formal expression… directly testable"), **Operation** (input → rules → calculations →
state transition → postconditions → error states — i.e. allium's `requires/ensures`),
**State Machine** (states + transitions + guards + effects + invariants), Event, Interface,
Mapping. Allium's `when/requires/ensures` rule *is* DomainSpec's Operation+Rule pairing
(`requires` = Rule guards / preconditions; `ensures` = postconditions + state transition +
event emission). **Owner: `implementation/domainspec/TAXONOMY.md`.** Importing the allium
language wholesale would duplicate this spine in a second notation — a duplicate-terminology
trap that allium's own `/distill` skill warns against ("Duplicate terminology… treat it as a
blocking problem").

### 2 — Code-first distillation (`/distill`) → `domainspec-brownfield-translation`
Allium `/distill` = "extract a spec from existing code, filter out implementation detail,
'would we rebuild this?' test, tag observed vs intended." DomainSpec's brownfield skill does
exactly this: audits `src/**`, builds an as-is feature inventory with confidence labels
(`observed / stated / hypothesized` — allium has no equivalent confidence taxonomy),
abstracts implementation detail into TAXONOMY artifacts, and emits ONTOLOGY-GAPS /
GOVERNANCE-GAPS. **Owner: `.claude/skills/domainspec-brownfield-translation/SKILL.md`.** The
distill *judgement heuristics* ("why does the stakeholder care?", "could it be different?",
template-vs-instance) are well-articulated in allium and DomainSpec's skill states the policy
more tersely — a possible prose-enrichment, not a new capability (see "what's genuinely
worth borrowing" below).

### 3 — Bidirectional reconciliation (`/weed`) → `domainspec-audit-alignment` + `DRIFT-CONVERGENCE.md`
Allium `/weed` = find divergences spec↔code, classify (spec bug / code bug / aspirational /
intentional gap), update either direction. DomainSpec's audit skill classifies each item
`compliant / partial / missing / extra` and emits prioritized remediation; `DRIFT-CONVERGENCE.md`
is the canonical home of the divergence concept (semantic/contract/runtime/governance/
coordination drift) and the convergence-trend definition — a *broader* frame than allium's
construct-by-construct diff. **Owners: `.claude/skills/domainspec-audit-alignment/SKILL.md`
and `implementation/domainspec/DRIFT-CONVERGENCE.md`.**

### 4 — Test generation (`/propagate`) → `tools/test-derivation-engine/` (DomainSpec is STRONGER)
This is the verdict where the asymmetry runs in DomainSpec's favour and is the moat-relevant
one. Allium `/propagate`: "Deterministic tools guarantee completeness… You handle the
implementation bridge" and "The implementation bridge is **LLM-mediated**." DomainSpec's
engine: "Compiles canonical Markdown feature docs into byte-stable test obligations — **with
no LLM and no network** in the derivation path, so determinism holds by construction"
(`tools/test-derivation-engine/README.md`), with `obligation_key = sha1(...)`, a δ pure rule
set, and an L0 round-trip falsification gate. The `domainspec-generate-tests` skill is
ENGINE-FIRST and forbids the LLM from authoring backend obligations ("You MUST NOT edit
inside the fence"). **Owner: `tools/test-derivation-engine/` + `TEST-PIPELINE.md` +
`.claude/skills/domainspec-generate-tests/SKILL.md`.** Importing allium's propagate as the
test path would be a *downgrade* (LLM-mediated where DomainSpec is deterministic-by-construction).
This is precisely the proprietary deterministic-engine moat (`MEMORY: engine-algorithm-proprietary`).
KILL as an import-of-mechanism; the only thing allium adds here is a richer *obligation
taxonomy enumeration* (PBT for invariants, state-machine action-map walks, data-flow-chain
tests) — a checklist to audit our δ rule coverage against, not a capability to adopt.

### 5 — Transition graph + reachability/completeness → `TAXONOMY.md` State Machine + `TEST-PIPELINE.md`
Allium v3 `transitions { … terminal: … }` + analyse's reachability/deadlock findings.
DomainSpec's State Machine meta-concept already carries "states, valid transitions, guards,
effects, invariants" and `TEST-PIPELINE.md` already derives: every transition row → 1 test;
**every state × event NOT in the table → a rejection test**; terminal-state no-outbound
tests; invariants → PBT "for all reachable states." That is the same completeness/reachability
surface allium's `analyse` claims. **Owner: `TAXONOMY.md` (State Machine) + `TEST-PIPELINE.md`.**

### 6 — Open-question gate + spec-maturity routing → discovery gate + readiness/decision gates
Allium's "done when… no open questions remain" + `assessing-specs` maturity routing (don't
run process-level checks on a coarse spec). DomainSpec owns both halves:
`domainspec-spec-feature` has a hard **discovery-existence precondition** that HALTs spec
authoring until a discovery (the open-question / intent artifact) exists or is explicitly
waived; `domainspec-readiness-gate` (profiles pilot/release-candidate/production) and
`domainspec-decision-gate` enforce "blocker-level decisions resolved" before progression;
`domainspec-verify-feature` is the convergence check. **Owners: `domainspec-spec-feature`,
`domainspec-readiness-gate`, `domainspec-decision-gate`, `domainspec-verify-feature`.**
DomainSpec's gate is *governance-grade* (planner gate, evidence, profiles); allium's is a
loop exit-condition note. Build-from-owned.

### 7 — Surface/contract boundary primitives → `TAXONOMY.md` Interface/Mapping/Event
Allium `surface` (facing/exposes/provides/contracts) + module-level `contract` (typed
signatures + `@invariant`). DomainSpec: **Interface** ("API boundary… request/response
shapes and the domain concepts they expose"), **Mapping** (field-by-field shape transform at
a boundary, with direction inbound/outbound/bidirectional), **Event** (typed payload +
consumers). The allium `exposes` field-level contract = DomainSpec Interface request/response
"Maps To" columns. **Owner: `TAXONOMY.md` (Interface, Mapping, Event).**

---

## OVERSHOOT-RISK — do not let this become a claim

### 8 — "Structure forces contradictions to surface on their own"
Allium's headline claim (README): "two rules with incompatible preconditions expose the
conflict without anyone needing to be clever enough to spot it… the structure does that work."
**This overshoots what allium's own artifact sustains.** Allium "has no compiler and no
runtime… purely descriptive, defined entirely by its documentation"; the contradiction
detection that isn't trivially syntactic is performed by the **CLI's semantic inference**
(`allium analyse`, a separate closed repo `allium-tools`) and, where that's absent, by the
**LLM reading the grammar**. So the mechanism is either (a) a separate semantic checker we
don't have the source for, or (b) LLM-mediated. DomainSpec must NOT import the *claim* that a
constrained Markdown/grammar by itself yields formal contradiction detection — that is exactly
the `claim ≤ proof` violation this role exists to catch. What DomainSpec genuinely owns
adjacent to this is the **ontology-view** layer (typed nodes + typed edges where forbidden
relationships are made *unconstructible* — "typed so no catalog edge admits the endpoint
pair," per the impl `CLAUDE.md` Route 3) and `validate-relationships.ts`. Those give real,
non-LLM structural contradiction detection on the *relationship* graph. Recommendation: frame
any borrow as "extend ontology-view / δ-engine cross-rule checks," NOT as "adopt a grammar
that surfaces contradictions for free." (This aligns with the standing FOL-validation finding:
`MEMORY: fol-constitution-validation-complement` — cross-rule structural checks are a
build-from-owned complement, not a free property of notation.)

---

## GENUINE-GAP — concede honestly (narrow, real)

### 9 — Harness-enforced post-write *spec-semantic* validator on the artifact
Allium wires a post-write hook + LSP so that **every edit to the spec artifact is structurally
re-validated in the same turn** (`allium check` / `allium-lsp`), failing closed before the
result is presented. DomainSpec has the *enforcement pattern* (`PreToolUse` on `Write|Edit`
for any `.md`, harness-enforced, per `.claude/README.md`) and the *validators*
(`validate-relationships.ts`, `validate-doc-links.ts`, `validate-orphans.ts`, the engine's
`check`/round-trip), but the Write|Edit hook today injects the **frontmatter cheatsheet**, not
a spec-semantic gate — and the engine `check` is a CLI step invoked by the generate-tests
skill, not a fail-closed post-write hook on every spec edit. So the *seam* is genuine: **no
single harness-enforced hook re-runs spec-semantic validation on every spec-doc write.**

Caveat that keeps this narrow (claim ≤ proof): this is a **wiring gap, not a capability gap**
— every piece (hook mechanism + deterministic validators) is already owned. The honest
import is "wire the existing engine `check` / `validate-*` into a PostToolUse fail-closed
hook on `docs/features/**` writes," which is build-from-owned plumbing, **not** an external
dependency on allium or its closed CLI. I flag it as a gap in *coverage*, not in *parts*.

---

## What is genuinely worth borrowing (prose/checklist only — zero capability import)

1. The `/distill` **abstraction-level heuristic tables** ("why does the stakeholder care?",
   "could it be different?", template-vs-instance, the means→ends table) — sharper prose than
   our brownfield skill carries; candidate enrichment to `domainspec-brownfield-translation`.
2. The `/propagate` **obligation taxonomy enumeration** as an *audit checklist* against our δ
   rule-set coverage (data-flow-chain tests, reachability walks, deadlock-scenario tests) —
   to find δ rules we may be missing, NOT to adopt allium's LLM-mediated generator.

Both are documentation borrows. Neither is a new mechanism, neither touches the moat, and
neither warrants importing the allium language or CLI.

---

## Bottom line for the strategist

Seven of nine mechanisms are ALREADY-OWNED and build-from-owned (none a kill, per the
precedent rule). One is an OVERSHOOT-RISK claim to refuse outright (free contradiction
detection from notation). One is a GENUINE but **narrow** gap — and even that is a wiring gap
over already-owned parts, not an external dependency. Net recommendation: **import zero
mechanism; borrow two prose/checklist items; wire one existing-parts hook.** Adopting the
allium language as a second spec notation would duplicate `TAXONOMY.md` and trip the very
duplicate-terminology hazard allium itself flags.
