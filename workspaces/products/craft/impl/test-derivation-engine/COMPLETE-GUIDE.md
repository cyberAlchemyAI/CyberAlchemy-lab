# Test Derivation Engine User Guide (Pre-release)

## Start here

The Test Derivation Engine, or TDE, turns a supported DomainSpec feature into a stable
list of things that must be checked.

```text
feature documents
  -> strict parser
  -> typed concept graph
  -> deterministic rules
  -> stable obligations
  -> test specification or runnable scaffold
```

The current derivation path uses no language model and no network. The same supported
input produces the same ordered obligations and identifiers.

Suppose a feature declares:

```text
Player -------- performs -------> OpenDoor -------- produces -------> DoorOpened
                                     ^
                                     |
                                  enforces
                                     |
                              OnlyKeyHolder
```

TDE does not build the game. It creates a precise checklist stating which declarations
and relationships later implementation checks must account for.

For the short overview, see [README.md](README.md). For the evidence system that
consumes TDE results, see
[the EVF guide](../../development/evolvable-validation-framework/COMPLETE-GUIDE.md).

## What TDE does

TDE currently helps a team:

1. read supported DomainSpec documents with a strict grammar;
2. reject malformed or unresolved declarations;
3. build a typed internal graph;
4. apply pure deterministic derivation rules;
5. assign stable machine and human IDs;
6. emit a test specification and selected runnable scaffolds;
7. compare derived obligations with committed expectations;
8. record provenance, omissions, rejections, and later commitments; and
9. hand neutral obligations to validation and evidence stages.

## What TDE does not do

TDE does not infer missing behavior, decide whether a requirement is correct, generate
a complete application, or prove implementation conformance merely by deriving an
obligation. It does not approve profiles, providers, results, releases, or deployments.
It also does not make the planned TypeScript/Python/Rust epoch current by documenting
it.

## Learn one idea at three levels

The invariant stays the same:

> Supported declarations produce deterministic, source-anchored obligations;
> unsupported meaning stays visible instead of being guessed.

### Level 1: add one field

Start with `Player.playerId`. TDE derives one obligation requiring the selected
implementation or harness to account for it. Add a supported `keyId` field and derive
again. Old obligations keep their identity and exactly one new obligation appears.

This demonstrates deterministic structural refinement. It does not prove that
`keyId` has the right business meaning.

### Level 2: derive a feature checklist

For the Key-and-Door graph above, TDE can create obligations for supported concepts,
fields, attributes, and relationships. The receipt separately records explicit
omissions and parser rejections.

This demonstrates accountable translation into a stable checklist. It does not prove
that `OpenDoor` checks the key at runtime.

### Level 3: render one neutral case through several languages

The planned multiformalism epoch keeps `price >= 0` neutral before rendering it:

```text
admitted bounded projection
  -> neutral cases: negative, zero, positive
       -> TypeScript -> exact provider -> normalized evidence
       -> Python     -> exact provider -> normalized evidence
       -> Rust       -> exact provider -> normalized evidence
  -> semantic parity comparison
```

Parity concerns obligation IDs, cases, outcomes, evidence classes, and ceilings—not
byte-identical code. Each language needs its own admitted profile and provider.

This is target architecture. The current r4 package is a pre-admission plan whose 22
planned witnesses remain unimplemented and unexecuted.

## Understand the current pipeline

```text
parse (documents -> G)
  -> derive (pure rules)
  -> obligation key
  -> emit specification or tests
```

### 1. Select the input dialect

The parser accepts legacy aspect documents such as `states.md` and `operations.md`, or
a normalized v2 `SPEC.md` when aspect documents are absent. The normalized adapter
reads explicit concepts, relationships, fields, attributes, and omissions. It does not
infer behavioral semantics or path equations from prose.

### 2. Parse into graph `G`

The strict parser creates typed records. It rejects malformed inputs, including missing
required tables and relationships whose endpoints are undeclared. Failing here is
safer than producing an empty checklist that looks successful.

### 3. Derive obligations

Pure rules map supported graph records to obligations. Each obligation has a source
anchor, rule type, canonical parameters, stable identities, and a structural condition.
It can require a field to be accounted for without deciding whether the field has the
correct domain meaning.

### 4. Assign stable identity

The machine key is content-addressed from source anchor, rule type, and canonical
parameters. Parameter ordering is normalized before hashing.

```text
same declaration -> same key
material change  -> changed key
```

### 5. Emit an output

TDE renders a generated test specification. Selected paths can emit runnable Vitest
scaffolds. Structural declarations are labelled when they still need an
implementation-specific harness. Generation is not execution.

### 6. Compare or record the boundary

Round-trip comparison checks whether derived semantics cover committed expectations.
The residue receipt separately records target declarations, source-backed
relationships, explicit omissions, parser rejections, and binding-side commitments.
It describes the translation; it does not approve its meaning.

## Run the current engine

Run from `projects/domainspec-v2/impl/test-derivation-engine`.

```bash
pnpm run typecheck
pnpm run typecheck:sfol
pnpm run test
```

Preview obligations:

```bash
pnpm exec tsx src/cli.ts derive <feature-directory>
```

Write generated output and stable human IDs only after reviewing the target:

```bash
pnpm exec tsx src/cli.ts derive <feature-directory> --out
```

Create a boundary receipt:

```bash
pnpm exec tsx src/cli.ts receipt <feature-directory>
pnpm exec tsx src/cli.ts receipt <feature-directory> --out
```

`--out` writes `RESIDUE-RECEIPT.engine.json` beside the input. Check generated drift
and canonical form with:

```bash
pnpm exec tsx src/cli.ts check <feature-directory>
pnpm exec tsx src/cli.ts lint <feature-directory>
pnpm run roundtrip
```

Round-trip and normalized derivation answer different questions. One passing route
does not prove every dialect or evidence lane passed.

## Read the implementation folders

```text
src/
  grammar/        supported document readers
  ir/             graph and obligation vocabulary
  rules/          pure deterministic derivation
  keys/           stable machine keys
  identity/       human-readable IDs
  emit/           specifications and test scaffolds
  provenance/     exact input identity
  residue/        boundary accounting
  roundtrip/      derived-versus-committed comparison
  bindings/       exact implementation bindings
  minted-project/ bounded EVF paths
  sfol/           logic, cases, evaluators, provider contracts
  bte/            backend type-test compatibility work
```

Co-location does not merge ownership. Derivation, binding, provider execution, EVF
composition, and consumer decisions remain separate.

## Understand residue

| Category | Meaning | Example |
| --- | --- | --- |
| Preserved | Source represented in the target | `enforces` becomes an obligation. |
| Omitted | Source deliberately absent | A row listed in omissions. |
| Rejected | Input violates the profile | Edge points to an undeclared node. |
| Added commitment | A later stage makes a choice | Binding selects an exact function. |
| Unsupported | Meaning outside the fragment | Prose workflow lacks admitted semantics. |

Residue is visible difference, not automatically error. The receipt does not turn
omission into loss, rejection into falsehood, or a binding into source meaning.

## Current engine versus planned epoch

| Area | Works now | Planned or gated |
| --- | --- | --- |
| Input | Aspect docs and normalized `SPEC.md` | FormalClaim envelopes and admitted projections |
| Derivation | Deterministic structural obligations | General language-neutral profile IR |
| Identity | Stable obligation keys and human IDs | Cross-language case/profile identities |
| Output | Test specs and selected Vitest scaffolds | Independent TypeScript, Python, Rust renderers |
| Evidence | Round-trip, residue, provenance, bounded EVF paths | General multi-language receipts and parity |
| Lean | Separate formal contracts | Exact routing to EVF; never ordinary rendering |
| Authority | Private candidate-local implementation | Admission, release, deployment remain external |

## The planned multiformalism flow

### 1. Verify one source authority

Intake requires exactly one current FormalClaim source, its logic semantics, and
digests. Floating `latest`, unresolved aliases, duplicate authority, or stale identity
blocks before derivation.

### 2. Interpret capability assessment

Validation governance classifies the claim as `executable-bounded`,
`solver-admissible`, `proof-provider-required`, `unsupported`, or `indeterminate`.
Unsupported, indeterminate, timeout, malformed, stale, or missing evidence never
passes.

### 3. Require a preservation-backed projection

An executable projection is separate from source meaning. It binds the source,
assessment, assumptions, bound, target profile, preservation evidence, currentness,
and claim ceiling. `price >= 0` may yield bounded negative, zero, and positive cases.
“Every account has an owner” is not automatically executable merely because it is
valid first-order logic.

### 4. Derive neutral cases

The core emits stable obligation IDs, case IDs, partitions, oracle needs, provenance,
and ceilings without language syntax.

### 5. Resolve one exact profile

The registry accepts only an explicit admitted descriptor with exact renderer,
toolchain, provider, normalization, version, and digest. Unknown, duplicate, stale,
conflicted, or provider-absent profiles block. There is no ambient plugin discovery.

### 6. Render and execute independently

Each renderer produces native artifacts. Its exact provider returns native evidence.
One language cannot inherit another language's admission.

### 7. Compare semantic parity

Parity compares obligations, cases, outcomes, evidence classes, and ceilings. One lane
failure leaves other results intact but blocks a required join. There is no majority
vote.

Lean follows a separate theorem-provider route through EVF. TDE does not translate
Lean into ordinary application tests.

## Read results safely

Ask:

1. Which dialect and exact source files were selected?
2. Did parsing reject anything?
3. What was preserved, omitted, or unsupported?
4. Which rule produced each obligation?
5. Did unchanged declarations retain identity?
6. Was only a specification emitted, or was real code bound and run?
7. Which provider and runtime produced any observation?
8. What does the claim ceiling permit?

| Result | Safe conclusion | Unsafe conclusion |
| --- | --- | --- |
| Parsing passed | Input follows the grammar. | Domain meaning is correct. |
| Obligations derived | A stable checklist exists. | Implementation satisfies it. |
| Output byte-stable | Supported input reproduced bytes. | Output is complete. |
| Round-trip passed | Derived set covers its comparison set. | Every route passed. |
| Test emitted | An artifact was generated. | Real code passed. |
| Languages agree | Exact normalized cases matched. | Languages are equivalent. |

## Troubleshooting

### `derive` refuses to emit

Read every parser violation. Fix malformed tables or undeclared endpoints; do not
bypass fail-closed parsing.

### `check` reports a missing ID map

Run `derive <feature-directory> --out` only after reviewing the intended write scope,
then inspect the diff.

### Unchanged declarations received new keys

Compare source anchors, rule types, and canonical parameters. A path or material
parameter change can change identity; object insertion order alone should not.

### A normalized feature produced too few obligations

Inspect the residue receipt. Confirm which concepts, relationships, fields, and
attributes are supported, omitted, or rejected. Do not infer behavior from prose.

### A generated test contains a harness placeholder

The source supplied structure but no admitted executable binding. Add a separately
governed binding instead of putting implementation choices into source meaning.

### TypeScript works but Python or Rust does not

Profiles are independent. Verify that language's renderer, toolchain, provider,
normalization, fixtures, and admission. TypeScript success grants no other admission.

## Extend TDE carefully

For a new derivation rule:

1. identify the supported source declaration and owner;
2. define one pure rule with exact cardinality;
3. choose stable anchors and canonical parameters;
4. add positive, malformed, refinement, and determinism fixtures;
5. update residue accounting;
6. verify unchanged obligations retain identity; and
7. state what the rule does not prove.

A new dialect must define grammar, precedence, rejection, provenance, omissions, and
equivalence. A new language profile needs its own descriptor, renderer, runtime,
provider, normalization, negative fixtures, validation, and admission. An unregistered
profile must be rejected without changing the neutral core.

## Current status

The package is an active private deterministic engine for its declared scope: aspect
and normalized parsing, deterministic rules, stable keys, selected emission,
round-trip comparison, residue, provenance, and bounded EVF/SFOL/BTE work.

The multiformalism r4 artifact is pre-admission planning material: no unit is selected,
mutation readiness is false, and all 22 planned witnesses remain unimplemented. Do not
infer profile admission, release, deployment, or production readiness.

## Source map

| Need | Start here |
| --- | --- |
| Short overview | [README.md](README.md) |
| Source explanation | [src/README.md](src/README.md) |
| Package commands | [package.json](package.json) |
| Next-epoch specification | [r4 SPEC](../../development/test-derivation-engine-next-epoch/invoke-define-design-plan/20260825T001515Z-tde-multiformalism-profile-epoch-r4/define/SPEC.md) |
| Next-epoch architecture | [r4 architecture](../../development/test-derivation-engine-next-epoch/invoke-define-design-plan/20260825T001515Z-tde-multiformalism-profile-epoch-r4/design/ARCHITECTURE.md) |
| EVF guide | [EVF COMPLETE-GUIDE.md](../../development/evolvable-validation-framework/COMPLETE-GUIDE.md) |

## Glossary

| Term | Plain meaning |
| --- | --- |
| Dialect | One explicitly supported document format. |
| Graph `G` | TDE's typed internal source representation. |
| Derivation rule | A pure mapping from declarations to obligations. |
| Obligation | A stable condition a later stage must account for. |
| Source anchor | Exact source location contributing to identity. |
| Obligation key | Deterministic machine identity from canonical inputs. |
| Provenance | Exact input-file identity for an output. |
| Residue | Preserved, omitted, rejected, added, or unsupported material. |
| Binding | A separate commitment to exact implementation. |
| Neutral IR | Language-independent obligations and cases. |
| Profile | Exact renderer, runtime, provider, and normalization contract. |
| Semantic parity | Agreement on cases and evidence, not source text. |

## Four questions before trusting a TDE claim

1. Which source declarations and rules produced the obligations?
2. What was preserved, omitted, rejected, unsupported, or added later?
3. Was anything actually bound and executed, or only generated?
4. What current evidence supports the result, and where does its ceiling stop?
