# CyberAlchemy Exchange — trading-network intake

Status: KEP co-ownership, permissionless participation, escrow funding and the Unlock purchase boundary selected; key-release mechanism and detailed network scope open. Authority effect: none.
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

## Selected project-sale meaning

The user selected **KEP co-ownership**. For a sale involving seller A and buyer B,
the fulfillment contract adds B to the co-owner set of the exact project/artifact
version: `{A} → {A, B}`. Existing co-owners remain; recipient key delivery and
acknowledgement are separate evidence. Payment conditions and failure handling
are still to be defined by Exchange. This records a scope decision and does not
implement or perform a sale, grant, payment, license or exclusive transfer.

## Selected participation model

Seller/provider entry is **permissionless**, selected explicitly by the user.
Participants can join under protocol rules without per-participant operator
approval. Eligibility evidence, proof of control, verification, dispute handling
and settlement still require explicit contracts. Validator/node admission and
consensus are distinct decisions not inferred from this answer.

## Selected project-sale purchase and delivery behavior

The user accepted the clarification with **“yes”**: **Unlock means complete my
purchase and give me access**. The buyer funds escrow first. Unlock commits the
purchase for verified recoverable access, with no separate acknowledgement
button. Before commitment, deadline expiry cancels the trade and refunds the
buyer. After commitment, download/app failures allow delivery recovery and retry;
the purchase remains valid even when a client receipt is missing.

This supersedes the earlier receipt-only payment release condition and the
missing-acknowledgement timeout rule. A UI click or an HTTP timeout alone does
not determine durable commitment. Successful builds/tests remain outside the
default acceptance requirement. KEP decryption acknowledgement remains separate
recipient evidence; canonical KEP definitions are unchanged.

The [design](DECRYPTION-SETTLEMENT-DESIGN.md) now separates this accepted product
behavior from its candidate architecture. Release-service trust, proof scheme,
ledger, finality and recovery implementation remain open. The previous candidate
is preserved in [history](history/before-unlock-acceptance/INTAKE.md).

## Open Questions

1. Which exact project package/version is listed, and how are its grant and
   unlock authorization and delivery evidence bound to the paid order?
2. What are the validator/node admission and verification rules supporting
   permissionless seller/provider entry?
3. Which key-release trust model and verification scheme provide recoverable
   access? Which deadline, payment asset, ledger, refund execution/fee rules and
   escrow implementation apply? How is the KEP grant sequenced with settlement?
4. Must the first release have its own repository and installable distribution?

Also define the project package/version boundary and reconcile existing product
naming through its owner. No prototype extraction, new chain/token, commercial
settlement or canonical KEP change has been performed by this intake correction.
