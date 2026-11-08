---
node_type: reference
is_session: false
status: candidate
created: 2026-07-02
authored_by: task-session (M1 — spec-comprehension-model)
source:
  - ./  (the per-type schema+md cards — the 13 active backend meta-types)
  - ../../../definitions/meta-types/meta-types.yml  (the 24 staged labels and differentiated maturity authority)
  - ../../../definitions/relationships/relationships.yml  (root relationship authority — 31 signatures; the edge reading-view below)
  - ../../../development/spec-comprehension-model/{DESIGN.md,ORDER.md}  (M1)
  - ../../../development/comprehension-novice-test/stall-dataset.md  (S1 individuation, S6 feature/context, S9)
promotion_boundary: PUBLIC reading aid. Tiering is a LEARNING order, never authority promotion — 13 backend types are active, nine UI labels are candidates, and two UI labels have differentiated deferred dispositions. Proposed definitions (§4) promote to definitions-governance separately.
---

# Meta-type learning order — read this before authoring a spec

DomainSpec currently has **13 active backend meta-types**, **nine UI candidates**, and **two deferred UI labels**, but an author does not meet all staged labels at once. This is a **learning
order**, not a new type system: backend types remain typed for the engine and validator; non-active UI labels remain guidance. Tier is a
**per-domain declarable lens** (Evans/Vernon: the same subdomain is core or generic depending on what the
org does) — a UI-heavy product may promote UI types; a pure-backend service may leave them generic.

**Tier ≠ category.** Category (Structural/Behavioral/Connective/Lifecycle/UI) is *where a type lives in the
graph*; tier is *when you learn it*. Event is Connective by category but Core by tier.

## 1. The three tiers (all 24 staged labels)

### CORE (6) — internalize these; one worked example each
| Type | One-line | Category |
| --- | --- | --- |
| **Entity** | has identity; tracked over time | Structural |
| **Value Object** | equal-by-fields; no identity | Structural |
| **Operation** | changes state | Behavioral |
| **Rule** | returns a boolean; blocks/allows | Behavioral |
| **State Machine** | states + transitions | Lifecycle |
| **Event** | announces something that already happened | Connective |

### SUPPORTING (6) — learn on demand, as "an X is a Y that…"
| Type | Learn it as… | Category |
| --- | --- | --- |
| **Enum** | a Value Object that is a finite value *set* | Structural |
| **Query** | an Operation that is **read-only** | Behavioral |
| **Calculation** | an Operation that **returns a value**, changes nothing | Behavioral |
| **Workflow** | orchestrates Operations with declared **intra-feature or cross-feature** scope | Behavioral |
| **Policy** | a Rule that **selects a strategy** instead of a boolean | Behavioral |
| **Interface** | an exposed boundary (what the outside can call) | Connective |

### GENERIC (12) — recognize + template; do not treat as active vocabulary
- **Mapping** — transforms fields between two shapes (has a direction).
- **Nine UI candidates** — Page, Layout, Component, View Model, Hook, Form, Action, Guard, and Binding.
- **Two deferred UI labels** — Adapter (merge-candidate toward Mapping) and State Indicator (split-candidate).
  Five labels have backend **shadow** relationships (see §2); none becomes active through this learning tier.

`6 core + 6 supporting + 12 generic = 24.`

## 2. The 5 shadows — a one-line dictionary (but they keep their own edge pressure)
Five retained UI labels mirror a backend type. Learn them as a lookup, **not** as active concepts — DS-D8
currently carries endpoint pressure for them, but edge use alone does not promote DS-D1 maturity:

| UI shadow | mirrors | its own edges (the root relationship authority) |
| --- | --- | --- |
| View Model | Value Object | `derives`←Entity, `displays`←Component, `shapes`←Adapter |
| Guard | Rule | `protects`→Page, `mirrors`→Rule |
| Binding | Interface | `fetches`→Query, `mutates`→Operation |
| Adapter | Mapping | `shapes`→View Model |
| State Indicator | State Machine / Enum | `reflects`→State Machine |

## 3. Edge reading-view (authority = the root relationship authority, NOT the card `edge_participation` slices)
> ⚠ The per-type `edge_participation` slices are known-inconsistent with the root relationship authority (novice stall S4,
> handed to R3). Until R3 reconciles them, **read edges from the root relationship authority.** Group the backend edges by
> what they express — with a `@cross` modifier for the cross-feature variants:

| Family | Base edge(s) | Reads as |
| --- | --- | --- |
| **actor** | `performs` | Entity does an Operation |
| **produce** | `produces` (→Event), `creates` (→same-feature Entity), `produces-for` (→cross-feature Entity) | an Operation's output or creation effect |
| **govern** | `enforces` (same verb with `@cross` placement), `applies` | a Rule blocks / a Policy steers an Operation |
| **derive / read** | `calculates`, `reads` | a Calculation derives from explicit inputs; a Query or Operation reads Entity data |
| **structure** | `contains` | an Entity embeds a Value Object |
| **lifecycle** | `transitions` | an Event moves a State Machine |
| **announce** | `emits` (Entity→Event), `triggers-cross` (`@cross`) | events out / cross-feature triggers |
| **expose / map** | `exposes`, `maps` | an Interface publishes; a Mapping reshapes |

Modifiers: **`@cross`** = spans features; the root signature decides whether the base verb or a dedicated
`-cross` verb carries that placement. **`@shadow`** = a UI mirror edge (§2).
*(This is a reading aid; the root relationship authority remains the source of truth and the validator's authority.)*

## 4. Two terms the surface never defined (proposed — promote via definitions-governance)
The novice could not resolve these from the surface; here are **working definitions** (S6, S1). These are
proposed for `definitions/DEFINITIONS.md` as DS-D terms — not yet canonical.

- **feature / bounded context** *(defines Workflow scope, S6):* a **feature** is the unit a spec
  is authored for — one `impl/spec/features/<name>/` package with its own concept registry. **Intra-feature**
  = all concepts resolve inside one such package; **cross-feature** (`@cross`) = a relationship or process
  whose endpoints live in two different packages. A Workflow declares `intra-feature` or
  `cross-feature` scope accordingly. *(This is the operational meaning; a fuller DDD "bounded context" definition — a boundary
  of language consistency — is a definitions-governance decision.)*
- **concept individuation cue** *(where one concept/operation begins & ends, S1):* one **Entity** = one
  identity (one thing you'd reference by id). One **Operation** = one state-changing action with a single
  transactional outcome and a single trigger — **split** it when there are two independent outcomes or two
  distinct triggers; **merge** when two steps always succeed or fail together. Value-vs-computation: model
  the *result* as a Value Object and the *computing* as a Calculation only when the result is referenced on
  its own. *(A cue, not a decision procedure — individuation is genuinely a judgment; Evans concurs.)*

## 5. Boundary
Tiering reorganizes **learning emphasis**; it does not promote candidate or deferred labels. **Completeness lives in the active type system**
(the engine/validator ranges over 13 backend types); **comprehensibility lives in this order.** The tier split is a
per-domain declarable lens. Adding a machine-readable `tier:` field to each `.schema.yml` is a **deferred**
follow-on — it must first confirm the schema validator accepts an optional field (else it regresses
`validate:*`). Until then, this doc is the authority for tier.
