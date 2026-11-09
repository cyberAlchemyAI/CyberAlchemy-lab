# Validation required before this design becomes an integration

This file specifies future checks. No successful implementation run is claimed.

## Copy and build

- Verify the upstream commit/tree, selected source hashes and original modes;
  compare every copied byte with the copy manifest.
- Retain MIT/in-file notices and record exceptions. Resolve optional generated
  checker-code licensing and dependency notices before those imports.
- Build copied Lean with 4.33.1. Record all selected targets and separately
  report targets not run. Build the whole default set before promoting a claim
  that the full copied proof workspace is healthy.
- Build Rust as its original Cargo root with original Cargo.lock and empty
  optional features. Verify the resolved Oxigraph fork revision; no silent
  lock rewrite or stable-version approximation.
- Pin binaries, compiler/runtime versions, imported `.olean` source/build
  closure and environment. A hash declared by an untrusted binary is not an
  independently anchored expected hash.

## Definition proof controls

| Control | Required outcome |
| --- | --- |
| Existing supported Provenance/Authority witness | Same scoped witness result as our evaluator; fresh concrete Lean proof for the selected exact model statement. |
| Explicit required population made empty | Reject that witness for the joint-population obligation, even if base theory is satisfiable. |
| P implies A added to the distinction example | Distinction obligation fails; report it separately from base consistency. |
| Countermodel omits or weakens a source clause | Reject exact source/required-set mismatch. |
| Missing, duplicate, permuted or out-of-range model table | Reject attribution/mapping error, not a new semantic conclusion. |
| Changed iff/quantifier/binder, Unicode identity or constant | Independent correspondence/proof challenge rejects it. |
| Additional sort/function/higher-arity symbol | Unsupported in the initial profile; no dropped fields. |
| Compiled checker succeeds but kernel proof is absent | Retain only the lower backend-check status. |
| Changed proof statement, same theorem name | Reject exact challenge mismatch. |
| Inserted axiom, native-decide escape or wrong compiled import | Reject closure/axiom/profile mismatch. |
| Model-existence proof submitted for universal obligation | Reject proposition/kind mismatch. |
| Proof exceeds deadline/output/memory policy | Incomplete/refused; no negative or stronger fallback claim. |

Recheck the general bridge and its actual implementation linkage. Formula
round trips and differential tests are finite evidence, not a universal
translation theorem. Source fidelity remains separately reviewed.

## Agent-view and change controls

- Remove an essential premise: distinguish lost support from unsupported in
  the original source. Add a triple outside the source: reject/disarm subset
  comparison with an explicit reason.
- Alter the rule table, source cut, review references, symbol map or qualifier
  binding: refuse stale/substituted evidence.
- Reach a non-fixpoint or scan limit: no clean preservation/conservativity.
- Plant a forged certificate, wrong premise index or wrong input file: the
  independently selected checker must refuse.
- Add an existing-vocabulary domain/range consequence: report the new
  conclusion even if no class is added or removed.
- Remove assertions in an extension question: report not-an-extension/undecided,
  not general conservativity.
- Run two jobs against old/new versions: retain separate results and demonstrate
  neither connects to a live daemon or changes the other's inputs.
- Simulate changed binary of the same size, missing checker, forged checker
  output, reordered batch envelopes, extra command and plan risk with exit 0:
  enforce exact build identity, command ledger and semantic result parsing.
- Check plan certificates are beneath the owned temporary root and are captured;
  reject unsupported plan profile/cap requests and verify G union delta equals
  the target actually analyzed.
- Permit two constant symbols to denote the same carrier member; independently
  reject accidental symbol or carrier-map collisions.

## Reuse upstream regressions without false coverage

Retain `tests/common/mod.rs`, model/Horn good and negative fixtures, and original
test code. Run only explicit targets after resolving their complete data/tool
closure. `OO_REQUIRE_FIXTURES=1` belongs in each profile that promises the tools;
missing required assets must fail rather than quietly skip.

The copied suite includes tests for other engine features and third-party
corpora that are not in the first fixture pack. Retaining their source does not
mean those tests were executed. Record discovered, selected, executed, failed,
skipped and deliberately unselected targets separately. Do not use Makefile
targets that swallow errors as the completion gate.

## Lab regression and readiness

Freeze accepted checker bytes and reference outputs before adapter work. The
new provider must not change existing finite-profile or E00–E06 results, reuse
their receipts for changed code, or weaken current-head/owner gates.

Promotion evidence includes exact source-copy/build receipts, profile closure,
bridge and concrete proof checks, hostile controls, source-fidelity posture,
performance/resource observations and human-readable examples. No technical
PASS alone accepts all definitions or authorizes an ontology change.
