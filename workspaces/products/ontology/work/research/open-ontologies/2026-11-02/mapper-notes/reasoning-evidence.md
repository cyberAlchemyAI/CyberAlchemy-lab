# Reasoning, formal evidence, and testing map

Repository: `/tmp/cal-open-ontologies.ANeAQC/repo`, commit `c7fd75f9491253c56e4d4f408ceac179de343e48` (2026-11-02). This is a static source review. No repository scripts, installs, builds, solver processes, or tests were run. Only Cargo was present on PATH; Lean/Lake, Rocq, Isabelle, Dafny, and Kani were not found.

## What the project actually contributes

Open Ontologies goes well beyond keeping a map and recording its changes: it asks what follows from that map, what a proposed change implies, which evidence a smaller view loses, and which answers can be checked by a smaller independent program. The most reusable contribution is its separation of an engine finding an answer from a checker accepting a particular evidence object.

Do not describe it as a generally verified Rust ontology engine. Most engine code is unverified; the repository says so explicitly in `docs/trusted-computing-base.md:1-15`. A verified checker proves a conditional about its parsed inputs. Whether those inputs accurately represent the selected source graph is a separate responsibility.

## Reasoning subsystem map

| Part | Concrete implementation | Actual scope and boundary |
| --- | --- | --- |
| RDF/SPARQL substrate | Oxigraph dependency; `src/graph.rs`; SHACL directly uses Oxigraph's parser/evaluator in `src/shacl.rs:1-8`. | Store/parser/query implementation is an external dependency, not the Lean theorem. Parent runtime mapper covers graph/state details. |
| Forward rule engine | `src/reason.rs`, especially `BuiltinRule` at 1069, typed row index `Rl` at 1087, `Reasoner` at 1390, `run_full` at 1435, `run_scoped` at 1522, `run_horn` at 3340. | RDFS / selected OWL RL / extended rules produce derivations. Fixed-arity rule rows share a data table; four list-dependent rules have variable premise arity. Rule profiles are fragments, not complete OWL semantics. |
| Supplied-rule front ends | `src/rulesyntax.rs:277` (`swrl_from_graph`), 641 (`rif_core_from_xml`), 1179 (`run_import`); `tests/rule_syntax_frontend_test.rs`. | Current SWRL and RIF Core front ends are implemented. Unsupported built-ins and external calls are refused/reported. A supplied rule's validity is an assumption, so its checked verdict differs from a built-in semantic entailment. |
| Incremental rule reasoning | `src/reason_incremental.rs:1-23`. | Semi-naive additions through subclass/subproperty/domain/range/transitivity/symmetry/inverse/sameAs/equivalence. Schema-level changes require a full pass; do not imply arbitrary deletion-maintenance. |
| OWL EL completion | `src/classify_el.rs:1-23`. | Normalizes to EL forms and computes completion; reports `complete: false` and lists omissions when axioms/parser features are unsupported. Its output is not machine-proved merely because a cited algorithm is sound. |
| SHIQ tableaux | `src/tableaux.rs:1-40`; `Verdict` at 2018; `DlReasoner` at 3222. | Native Rust SHIQ fragment. Nominals are not implemented; `oneOf` not parsed, `hasValue` approximated by atomic concept, datatype ranges skipped. Budgets yield `Unknown`, separate from satisfiable/unsatisfiable. Core fast solver is not formally verified. |
| DL model certificates | `src/tableaux.rs` model writer; `lean/Dl/Check.lean:205` (`satisfiable_of_checkModel`). | Finite interpretation checked against the exported DL axioms; no claim that arbitrary search failures or all unsupported OWL features are covered. |
| DL refutation producer | `src/dl_refute.rs:1-28`; `lean/Dl/Tableau.lean`, `lean/Dl/Refute.lean`. | Separate smaller search over the certified calculus; intentionally weaker/slower than fast tableaux. A successful check certifies supported refutations; failure to produce one leaves the fast result as engine evidence. |
| Rust SHACL | `src/shacl.rs:11-47`, report `Option<bool>` at 60-65; report RDF serialization `src/shacl_report.rs`. | Constraint-to-SPARQL validation with partial coverage. Skipped or unmatched load-bearing constraints suppress a clean conformance claim; undetermined is not true. Source comments themselves have historical text, so read implementation/tests together. |
| Verified SHACL path | `src/shacl_verified.rs:1-38`, checker discovery 57-80; `lean/Shacl/Report.lean:159`. | Optional runtime path invokes `oo-shacl`; Lean Core evaluator refuses SPARQL/user-defined extensions. Neither Rust nor Lean SHACL is a superset. No checker executable is included by building just the Rust binary. |
| Rule-coverage disclosure | `src/dlp.rs:22-44`, 46-100. | Separates axioms outside Horn/OWL-RL language from axioms inside that language but not implemented by this rule table. Certificate soundness is not rule completeness. |
| First-order export | `src/tptp.rs:1-34`, 75-107; emits TPTP FOF, CLIF, SMT-LIB and LADR. | Related OWL-to-FOL theorem lives in separate `owl-lean` project; Rust correspondence is tested, not proved. Unsupported export constructs are counted. Quoting/freshness/individual-typing guards matter semantically. |
| Solver finite-model path | `src/fol_solve.rs:1-32`; `src/fol_model.rs:1-28`; `lean/Fol/Check.lean:158`. | Export one formula representation to solver and checker forms, parse Z3/Mace4 model, and independently evaluate it. External solver verdict alone cannot mint `model_checked`. |
| Prover derivations | `src/tstp.rs:1-28`; `CertificateOutcome` at 1542; `to_fo_certificate` at 2429. | TSTP leaves checked against emitted problem, DAG checked, some inference steps replayed. Current code can certify the clausal resolution/factoring subset with `oo-resolution`; superposition and unsupported steps remain named/untranslated. Do not repeat outdated blanket assertion that all external refutations are uncheckable. |
| SAT/LRAT | `src/sat.rs:1-29`; `lean/Lrat/Check.lean:203`. | External SAT search plus independently checked LRAT refutation. Solver 'sat' in this module remains an unchecked report. |
| Claim checks | `src/claimcheck.rs:75-103`, compiled ontology 310, `check` 407, batch 531, residual oracle 574 onward. | Compiled checking and residual-oracle paths distinguish decision reach; parent integration mapper may cover user-facing application. |
| Explanations and repairs | `src/justify.rs:73-137`, 398; `src/repair.rs`; `src/defects.rs`, `src/vocab_check.rs`. | Bounded explanation/repair search and structural hygiene checks. Oracle-supported justifications are not automatically certificates. |
| Ontology modules | `src/module_extract.rs:1044-1057`, extract 1095, verify 1318. | Syntactic locality module extraction cites a paper; its locality theorem is not mechanized here. It can separately measure/check consequences under the actual rule table. |
| Projection checks | `src/projection_check.rs`, `src/projection_entailment.rs:1-35`, 1387; `src/closure_diff.rs:1-29`. | Checks whether a selected slice preserves specified ground positive goals under one pinned rule table. Four outcomes: preserved; lost by projection; source lacked support; impossible monotonicity/subset failure. Offline closure-difference audit supplements online goal checks. |
| Semantic change impact | `src/conservativity.rs:1-29`. | Uses shared closure/certificate logic to find new consequences over old vocabulary. This is conservativity relative to a Horn rule table, not full deductive/model conservativity for all OWL. |
| Action/plan semantics | `src/dynamics.rs`, `src/dynamics_bcplus.rs:1-29`, `src/plan_validate.rs:105`, `src/plan_classical.rs`, `src/plan_pddl.rs`, `src/shape_combinatorics.rs`. | Action effects, concurrent-action conflicts, static SPARQL invariants, defaults, and PDDL/plan integration. BC+ here has no full ASP stable-model backend; concurrent nondeterministic outcome enumeration is deferred. |
| Numeric evidence | `src/matcert.rs:53-127`; `lean/MatCert/Basic.lean:86`. | Checked integer matrix multiplication is separate from probabilistic Freivalds checks and floating point. Do not infer a verified general ML/numeric pipeline. |

## The evidence pipeline

1. A selected graph/rule scope is read.
2. Rust performs search/reasoning and writes asserted data, rule table, derivation/model/refutation files, plus scope metadata where applicable.
3. A separate checker reads those bytes and accepts/rejects/declines.
4. Rust prints a scoped verdict with checker result and evidence binding.

`Reasoner::run_full` documents the certificate files in `src/reason.rs:1410-1433`. The checker does not inspect the live RDF store. `scope.tsv` is human/script-checkable provenance; no Lean checker reads it (`docs/trusted-computing-base.md`, section TCB-6a). A correct proof about a mistaken union of graph versions can still be the wrong answer for the intended state.

`InferenceTarget` at `src/reason.rs:1381-1387` retains a historical default that merges inferences with assertions, alongside a separate inferred graph. Merged output makes next-run original/derived separation unrecoverable; named-graph scoped paths are the better integration choice. Read the duplicated historical TCB-8 narrative in that document carefully rather than treating every paragraph as current status.

### Evidence cannot be an arbitrary verdict string

`src/verdict.rs:1-28` defines private evidence constructors. `CheckerRun::spawn` hashes named input files (139-153, 168-197), runs a process, and only an actual successful result can produce `Certified`. Verdict types do not implement `Deserialize` (66-70). This prevents casually reading a JSON label as if a checker had run.

Still-open trust boundaries are explicitly stated at 34-65:

- Operator-selected checker path can be a hostile binary/script. Exit zero and self-reported fingerprint do not authenticate the executable.
- Input digests bind caller-selected files, not the intended dataset by magic; a caller can select the wrong files. Hash-before-spawn also is not an OS-level immutable-file guarantee.
- A theorem about bytes does not establish their correspondence to source events, selected graph versions, or the user's intended scope.

These are useful design boundaries for CyberAlchemy's evidence/admission separation.

## Formal workspace map

| Workspace | What is present | Boundary |
| --- | --- | --- |
| `lean/` | 84 files at this checkout. Core Lean libraries OOCert, Shacl, Dl, Fol, Institution, Lrat, Fo, MatCert, SelfId. `lean/lakefile.toml:1-8` lists all libraries/executables as default targets. | No Mathlib dependencies for this workspace. Checkers are built separately from the Rust binary. SelfId SHA-256 implementation is test-vector checked, not verified. |
| `isabelle/` | Independent Horn formalization, semantic model, parser, soundness, built-in table, end-to-end pipeline, Standard ML export. `isabelle/OO_Sound.thy:151`; `OO_Pipeline.thy:28,44`. | Ordinary CI runs committed generated ML with Poly/ML; it does not rebuild Isabelle theories or regenerate ML. Driver/extraction are additional trust boundaries. |
| `rocq/` | 18 files. Third Horn formalization and parser-to-verdict proof; `rocq/theories/Run.v:91`, built-in theorem `Builtin.v:508`. | Horn subset only, not the other Lean libraries. Extraction/driver trusted; README records semantic interpretation differences and known shared information. |
| `aeneas/` | 16 files. Separate generated Lean model of actual shared `src/boundary_core.rs`, proofs, and axiom audit. `aeneas/oo-boundary/src/lib.rs` reaches same source by path. | Optional workflow; Mathlib/Aeneas packages in a different Lean workspace. Not a verification of the whole Rust program. `aeneas/run.sh:3-24`, `docs/aeneas-boundary.md:85-109`. |
| `dafny/` | Rule-table grammar and interner specifications plus hostile-mutation runner. | Reimplementation, not actual Rust verification. Optional, outside normal make check/Cargo/Lean paths (`dafny/run.sh:3-25`). |
| Kani harnesses | Bounded symbolic checks of pure serialization/term/parser boundary functions; named targets in Makefile verify. | Finite bounds and narrow boundary functions; optional and not the normal CI theorem for the whole codebase. |

Selected proof entry points verified by source lookup: `lean/OOCert/Soundness.lean:459`, `lean/OOCert/Horn.lean:507,521`, `lean/OOCert/HornBuiltin.lean:438`, `lean/Shacl/Report.lean:159`, `lean/Dl/Check.lean:205`, `lean/Fol/Check.lean:158`, `lean/Lrat/Check.lean:203`, `lean/Fo/Check.lean:219`, `lean/MatCert/Basic.lean:86`. These source declarations were inspected, not rebuilt in this review.

## Testing and CI map

There are 244 top-level `tests/*.rs` integration-test files; 671 total files under tests including fixtures. No fresh count of passing tests is claimed.

- `.github/workflows/ci.yml:83-124`: ordinary build/test/clippy plus explicit skipped-fixture count. A passing non-strict Cargo run can contain skipped specialized checks.
- CI feature jobs `197-300` compile/check/clippy/test gated optional features and check collection. This matters because compiling a feature is not proof its tests ran.
- CI SHACL differential at `329-363` uses pinned pyshacl/rdflib. Python strict-fixture test legs at `475-478` and Lean job at `535` onward.
- CI `885-892`: strict certificate-boundary property tests, RL rule coverage, SWRL/RIF frontends, and rule table round-trip.
- CI `950-956`: Lean/Isabelle differential using a pinned Poly/ML runtime over committed ML export. Not rebuilding Isabelle proof sources.
- CI `982-1018`: pinned Rocq container builds source, checks axiom footprint, deliberately breaks a proof to show the gate rejects it, and runs differential tests.
- CI `1023-1024`: `ci_gate_coverage_test.rs` checks every potentially skippable Rust integration file is strict somewhere or explicitly excepted, and its documentation matches. Its source states the invariant at `tests/ci_gate_coverage_test.rs:20-32` and exceptions at `60-94`.
- W3C SHACL is a ratchet, not a pass-all gate. Committed `tests/w3c_shacl_baseline.json:1-12` records **62/120 pass, 15 fail, 43 undetermined** for the core comparison. The full tuple comparison records **54/120 pass, 23 fail, 43 undetermined**. These are committed baselines, not measurements rerun here. Some comments in CI still carry earlier 61/53 counts.
- `.github/workflows/benchmark.yml` is manual `workflow_dispatch`, not ordinary PR regression. Benchmarks use external corpora/provers/Java/Python/model data depending on profile.
- **Do not trust successful `make bench` as benchmark success:** Makefile bench targets often suppress stderr and use `|| echo Requires ...`, allowing failure to become a successful message.

## Documentation drift found

`docs/reasoning-systems-inventory.md` remains useful historical rationale but is not current capability truth: it labels RIF/SWRL under construction while current source and strict CI implement them; labels Aeneas declined while extracted shared-boundary proofs are now present; describes all external refutations as testimony while the current resolution/factoring path can produce checked certificates. Source and current tests take precedence.

## Best candidates for CyberAlchemy

1. **Projection adequacy as a task contract.** Given exact ontology/event cut, agent purpose and load-bearing claims, check which claims survive in its bounded context. Port the four-result vocabulary, not a vague percentage of graph coverage. Preserve the distinction between a missing premise and a claim unsupported by the source in the first place.
2. **Semantic change preview.** Beyond node/edge add/remove counts, compare consequences over an agreed vocabulary before admitting a change. Pin ontology cut, rule profile and results. An empty diff under a partial table is not universal conservativity.
3. **Evidence-producing search and smaller checkers.** Allow an untrusted generator/solver to propose a result, but require evidence checked against exact source bytes before printing the strong verdict. This complements existing EVF/TDE claim ceilings rather than conferring admission.
4. **Evidence-carrying result types.** Private constructors and no deserialization for earned verification states help make false status transitions hard to express. Adapt the pattern with stronger checker identity/input immutability than this implementation currently enforces.
5. **Coverage reports that separate unsupported language from implementation gaps.** A Lab relation/constraint can be in-spec but unimplemented, or outside a selected profile. Those require different remediation and should not collapse to a green gate or one generic unsupported bucket.
6. **Non-vacuous CI.** Require missing fixtures to fail a dedicated strict job, check skip coverage, and run hostile mutations to prove a gate can reject. Track source-specific proof/kernel boundaries rather than saying 'formally verified'.
7. **Module extraction for agent context.** Locality extraction and claim-preservation checks are useful experiments for small agent views. Retain exact cut and original artifact identity; do not replace Lab's canonical event history with an RDF cache.

A minimal integration experiment should export one frozen Lab ontology cut to a disposable RDF dataset, translate just a few selected relation kinds and qualifiers, run a pinned read-only preservation/impact check, and retain the mapping and evidence. No runtime migration or canonical-store replacement is implied. Semantics need deliberate mapping: OWL/RDF has open-world interpretation, and domain/range generally infer types rather than enforce Lab's exact allowed pair/qualifier rules. SHACL may serve structural constraints, but its partial coverage must be explicit.
