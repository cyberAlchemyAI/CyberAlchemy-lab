## CAV2-D49: Closed Authority-Kind Enumeration

Status: active
Term: closed authority-kind enumeration
Aliases: authority-kind closure, default-deny for unenumerated kinds
Promoted: 2026-06-23 from `source-clusters/authority-lifecycle.md` `CAV2-CAND-LIFECYCLE-002` (re-scoped per review CR-1 from "no authority without a lifecycle", which re-skinned the Authority Rule)

### Normative Definition

Closed authority-kind enumeration is the invariant that the set of authority
**kinds** is a closed enumeration (the `../AUTHORITY-MODEL.md` Authority Kinds
table). An artifact whose kind is **not** in that enumeration may not acquire or
exercise authority — it defaults to **blocked** pending an owner decision that adds
the kind to the enumeration with its declared lifecycle (`CAV2-D48`) and owner
route. Adding a kind is itself owner-gated.

### Formal Interpretation

```text
CAKE: Kinds is closed; for an artifact of kind k,
  k in Kinds      -> governed by k's own ladder/owner
  k not in Kinds  -> default-deny (blocked) until an owner amends Kinds
```

This **extends** `CAV2-D41` (which assumes a kind/owner exists and says "route to
it") to the case it assumes away — a kind with no enumerated owner/ladder yet.

### Operational Interpretation

Use when a new *type* of authority appears (a new **kind**, not a new artifact of
an existing kind). Live open instance: `AUTHORITY-MODEL` OQ-2 — `invariant` and
`axiom` govern (`CAV2-D16`/`D29`/`D38`) yet sit outside the kind table.

### Plain-Language Intuition

A new *type* of authority can't start governing just because it appeared. Until it
is on the official list of kinds — with its lifecycle and owner — anything of that
kind is blocked.

### Domain-Context Voice

This definition **names** the closure invariant. As of 2026-06-23 it is **enacted
in review mode**: a **default-deny catch-all row** was added to the
[AUTHORITY-MODEL Authority Kinds table](../AUTHORITY-MODEL.md#authority-kinds) by
decision-gate ([decision record](../decisions/2026-06-23-authority-kind-closure-catchall-row.md)),
so an unenumerated kind defaults to blocked. The **deterministic** enforcement (the
automated kind-enumeration scan, the former `CAV2-C16` validator) is still pending
(OQ-1). Per the OQ-2 recommendation, the kind-table amendment for `invariant`/`axiom`
as their own kinds stays a future decision-gate call (they currently govern as the
`Definition` kind).

### Boundary

Scoped to authority **kinds** (the enumeration), not individual artifacts (that is
the Authority Rule, `CAV2-D41`) and not the per-artifact promotion path (`CAV2-D48`
+ the promotion-policy ladder). Promoting this definition did not by itself enact
the kind table as closed-with-default-deny. Review-mode enactment now lives in
the [AUTHORITY-MODEL catch-all row](../AUTHORITY-MODEL.md#authority-kinds);
deterministic enforcement remains pending.

### Primary Consumers

- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- [DEFINITION-DRIFT-AUDIT.md](DEFINITION-DRIFT-AUDIT.md)
- [../AUTHORITY-MODEL.md](../AUTHORITY-MODEL.md)
- [source-clusters/authority-lifecycle.md](source-clusters/authority-lifecycle.md)
- [../constitutions/STABLE-REPOSITORY-CONSTITUTION.md](../constitutions/STABLE-REPOSITORY-CONSTITUTION.md)
