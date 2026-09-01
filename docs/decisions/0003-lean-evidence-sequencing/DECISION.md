<!-- Generated from decision.json. Do not edit this projection directly. -->

# Lean evidence sequencing

- Decision: `CAL-DECISION-0003-LEAN-SEQUENCING`
- Status: `owner-selected`
- Decision posture: `selected`
- Authority effect: `architecture-sequencing-only`
- Selected option: `LEANS-2` — Lean evidence is a parallel non-blocking lane after semantic snapshot acceptance
- Selected at: `2026-09-01T00:49:38Z`

## Admissibility binding

- Request: `admissibility-request.json` (`sha256:cf9f077b5861986ed119a92ae716edf029b9aa087427b22c388ff08f14e13540`)
- Canonical request digest: `c88df75863717dbf3b1b60b9c46dfe91555ecbe081d15a9fdf48c4af078e388c`
- Receipt: `admissibility-receipt.json` (`sha256:a80c89a81577d8726818be36f6a01a9d9886f3d4c2ab9aea6341620d8976e32f`)
- Route outcome: `gate`
- Presented options: `LEANS-1`, `LEANS-2`, `LEANS-D`, `LEANS-S`

## Binding effects

- CML-05 depends on the accepted CML-04 semantic Definition Snapshot.
- CML-06 depends on CML-05 and remains an independently accepted bounded-evidence branch.
- CML-07 depends directly on the accepted CML-04 semantic Definition Snapshot and does not depend on CML-05 or CML-06.
- Phase order is presentation order; explicit depends_on edges are the execution prerequisites.
- Lean provider failure or deferral leaves Lean evidence unresolved but does not revoke an accepted semantic snapshot or block the Craft identity branch.

## Non-effects

- This decision does not accept any Definition Snapshot, FormalClaim, Lean source, provider result, platform profile, environment lock, or architecture proposal.
- This decision does not authorize CML-01 or any migration, implementation, installation, Git, publication, release, or deployment effect.
- This decision does not make Lean a definition, runtime, implementation, release, or production authority.

## Remaining blockers

- The revised CAL-PROP-0001, CAL-PROP-0002, and CAL-PROP-0003 immutable digests still require one architecture-owner selection before CML-00 can complete.

## Claim ceiling

This decision selects only the dependency relationship between the semantic snapshot, bounded Lean evidence, and Craft identity phases. It does not admit artifacts, accept architecture bytes, complete CML-00, or authorize CML-01.

