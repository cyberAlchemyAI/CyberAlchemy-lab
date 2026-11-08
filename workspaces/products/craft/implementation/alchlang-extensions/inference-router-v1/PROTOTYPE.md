# Inference router D2/D3 prototype

Status: compiled selector candidate; authority effect none. Owner: Alch language and inference implementation owner.

The new product-capability and business-ontology scaffolds bind the eight D1
concepts to catalog, selection, dispatch and result responsibilities. They are
navigation and product prototypes, not admitted system ontology. Exact semantic
predecessors are `define/definition-pack.json` and the actual Define CLI result
in `define/cli-result.json`; its five open questions remain unresolved.

`provider-selection.alch` is an authored internal selection prototype using the
existing `declarative-function-v1` parser. `prototype.mjs` emits the actual
DomainSpec declarative contract and boundary model to `generated/`. These are
parser projections, not a compiled graph, generated runtime or conformance proof.
The generated contract expresses eligibility, minimum rank, stable identifier
sorting and selection. Their generated Node execution is covered by execution.test.mjs.

## Current product frontier

D2 scaffolds and the D3 selector now compile through the imported sibling
DomainSpec compiler. Seven generated HTTP-handler tests pass, alongside six
parser/schema tests. The source uses coalesce for its optional alias. A bounded
first() collection operation was added to the sibling DomainSpec compiler with
empty-list and type-rejection tests. Alch's TypeScript executable now has an
ALCHLANG_TYPESCRIPT_COMPILER override instead of requiring the old checkout path.

`compiler-binding.json` records the sibling package and exact built JavaScript
hashes. `run.mjs` checks those bytes and configures the existing Alch bridge.
The compiler is referenced from ../domainspec-core, not copied into this package.
The TypeScript toolchain currently lives in /tmp; after cleanup install the same
version and supply ALCHLANG_TYPESCRIPT_COMPILER explicitly.

Current runnable frontier: provider dispatch and request/response normalization,
followed by streaming, usage and bounded fallback tests. The selector is an
internal component, not a completed inference service. There is no current
compiler blocker for this Node selector. Rust parity remains untested.

The D65 chain is candidate definitions -> business/product scaffolds -> authored
Alch -> DomainSpec compilation -> generated Node selector -> local execution
tests. Product review and operational authority remain ungranted. The original
construction-evidence.json records the prior parser-only epoch;
execution-evidence.json owns the current test snapshot.

## Trust and scope

This is `/internal/select-provider`, not the public inference endpoint. Only the
trusted host supplies tenant identity, tenant-filtered permissions, policy ranks
and token estimates. The operator's catalog binding is fixed; request input
cannot set a URL or credential. The optional supplied catalog is for trusted
host calls and local fixtures only; exposing that envelope to end users would
let them forge eligibility. A shared internal bearer token is not tenant auth.

`required_context_tokens` must include input plus output reservation under a
binding-compatible estimator. Unknown fit must exclude a provider. This prototype
uses one common estimate; provider-specific tokenizer accounting is pending.
It accepts only text.generate and a selected strategy's precomputed rank.
Strategy/version resolution belongs to trusted configuration. No rank is a
measured price or latency claim.

The selector returns binding identity/version and policy version to the host.
The eventual public response must hide private binding IDs. It does not yet
implement provider calls, safe fallback, normalization of messages, SSE,
usage observations, idempotency, public discovery or a full host service.

## Checks

With Node >=26.8.1, from this directory:

```sh
node prototype.mjs --check
node run.mjs test
node run.mjs build /absolute/new/bundle
```

`node prototype.mjs` regenerates the two parser projections. This tool uses the
existing compiled Alch parser under `../../implementation/dist/`; its hashes are
recorded as tested binaries without asserting they match an unperformed build.
The generated selector tests execute real compiler output with local catalog fixtures; they do not invoke model providers.

## Operational support

- Inference operator and product owner: choose real providers, aliases, credentials
  and paid-call budget before live verification; no local parser-test dependency.
- Inference operator: choose production limits before candidate freeze.
- Product/runtime owner: choose retention and restart replay behavior before D7/D9.
- Define runtime owner: durable session continuity is deferred and does not block
  the local inference prototype.
- Product owner and VPS operator: deployment follows tested-product review and an
  exact deployment scope; no deployment is performed here.

## Open Questions

The five product questions remain in the Define CLI result (result record excluded).
Compiler question refinement: the imported compiler verifies and executes the selector schemas, mappings, quantifiers and stable ordering. The full public inference API, HTTP provider request bodies and SSE still need tested transport bindings. Other Define questions remain open; historical Define output is preserved.
