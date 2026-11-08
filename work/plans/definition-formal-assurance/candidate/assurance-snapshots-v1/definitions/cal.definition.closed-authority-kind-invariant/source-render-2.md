<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Closed Authority-Kind Invariant

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.closed-authority-kind-invariant`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope.shared-authority`
- Lifecycle posture reference: `candidate:artifact-reconstruction-l1/v1`

## Scientific/formal voice

Closed Authority-Kind Invariant is the normalized invariant identified by semantic.closed-authority-kind-invariant, owned within scope.shared-authority, and carried by type.invariant. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D49 without silently merging it with another target.

Bound source-semantic basis:

Closed authority-kind enumeration is the invariant that the set of authority
**kinds** is a closed enumeration (the `../AUTHORITY-MODEL.md` Authority Kinds
table). An artifact whose kind is **not** in that enumeration may not acquire or
exercise authority — it defaults to **blocked** pending an owner decision that adds
the kind to the enumeration with its declared lifecycle (`CAV2-D48`) and owner
route. Adding a kind is itself owner-gated.

```text
```text
CAKE: Kinds is closed; for an artifact of kind k,
  k in Kinds      -> governed by k's own ladder/owner
  k not in Kinds  -> default-deny (blocked) until an owner amends Kinds
```

This **extends** `CAV2-D41` (which assumes a kind/owner exists and says "route to
it") to the case it assumes away — a kind with no enumerated owner/ladder yet.
```

### Notation

| Symbol | Meaning |
| --- | --- |
| semantic.closed-authority-kind-invariant | Stable normalized identity for Closed Authority-Kind Invariant. |
| CAV2-D49 | Bound CyberAlchemy-v2 source-definition identity. |

### Boundary conditions

- Scoped to authority **kinds** (the enumeration), not individual artifacts (that is
the Authority Rule, `CAV2-D41`) and not the per-artifact promotion path (`CAV2-D48`
+ the promotion-policy ladder). Promoting this definition did not by itself enact
the kind table as closed-with-default-deny. Review-mode enactment now lives in
the [AUTHORITY-MODEL catch-all row](../AUTHORITY-MODEL.md#authority-kinds);
deterministic enforcement remains pending.

### Testable conditions

- The candidate identity remains cal.definition.closed-authority-kind-invariant.
- Every selected source-section digest remains current.
- The machine record validates against Definition/v1.
- The human projection is regenerated exactly from the machine record.

## Plain-language voice

A new *type* of authority can't start governing just because it appeared. Until it
is on the official list of kinds — with its lifecycle and owner — anything of that
kind is blocked.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

In CyberAlchemy-lab migration work, Closed Authority-Kind Invariant is a prototype meaning reconstructed from CAL-NORMALIZE-01. It remains non-authoritative until the correct Lab owner admits a fully validated candidate.

Source context retained for reconstruction:

This definition **names** the closure invariant. As of 2026-06-23 it is **enacted
in review mode**: a **default-deny catch-all row** was added to the
[AUTHORITY-MODEL Authority Kinds table](../AUTHORITY-MODEL.md#authority-kinds) by
decision-gate ([decision record](../decisions/2026-06-23-authority-kind-closure-catchall-row.md)),
so an unenumerated kind defaults to blocked. The **deterministic** enforcement (the
automated kind-enumeration scan, the former `CAV2-C16` validator) is still pending
(OQ-1). Per the OQ-2 recommendation, the kind-table amendment for `invariant`/`axiom`
as their own kinds stays a future decision-gate call (they currently govern as the
`Definition` kind).

### Examples

- Resolve semantic.closed-authority-kind-invariant by its machine identity rather than its directory name.
- Challenge source drift through the L1 drift audit before relying on Closed Authority-Kind Invariant.

## Applicability

Use when a new *type* of authority appears (a new **kind**, not a new artifact of
an existing kind). Live open instance: `AUTHORITY-MODEL` OQ-2 — `invariant` and
`axiom` govern (`CAV2-D16`/`D29`/`D38`) yet sit outside the kind table.

### Exclusions

- Admission, activation, publication, release, deployment, and external effects.
- Meanings assigned to split or reclassified sibling targets unless explicitly referenced.

## Boundaries

- Scoped to authority **kinds** (the enumeration), not individual artifacts (that is
the Authority Rule, `CAV2-D41`) and not the per-artifact promotion path (`CAV2-D48`
+ the promotion-policy ladder). Promoting this definition did not by itself enact
the kind table as closed-with-default-deny. Review-mode enactment now lives in
the [AUTHORITY-MODEL catch-all row](../AUTHORITY-MODEL.md#authority-kinds);
deterministic enforcement remains pending.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cyberalchemy-v2:CAV2-D49 | ## CAV2-D49: Closed Authority-Kind Enumeration | `9cf4a46ecbcb51df0e3248681ccb2cb83b7a98fe8be82999d4be0f96638f5037` | `candidate-unadmitted` |

## Primary consumers

- semantic.artifact
- semantic.artifact-lifetime
- semantic.authority-promotion
- semantic.canonical-representation-invariant
- semantic.invariant

## Lookup and drift

- Index: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/registry.json` / `cal.definition.closed-authority-kind-invariant@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/drift-audit.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.originates-from | cal.definition.closed-authority-kind-invariant | cyberalchemy-v2:CAV2-D49 | role:definition-owner |

## Evidence

- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0003-review-led-reconstruction/target-candidates/semantic/semantic-closed-authority-kind-invariant/v1/artifact.json
- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/receipts/validation.json
- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/receipts/validation.json

## Residue

- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/drift-audit.json

## Claim ceiling

Candidate Definition reconstructed from an accepted normalization scaffold and exact CyberAlchemy-v2 source sections. It is not admitted and grants no implementation, migration, registry, publication, release, deployment, or external-effect authority.
