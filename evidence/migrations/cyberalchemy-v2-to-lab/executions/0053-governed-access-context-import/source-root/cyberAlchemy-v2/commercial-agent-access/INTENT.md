# Self-Hosted Governed Instantiation Intent

Status: owner-directed candidate input
Decision date: 2026-09-01
Authority effect: none

## Selected first offer

CyberAlchemy will offer its command-line tools as interfaces to a
customer-self-hosted governed system-building service. A human operator or an
authorized agent can submit one typed request to instantiate an already-authored
DomainSpec node from its selected supported meta type into one supported target
language.

The customer operates the service inside its selected environment. CyberAlchemy
provides the bounded software, frozen catalogs, validators, generators, receipt
contracts, updates, and support terms. Self-hosting does not itself prove data
ownership, security, sovereignty, compliance, or production readiness.

## Agent-callable boundary

An agent may request instantiation; it does not receive general repository,
filesystem, ontology, deployment, or provider authority. The service must:

1. authenticate the caller and evaluate a current scoped entitlement and
   workspace authorization;
2. load one exact validated DomainSpec project and node;
3. derive the node's declared backend meta-type identity;
4. select only one realization from the frozen supported catalog for
   TypeScript, Python, or Rust;
5. reject unsupported, stale, ambiguous, escaping, colliding, or existing
   targets before publication;
6. publish only through the create-only contained target boundary; and
7. return the generated artifacts plus a baseline-bound receipt whose
   authority effect is `none`.

The agent cannot invent a meta type, select an unregistered generator, overwrite
an existing target, weaken validation, or turn a receipt into deployment
authority.

The current CLI also exposes formalization commands, but they are outside this
initial agent contract until separately selected, specified, bound, and tested.

## Interfaces

The DomainSpec CLI remains the operator and developer interface. Agents consume
an API through a Knowledge Exchange Protocol adapter that must translate one
KEP request envelope into the same typed instantiation contract and return one
KEP response envelope bound to the exact instantiation receipt. It may not
create a second semantic path.

KEP identity authenticates the exchange participant but does not authorize the
workspace operation. Authorization remains a separate, current decision over
the caller, entitlement, project, node, language, target root, and request
identity. Every request and response must preserve correlation, idempotency,
version, failure, omission, and authority-ceiling fields.

## KEP prerequisite

The current admitted KEP capability governs encrypted knowledge-artifact
co-ownership, recipient key envelopes, and acknowledgement. It does not define
a generic service invocation API. Before this adapter can be bound, the KEP
product owner must separately define and adopt an agent service-exchange
capability and business ontology records for request, response, failure, and
receipt transport. The commercial candidate cannot manufacture that admission.

The read-only Ontology CLI remains a supporting inspection interface and cannot
become an authority gate while its governed Rust replacement is unfinished.

## Product boundary

The stable outcome remains governed system-building access. CLI, KEP API,
container, and later transport adapters are replaceable self-hosted realization
surfaces. Hosted CyberAlchemy inference and a managed sovereign-agent product
remain later, separate directions.

## Current posture

The DomainSpec CLI is private, candidate, unreleased, and not production-ready.
The repository does not yet contain the accepted self-hosted service binding,
agent request contract, authentication and authorization boundary, packaging,
upgrade channel, operational conformance, or commercial terms required to sell
this product.

## Non-effects

This decision does not adopt the Product Capability, implement or deploy the
self-hosted service, publish either CLI, activate ontology enforcement, select
or adopt a KEP service-exchange capability, select pricing or licensing, handle
customer credentials or source, instantiate a customer node, run an agent,
overwrite a target, or authorize any downstream effect.
