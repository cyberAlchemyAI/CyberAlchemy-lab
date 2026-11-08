# Verification-profile authoring and lowering

Status: E01 candidate implementation. Authority effect: none.

## Boundary

A `verification-profile` declares one bounded question about one already
declared `FormalClaim`. It does not execute a provider, report an evaluation
result, admit a release, accept a context, or alter claim identity.

The source owns human-visible selectors and execution bounds. A separate
lowering binding supplies exact current artifact references for the selected
route, provider profile, runtime and optional InterpretationModel. Lowering
resolves every supplied reference against the caller-provided byte map before
forming output.

## Source form

```alchlang
verification-profile EligibleVerification:
  claim EligibleClaim
  context EvaluationContext:eligible-fixture version 1
  interpretation none
  route route:tde-execution
  provider provider:smt-qf
  runtime runtime:smt-fixture
  timeout-ms 5000
  memory-ceiling-bytes 268435456
  max-output-bytes 1048576
  network forbidden
  working-directory sandbox/verification
  environment-allow LANG
  assumption "Finite synthetic order scope."
  limit "Request formation only; no provider result."
  ceiling "Synthetic verification request only."
```

Every profile must explicitly name its claim, context identity and version,
interpretation selection, route, provider, runtime, resource bounds, network
policy, working directory, at least one limit and a nonempty ceiling. The only
current network policy is `forbidden`. Working directories must be bounded
relative paths. Environment names are allowlisted by name; values cannot be
embedded.

## Exact binding and output

The lowering input uses
`alchlang.verification-profile-bindings/v1`. It covers every authored profile
exactly once and binds each authored selector to an exact current reference:
path, SHA-256, byte size and `current: true`. Missing bytes, changed bytes,
selector mismatch, extra profiles, extra fields and a non-null binding for
`interpretation none` all reject.

Each profile emits:

- `verification-profiles/<profile>/evaluation-context.json`, conforming to the
  existing DomainSpec `EvaluationContext/v1-candidate` schema;
- `verification-profiles/<profile>/request.json`, conforming to the closed
  local verification-request candidate schema;
- one shared `verification-profiles/trace.json`, binding source bytes, lowering
  bindings, FormalClaim lowering trace, output references and authored
  selectors.

The request is always `ready`, `authority_effect: none`,
`release_admission: not-granted`, and contains no result. The trace explicitly
records that neither provider execution nor an evaluation result was observed.

## Identity rule

FormalClaim identity is computed before the verification context is joined.
Provider, route, runtime, InterpretationModel and execution bounds remain
excluded from the FormalClaim identity algorithm. Changing a provider therefore
changes the EvaluationContext and request digests while preserving the exact
FormalClaim `identity_inputs_digest`.

## Claim ceiling

This capability forms exact evaluation inputs only. It does not prove a claim,
admit a provider, execute a runtime, join EVF evidence, approve a product,
publish, release, deploy or establish production readiness.

## Open Questions

E02 owns the exact v4-to-current-v2 FormalClaim projection. E03 owns provider
execution outcomes and the EVF evidence join, including non-pass causality.
