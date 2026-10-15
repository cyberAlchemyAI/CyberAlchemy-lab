# CyberAlchemy Exchange — trading-network intake

Status: KEP co-ownership, permissionless participation, signed delivery evidence, escrow funding and timeout cancellation selected; cancellation consequences and detailed network scope open. Authority effect: none.
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

## Selected project-sale acceptance evidence

The user selected **A: delivery receipt** as the default. The buyer signs an
acknowledgement attesting receipt and decryption of the exact project version.
This provides the chosen delivery evidence for settlement; successful builds or
tests are not required by this default. Acknowledgement is not independent proof
of quality, and it does not alone define funding, release timing or dispute rules.

## Selected project-sale funding

The user selected **A: escrow**. Buyer funds are held before delivery; valid
buyer-signed receipt/decryption acknowledgement of the exact project version is
the selected release condition. This establishes the intended funding sequence,
not a chain, payment asset, escrow implementation or permission to transfer funds.
Missing acknowledgement does not imply automatic release or refund.

## Selected missing-acknowledgement behavior

The user corrected the previous interpretation: **the trade cancels** if the buyer
misses the agreed acknowledgement deadline. This supersedes automatic dispute
opening and the pending resolver-selection question. The previous record is
preserved in [history](history/before-cancellation-correction/INTAKE.md).
Escrow disposition and the consequences for any co-ownership already granted or
access already delivered remain open. Cancellation alone does not define those
consequences or make decrypted knowledge retractable.

## Open Questions

1. Which exact project package/version is listed, and how are its grant and
   selected signed delivery acknowledgement bound to the paid order?
2. What are the validator/node admission and verification rules supporting
   permissionless seller/provider entry?
3. Does timeout cancellation automatically refund the buyer? What happens to
   any co-ownership already granted or access delivered? What acknowledgement
   deadline applies? Which payment asset, chain and escrow implementation apply?
4. Must the first release have its own repository and installable distribution?

Also define the project package/version boundary and reconcile existing product
naming through its owner. No prototype extraction, new chain/token, commercial
settlement or canonical KEP change has been performed by this intake correction.
