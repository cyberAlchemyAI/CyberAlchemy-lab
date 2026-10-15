Selected digest profile and original relation — reviewed candidate

This component closes the free-profile and separate-frame gaps at the composite
entrypoint. Previously, callers could prepare profile evidence and separately call
the original relation pipeline using a different digest profile. This entrypoint
derives the relation digest profile from the checked evidence output. The evidence
stage is checked against exactly the supplied original World frame. No additional
profile frame or relation digest profile argument exists.

The current complete batch is authority + every declaration/selection occurrence +
source + qualifiers + the three complete context snapshots. For one declaration and
one selection this is eight captures. The shared count, total actual original byte
length and per-capture limits are tested before any captured-input hash or parser.
Successful batches necessarily meet both existing stage budgets. Duplicate input
occurrences remain separate budget charges.

The key theorem, run_exact, states that success is equivalent to the conjunction of
an independent combined BudgetMeaning, the original bounded profile evidence Meaning,
and the original captured-context relation Meaning under the EXACT profile returned
by that evidence. The original source structures, catalog coherence, qualifier
ownership, source digest join and original relation conclusions are preserved. The
Meaning does not replace the original SourceInterpretation with a narrower claim.

The order is precise: after the combined budget, profile captures are preflighted
under bootstrap before profile decoding. That decoding is necessary to select a
profile. Then all five relation captures are preflighted under that selected profile
before any relation/catalog typed decoding. This is not a claim that every capture
is preflighted before profile decoding, or that the guard bounds total time/memory.

The independent profile and relation meanings share world.frame. Successful relation
captures must all carry the selected profile's complete reference. The returned
profile declaration reference is digest-bound to its exact declaration bytes; a
bootstrap reference cannot be substituted for it, even if it specifies the same
hash algorithm. The checker-policy reference inside world.frame is a different
semantic role and is not replaced by the digest-profile reference.

There is still a material boundary: structural evidence success does not prove the
authority snapshot came from its real owner. actual_root_boundary_still_required
constructs owned selection only GIVEN policy.authoritativeSnapshot root world.frame
inputs.authority. The inherited ownership_requires_actual_snapshot_boundary theorem
also requires this premise. Synthetic fixture grants, reviews and trust roots provide
no actual root provider. No Boolean flag or unconditional True policy is introduced.

The worked fixtures now use one complete original relation frame, newly hashed
profile/selection bytes, exact issued source bytes, matching manifests, reviews and
grant scope. A missing-review authority has its own correctly recomputed hash, so
that control exercises an evidence join failure instead of a digest failure. The
fixture audit compares literal bytes and all concrete joins. It is not a proof of
a general serializer or authenticity. The relation fixtures remain unchanged apart
from their envelope digest-profile reference.

Verification checks ten general declarations in fresh compile/replay invocations,
with explicit axiom inspections and exact import resolution. Twenty-two runtime
cases per phase exercise success, frame/profile binding, full-budget refusals,
preflight positions, missing evidence and original relation/catalog refusals. The
129 unchanged dependency modules are reused only from their registered corresponding
phase outputs and exact source hashes; they are not claimed freshly rebuilt.
Same-kernel replay is not independent checking. Build times are not operational limits.

Remaining gaps: nested artifact bodies are not yet derived from and verified against
all original raw content/full references; World/claim are explicit typed inputs;
original 18 non-parser source policies remain genuine assumptions; future raw World
and provider adapters must extend the shared capture manifest; mandatory consumers
and the other relation/extension integrations remain unfinished. This completes only
the selected-profile composition component, not N01 or the plan. All 263 inherited
IDs remain open; the 90 original discharges retain their original scope. K00–K03
meanings are accepted, K04 and shared policies are pending. No live integration,
independent proof checking, measured resource envelope or final-use assessment is
claimed.
