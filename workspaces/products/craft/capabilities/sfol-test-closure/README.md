# SFOL Test Closure Capability

Status: implementation-directed candidate
Owner: DomainSpec v2 owner
Visibility: private
Authority effect: none

This package carries the capability-local D65 construction chain for bounded
SFOL test closure. It keeps product meaning, business semantics, authored
DomainSpec source, generated graph/system projections, implementation binding,
and conformance evidence distinct.

The package does not change the existing Lean claim, rewrite historical Auth
v1 evidence, admit its own definitions or ontology, or grant publication,
release, deployment, or production authority.

## Optional EVF successor

The adopted v1 capability and `domainspec-sfol-tde-api/v1` remain unchanged:
closing a v1 request still requires a passing EVF detection matrix. The
additive `domainspec-sfol-tde-api/v2` candidate makes EVF optional for the base
closure:

- an omitted matrix closes the base proof and records `evf_status` as
  `not_requested` with a null detection-matrix digest;
- a supplied matrix is still fail-closed and must be content-valid with
  `result: pass`, after which `evf_status` is `passed`;
- `not_requested` is an explicit absence of EVF evidence, never an EVF PASS.

The v2 Product Capability, business ontology, and conditional property
denominator are separate exact files. The repository user selected
`ADOPT-EXACT` for the v2 capability and `ADMIT-EXACT` for the v2 business
ontology and denominator. These semantic selections do not accept DomainSpec
source, admit a system ontology, or establish implementation conformance. The
prior v1 source-acceptance candidate must not be selected for this successor:
rebuilding after the implementation change makes its implementation and
generated-system bindings stale. The v2 profile-eligibility, DomainSpec-source
acceptance, and system-ontology admission selections are now bound separately
to this exact source/build epoch.

`optional-evf-transition.json` binds the exact candidate and implementation
bytes and records this transition's blockers and claim ceiling.

`product-ontology-amendment-candidate.json` is the exact v2 business/system/
bridge projection packet. It binds the selected profile, source, and
system-ontology decisions plus the generated and conformance receipts. The
canonical `projects/domainspec-v2/ontology/` package remains unchanged until
its pre-existing source-currentness blocker is reconciled and the package
validator can produce a fresh append-only receipt.

The additive authored source epoch is under `domainspec-v2/`. It leaves the
historical `domainspec/` tree and generated v1 evidence unchanged. Its explicit
development profile adds the `Policy` kind and the active `applies`
relationship so `EvfSelection` can select behavior for `BuildTestClosure`.
Run its read-only compiler-input check from the capability root:

```text
tsx scripts/check-v2-source.ts
```

The check compiles twice in memory, requires byte-identical graph and manifest
bytes, binds the exact v2 semantic selections, and writes no generated files.
Passing this check establishes deterministic authored-source inputs; the exact
profile-eligibility and source-acceptance decisions are recorded in the
corresponding selection files.

The selected decisions are available, so materialize the v2 candidate
projection and run the aggregate technical gate:

```text
tsx scripts/build-v2.ts
tsx scripts/validate-v2.ts
```

`build-v2.ts` writes only `generated-v2/` and records the exact system-ontology
candidate bytes. `validate-v2.ts` runs the source check, two complete SFOL test
runs, typecheck, two materializations, and exact implementation-map closure; it
writes `conformance/evidence-v2.json` and `construction-binding-v2.json` with
explicit blockers. This epoch's separate `ADMIT-EXACT` system-ontology
selection is recorded in `optional-evf-transition.json`.

The `decisions/` directory contains immutable, exact-byte owner-decision
candidates for definition admission, Product Capability adoption, business
ontology admission, and source acceptance. Both v1 and v2 semantic decisions
have separate exact selections; the old source-acceptance candidate remains
unselected. A decision is effective only through a separate owner selection
that binds the candidate and subject digests; editing a candidate requires a
new digest and review.

The definitions decision has a separate exact `ADMIT-EXACT` selection, and the
Product Capability decision has a prerequisite-bound `ADOPT-EXACT` selection.
The business ontology decision also has a prerequisite-bound `ADMIT-EXACT`
selection covering the ontology and its 21-property denominator. These
selections do not admit the generated system ontology, implementation, or
canonical product projection.

The authored DomainSpec source has a separate immutable acceptance candidate
binding the exact source-set manifest, development profile, compiled graph,
and build receipt. The v2 candidate is selected with `ACCEPT-EXACT`; the
historical v1 source-acceptance candidate remains unselected.

Source acceptance does not by itself admit the implementation-owned
development profile or system ontology. This epoch records separate
`ELIGIBLE-EXACT` and `ADMIT-EXACT` selections for those boundaries.

Run the deterministic compiler from the repository root with the TDE package's
installed `tsx` runtime:

```text
tsx projects/domainspec-v2/capabilities/sfol-test-closure/scripts/build.ts
```

Run the bounded conformance gate, including two complete SFOL test runs, two
compiles, CLI smoke validation, the 21-property denominator, immutable
owner-decision candidates, and immutable Lean/Auth-v1 digest checks:

```text
tsx projects/domainspec-v2/capabilities/sfol-test-closure/scripts/validate.ts
```

The capability-local development profile is necessary because the canonical
minted-profile registry currently binds an older meta-type digest. The v2
system ontology is admitted for this bounded private capability epoch, while
the package still grants no publication, release, deployment, or production
authority.
