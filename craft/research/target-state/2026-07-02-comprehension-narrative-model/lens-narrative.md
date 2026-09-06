# Lens: Narrative / Sentence-Contract Comprehension Layer for DomainSpec authoring

Role: research explorer (Alexander, Christopher). Read-only except this file.
Date: 2026-07-02. Angle: NARRATIVE / SENTENCE-CONTRACT (make the strongest case).
Claim discipline: claim ≤ proof. Sources cited with dates; owned corpus cited by repo path.

---

## 0. The problem this lens is aimed at

CONTEXT (from dispatch): DomainSpec is hard to grasp *at spec-authoring time* — an
author declaring a concept cannot see what abstraction is being proposed. When an
author writes `PaymentTransaction | Entity` in an aspect file, the only feedback they
get is a table shape and, later, a validator PASS/REJECT. The *idea* — "an Entity is a
thing whose sameness is its identity, not its field values" — is never rendered to the
author in a form they reason in. They must reverse-engineer the abstraction from a schema
or a fixture. That reverse-engineering is the comprehension gap.

Owner thesis under test: a **narrative / multi-form sentence contract** closes it —
express ONE idea in several forms so the abstraction is *understandable* (human forms)
AND *machine-checkable* (contract forms), with all forms pinned to a single criterion.

---

## 1. The owned corpus (the method already exists here)

### 1a. Optimization-Chain Method — the owned "one idea, N sentence forms" pattern
`projects/ontologize/OPTIMIZATION-CHAIN-METHOD.md` (read 2026-07-02).

The method's load-bearing sentence:

> "The chain is both a sentence and a contract. It lets CyberAlchemy explain the
> competitive advantage in plain language while preserving the governance rule that
> evidence, metrics, and candidates do not approve themselves." (lines 20–22)

It mandates **seven** sentence forms for the SAME idea (§ "Required Sentence Forms",
lines 83–96): `plain_language`, `operator`, `executive`, `contract`, `causal_careful`,
`dashboard_label`, `ontology`. Rule **OCM-009** (line 134): "All seven sentence forms
are required for client-facing use. → Reject deliverable." Rule **OCM-005/006** pin the
claim: a form "may not exceed the source association" and "causal wording requires
quasi-causal evidence gates." So the method already carries the exact governance the
comprehension gap needs: *multiple readable renderings, one underlying truth, no form
allowed to overclaim past the machine criterion.*

### 1b. DomainSpec ALREADY ships a mini version of this — at the wrong layer
`projects/domainspec-v2/definitions/meta-types/meta-types.md` (read 2026-07-02).

The DS-D1 Entity card (lines 25–48) is already a multi-form contract:
- **Formal voice** — restates `entity.schema.yml` (identity ≥1, typedness).
- **Plain-language voice** — "a thing you'd give an ID in a database and track over time".
- **Domain-context voice** — the DS-D8 edge slice (source of performs/contains/emits …).
- **Misuse warning** — "a field table with no identity + an Equality clause is a Value
  Object, not an Entity — the validator rejects it as Entity."

Finding: the multi-voice sentence contract is *owned and in use* — but only at the
**meta-type-definition** layer (what an Entity *is* in general). It is absent at the
**spec-authoring** layer (what *this* `PaymentTransaction` is, and whether the author
has understood it). The proposal is to project that same owned pattern one layer down,
onto the concept/spec/target-state the author is writing right now.

---

## 2. NDD source notes (date-checked, source-first)

The SEED (`projects/domainspec-v2/research/target-state/SEED.md`, lines 22–24) names two
primary sources: `https://narrativedriven.org/what-is-ndd` and `.../what-makes-a-narrative-buildable`.

**Access note (2026-07-02):** both SEED URLs return **HTTP 403** to WebFetch, and every
`narrativedriven.org` page 403s WebFetch directly. The site has been **restructured** —
the live equivalents are `/article/introduction-to-ndd`, `/explanation/origin-story`,
and `/article/glossary`. I could not retrieve raw page bodies; the quotes below are from
**WebSearch-surfaced snippets of those live pages, accessed 2026-07-02**, not from a
direct fetch. Treat them as second-hand-but-attributed, not verbatim-verified. This is a
source-fidelity gap the SEED's own "fetch and record before claiming" rule should log.

What NDD actually claims (narrativedriven.org, via search 2026-07-02):
- "The narrative is the durable review surface between prompt and code. People review it
  before implementation. When the product changes, the narrative changes first."
- "one product story humans can review before build."
- Structure: it "keeps **domains, narratives, scenes, moments, rules, and examples**
  stable for the team." NDD "brings together BDD, DDD, EventStorming, specification by
  example, story mapping, and component-level specs for the AI era."
- Origin (`/explanation/origin-story`): from Xolvio (consultancy, 15+ yrs); by ~2016
  named "spec-driven development," thesis "the specification was the medium, not a stop
  along the way." Proof point: a gaming loyalty platform delivered in 3 months, 90% test
  coverage.

**Two different "NDD"s — flagged honestly.** A separate source,
`test2doc.com/blog/2026/02/06/ndd/` (**dated 2026-02-06**), uses "Narrative-Driven
Development" to mean "writing tests like a tutorial / guided tests as living
documentation" — "Write your test steps as if you're explaining the app to a friend."
That is a *different* framing from narrativedriven.org's "one product story reviewed
before build." The SEED's intended sense is the **narrativedriven.org** one (buildable
narrative → coding agent). I do not conflate them.

What NDD gives this lens: the concept **"buildable narrative" = a narrative that is a
review surface AND drives the build** (changes first, is reviewed before implementation).
That is precisely the target-state primitive the SEED (lines 16–20) wants: "a target
state should read like a narrative you can actually build toward and check progress
against." What NDD does *not* give: any machine-checkable predicate. NDD's narrative is a
human review surface; its "buildable" is a *review/authoring* claim, not a *verifier*
claim. The owned optimization-chain method supplies the missing half (the `contract` +
`dashboard` forms that a validator can read). **The proposal = NDD's readable narrative
∪ OCM's checkable contract, pinned to one criterion.**

---

## 3. The proposed model — Comprehension Contract (spec-authoring layer)

A **Comprehension Contract** attaches to a *unit of authored intent* (a declared concept
/ a spec section / a target-state) and expresses that one unit in a small set of forms.
Every form is a rendering of the SAME underlying `criterion` (a `.schema.yml` for a
meta-type; a checkable predicate for a target-state). Forms split into two lanes:

- **Human lane (authored):** `plain`, `intent` (why it exists / what "done" looks like).
- **Machine lane (projected, NOT hand-authored):** `contract` (the schema restatement),
  `discriminator` (what it is NOT + why), `status` (validator verdict surface),
  `ontology` (edge-participation projection).

Adapted from OCM's seven forms (`OPTIMIZATION-CHAIN-METHOD.md` lines 87–96), retargeted
from client-BI to spec-authoring:

| Form | Lane | Source | Authoring cost |
| --- | --- | --- | --- |
| `plain` | human | author writes | 1 sentence |
| `intent` / `done-looks-like` | human | author writes | 1 sentence |
| `contract` | machine | **projected from** `<type>.schema.yml` | 0 (generated) |
| `discriminator` (`causal_careful`) | machine | projected from schema `distinguisher` | 0 (generated) |
| `status` (`dashboard`) | machine | the validator verdict | 0 (generated) |
| `ontology` | machine | projected from schema `edge_participation` | 0 (generated) |

**The three load-bearing rules** (borrowed from OCM, retuned):
1. **One criterion, many renderings.** Every form must restate the same criterion; a
   form that contradicts the criterion is a *visible authoring bug* (this is the whole
   value — see §5).
2. **No form exceeds the criterion** (OCM-005/006 analogue). The `contract` form is
   SHAPE-only because `entity.schema.yml` is shape-only ("semantic satisfiability is the
   engine moat and is NEVER checked here" — `entity.schema.yml` lines 4–5). So the layer
   may claim "well-formed / correctly-typed meta-type," never "semantically correct."
   Claim ≤ proof, enforced structurally.
3. **Machine lane is projected, not authored** (the ceremony defense — §6). Author fills
   ≤2 slots; the other four are generated from the schema the repo already has.

---

## 4. Worked example A — Entity (meta-type `PaymentTransaction`)

Grounded in `entity.schema.yml`, `entity-ok.md`, `entity-bad.md`, `meta-types.md` DS-D1.1.

Author declares `PaymentTransaction | Entity` and writes the fields table (the
`entity-ok.md` shape). The Comprehension Contract renders:

- **plain** (author writes): "A PaymentTransaction is a charge we track over its whole
  lifecycle; two charges with identical amount and status are still *different* charges
  because each has its own id."
- **intent / done** (author writes): "Exists so money movement is auditable per-instance;
  'done' = every charge is addressable by a stable id and never silently merged with a
  look-alike."
- **contract** (projected from `entity.schema.yml`): "Entity ⇔ ≥1 field flagged
  `Identity` (bounded ∃ over the fields table) ∧ every field has a non-empty `Type`."
- **discriminator** (projected from `distinguisher`): "NOT a Value Object: an Entity HAS
  an identity field; a Value Object has none and declares an Equality clause. If you find
  yourself writing 'two X are equal iff …', you have a Value Object, not an Entity."
- **status** (validator verdict): "PASS on `identity` (id: yes) and `typedness`."
- **ontology** (projected from `edge_participation`): "source of performs / contains /
  emits; target of queries / produces-for / derives."

**Where it earns its keep — the caught error.** `entity-bad.md` declares `Money | Entity`
with no identity field and "**Equality:** two Money are equal iff amount and currency are
equal." Today the author learns this is wrong only when the validator rejects it. Under
the Comprehension Contract, the author's own **plain** form ("two Money are equal iff…")
sits directly beside the **discriminator** form ("if you're writing 'equal iff', that's a
Value Object"). The contradiction is visible *at authoring time, in the author's own
words*, before the validator runs. That is the comprehension gap closing.

---

## 5. Worked example B — a Target-State (the NDD "buildable narrative")

The SEED wants a target-state that "reads like a narrative you can actually build toward
and check progress against." Applied to a DomainSpec feature (merchant onboarding):

- **plain / narrative** (author writes, NDD's review surface): "When onboarding is done,
  a brand-new merchant can accept a live payment within 10 minutes with no manual
  back-office step."
- **intent / done-looks-like** (author writes): the outcome the slices add up to.
- **contract** (checkable predicate — the half NDD lacks): "∃ path signup→first-live-
  charge with wall-clock ≤ 10 min ∧ manual_steps = 0, over the onboarding aspect's
  concepts." (A fitness-function / oracle, in the Lane-A vocabulary of `SEED.md` line 38.)
- **discriminator** (scope guard): "'Done' does NOT mean the merchant is *fully verified*
  (KYC is a separate target-state); it means *transacting*."
- **status / dashboard** (progress surface): "% of the named scenes landed; oracle
  green/red." This is how you "check progress against" the narrative.
- **ontology**: which concepts/edges the target-state touches (Merchant Entity,
  ProcessPayment Operation, the `performs`/`emits` edges).

This directly executes SEED Lane Z: it is a concrete target-state artifact, it is
checkable (the `contract` predicate), and it drives implementation (the `status` form is
the progress oracle). NDD supplies `plain`; OCM supplies `contract`+`status`; the pin
rule keeps them honest.

---

## 6. The honest ceremony risk (the argument the owner asked for)

The dispatch asks directly: does 7 forms ADD CEREMONY without adding direction? Honest
answer, in three parts:

**(a) If all forms are hand-authored per concept → yes, it's ceremony. REJECT that.**
25 meta-types × up-to-7 forms, hand-written and hand-maintained, is a drift factory: the
`plain` and `contract` forms would diverge and the author would trust the wrong one.
OCM-009 makes all seven *mandatory* — but that rule is scoped to *client-facing BI
deliverables*, where a human sells the story. Importing OCM-009 verbatim into
spec-authoring would be cargo-culting a rule out of its context. I flag this as a real
mis-transfer risk, not a feature.

**(b) The layer only adds direction under two conditions:**
1. **The machine lane is projected, not authored.** The repo already owns the source of
   truth — `entity.schema.yml` has `criterion`, `distinguisher`, and `edge_participation`
   as structured fields (lines 16–33). The `contract`, `discriminator`, `status`, and
   `ontology` forms are deterministic renderings of those fields. Author touches ≤2 slots
   (`plain`, `intent`). Marginal cost ≈ two sentences, not seven artifacts.
2. **It must catch a real error class.** It does: meta-type *mis-declaration*
   (Entity-that-is-a-Value-Object; Rule-that-is-a-Policy — `rule-bad.md`,
   `formal_return_type=strategy`). The `bad` fixtures *prove this error class is real and
   already anticipated*. Juxtaposing the author's `plain` form against the projected
   `discriminator` surfaces it earlier and in the author's own language.

**(c) Where it genuinely does NOT add direction — so make it opt-in, not mandatory.**
For a concept with no discrimination ambiguity and no target-state (e.g. a plain Enum),
the extra forms are noise. The layer should **trigger** only (i) on declaring a
*discriminable* meta-type (Entity|ValueObject, Rule|Policy, …) or (ii) on authoring a
*target-state*. Blanket-mandatory forms would reproduce exactly the ceremony the SEED
warns about ("where does the narrative framing add ceremony without adding direction",
SEED line 35). The correct claim is **conditional value**, not universal value.

**Load-bearing limitation (claim ≤ proof):** the `contract` form is only as strong as
the `.schema.yml`, which is SHAPE-only by design (the engine moat is never invoked here —
`entity.schema.yml` lines 4–5). So the Comprehension Contract can make the abstraction
*visible and shape-checkable and cross-form-consistent*. It CANNOT verify meaning. It is
a **comprehension** aid with a **shape** guarantee — never a semantic verifier.

---

## 7. Cross-corpus check — could the example FIXTURES just replace a narrative layer?

Skimmed `projects/domainspec-v2/impl/spec/__fixtures__/mt/` (28 files, ok/bad pairs;
`entity-ok.md`, `entity-bad.md`, `value-object-ok.md`, `rule-ok.md`, `rule-bad.md` read
in full, 2026-07-02). Argument that examples do NOT replace the narrative layer:

1. **Fixtures address a different reader.** They are validator-conformance artifacts
   ("Expected: **PASS**" / "Expected: **REJECTED as Entity**") for the *criterion author*,
   not the *spec author*. `entity-ok.md` shows a table that passes; it never says in words
   *why* PaymentTransaction is an Entity and Money is not.
2. **An example is one instance; it does not state the rule.** The author must generalize
   the abstraction from a single positive case — which is the exact "can't see the
   abstraction" problem. `entity-ok.md` (PaymentTransaction) and `value-object-ok.md`
   (Money) are near-identical field tables; the *discriminating idea* (identity vs
   equality-clause) lives only in the schema's `distinguisher`, not in either example.
3. **BUT — the honest counter that reshapes the proposal.** Examples are cheaper and
   drift-resistant vs. prose. NDD folds in "specification by example," and OCM's own set
   is example-adjacent. So the strongest position is NOT "narrative replaces examples" —
   it is: **the example is ONE form in the contract**, subsumed, not competed-with. The
   minimal viable layer is **two forms + the existing fixture**: `plain` (human) +
   `contract` (machine) + the ok/bad example the repo already has, all three pinned to
   one criterion. That is a far weaker/cheaper claim than OCM's seven-form mandate, and it
   is the one the evidence actually supports.

---

## 8. Verdict of this lens

A narrative / sentence-contract comprehension layer is **defensible but only in its
minimal, projected, opt-in form** — NDD's readable narrative for the human lane, OCM's
projected contract/status forms for the machine lane, one criterion pinning both, the
existing fixture as the example form. Its earned value is a specific, evidenced one:
surfacing meta-type mis-declaration and un-checkable "done" *in the author's own words at
authoring time*. Its ceiling is hard: shape-only, comprehension-only, never semantic
verification. The seven-form mandate (OCM-009) does NOT transfer — that would be the
ceremony the SEED warns against. Recommend the two-form-plus-example floor, triggered on
discriminable meta-types and target-states, as the honest scope.

---

### Sources
- `projects/ontologize/OPTIMIZATION-CHAIN-METHOD.md` (owned method; read 2026-07-02)
- `projects/domainspec-v2/research/target-state/SEED.md` (read 2026-07-02)
- `projects/domainspec-v2/definitions/meta-types/meta-types.md` (DS-D1 cards; read 2026-07-02)
- `projects/domainspec-v2/impl/spec/meta-types/structural/entity.schema.yml`,
  `.../behavioral/rule.schema.yml` (read 2026-07-02)
- `projects/domainspec-v2/impl/spec/__fixtures__/mt/{entity,value-object,rule}-{ok,bad}.md` (read 2026-07-02)
- NDD (WebSearch-surfaced snippets, accessed 2026-07-02; direct WebFetch 403'd — quotes
  attributed, not verbatim-verified): narrativedriven.org (home; `/article/introduction-to-ndd`;
  `/explanation/origin-story`; `/article/glossary`). SEED's cited `/what-is-ndd` and
  `/what-makes-a-narrative-buildable` both 403 (site restructured).
- test2doc.com/blog/2026/02/06/ndd/ (dated 2026-02-06) — a *different* NDD framing
  (guided-test living documentation), flagged as not the SEED's sense.
