# Lens: Distillation — comprehension comes from a small, sharp, shared vocabulary, not an added narrative layer

> Research subagent: Wittgenstein, Ludwig. Angle: DDD ubiquitous-language / distillation.
> Corpus: Eric Evans DDD (web, dated) + the DomainSpec spec surface (25 meta-types, 29 edges).
> Read-only except this file. claim ≤ proof. Dated: 2026-07-02.

---

## 0. Thesis (the counter-position)

The owner's instinct is **add a narrative layer** so the abstraction becomes graspable.
The DDD counter-thesis is that comprehension is not bought by *adding* a form; it is bought
by **distillation** — shrinking the vocabulary an author must actively hold to a small,
sharp, shared *core*, and demoting the rest to "recognize and template, don't relearn."

Wittgenstein's own frame sharpens Evans': *the limits of my language are the limits of my
world*, and *meaning is use*. You do not make a language easier to think in by bolting a
gloss onto it; you make it thinkable by keeping the words few, sharp, and shared, so that
their *use* is unambiguous. A narrative layer is a gloss. Distillation changes the language.

The load-bearing claim of this lens: **DomainSpec's authoring difficulty is a vocabulary-size
and vocabulary-sharpness problem, not a vocabulary-explanation problem.** 25 types + 29 edges,
with a large disambiguation apparatus and an explicit "shadow" column, is — by DDD lights —
already vocabulary bloat. The fix is to *distill*, not to narrate over it.

---

## 1. Evans source notes (dated, cited)

All quotes below are Evans' or direct paraphrase of Evans, from the sources cited. Evans'
book *Domain-Driven Design: Tackling Complexity in the Heart of Software* is **2003**; his own
condensed *Domain-Driven Design Reference* is **2015-03**.

**Ubiquitous Language.** Evans (2003), quoted by Fowler:
> "By using the model-based language pervasively and not being satisfied until it flows, we
> approach a model that is complete and comprehensible, made up of **simple elements that
> combine to express complex ideas**."
> "Domain experts should object to terms or structures that are awkward or inadequate to
> convey domain understanding; developers should watch for ambiguity or inconsistency that
> will trip up design."
(martinfowler.com/bliki/UbiquitousLanguage.html) — the language is ONE shared language, used
in speech, writing, and code; the model is its backbone. Comprehension is a property of the
language being *sharp and shared*, not of a second explanatory artifact.

**Distillation.** "The process of identifying, decoupling, isolating, clarifying, and making
the domain explicit, enabling focus on relevant elements while maintaining quality."
Strategic distillation "directs efforts to the vital parts of the domain; it makes the
overview of the system clearer; **it facilitates communication by identifying a core model of
reduced size**; it guides refactoring; and it guides outsourcing, use of off-the-shelf
components and decisions about assignments."
(herbertograca.com/2016/05/09/ddd-15-distillation/ ; Wikipedia: Domain-driven_design)
Note the mechanism: comprehension follows from a **core model of reduced size** — *fewer
words*, not more explanation.

**Core Domain.** Evans:
> "The greatest value of custom software comes from the total control of the Core Domain."
> "Successive distillation of a domain model produces an asset that gives the project **speed,
> agility, and precision of execution**."
The distillation techniques "aim either to **clarify** or to **unburden** the core domain."
(herbertograca, 2016)

**Generic Subdomains.** Evans:
> "Identify cohesive subdomains that are **not the motivation** for your project. Factor out
> generic models of these subdomains and place them in **separate modules**." — candidates for
> off-the-shelf/outsourcing; no competitive advantage. (herbertograca, 2016; Wikipedia)

**Supporting Subdomain** (Vernon, *Implementing DDD* 2013 / *DDD Distilled* 2016):
necessary for the org to succeed, **not** core, but **not** generic either — it "still
requires some level of specialization." You may start from an existing solution and extend it.
Crucially: **"the same subdomain can fall into different categories depending on what the
organization does."** (vaadin.com/blog/ddd-part-1-strategic-domain-driven-design ; deviq.com)

**Distillation techniques** (the toolkit Evans gives — note *none* of them is "add a narrative
layer"; all of them *reduce or isolate*): Domain Vision Statement, Highlighted / Flagged Core,
Distillation Document (minimalist), Cohesive Mechanisms, Segregated Core, Abstract Core,
Generic Subdomains. (herbertograca, 2016)

---

## 2. DDD diagnosis of the DomainSpec surface — is 25 + 29 already bloat?

Verdict: **yes, by DDD lights** — and the spec files carry their own evidence.
(Source: `projects/domainspec-v2/impl/spec/TAXONOMY.md`, `RELATIONSHIPS.md`.)

**(a) The vocabulary is ~3× Evans' tactical set.** Evans' author-facing tactical vocabulary is
small — Entity, Value Object, Service, Domain Event, Module (+ Aggregate/Repository/Factory as
implementation patterns). DomainSpec's *backend* 14 is largely Evans' one **Service** cell
exploded into seven behavioral words: Operation, Query, Calculation, Rule, Policy, Workflow,
Saga. That explosion is the backend locus of bloat. Enum is, in Evans, just a degenerate Value
Object; DomainSpec promotes it to a first-class word.

**(b) The UI layer is 11 words for a subdomain DDD calls generic.** In almost every product the
presentation/delivery layer is a **generic or supporting** subdomain, *not* the core. DomainSpec
spends **11 of 25 slots (44%)** on it. Worse, TAXONOMY.md's own "Backend Counterpart" column
declares **5 of the 11 to be shadows** of a backend word:
- View Model → Value Object · Guard → Rule · Binding → Interface · Adapter → Mapping ·
  State Indicator → State Machine / Enum.
A shadow term is, by ubiquitous-language lights, *the same concept wearing a UI hat* — pure
vocabulary bloat. An author who knows Rule does not need to *learn* Guard; they need to be told
"Guard is Rule, client-side."

**(c) The 29 edges are ~10 relations wearing context hats.** RELATIONSHIPS.md mints a *new edge
word* whenever the same relation crosses a bounded-context boundary:
`produces`/`produces-for`, `enforces`/`enforces-cross`, `produces→triggers`/`triggers-cross`.
That is the ubiquitous-language anti-pattern in miniature: one language should use **one word**
and let *context* disambiguate; DomainSpec coins "same verb + across a boundary" as a distinct
term. Likewise `maps` (backend) / `shapes` (UI) / `derives` (view model) are three names for
"transform shape," and `mirrors`/`reflects`/`contracts`/`fetches`/`mutates` are the "UI shadows
/ calls backend X" family. Real distinct relations: ~8–10. The 29 count is inflated by
(i) backend/UI duplication and (ii) a `-cross` *modifier* promoted to *vocabulary*.

**(d) The spec needs a large disambiguation apparatus — the tell.** TAXONOMY.md carries **two
"Common Confusion" tables (~17 rows)** — Rule vs Policy, Operation vs Workflow, Workflow vs Saga,
Calculation vs Rule, Adapter vs Mapping, Guard vs Rule, View Model vs Value Object, … A sharp
ubiquitous language does **not** need a "how to tell A from B" table; sharp words are
self-disambiguating in use. A 17-row confusion table is direct evidence that the vocabulary is
split *finer than its concepts are distinct*. The narrative-layer instinct would *add prose to
the confusion table*; distillation *deletes the confusion at its source* by merging or
subordinating the near-duplicate words.

---

## 3. The distilled-core proposal for DomainSpec

DDD says: partition the vocabulary into **Core** (total control, must internalize),
**Supporting** (some specialization, learn on demand, hangs off core), and **Generic**
(no differentiation, recognize + template + borrow). Apply it to the 25.

### 3.1 Candidate core-vs-generic split (all 25 classified)

| Meta-type | Class | Rationale (DDD lens) |
|---|---|---|
| **Entity** | **CORE** | The noun with identity — the irreducible "what exists." |
| **Value Object** | **CORE** | Identity-less concept — the other irreducible noun. |
| **Operation** | **CORE** | The verb / state change — the irreducible "what happens." |
| **Rule** | **CORE** | The invariant/constraint — where domain *truth* lives. |
| **State Machine** | **CORE** | Lifecycle — the domain's *temporal* truth. |
| **Event** | **CORE / supporting boundary** | Announces change; core in event-driven domains, else supporting. |
| Enum / Type | SUPPORTING | Degenerate Value Object (a constrained field); recognizable once VO is known. |
| Query | SUPPORTING | Read side; mechanical ("same result twice"); hangs off Entity. |
| Calculation | SUPPORTING | Pure function; a degenerate Operation/Rule; extract-on-demand. |
| Workflow | SUPPORTING | Composition of Operations; learned once Operation is held. |
| Policy | SUPPORTING | Choice logic; a flavored Rule ("choose" vs "block"). |
| Interface | SUPPORTING | Boundary; mechanical exposure of Operations/Queries. |
| Saga | GENERIC | "Workflow that crosses a context" — a scaling *modifier*, not a new concept for most authors. |
| Mapping | GENERIC | Shape transformation; plumbing; off-the-shelf pattern. |
| Page | GENERIC (UI ctx) | Delivery-layer; domain lives in its *route list*, not the word. |
| Layout | GENERIC (UI ctx) | Pure presentation shell. |
| Component | GENERIC (UI ctx) | Presentation building block. |
| Hook | GENERIC (UI ctx) | Reactive-data plumbing. |
| Form | SUPPORTING (UI ctx) | Carries a validation *contract* mirroring an Interface — the schema is domain, the wrapper generic. |
| Action | GENERIC (UI ctx) | Click→mutate plumbing. |
| Guard | GENERIC — **shadow of Rule** | Explicitly "Rule, client-side." |
| Binding | GENERIC — **shadow of Interface** | Explicitly "hook↔endpoint." |
| Adapter | GENERIC — **shadow of Mapping** | Explicitly "Mapping at UI boundary." |
| View Model | GENERIC — **shadow of Value Object** | Explicitly "VO, display-shaped." |
| State Indicator | GENERIC — **shadow of State Machine/Enum** | Explicitly "visual encoding of state." |

**Distilled core = 5 (+1) words:** Entity, Value Object, Operation, Rule, State Machine (+ Event).
**Active working set = core + 6 supporting ≈ 12 words.** The remaining **13** are one generic
scaling-modifier (Saga), one plumbing pattern (Mapping), and an 11-word UI **generic subdomain**
of which **5 are literal shadows** the author already understands the moment they know the
backend counterpart.

### 3.2 Distilled edge core

Collapse 29 → ~8 relations + 2 modifiers:
- **Relations:** `performs` (actor→op), `produces` (op→event), `enforces` (rule→op),
  `transitions` (event→state), `contains` (entity→VO), `exposes` (interface→op/query),
  `orchestrates` (workflow→ops), `transforms` (the maps/shapes/derives/adapter family).
- **Modifiers on any relation:** `@cross` (crosses a bounded context — replaces
  produces-for / triggers-cross / enforces-cross), and `@shadow` (UI mirrors backend X —
  replaces mirrors / reflects / contracts / and the fetches/mutates "calls" pair).

### 3.3 Name the bounded contexts (DomainSpec already has them, unnamed)

DomainSpec *already* draws context boundaries — `feature`, and the backend↔UI split, with the
`-cross` edges marking boundary crossings. The distillation move is to make the boundaries
**explicit and ranked**: the **backend domain model is the CORE context** (author spends
comprehension budget here); the **UI is a GENERIC delivery context** whose language is mostly
shadows; **cross-feature orchestration** (Saga, `-cross` edges) is a **supporting** context.
This is Evans' *Highlighted Core* + *Segregated Core*: don't explain more — mark what is core.

---

## 4. How the author learns the distilled language

Core-first, shadow-mapped, generic-deferred — a learning *order*, not a new artifact:

1. **Learn the 5–6 core words** (Entity, Value Object, Operation, Rule, State Machine, Event)
   against *one worked example*. This is Evans' Ubiquitous Language: use it "pervasively until
   it flows." Everything a domain needs to *mean* is expressible here.
2. **Learn the 6 supporting words on demand** — each is introduced as a *specialization of a
   core word* ("Query is a read-only Operation"; "Policy is a Rule that chooses instead of
   blocks"; "Calculation is a pure Operation you test alone"). No new mental model, a qualifier.
3. **Never "learn" the shadows** — they are presented as a one-line dictionary: *Guard = Rule
   (client-side); View Model = Value Object (display); Adapter = Mapping (UI); Binding =
   Interface; State Indicator = State Machine/Enum (visual).* Recognition, not acquisition.
4. **Defer the generic UI/Saga vocabulary** until the author actually authors that layer;
   provide templates so it is *filled in*, not *reasoned about*.

Active comprehension budget: **~6 words to fluency, ~6 more as qualifiers.** That is inside
Evans' "simple elements that combine to express complex ideas," and inside working-memory
limits — which a 25-word flat taxonomy is not.

---

## 5. Cross-corpus glance: the OCM 7-form contract is the anti-pattern

`projects/ontologize/OPTIMIZATION-CHAIN-METHOD.md` requires (rule **OCM-009**) that *every*
optimization chain express **the same idea in seven sentence forms** — `plain_language`,
`operator`, `executive`, `contract`, `causal_careful`, `dashboard_label`, `ontology` — and
"All seven sentence forms are required for client-facing use."

By DDD lights this is the **inverse of ubiquitous language**. Evans wants **one** model-based
language that "flows," used across speech, writing, and code. OCM mandates **seven dialects of
one sentence** — seven translations for seven audiences. That is precisely the translation
burden ubiquitous language exists to *eliminate*, and it is strictly **more to learn** (seven
templates + the rule that binds them).

The charitable read — the seven forms are *audience projections* (buyer, operator, exec, schema,
skeptic, dashboard, graph) — is exactly where the distinction bites: seven audiences are **not**
seven bounded contexts. Evans permits *different languages in different contexts*; he does not
permit *seven languages for one artifact in one context*. OCM's forms buy governance legibility
(each audience gets a claim-safe rendering) at the cost of a single sharp shared vocabulary.

**The punchline for DomainSpec:** the owner's "add a narrative layer" instinct is structurally
*the OCM move* — add an **eighth form**, a narrative dialect, on top of the taxonomy. DDD says
the opposite is the fix. Do not add a dialect; **distill the one model-language** to a core of
~6 words so it flows. Comprehension is bought by *subtraction and sharpening*, not addition.

---

## 6. Does distillation lose completeness?

**No — distillation reorganizes; it does not delete.** Three points:

1. **Completeness is a property of the type system; comprehensibility is a property of the
   learning order.** All 25 types stay in the spec as the complete typing surface the
   engine/validator ranges over. Evans' generic subdomains are *still modeled and still in their
   modules* — they are simply not where the human spends attention. The 25 remain; the *author's
   path through them* and the *document's emphasis* change (core-first, shadows dictionaried,
   generic templated). You lose nothing the machine checks; you gain the "core model of reduced
   size" Evans says *is* the comprehension win.

2. **The shadows were never independent completeness.** Guard/View-Model/Adapter/Binding/State-
   Indicator are, by the spec's own "Backend Counterpart" column, *derived* from backend words.
   Collapsing them to a dictionary removes redundancy, not coverage.

3. **The one real risk — and its fix.** Evans: *"the same subdomain can fall into different
   categories depending on what the organization does."* For a routing company, `Mapping` may
   *be* core; for a design-tool company, the UI layer may be core. So a **hard-coded** core/
   generic split *would* threaten completeness-of-emphasis. The completeness-preserving move is
   to make the split a **per-domain, author-declarable lens over the full 25**, not a deletion of
   13. DomainSpec keeps all 25 typed; each repo *declares its core context*, and the learning
   path, Highlighted Core, and templates are generated from that declaration.

Distillation therefore trades **nothing** on machine completeness and buys the entire
comprehension gain on the human side. That is why it beats adding forms: an added narrative
layer *raises* total vocabulary (25 types + N narrative constructs) and adds a translation
obligation; distillation *lowers* the actively-held vocabulary to ~6–12 while leaving the full
typed surface intact for the engine.

---

## 7. Claim ≤ proof ledger

| Claim | Support | Status |
|---|---|---|
| Evans grounds comprehension in a *small, sharp, shared* language and in a *core model of reduced size* | Fowler bliki (Evans quote); herbertograca DDD-15 (Evans quotes on distillation/core); Wikipedia | Sourced, dated (2003 book / 2015 ref) |
| DomainSpec surface = 25 types, 29 edges | `TAXONOMY.md` L1-3, `RELATIONSHIPS.md` L1-3 | Verified in-repo |
| 5 of 11 UI types are explicit shadows of backend words | `TAXONOMY.md` "Backend Counterpart" column (L28-40) | Verified in-repo |
| `-cross` edges are the same verb + a boundary modifier | `RELATIONSHIPS.md` L15-17 (produces-for/triggers-cross/enforces-cross) | Verified in-repo |
| Spec carries ~17 rows of "Common Confusion" disambiguation | `TAXONOMY.md` "Common Confusion" tables (L575-603) | Verified in-repo |
| OCM requires 7 sentence forms per chain (anti-ubiquitous-language) | `OPTIMIZATION-CHAIN-METHOD.md` L84-95, OCM-009 (L134) | Verified in-repo |
| Core/generic split must be per-domain, not hard-coded | Vernon/Vaadin: "same subdomain, different category by org" | Sourced |
| Distillation improves *actual author comprehension* (empirical) | — | **NOT proven.** This lens argues the DDD-consistent *mechanism*; it is a hypothesis, not a measured result. |

**Honest limit:** I do not have evidence that DomainSpec authors empirically struggle, nor that
a distilled presentation measurably improves them. The CONTEXT asserts the difficulty; I take it
as given and argue what DDD prescribes *if* it is real. The strong, verifiable half is the
*surface analysis* (bloat markers in the files) and the *Evans prescription* (distill, don't
narrate). The comprehension gain is a well-grounded hypothesis to test, not a proven outcome.

---

## Sources

In-repo (paths, verified):
- `projects/domainspec-v2/impl/spec/TAXONOMY.md` — 25 meta-types, Backend-Counterpart shadow column, Common-Confusion tables.
- `projects/domainspec-v2/impl/spec/RELATIONSHIPS.md` — 29 edges, `-cross` modifier duplication.
- `projects/ontologize/OPTIMIZATION-CHAIN-METHOD.md` — 7-form contract (OCM-009).

Web (dated):
- Eric Evans, *Domain-Driven Design* (2003) and *DDD Reference* (2015-03): https://www.domainlanguage.com/wp-content/uploads/2016/05/DDD_Reference_2015-03.pdf (PDF 403 on fetch; cited via secondary sources below).
- Martin Fowler, "Ubiquitous Language" (Evans quotes): https://martinfowler.com/bliki/UbiquitousLanguage.html
- Herberto Graça, "DDD-15 – Distillation" (2016-05-09, Evans quotes on distillation/core/generic): https://herbertograca.com/2016/05/09/ddd-15-distillation/
- Wikipedia, "Domain-driven design": https://en.wikipedia.org/wiki/Domain-driven_design
- Vaadin, "DDD Part 1: Strategic Domain-Driven Design" (Vernon core/supporting/generic): https://vaadin.com/blog/ddd-part-1-strategic-domain-driven-design
- DevIQ, "Subdomains in DDD": https://deviq.com/domain-driven-design/subdomain/
