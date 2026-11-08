# TDE and EVF integration

This is a derived human view of the candidate bridge contracts. It does not
replace the TDE or EVF architectures.

## Ownership

| Part | Owner | What it may say |
| --- | --- | --- |
| Business meaning and interpretation | domain project owner | what the rule means |
| FormalClaim and projections | formalization with domain ownership | the exact proposition and provider translations |
| Capability assessment | validation governance | which bounded route is admissible |
| Neutral obligation set | TDE | which provider-neutral cases and routing candidates follow from admitted input |
| Native execution | selected provider | what happened for exact inputs and environment |
| Provider selection and evidence join | EVF | which provider is selected and what exact current evidence supports |

## TDE boundary

TDE consumes one exact current FormalClaim, one capability assessment, and zero
or one preservation-backed executable projection. Its classification is one of:

- `executable-bounded`;
- `solver-admissible`;
- `proof-provider-required`;
- `unsupported`;
- `indeterminate`.

Only an admitted `executable-bounded` slice enters ordinary test derivation.
Lean remains on the EVF theorem-provider path. Solver, model-checker,
relational, and Datalog routes remain explicit provider paths. TDE does not
invent missing meaning or turn opaque implementation calls into formal facts.

The neutral obligation set contains stable obligation and case IDs, normalized
inputs, expected relations or oracle requirements, provenance, residue, and a
claim ceiling. It contains no TypeScript, Python, Rust, Lean, SMT, Alloy, TLC,
or Souffle branch.

## Provider boundary

An execution route has an exact provider-runtime binding: provider version and
digest, input artifact, command, environment allowlist, fixtures, timeout,
memory and output limits, network policy, and supported outcomes. Its
provider-evidence binding directly names that exact runtime binding and points
to provider-owned receipts; it does not replace them.

A Lean theorem route is separate. It carries a FormalClaimLeanBinding, an
EVF-owned theorem request, an exact provider runtime, and theorem evidence. It
does not require an ordinary TDE obligation set or pretend Lean is a generated
TypeScript, Python, or Rust test profile.

Raw evidence stays reachable. `unknown`, timeout, malformed output, provider
error, stale input, and unsupported behavior remain non-pass. One successful
provider cannot vote another unresolved provider into success.

## EVF join boundary

For an execution route, an EVF join binds these exact current identities:

- FormalClaim;
- neutral obligation set;
- projection and preservation binding;
- native-source bundle;
- formal profile;
- provider evidence and environment;
- result semantics.

For a theorem route, the join binds FormalClaim, capability assessment,
FormalClaimLeanBinding, theorem request, theorem evidence, runtime, profile,
environment, and theorem result semantics. Route-specific artifacts are
alternatives; missing artifacts for the selected route block the join.
`PASS_BOUNDED` additionally requires every bound ref to carry `current: true`;
a separate `all_current` assertion cannot override a stale ref.

The positive outcome is `PASS_BOUNDED`, never generic `PASS`. Every other
outcome stays typed: `NON_PASS`, `UNSUPPORTED`, `INDETERMINATE`, `STALE`,
`MISSING`, `FAILED`, or `BLOCKED`.

No join grants business acceptance, source authority, promotion, release,
deployment, or production correspondence.
