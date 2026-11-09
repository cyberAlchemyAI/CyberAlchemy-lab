# Review of assurance reuse proof design

Read-only review of `PROOF-PROFILES.md`, `ARCHITECTURE.md`, and `DELIVERY-LAYERS.md`, with `PROFILES.json` and `VALIDATION.md` consulted to resolve intended acceptance gates. No tests, installs, builds, or canonical document edits were performed.

## Disposition

**Pass with one wording clarification and explicit unimplemented gates.** The source-copy/native-check/fresh-kernel distinction is accurate. The initial supported signature matches upstream Fol after the declared connective lowering. Matching Lean 4.33.1 pins remove an obvious compatibility mismatch, but no successful import/build or bridge proof is established. Delivery layers correctly remain design seeds.

## Actionable wording issue

**P2 — distinguish carrier-map collisions from legitimate constant aliases.**

`PROOF-PROFILES.md:39-41` says to reject “aliased ... values” while mapping constants and tables. This should explicitly mean a noninjective or ambiguous carrier/symbol mapping, not two distinct constant symbols denoting the same carrier element. Both the Lab finite model and upstream Fol permit such constant aliases; rejecting them would silently impose a unique-name assumption absent from the selected source logic.

Suggested clarification: “Require an injective carrier renaming and exact complete table/constant interpretations. Reject duplicated or omitted table slots, mapping collisions and out-of-range indices; distinct constants may denote the same carrier element unless the selected theory requires their inequality.”

Evidence: upstream `lean/Fol/Check.lean:51-65` and `Fol/Semantics.lean:39-50` define a total constant interpretation without injectivity. Lab `craft/formalization/candidates/definition-assurance-v1/semantics.py:50-54` checks only that each constant's value belongs to its sort's domain.

## Required gates remain unimplemented

1. **Profile and semantic bridge.** The first restricted profile must validate the entire signature and all T/I/Q formulas, not just the emitted fragment. The source denotation and bridge are new work. Passing compiled `oo-folmodel` alone remains a check of exported data; the design correctly forbids calling that a kernel-checked Lab IR theorem before bridge proof and actual linkage are established.
2. **One exact witness for the right proposition.** Keep consistency, joint population and query obligations separate. All required I must hold in the same M that satisfies T. For a positive model-local Q, the generated leaf must also prove Q for that very M (e.g. a decidable `eval M ... Q = true` plus `eval_iff`, or an equivalent exact combined-model statement). The shown `model_exists` template alone only establishes model existence for its displayed theory. A model-existence theorem does not meet alias, disjointness, preservation, conservativity, or other universal obligations.
3. **Concrete kernel artifact.** Emit literal Γ/M/goal data, `by decide` checks, copied soundness applications, and inspect the actual declaration type/body/dependencies against an independently assembled challenge. Bind the source/required-set/model denominator and include negated Q correctly for countermodels. The upstream pattern is feasible by source precedent at `lean/Fol/Witness.lean:65-81`, not a build result from this review.
4. **Exact imported and generated proof closure.** Rebuild pinned source targets and bind the `.olean` closure. Actual Fol.Check theorem footprint `[propext, Quot.sound]` matches upstream `Check.lean:200-226`. New bridge/leaf footprints must be measured separately; a generic allowance for additional axioms, `native_decide`, `sorry`, user-selected imports or stale caches cannot inherit this profile's label. Compiling a fresh leaf is not by itself an independent replay of every imported proof artifact.
5. **Representation fidelity.** Verify the carrier bijection, complete predicate tables, all constant interpretations, fresh/capture-avoiding binders, exact labels/roles, and the independent round trip. `covers` only checks listed names, not source-table identity. External SHA-256 bindings are necessary because upstream FNV problem identifiers are not cryptographic commitments. Typecheck equality and constant aliases against source semantics.
6. **No strength inflation on failures or absence.** Timeouts, unsupported syntax, missing checker and bounded exhaustion remain incomplete/refused. A checked countermodel supplies non-entailment for its exact encoded formula; a failed search supplies no general absence theorem. Source-owner fidelity remains a separate gate even after the mathematics is checked.
7. **Context/change profiles stay narrower than definition theorems.** CTX-HORN1's subset/fixpoint/profile checks are about selected ground goals. RDF-CHANGE-RL1's empty consequence difference is only rule-relative. Neither can discharge existing Lab universal extension/closure theorems without a separately matched proposition and bridge. The documents make this limit explicit.

No other material proof-scope, same-model population, universal-claim, Fol-footprint, or compatibility error found. The plan maximizes unchanged source reuse while correctly leaving the Lab-specific encoding, semantic bridge, per-request proof assembly and provider-policy registration as future implementation work.
