# Exchange purchase and internal KEP delivery

Status: selected product meaning; purchase binding remains candidate architecture.
Not an admitted Definition Pack, implementation, or cryptographic security proof.
Owner: Exchange product owner. Consumers: Exchange design and later Alch/DomainSpec
construction. Decisions: [intake](INTAKE.md), [machine record](intake.json).
Prior design: [history](history/before-integrated-kep-correction/DECRYPTION-SETTLEMENT-DESIGN.md).

## Product structure

**CyberAlchemy Exchange is the product; KEP is its internal protocol.**
The user explicitly corrected the separate-project framing and required the
existing KEP model to remain unchanged. Exchange manages project delivery through
KEP rather than asking sellers to construct unrelated delivery envelopes.

The existing [KEP product model](../../../cyberalchemy-exchange/knowledge-exchange-protocol/README.md)
and [definitions](../../../cyberalchemy-exchange/knowledge-exchange-protocol/authority/definitions/DEFINITIONS.md)
own version identity, propagation policy, encryption epochs, identity/key
bindings, recipient envelopes, co-ownership grants, reissue and acknowledgements.
The [white paper](../../../cyberalchemy-exchange/knowledge-exchange-protocol/white-paper/v1/README.md)
already identifies Exchange as product and KEP as protocol.
Repository package boundaries do not make these separate user-facing products.

Keep existing KEP encryption and custody boundaries. In particular, do not infer
that Exchange servers receive plaintext or content keys from the fact that KEP
belongs to Exchange. KEP does not custody plaintext, content keys or the encrypted
artifact; recipient-specific envelopes and external ciphertext references retain
their existing meanings. Exchange is the selected trusted operator for holding
and releasing recipient-encrypted envelopes within the purchase workflow.

The earlier server-versus-client encryption question and separate seller-envelope
proof architecture were assistant-introduced scope, not selected requirements.
They are superseded. No new zero-knowledge scheme, threshold service or replacement
KEP cryptography is selected. Binding to the actual existing workflow comes first.

## Accepted purchase behavior

1. Buyer chooses an exact project version and funds escrow.
2. Exchange prepares access through its internal KEP workflow, retaining the
   existing version, policy, epoch, recipient and key bindings.
3. Buyer chooses **Unlock project**, in the UI or through the same API contract.
4. Successful durable purchase commitment establishes payment entitlement and
   the buyer's KEP co-ownership; Exchange releases access through KEP.
5. Buyer decrypts. The client records the KEP acknowledgement automatically;
   there is no separate acceptance button.
6. If delivery is interrupted after commitment, the buyer resumes retrieval.
   A missing client receipt does not cancel the purchase.

Before commitment, expiry cancels the trade and refunds the buyer. After
commitment, the purchase remains valid and access must be recoverable. A click,
submitted request or HTTP timeout alone does not establish committed state.
KEP acknowledgement remains recipient evidence under KEP-D12; local decryption
is not assumed remotely observable or inseparable from a later network message.
Successful builds/tests are not part of the default acceptance requirement.

## Responsibilities inside the product

| Part | Responsibility |
| --- | --- |
| Exchange market/order lifecycle | Offers, funding, deadline, purchase commitment, refund and payment entitlement |
| Internal KEP workflow | Exact version, policy, encryption/access bindings, co-owner addition, receipt and reissue semantics |
| Exchange trusted release operation | Withhold the recipient envelope before commitment; make delivery recoverable afterward |
| Alch | Express API operations and orchestration contracts for the selected lifecycle |
| DomainSpec | Model, validate and compile supported contracts and bindings |
| Native runtime dependencies | Realize cryptography, persistence, storage access and settlement effects with evidence |

These are responsibility boundaries within one product. They do not require
separate deployments or a separately operated KEP service. Existing identities,
wallets, signing keys, encryption keys and tenant principals retain their distinct
bindings.

## Candidate state and consistency requirements

| State | Successors | Required behavior |
| --- | --- | --- |
| Funded | Ready, Cancelled | Funds held; access not released by this purchase |
| Ready | Committed, Cancelled | Internal KEP preparation validated; envelope withheld |
| Committed | DeliveryAvailable | Payment entitlement and grant durable; delivery recovery required |
| DeliveryAvailable | Commercially terminal | Repeat retrieval permitted without a second purchase |
| Cancelled | Terminal | Refund entitlement; no purchase-triggered grant or envelope release |

Commit and expiry must serialize against one authoritative order state. Proposed
clock rule: commit strictly before the deadline; expire at or after it. Exact
clock and settlement execution are still unbound. Refund and seller entitlement
must be mutually exclusive and paid at most once. Retry uses the same operation
identity and reads durable state before deciding the outcome.

The exact order binds buyer/seller identities, price/asset, terms, version,
policy, epoch, ciphertext/envelope commitments, recipient key binding, deadline
and replay identity. Preserve existing co-owners. Missing acknowledgement cannot
silently erase a KEP membership. A pre-existing membership is not removed when a
new attempted purchase cancels.

Purchase commitment, grant and release authorization must have a demonstrated
consistency boundary. Calling internal components in sequence is not by itself
atomicity. If settlement uses an external ledger, specify finality and crash
recovery; do not expose a usable envelope in uncommitted/public transaction data.
Neither a failed transaction nor an API timeout can retract information already
disclosed. The design does not assume which ledger or compiler primitives exist.

## Correctness and trust

Exchange is trusted for correct withholding, release and durable recovery. It
must use the internal KEP workflow's actual creation and validation guarantees.
The seller-facing product should not require users to assemble arbitrary key
envelopes. Nonetheless, product membership or an official client alone does not
prove that malformed requests are impossible. Server-side checks, authorization,
version/key consistency and hostile-client behavior are implementation concerns
to inspect and test, not new product choices or assumed cryptographic guarantees.

The prior statement that simply using the same key makes a separate correctness
mechanism unnecessary was conditional on a controlled workflow. Whether the
current KEP implementation provides that control requires evidence. Record any
concrete missing guarantee after inspecting that workflow; do not invent a
replacement cryptographic architecture in advance.

Exchange failure or compromise can affect availability or leak access. This trust
choice does not prove the service reliable. Recovery storage, retention and access
controls need a tested implementation. Existing co-owners may disclose knowledge
outside Exchange; no purchase workflow can retract already decrypted knowledge.
Correct delivery is also not proof of project quality, legal rights or truth.

## Construction follow-through

Next technical work is a bounded inspection of the existing internal KEP workflow
and tests, followed by the exact purchase-lifecycle binding and gap report. No
runtime work or security tests were performed for this correction. JSON and local
links were checked; previous candidate decisions remain in history.

A later construction plan must follow D65: definitions, capability, business
ontology, DomainSpec binding, implementation, tests and product review. Current
KEP candidate runtime artifacts must not be presented as admitted or proven
merely because the product model is selected. A mock purchase lifecycle can be a
bounded prototype after its own gate; it cannot establish real payment security.

Proposed acceptance cases: correct unlock; precommit expiry/refund; duplicate
unlock; simultaneous commit/expiry; restart before/after commitment; incorrect
version/recipient/key binding; unauthorized or malformed direct API input;
concurrent co-owner additions; missing client receipt; interrupted retrieval;
failed payout recovery; no release from cancelled or non-final transactions.

## Open Questions

- Implementation owner: which exact existing KEP operations and checks realize
  project preparation, envelope creation and release? What demonstrated gaps, if
  any, prevent binding them to purchase commitment?
- Settlement owner: payment asset, ledger, atomicity/finality, deadline clock,
  refund/payout execution and fees.
- Exchange operator: envelope retention, backups, access controls and permanent
  failure recovery.
- Product owner: exact initial project-package scope and first-release distribution.

KEP's place inside Exchange and preservation of its current encryption model are
resolved. Other product questions are owned by [the intake](INTAKE.md#open-questions).
