# Alch semantic contract v1

This candidate extension makes the semantic prelude explicit in `.alch` source.
It adds compiler-level declarations for canonical **Axiom**, **Invariant**, and
**Constitution** references plus finite-fixture validation. It intentionally does
not add a `law` declaration: that name would overlap the existing invariant
concept without adding a distinct responsibility.

The compiler accepts `check`, `ontology`, and `build` for
`profile semantic-contract-v1`. A build follows this evidence pipeline:

`Alch source -> semantic-contract ontology -> Craft project -> DomainSpec compile -> runtime projection -> fixture validation`

The generated runtime supplies six pinned operations: `normalize-nfkc`,
`canonical-text`, `semantic-key`, `contains-token`, `contains-phrase`, and
`append-reason`. `canonical-text` means
NFKC followed by trim and the Node 26 lowercase operation; it does not claim a
complete Unicode case-folding algorithm.

The fixture set explicitly exercises semantic normalization, token
non-collapse, and operation orthogonality. Orthogonality here has a bounded,
observable meaning: `append-reason` preserves reason text and does not secretly
apply the separate text-normalization operation.

`consumer-runtime.mjs` is the compiled-artifact adapter for Define and Router
signal matching. ARE new-work intent reaches the same bytes through the
explicit `module-port/alch-semantic-adapter.mjs` binding, so request-intent can
load with zero optional adapters and report semantic unavailability locally.
The exact consumers and authority separations are declared in
`consumer-bindings.json`. `semantic-key`
and `contains-phrase` normalize separator runs without treating a substring
inside a larger token as evidence. Consumer-specific routing and quality policy
remains outside this shared semantic contract.

Run `node --test consumer-parity.test.mjs` to validate the binding and shared
normalization, phrase-matching, non-collapse, and orthogonality fixtures.

`governance-candidate/` now supplies the L3 capability-local Constitution,
compatibility policy, fail-closed degraded-mode policy, exact conformance
evidence, and an unselected adoption request. The Constitution is the human
rule surface for the `governed-by SemanticPreludeConstitution` declaration
already present in `semantic-prelude.alch`; it does not replace that source.
Run `node --test governance-candidate/validate.test.mjs` to check its digest
closure and hostile silent-fallback and implicit-adoption cases.

All ontology relationships are compiler-local candidate links. The Constitution
reference is unadopted, fixture results are finite evidence rather than universal
proof, and every output has `authority_effect: none`.

## Open Questions

- Should a later profile add property-based evidence without describing it as a proof?
- Will the AlchLang language owner adopt, defer, or reject the exact candidate
  Constitution presented by `governance-candidate/adoption-request.json`?
- Should semantic operations later become callable from ordinary `function-v1` expressions?
- If a separately admitted deployment needs a service boundary, what degraded
  mode replaces the current deterministic local import?
