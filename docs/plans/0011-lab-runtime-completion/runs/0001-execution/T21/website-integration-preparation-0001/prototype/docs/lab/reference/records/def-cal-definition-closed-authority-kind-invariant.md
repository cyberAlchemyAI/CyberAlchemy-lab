[Documentation home](../../README.md)

# Closed Authority-Kind Invariant

<a id="def-cal-definition-closed-authority-kind-invariant"></a>

[Reference](../README.md#reference) / [Definitions](../definitions.md#catalog-definitions) / Closed Authority-Kind Invariant

# Closed Authority-Kind Invariant

Requires authority-bearing kinds to belong to an explicitly closed allowed set, with an owner and declared lifecycle. A new kind is blocked pending an owner decision; the source distinguishes this rule from still-pending deterministic enforcement.

**When it applies**

Use when a new *type* of authority appears (a new **kind**, not a new artifact of an existing kind). Live open instance: `AUTHORITY-MODEL` OQ-2 — `invariant` and `axiom` govern (`CAV2-D16`/`D29`/`D38`) yet sit outside the kind table.

**Record formats**

No record-type contract in this selected catalog declares this exact definition among the meanings it uses.

**A stated exclusion**

Admission, activation, publication, release, deployment, and external effects.

### Formal definition, source explanation and boundaries

The formal statement governs the meaning. The short introduction above helps you read it; it does not replace its requirements.

<a id="def-cal-definition-closed-authority-kind-invariant-section-2"></a>

## Source explanatory wording

A new *type* of authority can't start governing just because it appeared. Until it is on the official list of kinds — with its lifecycle and owner — anything of that kind is blocked.

<a id="def-cal-definition-closed-authority-kind-invariant-section-3"></a>

## Exact governing statement

Closed Authority-Kind Invariant is the normalized invariant identified by semantic.closed-authority-kind-invariant, owned within scope.shared-authority, and carried by type.invariant. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D49 without silently merging it with another target.

Bound source-semantic basis:

Closed authority-kind enumeration is the invariant that the set of authority **kinds** is a closed enumeration (the `Authority model` Authority Kinds table). An artifact whose kind is **not** in that enumeration may not acquire or exercise authority — it defaults to **blocked** pending an owner decision that adds the kind to the enumeration with its declared lifecycle (`CAV2-D48`) and owner route. Adding a kind is itself owner-gated.

````
```text
CAKE: Kinds is closed; for an artifact of kind k,
  k in Kinds      -> governed by k's own ladder/owner
  k not in Kinds  -> default-deny (blocked) until an owner amends Kinds
```

This **extends** `CAV2-D41` (which assumes a kind/owner exists and says "route to
it") to the case it assumes away — a kind with no enumerated owner/ladder yet.
````

- Scoped to authority **kinds** (the enumeration), not individual artifacts (that is the Authority Rule, `CAV2-D41`) and not the per-artifact promotion path (`CAV2-D48` + the promotion-policy ladder). Promoting this definition did not by itself enact the kind table as closed-with-default-deny. Review-mode enactment now lives in the [AUTHORITY-MODEL catch-all row](Authority model#authority-kinds); deterministic enforcement remains pending.

**Acceptance status**

Accepted `(admitted)`

**Acceptance record**

Complete definition intake admission

**Original definition**

[Read the original record](../../assets/067721443c09-definition.json)

### Exact identity, version and content fingerprint

**Exact reference**

cal.definition.closed-authority-kind-invariant@1.0.0-candidate.1

**Content fingerprint · SHA-256**

067721443c09705f2482ebaf50092a5d3e0dea5284820f5842b7faf9e8f05ba8

The reference identifies this definition and version. The fingerprint identifies its captured contents; it is not evidence that the definition is true.

### Where this definition applies—and its exclusions

Scope identifies the purpose and authority boundary. Exclusions state what this definition does not cover.

````json
{
  "applicability": "Use when a new *type* of authority appears (a new **kind**, not a new artifact of\nan existing kind). Live open instance: `AUTHORITY-MODEL` OQ-2 — `invariant` and\n`axiom` govern (`CAV2-D16`/`D29`/`D38`) yet sit outside the kind table.",
  "authority_scope_ref": "scope.shared-authority",
  "exclusions": [
    "Admission, activation, publication, release, deployment, and external effects.",
    "Meanings assigned to split or reclassified sibling targets unless explicitly referenced."
  ]
}
````

[Return to Definitions](../definitions.md#catalog-definitions)
