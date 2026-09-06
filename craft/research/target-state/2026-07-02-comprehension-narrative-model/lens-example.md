---
artifact_id: comprehension-narrative-model-lens-example
artifact_type: research-lens
lens: example-first / BDD (methodology corpus)
persona: Polanyi, Michael ("we can know more than we can tell")
date: 2026-07-02
dispatch: comprehension-narrative-model (target-state tower, Lane research)
boundary: LOCAL RESEARCH ONLY. Proposes a comprehension ordering; promotes nothing.
          No template/validator field is added here (SEED promotion boundary).
claim_discipline: claim <= proof. Fixture claims are read from disk; BDD/DDD/Polanyi
                  claims are dated source notes, cited below.
---

# Lens — Example-First Comprehension

## Thesis (the persona claim)

An author does not come to understand a meta-type (or an abstraction, or a
target-state) by reading its **definition** or by learning its **narrative form**.
Understanding *is* a classification skill — the ability to correctly type a **new**
concept — and that skill is **tacit**: it transfers from worked exemplars, not from
prose. Polanyi's paradox names exactly this gap: *"we can know more than we can
tell"* — we recognize a known face among a thousand yet cannot state the rule by
which we recognize it (Polanyi, *The Tacit Dimension*, Univ. of Chicago Press,
1966). A definition is the "telling"; it is downstream of, and weaker than, the
recognition it tries to describe.

The strong, cheap comprehension unit is the **discriminating minimal pair**: one
worked **positive** example plus a **negative** that differs by the *single* feature
that flips the classification. The pair is built **at the category boundary**, which
is exactly where the author's hard cases live ("*is Money an Entity?*"). A definition
describes the **center** of a category and under-determines its edge.

**DomainSpec has already built this pair — and files it as validator plumbing instead
of leading with it as the comprehension aid.** That is the underused asset this lens
recovers.

---

## Source notes (dated, cited)

BDD / Specification-by-Example corpus — the discipline that already made
"comprehension = concrete example" its first principle:

- **Adzic, *Specification by Example*** (Manning, 2011). Seven process patterns;
  the load-bearing ones here are **"illustrating using examples"** and **"evolving a
  living documentation system"** — concrete, realistic examples *are* the
  specification, and they stay true because they execute. Ambiguity that abstract
  requirements leave open is closed by the example.
  <https://www.manning.com/books/specification-by-example>
- **Wynne, "Introducing Example Mapping"** (Medium, **2015-12-15**). Rules go on
  **blue** cards; *"For each rule, we may need one or more **examples** to illustrate
  it,"* written on **green** cards placed **under** the rule. Diagnostic corollary:
  *"some rules are so obvious you don't need examples at all"* — and, conversely, when
  a rule yields no examples the rule is not yet understood. The example is the test of
  whether the rule is real.
  <https://medium.com/@mattwynne/introducing-example-mapping-42ccd15f8adf>
- **Given-When-Then** (North & Matts; via Fowler bliki + Cucumber docs). *"A scenario
  is a concrete example that illustrates a business rule … In addition to being a
  specification and documentation, an example is also a test."* The same artifact is
  spec + docs + test — the definition of **living documentation**.
  <https://martinfowler.com/bliki/GivenWhenThen.html> ·
  <https://cucumber.io/docs/gherkin/reference/>

Cross-corpus concession source (where a *term* is still required):

- **Evans, *Domain-Driven Design*** (2003) — **Ubiquitous Language**: a shared,
  rigorous vocabulary that removes the translation friction between two jargons. An
  example is always an example *of* something; that "something" needs a stable name to
  be referenced, reused, and agreed on.
  <https://agilealliance.org/glossary/ubiquitous-language/>

---

## The asset DomainSpec already has (read from disk, 2026-07-02)

The structural meta-types ship a **crossed** discriminating pair — the strongest form
of the device, because the *negative of one type is the positive of the other*:

| File | Concept | Declared as | Shape | Verdict |
| --- | --- | --- | --- | --- |
| `impl/spec/__fixtures__/mt/entity-ok.md` | `PaymentTransaction` | Entity | has `Identity` field | **PASS** |
| `impl/spec/__fixtures__/mt/entity-bad.md` | `Money` | Entity | **no identity** + **Equality** clause | **REJECTED as Entity** |
| `impl/spec/__fixtures__/mt/value-object-ok.md` | `Money` | Value Object | no identity + Equality clause | **PASS** |
| `impl/spec/__fixtures__/mt/value-object-bad.md` | `Account` | Value Object | has `Identity` field | **REJECTED as Value Object** |
| `impl/spec/__fixtures__/mt/enum-ok.md` | `PaymentMethod` | Enum | `Value \| Description` table | **PASS** |
| `impl/spec/__fixtures__/mt/enum-bad.md` | `Status` | Enum | typed **field** table (no `Value`) | **REJECTED as Enum** |

The crossing is the whole lesson in one glance: **the very same `Money`** is
*rejected* as an Entity (`entity-bad.md`) and *accepted* as a Value Object
(`value-object-ok.md`). Nothing about `Money` changed — only the **claimed class** and
the **one contrast axis** (an `Identity`-flagged field vs. none + an Equality clause).
An author who reads that pair can now type a **new** concept without being able to
recite the criterion — Polanyi's "know more than we can tell", made operational.

**Where it is filed today.** The pair lives under `__fixtures__/` (validator inputs).
The companion card `impl/spec/meta-types/structural/entity.md` *does* link it — but as
its **5th of 6 sections** ("Fixtures (the discriminating pair)"), after
`Formal criterion`, `Required structure`, `Edge participation`, `Distinguisher`. The
card is **definition-first, examples-last**. The schema
`entity.schema.yml` even carries the discriminator as data
(`distinguisher: {vs: ValueObject, rule: "an Entity HAS an identity field; a Value
Object has none and declares an Equality clause"}`) — the contrast is *already
machine-present*; it is simply not the author's entry point.

---

## The model — Example-First Comprehension

**Invert the card ordering. The discriminating minimal pair is the entry point; the
criterion prose is a gloss on the contrast axis the pair reveals.**

Comprehension unit (per meta-type / abstraction / target-state):

1. **Worked positive** — the smallest fully-formed instance that *is* the thing.
2. **Discriminating negative** — the nearest neighbour that is *not* the thing,
   differing by exactly the feature that flips the class (a **minimal pair**).
3. **Named contrast axis** — one short label for *what* differs
   (here: `Identity` field ± `Equality` clause). This is the only irreducible prose.
4. **Class name** — the ubiquitous term the pair is an example *of* (Entity, Value
   Object, Enum, or a target-state's name).

Read order for the author: **example → discriminator → (thin) definition**, not the
reverse. The definition survives only as the caption on axis (3) and label (4).

This is not new machinery — it is BDD's own claim ("*a scenario is a concrete example
that illustrates a business rule*") applied to the **meta-level**: the "rule" is the
meta-type criterion; the "green cards" are `*-ok.md` / `*-bad.md`; the card is the
living document that stays true because the validator runs the same pair.

---

## Worked authoring experience #1 — a meta-type

Author is modelling `Money` and must pick a meta-type. **Definition-first** (today's
card) hands them: *"an Entity is an identity-bearing, lifecycle-tracked domain
object."* `Money` has a lifecycle (it flows through a payment) and could carry an id
in a table — the definition **does not resolve** the choice; the author guesses.

**Example-first** hands them the crossed pair first:

> **This is a Value Object** (`value-object-ok.md`): `Money{amount, currency}`, no
> identity, **Equality:** two `Money` are equal iff `amount` and `currency` match.
> **This same `Money`, declared an Entity, is REJECTED** (`entity-bad.md`) — it has
> no identity field and defines equality by value, so it is a **mis-typed Value
> Object**.
> **An Entity looks like this instead** (`entity-ok.md`): `PaymentTransaction{id▸,
> amount, status}` — equal-by-**id**, not by fields.

The author now classifies by the axis the pair exposed — *"do two of these count as the
same thing because their fields match (VO), or because they share an id (Entity)?"* —
and never needed the sentence. The one-line gloss ("Entity = equal-by-id; VO =
equal-by-fields + Equality clause") is retained *underneath* as the caption, not the
lead.

---

## Worked authoring experience #2 — a target-state

The target-state SEED asks for a **checkable** answer to *"what does done look like?"*
and flags the open risk that a **narrative** target-state adds ceremony without
direction (`research/target-state/SEED.md`). Example-first answers with the same
device: a target-state is a **worked "done" example + a discriminating "not-done"
near-miss** — an *oracle-by-example*, which is precisely the Lane-A "invariants /
oracles / acceptance-criteria" alternative the SEED names.

Feature: **Refund a captured payment** (reuses the fixture domain —
`PaymentTransaction`, `Money`, `PaymentStatus`).

> **DONE looks like this** (positive):
> **Given** a `PaymentTransaction{id, amount: Money, status: CAPTURED}`
> **When** a full refund is issued
> **Then** `status = REFUNDED`, **and** a `Refund{refunds: <txn id>, amount: Money}`
> is emitted, **and** `sum(ledger entries for txn) = 0`.
>
> **NOT-DONE — the near-miss that looks done** (discriminating negative):
> same Given/When, **Then** `status` flips to `REFUNDED` **but no `Refund` is emitted
> and the ledger is not balanced.** The status flag is set, so a dashboard would call
> it done — **REJECTED as done.**

The single flipped feature is **the evidence artifact** (the emitted `Refund` + the
balanced ledger), not the state flag. That negative *is* the acceptance boundary: it
pins the exact near-miss that must not count as arrival — the thing a narrative
target-state ("we want refunds to work") cannot express and an agent cannot verify.
Comprehension and the "done" check are the **same artifact** (living documentation),
so the author who understands the target-state has, in the same stroke, written its
oracle. (Local research only — this proposes the *shape*; adding a target-state
section to a template requires a later approved `task-session`, per the SEED.)

---

## Concede: where a term is still required

Examples do **not** make vocabulary optional — they **relocate and shrink** it. Two
naming obligations survive, and DDD's Ubiquitous Language (Evans, 2003) is right that
they must:

1. **The contrast axis must be named.** The pair only teaches if both authors agree
   the difference is `Identity` (± an `Equality` clause) and not, say, "`Money` is
   simpler than `PaymentTransaction`." Strip the label and the minimal pair becomes
   an ambiguous pair — the reader can *see* two cases differ but not *on what*.
   `entity-bad.md` works as a discriminator **because** its columns are the named
   `Field | Type | Required | Identity | Description` and it carries a labelled
   `Equality:` clause.
2. **The class must be named.** An example is an example *of* something; without the
   stable terms `Entity` / `Value Object` / `<target-state name>`, the pair cannot be
   referenced, reused, indexed, or validated. The name is the handle the tacit skill
   attaches to.

So the honest position is **not** "definitions vanish." It is: **definitions collapse
to two labels — the axis and the class — and everything else (the descriptive
sentence, the narrative form) is demoted below the pair.** Forms are not deleted;
they are re-ordered from lead to caption.

---

## Why examples beat definitions and forms

- **Boundary vs. center.** A definition states the category's center
  ("identity-bearing, lifecycle-tracked"); the author's hard cases are always at the
  **edge** (`Money`). The minimal pair is *built at the edge* — it answers the
  question the definition dodges.
- **Discrimination vs. description.** A narrative/form gives ordering ceremony but no
  cut: a paragraph on "what an Entity is" still leaves VO-shaped `Money` ambiguous;
  **one negative line resolves it** (Wynne: examples are what prove a rule is real,
  2015-12-15).
- **It runs.** The same `*-ok.md` / `*-bad.md` that teaches the author is the fixture
  the validator executes — comprehension and test are one **living document** (Adzic
  2011; Cucumber). A definition cannot be run, so it silently rots; a fixture that
  rots **fails CI**.
- **Tacit-first.** You can recognize the face before you can state the rule (Polanyi
  1966). Lead with the recognition (the pair); let the rule follow as a caption for
  those who want it.

---

## Claim ≤ proof ledger

| Claim | Proof | Strength |
| --- | --- | --- |
| DomainSpec already ships a crossed discriminating pair; same `Money` is rejected-as-Entity and accepted-as-VO | Read `entity-bad.md`, `value-object-ok.md`, `entity-ok.md`, `value-object-bad.md`, `enum-{ok,bad}.md` (2026-07-02) | **Strong** (on disk) |
| The pair is filed as validator plumbing and the card is definition-first (examples 5th of 6) | Read `meta-types/structural/entity.md` section order + `entity.schema.yml` `distinguisher` field | **Strong** (on disk) |
| BDD/SbE holds "concrete example illustrates the rule; example = spec + docs + test" | Adzic 2011; Wynne 2015-12-15; Fowler/Cucumber (dated notes above) | **Strong** (cited) |
| A named term is still required for axis + class | Evans 2003 Ubiquitous Language; internal argument from the fixtures | **Medium** (argued, not measured) |
| Example-first target-state is *more checkable* than a narrative one | Constructed refund example + SEED Lane-A framing | **Medium** (illustrative; not A/B tested) |
| Authors comprehend faster example-first than definition-first | — | **Unproven** (would need a reader study; NOT claimed) |

**Residue for the tower:** (1) the reader-comprehension speed claim is unmeasured — do
not promote on it; (2) the crossed-pair device is only demonstrated for *structural*
meta-types — behavioral/lifecycle/connective types may not admit a clean minimal pair;
(3) whether target-state pairs belong in the spec, the dispatch, or a new artifact is
still the SEED's open question, unchanged by this lens.
