# DomainSpec integration definitions

This package is the candidate vocabulary that must be settled before DomainSpec integration syntax, compiler profiles, generated layouts, or runtime adapters are changed.

It defines 36 concepts across six concerns while reusing the active DomainSpec meanings of D45–D49. It is provider-neutral and language-neutral. Its authority, implementation, and promotion effects are all `none`.

## The model

```text
domain/application meaning
        |
        v
concern-specific dependency contract (D45) or inbound application boundary
        |
        v
integration binding -- policies -- failure outcome binding (D48)
        |
        v
provider realization -- provider profile -- configured resource
        |
        +--> bounded runtime receipt
                    |
                    v
          integration observation --> ORODI adapter --> ORODI evaluator
                                      (one way only)
```

The binding layer preserves meaning. The provider realization supplies mechanics. Runtime receipts and observations state only what was actually observed.

## Reused DomainSpec definitions

| ID | Definition | Why it remains authoritative |
| --- | --- | --- |
| D45 | Concern-Specific Dependency Contract | Keeps provider mechanics out of consumer signatures. |
| D46 | Persistence Binding | Separates entity, contract, adapter, resource, mapping, and evidence. |
| D47 | Transaction Guarantee Binding | Bounds atomicity to an explicit local commit boundary. |
| D48 | Failure Outcome Binding | Classifies failures without choosing continuation. |
| D49 | Durable Workflow Runtime Binding | Composes durability services without selecting their providers. |

## Shared integration definitions

| Definition | Role |
| --- | --- |
| Integration Binding | Joins one logical boundary to a provider realization through explicit policies and evidence. |
| Provider Profile | Declares a provider kind's configuration vocabulary and supported capabilities. |
| Provider Realization | Names the configured adapter and resource that realize a profile. |
| Serialization Profile | Defines a versioned storage or wire representation. |
| Runtime Receipt | Records a bounded runtime observation without inflating it into an external effect. |
| Integration Artifact Layout | Places contracts, bindings, adapters, configuration, migrations, deployment artifacts, and evidence in profile-idiomatic locations. |

## Persistence definitions

| Definition | Role |
| --- | --- |
| Persistence Mapping | Maps entities, value objects, enums, sums, collections, and references to physical records without collapsing them. |
| Migration Contract | Defines physical-model evolution, compatibility, data transformation, rollback posture, and verification. |

The complete persistence chain is:

```text
Entity / Value Object / Enum / Sum
        |
        v
Concern-Specific Dependency Contract (D45)
        |
        v
Persistence Binding (D46)
        +--> Persistence Mapping
        +--> Provider Realization
        +--> Transaction Guarantee Binding (D47)
        +--> Failure Outcome Binding (D48)
        +--> Migration Contract
```

## Messaging definitions

| Definition | Role |
| --- | --- |
| Message | A versioned transport representation of an event, command, query, response, or integration document. |
| Message Envelope | Keeps identity, timing, correlation, routing, and tracing metadata outside the payload. |
| Message Channel | The logical destination family. |
| Queue | Competing consumption: one successful consumer path per available message. |
| Topic | Fan-out to independently configured subscriptions. |
| Stream | Retained ordered log with positions and replay. |
| Dead-Letter Channel | Isolation and governed redrive after terminal delivery failure. |
| Publication Binding | Maps a logical result to a message and offers it to a channel. |
| Subscription Binding | Maps a delivered message to an application operation and its completion boundary. |
| Delivery Policy | Declares at-most-once or at-least-once transport behavior, retries, and terminal disposition. |
| Acknowledgement Boundary | States exactly when processing may be acknowledged. |
| Ordering Policy | Supports unordered, key-ordered, and globally ordered claims with explicit observation boundaries. |
| Deduplication Policy | Declares key, owner, retention, atomicity, and duplicate outcome. |
| Transport Failure Policy | Maps provider failures to stable D48 outcomes without performing continuation. |

Example composition:

```text
OrderSubmitted
  -> OrderSubmittedToMessage
  -> OrderSubmittedMessage
  -> PublicationBinding
  -> OrderEventsTopic
  -> BillingSubscription
  -> OrderSubmittedToCreateInvoice
  -> CreateInvoice operation
```

The arrows describe canonical relationships. They do not turn the mapper into a calculation or the operation into a consumer.

## External API definitions

| Definition | Role |
| --- | --- |
| Inbound Endpoint Binding | Maps protocol request/response handling to one application operation. |
| External API Contract | The domain-facing remote capability, specializing D45. |
| External API Binding | Maps that contract to one concrete provider operation. |
| Webhook Binding | Adds sender verification, replay protection, external event identity, and bounded acknowledgement to an inbound endpoint. |
| Authentication Binding | References schemes and credential slots without containing secrets. |
| API Resilience Policy | Separates timeouts, safe retries, backoff, concurrency, and circuit behavior. |
| API Failure Mapping | Translates protocol/provider failures into the D48 failure surface. |

Example outbound composition:

```text
AuthorizePayment workflow step
  -> PaymentGateway contract
  -> PaymentExternalApiBinding
  -> request mapper
  -> provider operation
  -> response mapper / API failure mapping
  -> PaymentAuthorizationResult or declared failure outcome
```

## ORODI observation definitions

`Integration Observation` is an immutable, disclosure-safe, non-actuating account of a bounded runtime fact. `ORODI Observation Binding` specializes it with a one-way projection:

```text
runtime -> observer -> ORODI adapter -> ORODI evaluator
```

There is no reverse edge. ORODI cannot use this binding to write the database, retry a message, call an API, deploy, or otherwise control the observed runtime.

## Required non-collapse laws

- Entity is not table; value object is not record.
- Domain event is not message.
- Operation is neither endpoint nor message consumer.
- Query is not external API call.
- Dependency contract is not provider adapter.
- Queue, topic, and stream remain different channel semantics.
- Provider acceptance, transport delivery, application commit, and business completion are four different facts.
- Runtime receipt is not external effect.
- Failure classification is not continuation selection.
- ORODI observation is not runtime control.

## Validate

From this directory:

```bash
python3 validate.py
```

The validator checks exact concept closure, all five definition voices, reuse and specialization references, relationship endpoints, source-byte digests, the non-collapse laws, and the candidate-only effect ceiling.

## Status and next boundary

This package may be reviewed, challenged, or used as input to a governed design plan. It does not admit canonical definitions and does not prove compiler, schema, generator, runtime, provider, ORODI, or multi-language support. The next stage is a drift-and-coverage reconciliation against the DomainSpec meta-type profiles and each target-language generator.
