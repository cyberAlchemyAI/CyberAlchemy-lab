# Evidence contract and the boundary between accounting and acceptance

E01 defines a closed submitted evidence bundle. It binds exact source versions and bytes, a selected snapshot, interpretation records, dependency graph, theory, assumptions, couplings, the independently required set, logical result records and administrative/semantic gate records. Every bundle remains a candidate with readiness unassessed and authority effect `none`. The full episode still covers all 183 current definitions; this unit establishes the evidence accounting contract rather than source translations or their proofs.

## Requirements have their own denominator

The required set comes from A06 before submitted results are examined. It includes the logical statements, minimum strengths, assumption context, sources, dependencies, populations, direction, applicability prerequisites and semantic/administrative gates. E01 compares the submitted required set with that independently selected object exactly. It then requires one logical record and one gate record for every required identity.

A missing result has a record with a missing verdict, no attained strength, no native data and unassessed readiness. A missing interpretation also remains an explicit row for its exact source. Removing those rows would change the denominator and is rejected. Duplicating one identity with different metadata cannot substitute for another required identity. Statement, theory, context and gate-prerequisite substitutions are rejected independently of JSON structural conformance.

This comparison establishes that a submission accounts for the selected requirements. It does not authenticate the source of the selected requirements. The later verifier must regenerate them from independently selected source/theory/policy inputs, rather than trusting a producer's list or a claimed passing receipt.

## The evidence dimensions stay separate

| Dimension | Meaning in this contract | Independent check still needed |
| --- | --- | --- |
| Execution | Completed, not-run, timeout, cancelled or error | Actual provider/process evidence and exact input applicability |
| Source currentness | Reported current, stale or unknown | Live byte, registry-selection and dependency checks |
| Source fidelity | Pending, rejected, not assessed, or reported reviewed with an exact reference | Attributable review of meaning correspondence and losses |
| Logical verdict | Supported, counterexample, inconsistent, vacuous, malformed, missing, stale, unsupported or unknown | Actual model/solver/proof semantics for the exact required statement |
| Evidence strength | Structural, review, witness, finite exhaustion, solver result, theorem or none | Proposition-dependent minimum and provider trust conditions |
| Readiness | Always unassessed in a submitted candidate bundle | Separate independent verification report covering every requirement |
| Authority effect | None | Separate owner dispositions and any later exact admission |

A completed run can yield unknown. A byte-current result can lack source fidelity. A model witness can be too weak for a required theorem. A referenced review can remain an unverified report. The schema does not collapse these facts into a single pass flag.

Logical support, counterexamples, inconsistency and vacuity claims require actual native result data and explicit native input, profile, toolchain and evidence references. Reported gate support likewise requires actual result data and references. A result labeled reviewed must include its review reference. These are accountability conditions; satisfying them does not make the payload's claim true.

## Native data and byte bindings

The contract derives a closed set of artifact references from defined fields. It does not treat every path-like string inside untrusted provider data as a new file to ingest. Two references to one path must select identical bytes. With resolved input artifacts, every selected file is rehashed and each native result's parsed data is compared with the data stored in its bundle record. Required-set data is also bound to the actual selected required-set file.

The checking interface supports a read-only repository root or a captured byte map. Captured maps must contain exactly the derived artifact paths, so omitted and extra files are rejected. Symlinks/traversal are rejected by the existing descriptor-relative resolver. Without resolved bytes, the output explicitly says native bytes were not resolved. Even with byte binding, evidence verification remains false: hashing an inaccurate report does not prove it accurate.

The artifact set closes over the evidence contract's explicit inputs. Toolchain records can contain exact external runtime requirements; their binaries are not automatically ingested by searching arbitrary nested strings. Later runtime applicability checks must resolve those selected requirements independently. This unit does not claim a portable or hermetic runtime distribution.

## Finite-provider vocabulary bridge

P02 reports `bounded-exhaustion`; the frozen A01 result vocabulary uses `finite-exhaustion`. E01 maps those labels explicitly while preserving exact finite scope, completion and witness conditions. It does not promote either to mechanized-theorem evidence.

An exact witness result maps to supported model-witness evidence, and a countermodel maps to counterexample model-witness evidence. A complete bounded supported result maps to supported finite exhaustion. Bounded no-theory-model and no-witness outcomes retain an unknown general verdict with scoped absence in their native data. Bounded no-admissible-model maps to finite-scope vacuity. Timeout, cancellation, resource-limit, malformed, unsupported, provider error and unresolved bindings retain no attained evidence strength.

The bridge rejects claimed exhaustion without a complete flag, execution failures carrying witness/absence evidence, unknown finite status names, or substitutions of the reported execution/verdict/strength dimensions. This is protocol checking. The contract deliberately does not evaluate a native witness's model or check a theorem term; E03 must do that against the selected semantics and exact query. Some negative controls contain structurally bound but mathematically unjustified payloads precisely to verify that accounting does not self-grant semantic readiness.

## Validation and remaining work

All 24 tests pass. They cover full missing-evidence accounting, each omitted result/gate, duplicate identities, weakened or substituted requirements, statement/context/source/dependency bindings, native data versus actual file bytes, finite strength ceilings, stopped executions, reported review/gate references, stale inputs, closed captures, conflicting path hashes, self-declared authority/readiness and nonlocal schema references. The schema includes 21 local definitions and preserves the original A01 schema bytes.

The worked example is a synthetic two-definition source capture with five required logical results and six gates, all explicitly pending. It demonstrates complete accounting without accepted translations or proofs. Its captured inputs and report are retained for inspection. This is candidate agent review evidence, not an independent source-owner disposition.

E02 will publish the exact captured contract inputs create-only while preserving collisions and interrupted attempts. E03 will independently regenerate required sets, check model witnesses and distinguish actual provider trust from mechanized proof. The full episode still requires current-source interpretation/dependency coverage, joint theories and populations, required universal evidence, source-fidelity review and the final completion audit.
