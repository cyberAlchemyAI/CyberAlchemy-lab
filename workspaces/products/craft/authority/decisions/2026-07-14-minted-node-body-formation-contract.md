# Decision Gate — Minted Node Body Formation Contract

Status: `PASS`; Option 1 selected by operator  
Target: `SWU-MNP-003`

## Blocking Question

How should canonical meta-type formation criteria be represented and validated
inside a minted project's machine JSON node `body`?

## Evidence

- Canonical formation schemas are table-oriented `.schema.yml` contracts.
- Operation, Rule, and Event criteria have apparent flat declared-attribute
  keys: `state_change`, `formal_return_type`, and `temporal`.
- Entity requires both at least one identity field and nonempty type cells.
- The current Key/Door Player body has `identity_fields` but no field types.
- No production mapping from those criterion schemas to JSON body fields exists.

## Options

### 1. Per-kind machine body schemas — Recommended

Add explicit machine body schemas for the four admitted kinds, reference them
from the supported profile, and repair the Key/Door fixture so Entity proves
typedness and identity. Benefit: bounded and authority-aligned. Cost: reopens a
small part of SWU-MNP-001 before compiler work. Downstream: compiler validates
the selected body schema and can make an honest formation claim.

### 2. One generic fields-and-attributes representation

Standardize every node body on `fields[]` plus `attributes{}` and translate all
formation criteria through that representation. Benefit: uniform expansion to
future kinds. Cost: larger contract/fixture migration and more abstraction now.
Downstream: future profiles gain one adapter, but SWU-MNP-003 starts later.

### 3. Minimal current-fixture adapter

Treat flat declared keys as formation and accept nonempty `identity_fields` as
the Entity check. Benefit: fastest and no fixture migration. Risk: canonical
typedness is not proven, so “formation validation” is weaker than the authority
it cites. Downstream: conformance/release must repair the semantic debt.

### 4. Explain / more context

Non-committal. Expand consequences and re-present options; does not resolve the
gate.

## Selection

- Selected option: 1, per-kind machine body schemas.
- Rationale: preserve an honest mapping to canonical formation criteria without
  imposing a premature generic body abstraction.
- Source: operator response `1` on 2026-07-15.
- Remaining blockers: none; execute `SWU-MNP-001-R1` before resuming 003.
