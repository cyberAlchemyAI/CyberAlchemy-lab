# Exchange project unlock and settlement — candidate design

Status: Unlock purchase behavior accepted; architecture remains candidate, not an admitted Definition
Pack, construction plan, cryptographic protocol, or implemented payment system.
Owner: Exchange product owner; KEP owns its existing definitions.
Consumers: Exchange product design, later Alch/DomainSpec construction, KEP integration.
Intent source: the user said “it cancels the trade”, “but the decryption should
be the acknowledgement”, and “lets design it”.
Accepted scope and historical decisions: [intake](INTAKE.md).

## Product contract and necessary distinction

The desired experience is one **Unlock project** action: obtain the exact project
version, become a KEP co-owner, and complete payment without a second acceptance
button. Ordinary local decryption cannot itself notify a remote settlement ledger.
A modified client can decrypt and suppress any following network request. A buyer
signature or proof voluntarily sent after decryption does not remove that attack.
The earlier suggestion that auto-submitting a signature makes these actions one
inseparable protocol operation was too strong.

Accepted commercial meaning (user “yes” to the plain-language clarification): the buyer authorizes payment for verified,
recoverable access to the committed version. A finalized settlement commitment
ends cancellation eligibility. Actual local decryption produces the KEP receipt
automatically as delivery telemetry; withholding it does not reverse payment.
This supersedes the earlier receipt-only release condition and narrows timeout
cancellation to the period before commitment. Refund on pre-commit timeout is
accepted. The user accepted this product behavior, not the release-service trust
model, cryptographic scheme, chain or implementation. A click initiates the
operation; the authoritative durable transition determines commitment.
Previous candidate: [history](history/before-unlock-acceptance/DECRYPTION-SETTLEMENT-DESIGN.md).

If the requirement is instead payment strictly after proven local decryption,
with cancellation/refund whenever the buyer sends nothing, this design does not
satisfy it. Additional trusted execution or a reviewed fair-exchange protocol
with different failure rules would be required.

## Existing authority and evidence

[KEP definitions](../../../product/knowledge-exchange-protocol/authority/definitions/DEFINITIONS.md):
KEP-D2 binds immutable content and policy; D4 binds the recipient encryption key;
D5/D6 preserve existing co-owners and separate grant from sale; D8 distinguishes a
ciphertext commitment from availability; D9 keeps content keys private; D12 makes
acknowledgement recipient-authorized evidence, separately recorded from the grant.
Missing acknowledgement does not silently remove admitted membership.
[KEP product boundary](../../../product/knowledge-exchange-protocol/README.md)
excludes protocol custody of plaintext, content keys, and encrypted artifacts.
None of these canonical files is changed by this proposal.

[FairSwap (authors' paper)](https://eprint.iacr.org/2018/740.pdf) describes
smart-contract-mediated fair exchange with the contract acting as an external
judge. Its abstract was available through search; the full PDF fetch failed.
[Proxy re-encryption fair trade (authors' abstract)](https://arxiv.org/abs/2306.01299)
proposes repeatable encrypted sales and an arbitration protocol. These are
research leads, not evidence that either scheme is implemented or that our
no-human-dispute design is secure. Neither establishes that a plain decryption
callback is atomic settlement. No Telegraph key/payment atomicity is claimed.

## Proposed architecture

Separate the Exchange settlement ledger, an external release service, recipient
client, and external artifact storage. Seller/provider admission can remain
permissionless while a trade names the release service and its trust terms.
Permissionless entry alone does not decentralize release authority.

The seller encrypts a canonical project package as ciphertext C under content
key K. Its plaintext commitment must correspond to the exact KEP version under
an explicit canonicalization rule. The seller creates recipient envelope E,
wrapping K for the buyer's bound encryption key and binding version, epoch and
identity. Neither K nor a usable E reaches the buyer before commitment.

The external release service durably stages E confidentially. It possesses
recipient-encrypted material, not the buyer's private key or plaintext K. The
buyer already downloads and hashes C before authorizing unlock, avoiding reliance
on a URL as proof of delivery. Storage credentials and shared download caches
must never expose E early. The service must retain E for recovery after commit.

A required verification relation binds C, the committed package/version, K and E:
C authenticates and decrypts under K to bytes matching the version commitment;
E wraps that same K for the pinned buyer binding with the exact context. A digest
of E or H(K) alone proves none of these relationships. A zero-knowledge/verifiable
encryption construction could supply this evidence without exposing K, but its
scheme, proof circuit, encryption compatibility and cost are unresolved. Merely
calling this input a proof is not an implementation. A mock verifier may validate
fixtures for a prototype only; it cannot enable real-money settlement.

The release service attests durable custody of this exact E and its release
policy. This is a trust assertion about availability and early disclosure, not a
cryptographic guarantee. A future threshold service would require its own
corruption threshold, recovery and liveness specification; multiplying servers
alone does not establish those properties.

## Buyer and seller journey

1. Seller lists exact version, policy, ciphertext commitment, price and terms.
   A seller must already have grant authority under that policy.
2. Buyer selects the listing and funds escrow. The order pins identities, price,
   settlement domain, encryption-key binding, deadline and release service.
3. Buyer downloads C and verifies its digest. Seller stages E with the release
   service; the required content/envelope proof and durable-custody evidence are
   checked. Invalid or absent evidence leaves the order uncommitted.
4. Buyer presses Unlock project (or an agent calls the same API). The client
   signs conditional unlock authorization for this exact order. This is consent
   to settlement, not a retrospective KEP decryption acknowledgement.
5. Before the deadline, the ledger atomically consumes that authorization,
   verifies current grant authority/key binding, reserves the validated delivery,
   records the KEP co-owner addition and creates an irrevocable seller payment
   entitlement. Existing co-owners remain. All of these must share one atomic
   settlement domain; separate API calls are insufficient.
6. Only after the selected finality condition, the release service makes E
   recoverable by the buyer and records delivery availability. The seller's
   entitlement is paid exactly once. Precise payout mechanics are a later binding;
   the buyer cannot reclaim committed funds because its client stays silent.
7. The client unwraps E, decrypts C, checks authenticity and content commitment,
   and automatically submits KEP-D12 evidence. A failed client/network can resume
   recovery and retry this receipt without purchasing or granting again.

The product shows “Preparing”, “Ready to unlock”, “Unlocking”, then “Available”.
After commitment, interruption shows “Delivery recovery pending”; it must not
show “Cancelled” or promise a refund. A successful ledger commit is not proof
that the buyer's machine has decrypted anything.

## State and deadline rules

| State | Permitted successor | Meaning |
| --- | --- | --- |
| Funded | Ready, Cancelled | Funds held; buyer has no release-service-delivered E or new grant |
| Ready | Committed, Cancelled | Evidence ready; no usable E released |
| Committed | DeliveryAvailable | Grant and payment entitlement final; recovery required |
| DeliveryAvailable | remains terminal commercially | Buyer can fetch E; KEP receipt tracked separately |
| Cancelled | terminal | No new grant or E release; refund entitlement selected |

The authoritative ledger accepts commit only while its time is strictly before
the deadline. At or after the deadline, uncommitted orders are eligible for a
permissionless expiry transaction; wall-clock passage alone does not execute a
blockchain transaction. Commit and expiry serialize against the same order state.
Refund claim and seller claim are mutually exclusive and independently retryable.
An HTTP timeout does not determine order outcome: read durable state first.

The service releases nothing on a submitted transaction, simulation, mempool
observation, reverted transaction or insufficiently final confirmation. Publishing
a decryptable envelope or unlocking secret in a public transaction payload can
leak it even if that transaction fails. Encrypting it solely to the buyer does
not solve this: the buyer is exactly the party who can read it before inclusion.
A plain hashlock or a single transaction label is therefore not sufficient.

## Guarantees, assumptions and limits

Under an honest, durable release service, sound verification, uncompromised keys,
and the selected ledger finality assumptions: an uncommitted expired order can
cancel; the release service cannot deliver usable E to a buyer who then cancels
that same committed order; committed delivery is recoverable without seller or
buyer acknowledgement cooperation. Ledger transfer/grant atomicity does not
make off-chain delivery simultaneous or unconditional.

Service collusion can leak E before commitment. Permanent loss or withholding
of staged E after commitment can strand a paid buyer. The proposed design does
not cryptographically eliminate these service failures. Backup/recovery and the
trust decision are required before use with real funds. A proof of key correctness
does not prove durable custody. A refund after secret leakage cannot erase access.

The seller or an existing co-owner already knows the project and can disclose it
out of band. The scope is protocol-mediated delivery and correct settlement,
not preventing all redistribution or proving that a buyer never knew the content.
Correct decryption verifies the committed package, not quality, build success,
legal rights, novelty or correspondence to vague marketing claims.

## Alch, DomainSpec and KEP integration

| Component | Proposed responsibility |
| --- | --- |
| Exchange | Offer/order terms, escrow state, deadline, evidence policy, settlement and recovery status |
| KEP | Exact version, policy, identity/key binding, preserved co-owner set, envelope and separate decryption receipt |
| Alch | Public operations and orchestration contracts expressing the selected state transitions |
| DomainSpec | Models and validation/compiler bindings for those contracts and invariants |
| Native cryptography/release/ledger implementations | Proof verification, durable confidential staging, finality observation, atomic ledger effects and delivery |

Candidate API operations: create/fund order, stage delivery evidence, authorize
unlock, commit settlement, recover delivery, record KEP receipt, expire order and
claim entitled funds. Reads return authoritative state and operation IDs. Envelope
retrieval requires recipient authorization; URLs must not contain secrets.
Every signed operation binds network/ledger, protocol version, order ID, listing
and terms digest, buyer/seller identities, version/policy/epoch, ciphertext and
envelope commitments, recipient binding, amount/asset, deadline and replay nonce.
Identity, wallet, tenant and caller principal remain distinct bindings.

Do not claim DomainSpec currently expresses ledger finality, zero-knowledge
verification or distributed atomic commit without auditing the exact selected
profile and compiler. These are construction requirements, not proven features.
A saga that grants first and refunds later cannot undo disclosed knowledge.
If KEP grant and payment cannot share an atomic domain, stop at the integration
boundary and design a reviewed cross-domain protocol before enabling paid unlock.

## Review and future construction frontier

This document records the selected product behavior and candidate architecture only. It does not admit an
execution plan. Following a selected product contract, a separately routed plan
should carry the D65 definition → capability → business ontology → DomainSpec
binding → implementation → test → product review chain.

The useful first prototype is a no-money state model and mock release service,
with an explicit fixture verifier. Its checks must cover modified-client receipt
withholding, commit/expiry races, duplicate requests, wrong content/envelope/key
binding, concurrent grants, service restart before/after commitment, missing
ciphertext, finality/reorg handling, early-envelope exposure, failed payout and
recipient recovery without seller cooperation. No tests were run for this design;
these are proposed acceptance cases, not security evidence.

Operational work belongs to the Exchange operator, crypto reviewer and KEP owner:
select custody/trust, proof scheme, ledger and finality, durable release recovery,
asset and deployment. Those block real paid settlement; they need not block a
clearly labelled mock state-model prototype after its own construction gate.

## Open Questions

1. Product behavior is resolved: the user accepted Unlock as purchase completion,
   precommit deadline cancellation/refund, and postcommit delivery recovery. Exact
   proof of readiness and durable commitment semantics still need implementation
   bindings; no UI event alone establishes settlement.
2. Product owner: accept an explicitly trusted external release service initially,
   or require a reviewed decentralized fair-exchange construction first?
3. Product/KEP owners: exact package canonicalization, grant pre-state concurrency,
   identity bindings and refund execution/fee details. Canonical KEP remains unchanged.
4. Crypto/implementation owners: concrete sound proof/envelope scheme, performance,
   service key protection, permanent-failure handling and independent review.
5. Settlement owner: one atomic domain for KEP grant and payment entitlement,
   asset, fees, deadline clock, finality/reorg assumptions and payout mechanics.
6. Storage/release owner: retention period and verifiable recovery requirements.

Other product questions remain owned by [the intake](INTAKE.md#open-questions).
