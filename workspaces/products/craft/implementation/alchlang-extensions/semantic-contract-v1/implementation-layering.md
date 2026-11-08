# Semantic contract implementation layers

## Target

Move previously host-only semantic primitives into declared Alch source while
preserving the distinction between executable validation evidence and owner
authority.

## L0 - Minimum working semantic contract

- Parse and type `axiom`, `intrinsic`, `invariant`, `governed-by`, and
  `validation` declarations.
- Reject unresolved references, duplicate identities, unknown operations, and
  any Constitution binding that is adopted or authority-bearing.
- Project compiler-local ontology and a Craft/DomainSpec project.
- Compile a deterministic Node runtime for six bounded semantic operations.

Value: the semantics are declared in `.alch` and compiled through the ontology
and Craft pipeline. Cost: a small closed grammar and fixed operation registry.

## L1 - Finite conformance evidence

- Bind every invariant to exactly one fixture validation.
- Execute checked fixtures during both `check` and `build`.
- Preserve source and fixture digests in a deterministic manifest.
- Exercise normalization, token non-collapse, and ordered distinct reasons.

Value: catches executable regressions and semantic collapse over declared cases.
Cost: fixtures do not establish a universal theorem.

## L2 - Cross-consumer binding

- Bind Define and Router directly, and ARE request-intent through its injected
  Module Port adapter, to the exact same compiled semantic runtime.
- Preserve each consumer's independent policy and authority boundary.
- Run shared parity fixtures plus consumer-specific routing and intent tests.

Value: separator normalization and substring non-collapse no longer drift among
the three consumers, while request-intent remains loadable when the optional
adapter is absent. Cost: configured semantic behavior still assumes the local
compiled runtime is present; deployment and fallback remain deferred.

## L3 - Governance candidate

- Supply a capability-local Constitution for the existing `.alch`
  `governed-by` declaration without promoting it into repository authority.
- Bind compatibility and fail-closed degraded-mode policies to exact candidate
  bytes.
- Preserve local validation `PASS` separately from governed conformance
  `not_evaluable`.
- Present adopt, defer, and reject options without selecting one for the owner.
- Reject digest-valid silent fallback and implicit adoption mutations.

Value: the owner can review one exact governance candidate whose policy,
evidence, and failure posture are explicit. Cost: adoption, runtime admission,
and enforcement remain separate decisions.

## Deferred layers

- Property-based exploration beyond fixed fixtures.
- Universal proof or a stronger formal logic profile beyond `sfol-v1`.
- Owner selection over the exact adoption request and any later enforcement.
- General use of these intrinsics inside every Alch function profile.
- Service deployment, degraded-mode behavior, and runtime admission for the
  cross-consumer binding.

The degraded-mode behavior is now specified and validated as a candidate; its
runtime implementation and activation remain deferred.

These are separate decisions because they change proof strength, authority, or
language-wide compatibility rather than merely hardening this bounded profile.

## Open Questions

See [README.md](README.md#open-questions).
