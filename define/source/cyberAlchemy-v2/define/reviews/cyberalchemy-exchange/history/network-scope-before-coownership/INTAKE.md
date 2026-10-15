# CyberAlchemy Exchange — trading-network intake

Status: user-corrected scope, candidate detailed model. Authority effect: none.
Machine record: [intake.json](intake.json). The previous inference-only proposal
is superseded and preserved under history/inference-only-intake/.

CyberAlchemy Exchange is a standalone Telegraph-like trading network. Inference
is one offering type; projects sold using KEP are another. The general product
must accommodate further offering types rather than define every trade as an
inference request. This scope is explicit user direction.

Proposed common model: seller/provider, buyer, offering, terms, order, fulfillment,
acceptance evidence and settlement. Each offering type defines what is delivered
and what evidence satisfies its terms. A generated model answer, a decryptable
project version and completed commissioned work require different fulfillment
contracts. A generic API success response cannot settle all three by itself.

Exchange would own discovery, offers, orders and market/network behavior. KEP
would provide the selected knowledge-artifact exchange semantics for project
fulfillment. Alch authors contracts/behavior; DomainSpec validates and compiles
them. Identity/authentication and knowledge identity bindings must be made explicit
rather than equating a tenant, login, wallet and KEP identity.

The existing [KEP white-paper introduction](../../../product/knowledge-exchange-protocol/white-paper/v1/README.md)
already describes Exchange as the product and KEP as its technical protocol.
Its product-local canonical authority is the [KEP definitions](../../../product/knowledge-exchange-protocol/authority/definitions/DEFINITIONS.md).
KEP-D1/D2 separate artifact/version identity from files, keys and legal rights;
KEP-D5/D6 define non-exclusive co-ownership and its grant. A grant preserves
existing members and is not a sale, payment, license or exclusive transfer.
Project trading must define its commercial and fulfillment terms explicitly.

The linked Telegraph site was unavailable to the web reader. Its
[published documentation source](https://github.com/telegraphprotocol/telegraph-docs)
was inspected instead. It describes standardized provider interfaces, discovery,
paid invocation, validators and on-chain jobs. Those are reference patterns;
this intake does not select Telegraph's chain, token or scoring system for Exchange.

## Open Questions

1. What does buying a project grant: licensed access/copy, KEP co-ownership,
   exclusive rights, or delivery of commissioned work?
2. How may providers/operators join the initial network: curated, federated, or
   permissionless?
3. What are the first payment, acceptance/dispute and settlement terms?
4. Must the first release have its own repository and installable distribution?

Also define the project package/version boundary and reconcile existing product
naming through its owner. No prototype extraction, new chain/token, commercial
settlement or canonical KEP change has been performed by this intake correction.
