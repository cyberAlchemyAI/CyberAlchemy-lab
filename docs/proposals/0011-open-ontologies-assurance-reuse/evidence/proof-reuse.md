# Design note: reuse upstream proof code without rewriting its proofs

Design evidence only, 2026-11-02. No files were copied into the Lab, no dependency installed, and no builds/checkers were run. Upstream is the inspected checkout at commit `c7fd75f9491253c56e4d4f408ceac179de343e48`.

## Recommendation

Copy the complete pinned upstream `lean/` workspace unchanged into a clearly separated third-party source tree when implementation is authorized. Keep the new Lab adapters outside that tree. It is only **84 tracked files / 1,136,038 bytes** (static inventory), has **no Lake package dependencies**, and already contains the required libraries, parsers, executables, negative examples, and proof audits.

This maximizes source reuse while avoiding the risk of accidentally omitting a theorem, default build target, parser, or self-identification helper. A separate workspace also avoids collisions with the Lab's existing global executable helper names and namespaces, and permits direct upstream diffs later. Do not flatten these files into an existing Lab proof tree or rename imported theorems merely for local style.

Proposed copy home (design): `third_party/open-ontologies/c7fd75f9491253c56e4d4f408ceac179de343e48/lean/`, with the upstream root `LICENSE` adjacent, plus a Lab-authored provenance/copy manifest outside the copied files. The manifest should enumerate repository URL, full commit, selected paths, per-file SHA-256, license, local build toolchain, and any later patch disposition. Do not copy `.lake`, compiled binaries, dependency caches, or upstream `.git` as a build input.

### Toolchain compatibility

- Upstream `lean/lean-toolchain`: `leanprover/lean4:v4.33.1`.
- Lab `craft/formalization/candidates/relational-theorem-checker/v1/formal/lean-toolchain`: same `leanprover/lean4:v4.33.1`.
- Lab `craft/formalization/candidates/relational-theorem-checker/v3/e06/tools/lean4export/lean-toolchain`: same `leanprover/lean4:v4.33.1`.
- No `lean` or `lake` executable was found on this session's PATH. Matching files remove an obvious version mismatch; they are not a successful build result.
- Upstream `lean/lake-manifest.json` has `packages: []`. `lakefile.toml` keeps all formal libraries and executables in `defaultTargets`. Preserve that exact list; upstream previously missed a broken proof because an omitted target never built.
- Upstream `.github/actions/lean-build/action.yml` is useful CI source to copy/adapt separately: pinned elan version/digest, bounded install retries, and a source build of the complete workspace. Its `working-directory` and cache paths require adaptation to the new location. Do not run the existing script unchanged against a different tree.

## Reuse units

| Unit | Direct unchanged source copy | New Lab work |
| --- | --- | --- |
| U-PROOF-TREE | Entire `lean/`, root MIT `LICENSE`. | Copy manifest, build/run policy and executable-path binding. No new proof code required. |
| U-MODEL | `Fol/`, `FolMain.lean`, `SelfId/`, plus original workspace files via U-PROOF-TREE. | Restricted Lab IR/model exporter and exact source-to-export mapping checker. |
| U-HORN | `OOCert/`, `OOCert.lean`, `Main.lean`, `HMain.lean`, `RefuteMain.lean`, SelfId via U-PROOF-TREE. | Lab relation/rule export, certificate selection, result envelope; use upstream producer code if the chosen sidecar already writes the files. |
| U-REFUTE | `Fo*`, `Lrat*`, `Dl*` via U-PROOF-TREE. | Select a matching input profile and existing producer path; bind clauses/axioms to selected Lab input. Do not add a new prover. |
| U-FIXTURES | Selected upstream-owned fixtures under `tests/fixtures/folmodel/`, `horn/`, `refute/`, `dlmodel/`, and relevant recorded TSTP files, with original provenance. | A small runner using unchanged bytes and expected outcomes; additional Lab bridge mutants. Avoid treating upstream Rust test sources as standalone programs. |
| U-HORN-SECOND/THIRD | Entire `isabelle/`, entire `rocq/`, and `tests/fixtures/horn/` in original relative layout. | Separate optional CI profiles and result collection; no editing the independent definitions to force agreement. |

A static import scan finds the minimal `oo-folmodel` local source closure is 11 Lean files: `FolMain.lean`, all seven `Fol/{All,Check,Free,Parse,Semantics,Syntax,Witness}.lean`, and `SelfId/{All,Report,Sha256}.lean`. That would also require workspace/toolchain files and a **modified** lakefile to stop default targets naming absent files. It is therefore a possible future size optimization, not the recommended initial copy. Other static closures are HMain 20, Main 19, ShaclMain 14, DlMain 15, DlRefuteMain 15, RefuteMain 13, FoMain 10, LratMain 9, MatCertMain 6. These are source-import counts, not rebuilt packages.

## Executable ABI and actual signatures

The original executables should retain their upstream names and command shapes. A Lab wrapper can present friendlier names without modifying them.

| Executable | Invocation and input | Acceptance means |
| --- | --- | --- |
| `oo-folmodel` | `oo-folmodel PROBLEM.tsv MODEL.tsv` | Supplied finite model satisfies the parsed exported problem; `Fol.satisfiable_of_check`. For an explicitly negated goal, `Fol.not_entails_of_check` can establish exported non-entailment. |
| `oo-horn` | `oo-horn rules`; `oo-horn check RULES.tsv ASSERTED.tsv HORN.tsv` | Rules exactly equal built-in table: `OOCert.entails_of_builtin_horn`; any supplied/modified table: `OOCert.horn_certificate_sound`, conditional on those rules. |
| `oo-cert` | `oo-cert ASSERTED.tsv DERIVATIONS.tsv` | Supported mixed built-in derivation certificate checks; `OOCert.certificate_sound`. |
| `oo-refute` | `oo-refute check ASSERTED.tsv REFUTATION.tsv` | Supported derivation-plus-clash certificate checks; `OOCert.refutation_fast_sound`. |
| `oo-dlmodel` | `oo-dlmodel AXIOMS.tsv MODEL.tsv` | Finite interpretation satisfies supported exported DL axioms; `Dl.satisfiable_of_checkModel`. |
| `oo-dlrefute` | `oo-dlrefute AXIOMS.tsv REFUTATION.cert` | Supported closed-tableau certificate checks; `Dl.unsatisfiable_of_check` over the general interpretation semantics. |
| `oo-resolution` | `oo-resolution REFUTATION.cert` | Resolution/factoring certificate refutes the included clause set; `Fo.unsat_of_check`. Not general superposition proof replay. |
| `oo-lrat` | `oo-lrat PROBLEM.cnf PROOF.lrat` | Propositional LRAT refutation checks; `Lrat.unsat_of_check`. |
| `oo-shacl` | `oo-shacl validate DATA.nt SHAPES.nt` | Supported compiled SHACL Core evaluation; `Shacl.validate_spec`. Shape compilation and N-Triples parsing are outside that theorem. |
| `oo-matcert` | `oo-matcert CERT.matcert` | Integer matrix product certificate; `MatCert.mul_of_check`. No floating-point/whole ML guarantee. |

Ordinary checker exits: 0 accepted, 1 rejected certificate/model, 2 unreadable/unparseable. SHACL differs: 0 reports an evaluated verdict (which can be non-conformance); 3 is undetermined. A wrapper must decode each ABI rather than treating any exit zero as universal conformance. Each supports `--version` and reports a self-description, but self-description alone does not authenticate the executable.

### FOL ABI: important mismatch with the Lab generic evaluator

The model checker is **not a generic many-sorted first-order engine**. `lean/Fol/Syntax.lean:45-62` explicitly supports:

- One nonempty carrier.
- Unary and binary predicates, constants, equality, true/false, negation, binary conjunction/disjunction/implication, and both quantifiers with natural-number variable identifiers.
- No explicit sort syntax; no predicates of arity three or higher; no positive-arity function symbols; no direct biconditional constructor.

`problem.tsv` is one `ROLE TAB LABEL TAB FORMULA` per line, with ROLE `axiom` or `goal_negated`. Prefix formula syntax is documented at `Syntax.lean:64-88`. Labels are diagnostic and are **not** in the semantic problem digest.

`model.tsv` records `domain N`, `problem HEX`, declarations (`decl1`, `decl2`, `declc`), unary bitsets, all binary bitset rows, and constant indices in `0..N-1`. Missing/duplicate/ill-sized rows are refused; see `Syntax.lean:91-126` and `Fol/Parse.lean`.

The embedded problem digest is FNV-1a 64 over canonical parsed formulas and roles. It is not a cryptographic commitment. The outer Lab evidence envelope must additionally hash exact source, mapping and exported files with SHA-256, including diagnostic-label mappings where they identify obligations.

The Lab's `semantics.py`/`ir.py` supports multiple sorts, arbitrary declared predicate/relation arities, and total functions. Do not silently erase these features in a direct exporter. There are two defensible stages:

1. **First profile, no new proof code:** admit only a precisely declared single-carrier, unary/binary, function-free closed-formula subset. Allocate injective whitespace-free symbol IDs and fresh variable IDs. Preserve constants, expand n-ary and/or and iff deterministically, and refuse all unsupported constructs. Retain source/target node mapping and every selected formula/obligation denominator. Run existing independent Lab model verification on the original input too. Strong label is “upstream checker accepted this exact exported encoding”; source faithfulness remains separately assessed.
2. **Later larger profile:** many-sorted lowering via explicit carrier predicates and guarded quantification, or functional relationalization, needs an exact adequacy contract and appropriate model transport. A kernel theorem that the original Lab IR has the same semantics is **new proof work**, not obtained by copying the upstream model checker. Do not design such work as already solved.

Even the first subset's translation is not mechanically proved simply because it is small and tested. This design maximizes unchanged proof reuse while keeping the unproved adapter boundary visible. The existing Lab `mechanized_proof:false` fields must not be globally flipped; a new evidence-policy binding must say exactly which exported obligation an upstream result can support.

### Horn ABI

`asserted.tsv` is `s TAB p TAB o` per triple. `derivations.tsv` is built-in rule name, conclusion triple and premise triples. `rules.tsv` is rule name, body count, triple patterns, and head; fields prefixed `?` are variables. `horn.tsv` is rule index, binding count, variable/term pairs, conclusion and premise triples. See `lean/OOCert/Parse.lean:4-16` and `HornParse.lean:5-16`.

The supplied rules are assumptions; a Lab-specific allowed-endpoint rule does not become an OWL fact just because Horn checking accepts it. Keep source-selected rules, graph scope and reasoner completeness separate. Triples represent one exported view, not the union of unrelated ontology versions. A checked Horn derivation is not by itself a global Lab Typed Relation or owner approval.

## Independent Horn checker workspaces

Direct copying is possible and useful, but optional initially:

- **Isabelle:** preserve all theories, `ROOT`, scripts, generated `driver/oo_horn_generated.ML`, CLI/driver files and fixtures. A full Isabelle2025-2 rebuild regenerates the export. `build_native.sh` merely compiles/links committed generated ML with a full Poly/ML runtime (upstream pins 5.9.2-2 in CI). Its native binary is `isabelle/build/oo-horn-isabelle` and supports the same `check RULES ASSERTED CERT` shape. Running that binary does not freshly rebuild the Isabelle proof sources.
- **Rocq:** preserve `_CoqProject`, all `.v` sources, OCaml driver, `build.sh`, `gen_fixture_data.sh`, and shared Horn fixtures at `../tests/fixtures/horn`. The generator creates untracked `theories/FixtureData.v` from those bytes. Rocq 9.2 plus OCaml builds `rocq/build/oo-horn-rocq`. The source build includes axiom audit and a hostile mutation option `--prove-the-gate-can-fail`.
- Both concern the Horn layer, **not** the FOL finite-model/DL/SHACL checkers. Do not claim a three-kernel check of generic Lab finite models.
- Compare outputs over the same immutable certificate input and preserve divergence as a finding. Do not apply majority vote or change one formalization to imitate another.

Aeneas and Dafny need not be on the first reuse path. They have distinct purposes/toolchains: actual shared Rust boundary extraction versus a rewritten specification. Copying the proven checker source is already the minimum-new-proof route.

## What stays new, and small

The required Lab-specific work is an adapter, a capability/format guard, an exact input-output mapping manifest, a runner policy, result-strength accounting, and bridge-specific hostile tests. Reuse upstream checkers, parsers, fixtures, producer formats and algorithms. Keep original Lab interpretation/fidelity gates, finite provider/checker, dependency invalidation, revision requirements and owner decisions.

Runner design should pin and externally hash the executable, use immutable isolated input copies, record exact argv/input hashes/stdout/stderr/exit, bound wall time and output, and bind the result to source snapshot, meaning/review cuts, selected assumptions, formula IDs and translation version. Treat unavailable checker, rejected certificate, malformed input, timeout and unsupported profile as different outcomes. A fake checker or altered file must not mint a strong Lab label.

The copied proofs establish statements about supported formal objects; no copying strategy makes the source translation, RDF scope, input parser, checker binary provenance, model claims, or owner permission automatically proved.

## Primary source anchors

- `lean/lakefile.toml:1-14`; `lean/lean-toolchain`; `lean/lake-manifest.json` — complete workspace/default targets, version and zero dependency packages.
- `lean/Fol/Syntax.lean:45-141`; `lean/Fol/Check.lean:147-195`; `lean/FolMain.lean:1-43,161-169` — ABI, signature limits, theorem, parse/translation scope.
- `lean/HMain.lean:63-106`; `lean/OOCert/HornParse.lean:5-16` — exact supplied-vs-built-in theorem discipline and formats.
- `lean/FoMain.lean:4-37`; `lean/ShaclMain.lean:4-40` — refutation and shape-checker distinct limitations/exit meanings.
- `isabelle/build_native.sh:3-25`; `rocq/gen_fixture_data.sh:22-49`; `rocq/README.md:95-133` — independent workspace copy and rebuild boundaries.

## Addendum: per-request kernel replay with no rewritten proof engine

The compiled `oo-folmodel` binary is a useful preflight and portable checker, but its acceptance is not a fresh Lean kernel proof of each Lab obligation. It runs the proved Boolean evaluator through compiled code, the Lean compiler/runtime and host process. A result claiming a freshly checked theorem should have a separate per-request proof-artifact path.

The parent's proposed path is feasible from source inspection and has an exact upstream precedent at `lean/Fol/Witness.lean:65-81`: define a concrete `FinModel 2`, prove `check employmentModel employment = true` with **`by decide`**, then apply the unchanged `satisfiable_of_check`. Nothing in that pattern requires writing a new model checker or another proof of its soundness. This feasibility has not been compiled in this review.

Recommended fresh-artifact shape:

1. Keep the vendor workspace unchanged and build all its pinned default targets. The new candidate provider emits a separate scratch module in a digest-qualified Lab namespace.
2. The module contains literal/reified concrete formula list `Γ`, goal where applicable, exact finite model `M`, and exact declared unary/binary/constant signature lists.
3. Prove `Fol.covers d1 d2 dc Γ = true` and closedness for the selected formula list with `by decide`. Prove `Fol.check M Γ = true` with `by decide`.
4. Apply the unchanged `Fol.satisfiable_of_check` to obtain `Fol.Satisfiable Γ`. For a countermodel, prove `Fol.check M (.neg φ :: Γ) = true` and apply unchanged `Fol.not_entails_of_check` to obtain `¬ Fol.Entails Γ φ`.
5. Inspect the actual theorem declaration, referenced definitions and axiom footprint against the independently selected source/goal/model mapping. Seal exact source, generated file, compiled proof artifact, toolchain/build/import hashes, statement, required denominator and inspection output into a new reviewed provider result. A theorem whose type is merely `True`, a renamed/easier goal, a truncated premise set, or a different model must fail selection even if Lean accepts it.

### Specific implementation pitfalls to account for

- **Positive cardinality and inference.** `FinModel` itself accepts a natural index, but `toStruc`, `check` and the soundness theorem require `FinModel (n+1)`. Use explicit small positive numeral `N` and, where helpful, `n := N-1` in theorem application; never accept zero or rely on an unchecked `N-1` coercion to establish positivity. The existing Lab profile caps each selected carrier at three, which makes first experiments tractable.
- **Total-function defaults and attribution.** `FinModel.p1`, `.p2`, and `.const` are total functions. Finite `if`/match tables with `false` and `0` defaults make executable definitions easy, but a dropped row still defines a mathematical model. `covers` checks that symbol names are listed, not that the declaration list faithfully describes every model row. Independently compare emitted table contents, carrier indexing, constants and symbol mapping with the exact supplied Lab model; do not use a true covers theorem as a substitute for those checks.
- **Variable binding.** Upstream binders use `Nat` names and assignments, not source string identifiers. Alpha-renaming must be injective and capture-avoiding, especially with nested shadowing. Require closed formulas at this first profile; the upstream general satisfiability statement existentially binds an assignment, which would otherwise let a free source variable acquire an accidental interpretation.
- **Connective lowering.** Upstream has binary `and/or/imp`, not arbitrary source n-ary constructs or `iff`. Preserve empty conjunction/disjunction as true/false and expand iff explicitly. Do not “normalize” away required populations or claim queries. Preserve logical roles and exact premise/query denominator.
- **Proof evaluation budget.** `by decide` produces a term checked by Lean's kernel; **do not replace it with `native_decide`, an axiom, `sorry`, a host-run assertion, or only the CLI's exit code** to obtain speed. Finite does not mean cheap: quantifier nesting can still explode, so timeout is an incomplete execution outcome.
- **Actual axiom footprint.** `lean/Fol/Check.lean:200-226` pins `eval_iff`, `check_iff`, `satisfiable_of_check`, `check_complete`, and `not_entails_of_check` to **`[propext, Quot.sound]`**, without `Classical.choice`. A fresh final theorem that uses these results should have its observed footprint checked, not inherit a generic three-axiom allowance just because other upstream families use one. Generated finite check/coverage proofs may have a smaller footprint; record each actual result.
- **Imported artifact trust.** A fresh leaf module uses imported upstream declarations. Bind imported compiled artifact hashes to the pinned source build and selected Lean toolchain; do not accept arbitrary pre-existing `.olean` files or unrelated caches. If the Lab claims an independent exported proof/kernel replay, the new provider must use the existing reviewed export/replay path rather than only compile a leaf and equate that with all imported declarations being independently rechecked.
- **Source bridge remains separate.** Freshly proving `Satisfiable Γ` establishes the theorem about `Γ`. To call it a kernel-checked theorem about the original Lab typed IR requires an adequate semantic bridge between that IR and `Γ`, with an exact inspected statement and source selection. Kernel verification does not approve the natural-language definition's whole translation or source faithfulness.

This extension still reuses all upstream mathematics unchanged. New proof text is a small generated application of imported theorems to concrete data. A general many-sorted/functionful adequacy theorem is separately scoped new mathematics; the first profile should avoid needing it by declaring/refusing unsupported syntax and naming the remaining bridge obligation precisely.
