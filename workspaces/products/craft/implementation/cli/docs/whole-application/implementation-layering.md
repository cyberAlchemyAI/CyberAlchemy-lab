---
title: DomainSpec Canonical Application Graph Implementation Layering
status: implemented
updatedAt: 2026-09-16
owner: DomainSpec product construction
scope: canonical application graph, integration relationships, and generated-code minimization
authorityEffect: none
---

# DomainSpec Canonical Application Graph Implementation Layering

> Reconciliation result (2026-09-16): the canonical graph formation and its
> whole-application consumers are implemented. Strict unused-code checks,
> authored graph closure, provider-to-operation wiring, migration dependency
> safety, runnable entrypoints, and external native-runtime receipts are covered.
> The executed dependency order and bounded evidence are recorded in
> [runtime-remediation-dag.md](runtime-remediation-dag.md). This remains a
> construction result, not publication, release, deployment, or production
> authority.

This implementation replaces compatibility-preserving generated support with one minimal-output behavior and makes application integration relationships first-class compiled graph facts. There is no compact-support profile and no requirement to preserve prior generated source bytes.

The plan produces construction candidates only. It does not grant product approval, publication, release, deployment, provider execution, or runtime-conformance authority.

## Resolved product decisions

- Generated TypeScript support is always capability-derived. Full unused support and its byte-pinned compatibility tests are removed.
- Domain meta-types remain distinct from integration node kinds. `Message Contract`, `Inbound Endpoint`, `Publication`, and `Request Contract` do not inflate the DS-D1 backend meta-type denominator.
- The existing domain relationship `Entity --emits--> Event` keeps its meaning. Publication uses the distinct canonical relationship `Publication --publishes-event--> Event`; reusing `emits` would collapse domain-event provenance with transport publication.
- Integration references compile into typed nodes and edges before generators run. Generators consume the compiled application graph and do not reconstruct relationships from parallel reference fields.
- Relationship endpoints, direction, multiplicity, provenance, and role are validated fail-closed.

## Target graph

```text
Mapping          --reads-payload-from--------> Event
Mapping          --produces-message-contract-> Message Contract
Inbound Endpoint --invokes-------------------> Operation
Operation        --accepts-request-----------> Request Contract
Publication      --publishes-event-----------> Event
```

Concrete commerce slice:

```text
OrderSubmittedToMessage  --reads-payload-from--------> OrderSubmitted
OrderSubmittedToMessage  --produces-message-contract-> OrderSubmittedMessageV1
POST /orders             --invokes-------------------> SubmitOrder
SubmitOrder              --accepts-request-----------> SubmitOrderRequest
OrderSubmittedPublication --publishes-event----------> OrderSubmitted
```

The user-facing renderer may display arrows, but the compiled form carries stable node IDs, edge IDs, exact node kinds, source pointers, and authority digests.

## Graph composition model

```text
CompiledProjectGraph
  domain nodes + DS-D8 relationships
                    \
                     +--> CompiledApplicationGraphV1 --> validators --> generators
                    /
CompiledIntegrationGraphV1
  integration nodes + integration relationships
```

`CompiledApplicationGraphV1` is a composed traversal surface, not a flattened authority source. It preserves:

- the original domain graph and DS-D8 relationship authority digest;
- a separate integration relationship authority digest;
- the typed join edges between domain and integration nodes;
- the source JSON pointer and source digest for every integration node and edge;
- deterministic ordering and a canonical graph digest.

## Canonical integration node kinds

| Node kind | Stable identity source | Required semantic payload |
| --- | --- | --- |
| `message-contract` | `message_types[].message_type_id` | message kind, logical payload reference, serialization profile, version |
| `inbound-endpoint` | `inbound_endpoint_bindings[].binding_id` | protocol operation, authentication boundary, provider realization |
| `publication` | `publication_bindings[].binding_id` | producer contract, channel, delivery policy, acceptance boundary |
| `request-contract` | external API operation request or Operation input contract | exact structural request shape and owning Operation |

Domain endpoints retain their compiled project selectors and kinds: `Mapping`, `Event`, and `Operation`.

## Canonical integration relationship signatures

| Relationship | Source -> target | Multiplicity | Required agreement |
| --- | --- | --- | --- |
| `reads-payload-from` | `Mapping -> Event` | many mappings to one or more event payloads | Mapping typed inputs include the exact Event payload selector |
| `produces-message-contract` | `Mapping -> message-contract` | each outbound message Mapping has exactly one target | Mapping result shape agrees with the message contract payload and version |
| `invokes` | `inbound-endpoint -> Operation` | each endpoint invokes exactly one Operation; an Operation may have many endpoints | endpoint request/response mappings agree with the Operation signature |
| `accepts-request` | `Operation -> request-contract` | each bound Operation request use has one exact contract | Operation input and request contract are structurally identical |
| `publishes-event` | `publication -> Event` | each publication names exactly one logical Event | publication source, mapper input, and message payload all agree on the Event |

Every signature defines endpoint kinds, direction, multiplicity, admitted scope, non-examples, composition meaning, and validation obligations. Missing, duplicate, reversed, mistyped, or semantically disagreeing edges are rejected before generation.

## Layer decision table

| Layer | Decision question | Minimum working unit | User/operator outcome | Risk reduced | Exit evidence |
| --- | --- | --- | --- | --- | --- |
| L0 | After this layer, we know whether one messaging and HTTP slice can be represented as a typed composed graph without inventing domain meta-types. | New integration authority, four integration node kinds, five relationship signatures, and one compiled commerce graph. | The five arrows are inspectable compiled facts with source provenance. | Relationship meaning no longer lives only in disconnected reference fields. | Golden compiled graph, deterministic digest test, endpoint non-collapse tests. |
| L1 | After this layer, we know whether contradictory integration declarations fail before code generation. | Cross-node agreement validator for Mapping inputs/outputs, endpoint invocation, request shape, and publication Event identity. | Invalid application wiring reports an exact edge and source pointer. | Wrong mappings, request drift, reversed endpoints, and inferred wiring fail closed. | Positive commerce fixture plus one negative mutant per obligation. |
| L2 | After this layer, we know whether generators can consume only canonical graph relationships and produce minimal warning-free code. | TypeScript generators use the graph for imports and wiring; all structured value support becomes capability-derived. | Generated code contains the required mapper, endpoint, request, and publication wiring without dead helpers. | Parallel look-alike wiring and unused generated code are removed. | TypeScript strict compile with unused locals/parameters denied; AST assertions prove graph-selected dependencies. |
| L3 | After this layer, we know whether the same graph has deterministic Python and Rust projections and a coherent standalone application candidate. | Python and Rust relationship consumers, regenerated commerce application, installed-consumer verification. | All three languages expose equivalent application structure. | Language drift and target-specific relationship inference are removed. | Three-language generation, compilation, graph-equivalence receipt, warning-denied Rust, Python import/compile checks. |

## Capability progression

| Area | L0 | L1 | L2 | L3 |
| --- | --- | --- | --- | --- |
| Graph | Materialize typed integration nodes and edges | Enforce semantic agreement | Drive TypeScript generation | Prove cross-language equivalence |
| Relationships | Five canonical signatures | Obligation witnesses and hostile mutants | Exact generated imports/wiring | Equivalent language projections |
| Mapping | Event input and message output are explicit | Input, output, totality, and version agreement | Mapper source uses only declared capabilities | Python/Rust parity |
| HTTP | Endpoint and request contract are explicit | Invocation and structural request agreement | Router and Operation signatures derive from graph | Python/Rust parity |
| Messaging | Publication-to-Event is distinct from domain `emits` | Publication, mapper, message, and channel closure | Publisher wiring derives from graph | Python/Rust parity |
| Generated support | Current Query specialization retained | No change | One always-minimal TypeScript support renderer | Strict clean output in all targets |

## Formation waves already implemented

### W0 - Define and compile the integration graph — formation complete

1. Add a canonical integration relationship authority source beside, not inside, the DS-D8 domain relationship authority.
2. Define the four integration node kinds and five relationship signatures with examples, non-examples, multiplicity, scope, and obligations.
3. Add closed schemas and TypeScript types for `CompiledIntegrationGraphV1` and `CompiledApplicationGraphV1`.
4. Materialize nodes and edges deterministically from messaging and external-API compositions.
5. Compose them with `CompiledProjectGraph` while preserving both authority digests and source provenance.
6. Add the concrete commerce graph fixture and exact snapshot.

Verification:

- identical inputs produce identical node ordering, edge ordering, and graph digest;
- `Entity --emits--> Event` and `Publication --publishes-event--> Event` remain orthogonal;
- integration node kinds cannot enter DS-D1 meta-type counts;
- reversed or unknown edges fail closed.

### W1 - Enforce relationship obligations — formation complete

1. Replace reference-only application binding checks with graph-edge checks.
2. Validate `reads-payload-from` against typed Mapping inputs.
3. Validate `produces-message-contract` against Mapping result shape, message payload, and message version.
4. Validate `invokes` against the exact Operation selector.
5. Validate `accepts-request` using structural request compatibility, including optional, list, set, sum, enum, entity-reference, and value-object shapes.
6. Validate `publishes-event` across Publication, Mapping input, Message Contract logical payload, and channel acceptance.
7. Emit one deterministic diagnostic code and JSON pointer per failed obligation.

Verification:

- positive whole-commerce binding;
- missing-edge, duplicate-edge, wrong-direction, wrong-kind, wrong-multiplicity, wrong-request-shape, wrong-message-version, and publication/Event drift mutants;
- non-collapse and orthogonality assertions for all five signatures.

### W2 - Make TypeScript consume the graph and remove compatibility output — complete

1. Remove `structuredRuleSupport` as a full-support output.
2. Remove the `selectiveSupport` switch; `createStructuredValueRenderer` always records used capabilities and emits only those capabilities.
3. Update Rule, Mapping, Policy, Operation, Workflow, Interface, Event, Entity, Value Object, State Machine, Query, and public-mapping generators to the single minimal behavior.
4. Remove byte-pinned tests whose only purpose is preserving unused helper text; replace them with semantic output and AST dependency tests.
5. Generate Mapping imports, router invocation, request contracts, and publication wiring from graph edges only.
6. Reject any generator request whose required edge is absent instead of recovering from legacy reference fields.

Verification:

- the complete generated TypeScript application passes `noUnusedLocals` and `noUnusedParameters`;
- each generated file imports only dependencies reachable through its canonical edges;
- removing a required edge fails generation;
- identical graphs reproduce exact bytes.

### W3 - Cross-language reconciliation and standalone regeneration — complete

1. Add the same application-graph consumers to Python and Rust generation.
2. Generate a language-neutral relationship manifest beside each application.
3. Assert that TypeScript, Python, and Rust manifests contain the same node IDs, edge IDs, relationship IDs, and endpoint selectors.
4. Regenerate the standalone commerce application from the updated vendored CLI.
5. Update documentation to teach the arrow model and distinguish domain Event creation from transport publication.
6. Remove obsolete compatibility fixtures, stale output hashes, and superseded reference-field-only tests.

Verification:

- package typecheck, build, and focused relationship suites;
- whole-application generation and verification in all three languages;
- TypeScript strict unused checks, Python compile/import checks, and Rust warnings denied;
- installed-consumer regeneration from an empty output directory;
- no generated build caches retained in the example project.

## File-impact map

| Surface | Planned change |
| --- | --- |
| `definitions/relationships/` | Preserve DS-D8 authority; add separately owned integration relationship definitions and non-collapse evidence. |
| `impl/cli/contracts/` | Add integration/application graph schemas; revise messaging and external-API composition schemas only where a stable node identity is missing. |
| `impl/cli/src/system-integration/` | Compile integration nodes/edges, compose the application graph, and enforce cross-edge agreement. |
| `impl/cli/src/input/project-model.ts` | Remain the domain-graph compiler; expose stable domain endpoints to the application graph without accepting integration node kinds as domain meta-types. |
| `impl/cli/src/generation/` | Consume canonical graph relationships and make TypeScript value support always minimal. |
| `impl/cli/examples/reconciled-commerce/` | Author the complete five-edge example and expected graph/binding snapshots. |
| `impl/cli/test/` | Add obligation mutants, graph determinism, non-collapse, strict-unused, and three-language equivalence coverage. |
| standalone commerce project | Regenerate all targets and documentation after package validation passes. |

## Non-regression guardrails

- Domain relationships and integration relationships retain separate authority sources and digests.
- `Entity --emits--> Event` never becomes a synonym for publication.
- Integration nodes never masquerade as Entity, Value Object, Event, Operation, or another DS-D1 meta-type.
- A generator cannot infer a missing canonical relationship from field names, selector spelling, or adjacent configuration.
- Mapping calculations remain explicit inputs; a Mapping does not call a Calculation implicitly.
- Policy continues to select already declared behavior and does not execute its target.
- Formation and compilation evidence never becomes runtime-delivery, provider-call, publication, or deployment evidence.
- Deterministic ordering and exact-input reproducibility remain mandatory after old byte compatibility is removed.

## Implemented result and evidence boundary

- The integration relationship authority is separate from DS-D8 and carries all five signatures plus explicit `emits`/`publishes-event` non-collapse evidence.
- Application binding compiles and validates a deterministic composed graph before whole-application generation.
- TypeScript structured-rule support has one behavior: helpers are emitted only for capabilities referenced by the specialized generated program.
- TypeScript, Python, and Rust plans emit the same language-neutral `.domainspec/application-graph.json`, bound by `application_graph_sha256` in the plan and receipt.
- The reconciled commerce source exercises every relationship, including an inbound endpoint and exact request contract.
- Compatibility-only full-support output and its monolithic observer hash are no longer part of the product behavior.

These facts now support generated runnable application candidates. Provider
adapters implement their declared ports, migrations use dependency-safe ordering,
and each language has an executable entrypoint. Formation receipts deliberately
continue to say that native compilation was not performed during generation;
the separate `verify-runtime` command records native compilation and bounded
signed-loopback behavior in an external receipt. Neither receipt establishes
live PostgreSQL, live NATS, outbound-provider delivery, consumer completion,
deployment, or production readiness.

## Verification evidence

- application binding and graph obligation tests, including deterministic digest and `emits`/`publishes-event` orthogonality;
- whole-application generation, verification, and disposed-root compilation across TypeScript, Python, and Rust;
- independent capability-chunk observers for generated TypeScript support;
- installed-package schema and package-boundary checks;
- external runtime-evidence receipt validation and target non-mutation checks;
- regenerated standalone commerce source and all three language targets, with
  native compilation and signed loopback runtime evidence for each language.
