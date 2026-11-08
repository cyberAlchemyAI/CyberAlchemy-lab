# Alch event bindings v1

Status: prototype. Craft owner: [ORODI](/home/vlad_/projects/cyberAlchemy-v2/product/craft/capabilities/orodi/README.md).

## Definitions and construction

A channel names allowed business events and their publishing/consuming operations.
Delivery and transport-failure policies specialize existing DomainSpec contracts.
An observation profile describes operational evidence about individual delivery
stages; it never substitutes for a business event or consumer commit.

Product construction: a reviewable order module, closed parser, reference checks,
DomainSpec binding lowering, TypeScript/Rust contract generation, and local
outbox/inbox fault tests. Product approval and deployment are not claimed.
Operational support: historical Craft source-binding migration remains separate.
It does not block this prototype. Runtime commissioning remains deferred.

## Ontology scaffold

Operation produces Event; Channel carries Event and connects publishing and
consuming Operations; TransportBinding selects Channel and DeliveryPolicy;
ObservationProfile observes TransportBinding. These are navigation relationships,
not newly admitted DomainSpec meta-types. Existing DomainSpec Event and Operation
meanings and provider-neutral integration bindings remain the target contracts.

## Open Questions

A generated Rust durable runtime and provider-specific consumer execution remain
later work. This slice generates and compiles Rust binding contracts; local
execution evidence uses the existing TypeScript SQLite outbox/inbox runtime.

## Try the order module

From the repository root with Node 26.8.1 and the built DomainSpec 1.0.0 package:

```bash
projects/domainspec-v2/impl/node_modules/.bin/tsx cyberAlchemy-v2/language/capabilities/alchlang/plans/general-compiler-v1/implementation/src/cli.ts check cyberAlchemy-v2/language/capabilities/alchlang/plans/general-compiler-v1/extensions/event-bindings-v1/order-events.alch
```

Use `build <same-file> --out <new-directory>` to regenerate the contracts.
Read [order-events.alch](order-events.alch), [binding-set.json](/home/vlad_/projects/cyberAlchemy-v2/language/capabilities/alchlang/plans/general-compiler-v1/extensions/event-bindings-v1/generated/binding-set.json),
[TypeScript contract](/home/vlad_/projects/cyberAlchemy-v2/language/capabilities/alchlang/plans/general-compiler-v1/extensions/event-bindings-v1/generated/bindings.ts), and [Rust contract](/home/vlad_/projects/cyberAlchemy-v2/language/capabilities/alchlang/plans/general-compiler-v1/extensions/event-bindings-v1/generated/bindings.rs).
The binding set includes the registered SQLite persistence/transaction contracts
selected by the declared effect and the authored message delivery policies.
The source checkout contains this existing registered binding dependency.

## Language surface

`profile event-function-v1` retains the general Alch entity, SFOL rule, operation,
effect, permission, and event syntax. Additional closed declarations are `channel`,
`delivery`, `transport-failure`, `transport`, and `observation`. Fields in the example
are required. `none` explicitly declares an empty publisher or consumer set for a
dead-letter channel. Publishers and consumers must be declared Operations; a
publisher must emit its selected Event and bind a supported transactional outbox.
No implicit operation, Event, mapper, or meta-type is created.

Delivery supports at-least-once, provider-accepted acknowledgement, no ordering,
and inbox message-ID deduplication. The DomainSpec public API owns validation
and rendering. Alch performs local declaration closure and maps syntax to that API.
An `observation` selects its transport, message-ID correlation, explicit stages,
closed attributes, cardinality budget, and simulation evidence. It never grants
runtime evidence admission.

## Execution evidence and limits

The local `LocalEventFlow` harness uses the generated policy and existing SQLite
outbox/inbox transactions. Tests use an injected provider and consumer handler;
this is not a generated serverless deployment or full execution of Alch operation
permissions and rules. Caller-supplied handlers are test/runtime implementation
code, not embedded Alch source. A Rust durable consumer is not generated here.
Queue retention and maximum receive counts are declared provider policies, not
implemented by the local harness. Terminal retries quarantine the local outbox
record as dead; they do not publish to a real dead-letter queue.

Observations are ORODI observation/v1 records. Local records remain pending
telemetry with exported=0; cardinality rejection is counted separately in the
collector accounting. Missing observations remain missing in the ORODI evaluator.
Conserved counts do not establish telemetry export or business delivery.

## Validation

The focused test suite checks deterministic TS/Rust bindings and invokes rustc,
rejects ten malformed or overclaiming variants, and exercises duplicates, atomic
rollback, consumer failure/redelivery, lost acknowledgements, retry termination,
and ORODI missing/conservation evaluation. The full Alch regression results are
recorded in validation.json after the run.
