# Self-Hosted Governed System-Building Service

Status: candidate
Construction stage: Product Capability plus capability-local business ontology
Authority effect: none

The first proposed CyberAlchemy product is a customer-self-hosted service for
bounded DomainSpec instantiation. We offer the CLI, and an authorized agent can
call the same typed service contract to instantiate one already-authored node
from a supported DomainSpec meta type.

The stable Product Capability remains
`CA2-CAP-PROVIDE-GOVERNED-SYSTEM-BUILDING-ACCESS`. The CLI and agent-callable
self-hosted service are realizations of that outcome, not separate sources of
meaning or authority.

## Product shape

```text
customer-controlled environment
└── self-hosted CyberAlchemy service
    ├── DomainSpec CLI                         operator/developer interface
    ├── KEP API adapter                        agent exchange interface
    ├── typed instantiation request            internal semantic contract
    ├── validated DomainSpec project + node    semantic input
    ├── frozen meta-type realization catalog   closed selection boundary
    ├── create-only contained target           artifact output
    ├── baseline-bound receipt                 reproducible evidence
    └── read-only Ontology CLI                  supporting inspection
```

The current DomainSpec evidence supports 13 backend meta-type kinds, a closed
realization catalog, and TypeScript, Python, and Rust targets. A request selects
one authored node and language; the service derives and validates the node's
meta-type identity and realization. The agent cannot invent a type or generator.

## Authority and custody boundary

- Authentication identifies the caller; it does not authorize instantiation.
- A KEP identity identifies an exchange participant; it does not authorize a
  workspace operation.
- A current entitlement and exact workspace/project authorization are required.
- The service receives only declared project and node inputs.
- Output publication is create-only and contained; existing targets fail closed.
- Generated artifacts and receipts do not authorize execution or deployment.
- Self-hosting keeps operation inside customer-selected infrastructure but does
  not by itself prove sovereignty, security, ownership, or compliance.
- The current Python Ontology CLI stays read-only and non-enforcing.

## Knowledge Exchange Protocol binding

The API shape is a thin adapter:

```text
KEP request envelope
  -> authenticate participant
  -> evaluate entitlement + workspace authorization
  -> translate to exact DomainSpec instantiation request
  -> execute one bounded create-only instantiation
  -> bind artifact and receipt identities
  -> KEP response or typed failure envelope
```

The existing admitted KEP capability is specifically encrypted knowledge
co-ownership. It does not yet authorize or define generic service invocation.
The KEP product owner must separately adopt a service-exchange capability and
ontology extension before the API adapter can receive an exact realization
binding. Until then, “KEP API” is selected direction with a visible blocker.

## Offer sequence

```text
first: self-hosted DomainSpec instantiation service + CLI + KEP API direction
  -> supporting: read-only Ontology CLI
  -> later: other protocol adapters preserving the same typed contract
  -> separate later product: person-owned sovereign agent service
```

## D65 position

```text
canonical definitions                                      selected sources
  -> Product Capability candidate                          present
  -> capability-local business ontology candidate         present
  -> commercial-offer DomainSpec source                    absent
  -> compiled graph and system ontology                    absent
  -> self-hosted service and CLI implementation binding    absent
  -> security, operational, and commercial conformance     absent
```

Existing CLI code and receipts are realization evidence only. They do not prove
the self-hosted product adopted, bound, production-ready, published, deployed,
licensed, or ready for sale.

## Validate this candidate

```sh
PYTHONDONTWRITEBYTECODE=1 python3 cyberAlchemy-v2/commercial-agent-access/scripts/validate.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s cyberAlchemy-v2/commercial-agent-access/tests -p 'test_*.py' -v
```
