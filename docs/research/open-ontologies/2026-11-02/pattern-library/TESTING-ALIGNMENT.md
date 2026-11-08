# Tests and evidence coverage

There are 244 top-level Rust integration-test files, 671 tracked paths under
tests including fixtures, and additional unit, Python, UI, demo and formal
tests. These are file counts, not counts of tests that passed in this review.

## Checks matched to responsibilities

| Responsibility | Evidence or test family | Interpretation |
| --- | --- | --- |
| Writer progress during a fixed read | [writer-progress test](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/tests/read_does_not_block_writers_test.rs#L1) | A better test than progress between separate reads. Not a general distributed concurrency proof. |
| Plan selection | Plan ownership/persistence/delta/logic integration files | Ownership of default latest-plan selection is not an ACL; no-base-version apply remains. |
| Rule reasoning and certificates | Certificate, Horn, rule-syntax, binding and hostile-input tests | Scope depends on exact rule table, parser and checker availability. |
| Shape validation | W3C core/result suites and committed baseline | Ratcheted partial coverage, not pass-all standards conformance. |
| Different implementations | Rust/Python/Lean and Horn cross-kernel differential tests | Agreement is evidence; each pipeline has its own translation/trust boundary. |
| Intake, models and UI | Rust intake/plugin/vector tests, Python tests, Vitest and demo tests | Optional providers/assets can be absent and specialized tests can skip. |

## Current formal checker families

| Family | What it checks | Inspected source |
| --- | --- | --- |
| OOCert | Built-in and supplied Horn derivations | [lean/OOCert/Soundness.lean](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/lean/OOCert/Soundness.lean#L459) |
| SHACL | Supported Core evaluator and result report | [lean/Shacl/Report.lean](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/lean/Shacl/Report.lean#L11) |
| DL | Finite interpretations; separate restricted closed-tableau refutations | [lean/Dl/Check.lean](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/lean/Dl/Check.lean#L7) |
| FOL | Finite first-order interpretations | [lean/Fol/Check.lean](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/lean/Fol/Check.lean#L4) |
| LRAT | Propositional refutations | [lean/Lrat/Check.lean](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/lean/Lrat/Check.lean#L4) |
| Resolution | First-order resolution/factoring subset | [lean/Fo/Check.lean](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/lean/Fo/Check.lean#L42) |
| MatCert | Integer matrix products | [lean/MatCert/Basic.lean](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/lean/MatCert/Basic.lean#L11) |

These declarations were inspected, not rebuilt. Proofs concern specified
inputs/encodings and supported fragments. They do not establish that arbitrary
RDF is faithful to the Lab, that imported statements are true, or that all
Rust search results have certificates.

Isabelle and Rocq provide separate Horn formalizations. Normal CI runs committed
Isabelle-generated ML with Poly/ML; it does not rebuild the Isabelle theories.
Rocq has a dedicated source-build and mutation gate. Aeneas extracts narrow
shared Rust boundary code into a separate proof workspace. Dafny specifications
are rewrites; Kani harnesses check bounded boundary functions. These are
different claims, not six interchangeable proofs of the whole engine.

## Known limits

The committed core SHACL baseline is **62/120 pass, 15 fail, 43 undetermined**.
Full result comparison is **54/120 pass, 23 fail, 43 undetermined**. Rust and
Lean SHACL paths have different supported subsets; neither should be described
as a superset of the other. Source: [recorded SHACL baseline](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/tests/w3c_shacl_baseline.json#L1).

The native description-logic solver approximates or omits some OWL constructs
and can return unknown at a budget. Incremental reasoning covers selected
additions, not arbitrary deletion maintenance. First-order exports count
unsupported constructs. Consequence preservation/change reports are relative
to a selected rule table. Full OWL correctness does not follow from any one
checked fragment.

## CI that refuses empty success

Specialized CI jobs set `OO_REQUIRE_FIXTURES=1` to turn missing required fixtures
into failures. The [CI skip-coverage checks](https://github.com/fabio-rovai/open-ontologies/blob/c7fd75f9491253c56e4d4f408ceac179de343e48/tests/ci_gate_coverage_test.rs#L1) reconciles potentially skippable files with strict
jobs or explicit exceptions. Python has its own skip guard. Some differential
tools also fail when no cases were compared.

Benchmark workflow is manually dispatched. Some Makefile benchmark targets
turn failures into explanatory successful echoes; a successful `make bench`
alone is not evidence of benchmark completion.

For this review, only the three stdlib browser-install tests and Cargo metadata
command were run. See [verification](../VALIDATION.md).
