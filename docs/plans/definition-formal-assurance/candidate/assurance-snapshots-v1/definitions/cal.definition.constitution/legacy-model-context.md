# CyberAlchemy v2 Authority Model

Status: active local authority model
Owner: CyberAlchemy v2 authority owner
Canonical definition: [CAV2-D41 authority model](definitions/DEFINITIONS.md#cav2-d41-authority-model)

## Purpose

This model explains how CyberAlchemy v2 decides what may count as evidence,
candidate meaning, local authority, implementation work, validation evidence, or
future standalone repository material.

It binds together the authority surfaces already present in this project:

- [definitions/DEFINITIONS.md](definitions/DEFINITIONS.md)
- [constitutions/](constitutions/)
- [../disciplines/DISCIPLINES.md](../disciplines/DISCIPLINES.md)
- [decisions/](decisions/README.md)
- [promotion-policy.md](promotion-policy.md)
- [boundaries.md](boundaries.md)
- [../ontology/](../ontology/README.md)

## Authority Rule

Authority moves by owner route, not by proximity, usefulness, or repetition.

If a claim, term, rule, method, artifact, signal, or source fragment would change
what CyberAlchemy v2 is allowed to rely on, it must be routed to the narrowest
responsible owner before it governs work.

## Core Flow

The default movement is:

```text
source evidence
  -> import candidate
  -> inventory or ontology candidate
  -> owner-routed local authority
  -> implemented or validated behavior
  -> stable repository asset
```

This is a review flow, not an automatic pipeline. A later state can be blocked,
deferred, demoted, or re-routed when the evidence, owner, boundary, or validation
surface is inadequate.

## Authority Kinds

| Kind | Owner route | Counts where | Must not collapse into |
| --- | --- | --- | --- |
| Definition | definitions-governance | `authority/definitions/DEFINITIONS.md` | glossary usage, ontology naming, source wording |
| [Constitution](definitions/DEFINITIONS.md#cav2-d58-constitution) | constitution-governance | `authority/constitutions/` | preference, one-off review comment, hidden validator |
| Discipline | discipline-governance | `disciplines/` | canonical term, sigil, spell, implementation task |
| Decision | decision-gate | `authority/decisions/` | unresolved discussion or ambient consent |
| Spec | spec owner plus decision-gate | `specs/` after promotion | research finding or interface idea |
| Runtime contract | task-session after owner gates | `implementation/` or generated surface contract | successful generation or projection |
| Projection | ontology route plus source owner | `ontology/projections/` or generated read model | promotion decision |
| Evidence | source, inventory, validation, or observability owner | source, inventory, validation, observability | authority by itself |
| Residue | route named by residue type | gap ledger, Craft, or owner route | defect by default |
| *(any unenumerated kind)* | decision-gate + constitution-governance (add it here first) | nowhere — not authority until promoted into this table | a silently-governing new kind; **default-deny** ([CAV2-D49](definitions/DEFINITIONS.md#cav2-d49-closed-authority-kind-enumeration)) |

**Closure (default-deny).** This enumeration is **closed**: an artifact whose kind
is not a row above may not acquire or exercise authority — it defaults to
**blocked** pending a decision-gate + constitution-governance decision that adds
the kind (with its [CAV2-D48](definitions/DEFINITIONS.md#cav2-d48-authority-promotion-lifecycle)
lifecycle and owner route). Enforcement is **review-mode** today; the deterministic
kind-enumeration scan is pending (OQ-1). Decision record:
[2026-06-23 authority-kind closure catch-all row](decisions/2026-06-23-authority-kind-closure-catchall-row.md).
(Active Axiom/Invariant definitions `CAV2-D53`/`D54` and specific invariant
definitions `CAV2-D16`/`D29`/`D38`/`D49` govern **as the `Definition` kind** —
not blocked; whether to elevate `invariant`/`axiom` to their own kinds is OQ-2,
deferred.)

## Authority Postures

Authority posture says how a source or artifact may be relied on before
promotion.

| Posture | Allowed use | Blocked use |
| --- | --- | --- |
| Original authority | Cite for its own source scope. | Treat as CyberAlchemy v2 authority without import and promotion. |
| Evidence | Support candidates and gates. | Replace owner decision. |
| Template | Reuse shape with attribution. | Copy semantics as canon. |
| Research | Support design and owner review. | Become spec or definition automatically. |
| Generated projection | Support search, navigation, or traceable read models. | Canonical source. |
| Private evidence | Support private-parent reasoning. | Public artifact without scrub. |
| Public framework | Support public-safe framework evidence. | Local authority by proximity. |
| Unknown | Stage as unresolved. | Promotion or public reuse. |

## Narrowest Owner Rule

When a candidate crosses a boundary, route it to the smallest authority owner
that can decide the movement.

| Movement | Owner route |
| --- | --- |
| A term becomes load-bearing. | definitions-governance |
| A rule should constrain future artifacts. | constitution-governance |
| A recurring practice needs a steward and hardening path. | discipline-governance |
| A promotion, scope, naming, or public/private choice is contested. | decision-gate |
| A bounded implementation mutation is ready. | task-session |
| Source material must be staged before local use. | authority import |
| Candidate meaning needs mapped relations, confidence, and promotion requests. | ontology route |

## Invariant, Axiom, Constitution

The model has two directions that must not be collapsed:

```text
discovery:     invariant -> ask "why must this hold?" -> axiom
justification: axiom -> invariant -> constitution rule -> validator/gate -> governed subject behavior
```

An invariant states what must remain true or what violation counts as drift. An
axiom admits the load-bearing principle that explains why action or governance
must be constrained. A constitution rule operationalizes an invariant for
scoped artifacts, tasks or workflows, repository-owned agent actions, system
operations or state transitions, validation surfaces, or authority movements.
A constitution supplies owner-adopted authority and scope; a selected validator
or gate performs or checks enforcement. A discipline may steward the recurring
evidence, assessment, and routing practice, but it cannot author or adopt a
constitution.

This is a routing pattern, not a law. Some constitutions may encode invariants
directly. Some axioms may remain source-local. Some invariants may stay
diagnostic until a later owner route promotes them.

## Non-Collapse Rules

1. Evidence can support authority, but it is not authority by itself.
2. Ontology can model authority, but it cannot decide authority.
3. Inventory can reduce search and preserve evidence, but it cannot promote.
4. A discipline can recommend a route, but it cannot define a term or author a
   constitution.
5. A constitution can constrain future artifacts, but it does not prove the
   source claim that motivated it.
6. A successful implementation or validation run does not redefine the term,
   rule, or method it exercised.
7. Public-safe language must not inherit private evidence by proximity.

## Gate Vocabulary

Authority gates use the project vocabulary from [CAV2-D37 gate](definitions/DEFINITIONS.md#cav2-d37-gate):

- `pass`: evidence, owner, boundary, and validation surface are adequate.
- `flag`: movement may continue with named risk and follow-up.
- `block`: movement must stop until the named gap closes.
- `defer`: movement is not rejected, but the owner route or timing is not ready.

## Validation Surface

Current validation is review-first and link-backed:

- [promotion-policy.md](promotion-policy.md) defines the ladder and required gates.
- [constitutions/STABLE-REPOSITORY-CONSTITUTION.md](constitutions/STABLE-REPOSITORY-CONSTITUTION.md) constrains authority layer separation, import-before-promotion, public/private boundary, and standalone extraction.
- [definitions/DEFINITION-DRIFT-AUDIT.md](definitions/DEFINITION-DRIFT-AUDIT.md) records semantic drift and undefined critical terms.
- [../ontology/AUTHORITY-KINDS.md](../ontology/AUTHORITY-KINDS.md) and [../ontology/AUTHORITY-POSTURES.md](../ontology/AUTHORITY-POSTURES.md) remain candidate model views under the ontology route.

## Open Questions

### OQ-1. Should authority kinds become validator-backed?

Context: the kind table is currently review-governed. Recommendation: write a
deterministic check only after the authority object schema and promotion records
are stable enough to avoid freezing the wrong shape. Status: OPEN.

### OQ-2. Should invariant and axiom become first-class authority kinds?

Context: generic `axiom` (`CAV2-D53`) and `invariant` (`CAV2-D54`) are active
definitions, but both currently govern under the `Definition` authority kind.
Recommendation: decide separately whether either warrants a first-class row;
their definition status does not answer that authority-kind question. Status: OPEN.
