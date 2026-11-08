# Decision Gate — Empty Minted Project Contract

Status: `PASS`; Option 1 selected by operator  
Target: `SWU-MNP-005`

## Blocking Question

How should the factory satisfy both an empty/example-free consumer project and
an immediately valid compile/view receipt when the v1 project and feature
schemas currently require at least one feature and at least one node?

## Evidence

- `project.schema.json` sets `features.minItems` to `1`.
- `feature.schema.json` sets `node_sources.minItems` to `1`.
- The resolver independently rejects either array when empty.
- SWU-MNP-005 requires an empty/example-free feature root, a compile/view smoke
  receipt, no consumer semantics in the factory template, and a clean promoted
  result.
- A template-owned placeholder node would be authored semantics, even if named
  generically; a structurally incomplete project would not satisfy compile/view
  acceptance.

## Options

### 1. Admit empty projects in v1 — Recommended

Repair the project/feature contracts and resolver/compiler behavior so zero
features and zero nodes compile to a valid empty graph, manifest, Markdown view,
and receipt. Benefit: a clean factory output contains no borrowed semantics and
is immediately verifiable. Cost: reopen the bounded contract as
`SWU-MNP-001-R2`, repair affected fixtures/digests, then resume SWU-MNP-005.

### 2. Require consumer-supplied bootstrap semantics

Make mint inputs include at least one consumer-authored feature and node, then
compile those inputs during staging. Benefit: preserves the current non-empty
v1 contract. Cost: `mint` is no longer a clean empty-project operation and the
caller must understand node formation before a project can exist.

### 3. Emit a removable template-owned bootstrap node

Ship one neutral-looking Entity node and tell consumers to replace it. Benefit:
smallest code change. Risk: violates the explicit no-consumer-semantics template
boundary and makes generated factory content appear canonical; not recommended.

### 4. Split scaffold from validation

Mint an incomplete empty scaffold and run compile/view only against a temporary
smoke project that is removed before promotion. Benefit: keeps promoted bytes
example-free. Risk: the delivered project itself is not compile-valid, so the
receipt does not prove what was minted.

## Selection

- Selected option: 1, admit empty projects in v1.
- Rationale: preserve a compile-valid, example-free factory output without
  introducing template-owned domain semantics.
- Source: operator response `1` on 2026-07-15.
- Remaining blocker: none; execute `SWU-MNP-001-R2`, then retry SWU-MNP-005.
