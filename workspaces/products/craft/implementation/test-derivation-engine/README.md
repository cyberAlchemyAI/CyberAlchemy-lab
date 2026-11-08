# @domainspec/test-derivation-engine

Deterministic test-derivation engine. Compiles a feature's **canonical Markdown feature docs** into **byte-stable test obligations** — with **no LLM and no network** in the derivation path, so determinism holds _by construction_ (paper claim C2).

For a concrete walkthrough of the current engine, result interpretation, and the
planned multiformalism boundary, see [COMPLETE-GUIDE.md](COMPLETE-GUIDE.md).

> Replaces the LLM-backed `domainspec-generate-tests` / `domainspec-test-designer` derivation. See the design baseline in
> `../../development/deterministic-test-derivation-engine/` (source binding requires reconciliation)
> (SPEC, ARCHITECTURE, GLOSSARY, WORK-PACK) and the refinement evidence in
> `../../development/refinement-runs/2026-06-12-test-derivation-c2-cluster/` (source binding requires reconciliation).

## Pipeline

```
parse (docs → G) → derive (δ: pure) → obligation_key (sha1) → emit_spec / emit_tests
```

The parser accepts two explicit input dialects:

- legacy aspect documents (`states.md`, `operations.md`, and siblings); or
- normalized v2 `SPEC.md` when no aspect documents are present.

The normalized adapter derives structural conformance obligations for declared
concepts, relationships, fields, and attributes. It does not infer behavioral
semantics or path equations from prose.

Generate a machine-readable boundary receipt with:

```bash
pnpm exec tsx src/cli.ts receipt <feature-directory>
# add --out to write RESIDUE-RECEIPT.engine.json beside the input spec
```

The receipt separates normalized target declarations, source-evidenced preserved
relationship rows, explicitly omitted source rows, parser rejections, and
binding-side commitments. It is structural accounting, not a claim of semantic
satisfiability or application generation.

- `src/grammar/` — strict-grammar parser → typed concept graph `G` (SWU-ENG-001)
- `src/ir/` — `G` types (Node/Edge/Obligation), deterministic serialization
- `src/rules/` — pure δ rule functions with **exact** cardinalities (SWU-ENG-003)
- `src/keys/` — `obligation_key = sha1(source_anchor | rule_type | canonical_params)` ✅ implemented
- `src/emit/` — `emit_spec` (TEST-SPEC.md) and `emit_tests` (runnable vitest)
- `src/roundtrip/` — L0 falsification gate: engine set ⊇ committed ⇒ PASS

## Status

**Active deterministic engine.** Aspect-document parsing, normalized-`SPEC.md`
structural parsing, derivation rules, content-addressed obligation keys, round-trip
comparison, receipt accounting, and test emission are implemented and tested. See
`CRAFT.md` and the test suite for the current bounded gates; this status does not
claim semantic satisfiability or application generation.

## Develop

```bash
# from this folder (deps resolved via the workspace toolchain / pnpm dlx tsx)
pnpm install        # or: pnpm dlx tsx, matching repo convention
pnpm run typecheck  # tsc --noEmit
pnpm run test       # vitest run
```

## Test the admitted Auth SFOL case derivation

From this package directory, derive the eight Boolean cases from the exact
selected Auth SFOL claim, module, admission decision, and clause manifest:

```bash
npm run sfol:claim-cases -- \
  --root ../../../../../auth-foundation \
  --selection src/sfol/claim-cases/examples/auth-command-boundary.selection.json \
  --summary
```

Omit `--summary` to obtain the complete candidate case set. Save that JSON
and pass `--replay <saved-case-set.json>` to recompute it from the selected
current source bytes. A changed source or case set fails closed. This is a
TDE-owned typed finite-case derivation, not a DomainSpec v4 neutral obligation
set, independent proof of the manifest's graph/build provenance, provider
observation, or an F5 satisfying result.

To compare those eight cases with the Auth Rust command-boundary executable,
build the real native target and run the candidate local link:

```bash
# build from the repository root
tools/toolchain/run cargo build --offline --locked \
  --manifest-path auth-foundation/implementation/sfol-conformance/Cargo.toml

# then, from this package directory
npm run sfol:native-link -- \
  --root ../../../../../auth-foundation \
  --selection src/sfol/claim-cases/examples/auth-command-boundary.selection.json \
  --executable ../../../../../auth-foundation/implementation/sfol-conformance/target/debug/auth-foundation-sfol-conformance \
  --summary
```

Omit `--summary` to save the full link and use `--replay <saved-link.json>`
to re-execute against independently selected current sources and executable
bytes. The CLI pins the binary bytes it sees; it does not prove how the binary
was built. A matched replay is trusted-local observation only, with no
isolation, independent SFOL semantic proof, DomainSpec v4 neutral set, EVF
join, F5 satisfaction, or production runtime guarantee.
