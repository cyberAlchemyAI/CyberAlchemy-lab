# DomainSpec architecture-conformance factory

This package makes a bounded DomainSpec architecture proof reproducible from explicit inputs. It does not invent a business rule, obligation, expected outcome, mutant, ontology mapping, or authority decision.

## Plain-language model

Think of one factory run as a sealed experiment:

1. A request names the proof nodes and repository-owned source inputs.
2. Each registered provider declares the complete inputs, implementation components, tools, and dependencies it needs. The request cannot narrow that closure.
3. `plan` hashes those bytes and tool identities into one immutable lock and a deterministic dependency order.
4. `run` copies the locked bytes into private snapshot evidence, executes every node, and gives join nodes only verified results created in that same run.
5. Every node is repeated in a separate child process. A different semantic result blocks the whole run.
6. Semantic facts and process facts are stored separately. Paths, PIDs, clocks, and temporary names cannot alter the semantic digest.
7. The complete run is verified before one atomic rename publishes it. Existing output is never overwritten.
8. `reproduce` runs the same lock under two different parent roots. Both runs must verify and produce the same semantic receipt digest.

The result is evidence, not authority. A passing receipt proves only the claim ceiling recorded in its request and providers.

## Commands

Run commands from the existing implementation package through npm:

```sh
npm --prefix projects/domainspec-v2/impl run factory -- plan \
  --request architecture-conformance/factory/fixtures/reference-suite.request.json

npm --prefix projects/domainspec-v2/impl run factory -- run \
  --request architecture-conformance/factory/fixtures/reference-suite.request.json \
  --output ../development/meta-type-factory-reproducibility/runs/manual

npm --prefix projects/domainspec-v2/impl run factory -- replay --run <terminal-run-path>
npm --prefix projects/domainspec-v2/impl run factory -- verify --run <terminal-run-path>

npm --prefix projects/domainspec-v2/impl run factory -- reproduce \
  --request architecture-conformance/factory/fixtures/reference-suite.request.json \
  --output ../development/meta-type-factory-reproducibility/runs/final

npm --prefix projects/domainspec-v2/impl run factory -- run \
  --request architecture-conformance/factory/fixtures/w3-effects-connections.request.json \
  --output ../development/meta-type-factory-reproducibility/runs/w3
```

All command results are single-line JSON. Failures contain a stable `FACTORY_*` code. The CLI resolves repository and implementation roots from its own module location, not from the caller's current directory.

## Current reference graph

The reference request contains nine nodes:

- two independent TypeScript Enum proofs: `OrderStatus` and `ShipmentPriority`;
- the `CanSettlePayout` Rule in TypeScript, Python, and Rust;
- semantic parity across the three Rule targets;
- the `CompleteSettlement` TypeScript Operation;
- the TypeScript `Rule enforces Operation` composition proof;
- a non-authorizing projection that connects current-run handles to the 25-meta-type readiness matrix.

The `enforces` provider never accepts a path to an old Rule or Operation proof. The parity and readiness providers likewise receive only current-run verified upstream handles.

The separate W3 request locks and replays four content-addressed Financial Settlement descriptors for Mapping, Interface, Event, and Operation. Native TypeScript, Python, and Rust tests remain independent evidence; the factory node does not inflate their existence into production or cross-host proof.

## Starting a new meta-type

`inspect` and `init` consume a `FactoryKitPackage/v1` prepared by the ontology/profile/descriptor owners. The package contains:

- one `MetaTypeAdmission/v2`;
- one matching `MetaTypeDescriptor/v2`;
- the exact referenced documents keyed by reference ID;
- `authority_effect: "none"`.

```sh
npm --prefix projects/domainspec-v2/impl run factory -- inspect \
  --package <ontology-owned-kit-package.json>

npm --prefix projects/domainspec-v2/impl run factory -- init \
  --package <ontology-owned-kit-package.json> \
  --output <new-empty-kit-path>
```

`init` accepts only an active, mapped, internally consistent package. Candidate mappings, candidate/deferred/superseded meta-types, stale bytes, missing refs, and forged handles are refused. There is no `--allow-candidate` option.

On success it atomically publishes exactly six empty files:

```text
kit.json
definition/empty.json
binding/empty.json
obligations/empty.json
mutations/empty.json
expected-red/manifest.json
```

Those files contain no business behavior. The family owner must author the definition and independent obligations/mutants; the target/realization owner must provide the candidate implementation and binding.

## Adding a provider

A new architecture meta-type or language target extends the process through one registered provider:

1. Keep the semantic evaluator with its family owner and the executable observation with its target/realization owner.
2. Add a provider adapter under `registry/providers/`.
3. Give it one stable provider ID and version.
4. Declare exact compatible node kinds, required raw roles, transitive component paths, and tool IDs.
5. Consume only the locked raw map and verified same-run upstream handles.
6. Return the common `FactoryNodeSemanticResult/v1` with complete positive/mutant accounting and a bounded claim ceiling.
7. Add the provider explicitly to `factory-node-registry-v1.ts`; there is no ambient discovery.
8. Add an expected-red fixture before changing the implementation, then positive, mutant, replay, tamper, collision, and cleanliness tests.
9. Add the node to a request only after its provider tests pass.

The generic request, lock, graph executor, semantic normalizer, publisher, and verifier should not change merely because a new meta-type is added.

## Evidence and equality

`semantic-receipt.json` carries equality-bearing meaning: request and lock digests, ordered node results, accounting, dependency edges, claim ceilings, and authority effect.

`process-observation.json` carries locations, PIDs, times, and child identities. It is integrity-indexed but excluded from semantic equality. Two correct runs should have different process observations and the same semantic receipt digest.

Every terminal run also includes the request, lock, plan, snapshot index, node semantic/replay evidence, terminal receipt, and a complete byte index. `verify` rejects missing, changed, foreign, or unindexed bytes.

## Boundaries

The current proof is same-host and local. It pins installed tool bytes and versions but does not provision identical toolchains on another host. It proves the bounded reference graph, not every DomainSpec meta-type, production behavior, ontology promotion, publication, release, deployment, or runtime performance.
