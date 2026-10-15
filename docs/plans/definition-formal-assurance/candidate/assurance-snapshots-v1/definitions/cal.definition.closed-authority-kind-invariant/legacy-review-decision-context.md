# Decision: Authority-Kind Closure — Default-Deny Catch-All Row

Status: pass
Owner route: decision-gate + constitution-governance
Timestamp: 2026-06-23
Target: [AUTHORITY-MODEL.md](../AUTHORITY-MODEL.md) Authority Kinds table
Enacts: [CAV2-D49 closed authority-kind enumeration](../definitions/DEFINITIONS.md#cav2-d49-closed-authority-kind-enumeration)

## Consequential Work

This decision adds a **default-deny catch-all row** to the AUTHORITY-MODEL
Authority Kinds table, enacting the closure invariant `CAV2-D49` in **review
mode**. It is the owner-gated act `CAV2-D49` itself requires — adding or changing
an authority kind routes through decision-gate. It does **not** build the
deterministic validator; the automated kind-enumeration scan (the `CAV2-C16`
hybrid adapter) remains pending under OQ-1 / sigil-development.

## Decision: add the catch-all row (fold-into-table fork)

Selected option: add a default-deny catch-all row to the Authority Kinds table.

Rejected options:

- **Stand-alone `CAV2-C16` constitution rule only** (no table row) — chose instead
  to fold the closure into the table where the kinds are enumerated, so closure is
  self-documenting at its natural home.
- **Add `invariant` + `axiom` as kinds now** — sequencing-blocked by AUTHORITY-MODEL
  OQ-2 ("promote the generic definitions before adding to the kind table"); those
  definitions are not yet promoted.
- **Do nothing** — leaves closure defined (`CAV2-D49`) but unenacted.

Rationale: lowest-risk and in-policy now. The catch-all row enacts review-mode
closure (any kind not enumerated above defaults to blocked / route-to-owner)
without requiring the deterministic validator. It realizes `CAV2-D49` at the table
where authority kinds live.

Enforcement mode: **review** (the deterministic scan — `CAV2-C16`'s automated
check — remains pending; tracked under OQ-1 validator-backing + sigil-development).

## Downstream effect

- **`CAV2-C16` as a stand-alone constitution rule is superseded** by this table row
  plus the future validator; the "fold into kind table" fork is chosen.
- **OQ-2 stays OPEN.** Note: the existing invariant definitions (`CAV2-D16`/`D29`/
  `D38`/`D49`) currently govern **as the `Definition` kind** (enumerated) — the
  catch-all does **not** block them. OQ-2 is the separate question of whether to
  elevate `invariant`/`axiom` to their own kinds; until then they remain Definitions.

## Residue

- The deterministic validator (automated kind-enumeration scan) is not built.
- `invariant`/`axiom` kind-table addition remains deferred (definitions-first).
