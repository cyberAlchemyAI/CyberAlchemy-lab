# Solana Co-Ownership Realization Definitions

Status: candidate capability-local source
Owner: Knowledge Exchange Protocol product owner
Candidate set: `KEP-SOL-DEFINITION-SET-001`
Predecessor authority: `KEP-D1` through `KEP-D12` at exact digest `e67deba09ec6df02a4a8542fbf8fbbcb68d27ca87839c5fffe2c1db708df7701`

## Authority Rule

This file proposes Solana-specific realization meanings for the Knowledge
Exchange Protocol. The terms are candidate-only until the product owner accepts
one exact digest. They refine the admitted `KEP-D*` business meanings but do not
replace or reinterpret them.

The existing admitted definition source remains immutable. A Solana public key
does not become a Knowledge Identity, a program account does not become the
Knowledge Artifact, and an on-chain membership record does not establish legal
title. Downstream Product Capability, ontology, DomainSpec, and implementation
work may reference this candidate set only with its exact digest and candidate
posture until a separate admission decision exists.

## KEP-SOL-D1: Solana Signing-Key Binding

Status: candidate
Term: Solana signing-key binding
Aliases: Solana signer binding, knowledge-identity signer binding

### Normative Definition

A Solana Signing-Key Binding is a versioned, scope-bounded assertion that one
Solana public key may authorize named protocol operations for one Knowledge
Identity during a declared validity interval. The binding represents an
authorization relationship; the public key is not the Knowledge Identity.

### Formal Model

Represent a binding as
`(knowledge_identity_id, solana_public_key, operation_scope, valid_from_slot,
valid_until_slot?, binding_version, status)`. A protocol operation at slot `s`
may rely on it only when the requested operation is in `operation_scope`,
`valid_from_slot <= s`, `valid_until_slot` is absent or `s <= valid_until_slot`,
and `status = active` for the exact `binding_version`.

### Operational Interpretation

Resolve the grantor's signer through the current binding before accepting a
co-ownership grant. Bind the instruction to the Knowledge Identity and binding
version so key rotation, expiry, or revocation fails closed instead of silently
changing who acted.

### Plain-Language Intuition

It is the protocol's dated permission slip connecting an identity to the
Solana key currently allowed to sign a particular action.

### Domain-Context Voice

For the first Solana proof, A and B remain Knowledge Identities. A's transaction
signature proves control of an authorized Solana key; it does not collapse A
into a wallet address. B's encryption-key binding remains separate from B's
Solana signing-key binding.

### Boundary

A Solana Signing-Key Binding is not a Knowledge Identity, wallet, private key,
Identity Encryption-Key Binding, owner membership, legal identity proof,
permanent authority, or permission to perform operations outside its scope.

### Primary Consumers

- candidate Solana Product Capability
- candidate Solana business ontology
- future DomainSpec v2 authorization nodes

## KEP-SOL-D2: Solana Knowledge-Artifact State Aggregate

Status: candidate
Term: Solana knowledge-artifact state aggregate
Aliases: artifact state aggregate, Solana artifact state

### Normative Definition

A Solana Knowledge-Artifact State Aggregate is the explicitly bounded set of
program-controlled Solana accounts that together represent the protocol state
for one exact Knowledge Artifact Version. It binds that version, its
Propagation Policy, state revision, Encryption Epoch, membership namespace,
ciphertext commitment, and program realization without storing the knowledge
artifact, plaintext, content key, or recipient private keys.

### Formal Model

For artifact version `v`, define aggregate `S(v)` as the closed account set
selected by the admitted address-derivation rules. Its root state commits to
`(artifact_version_id, propagation_policy_id, revision, encryption_epoch,
membership_namespace, ciphertext_digest, program_realization_id)`. Every child
record used by a transition must prove membership in `S(v)` under those rules.

### Operational Interpretation

Treat the state as an account graph rather than assuming one indefinitely
growing account. Require every instruction to identify the exact version and
pre-state revision and reject accounts derived for a different artifact,
program, policy, or namespace.

### Plain-Language Intuition

It is the on-chain ledger for one exact knowledge edition, not the knowledge
itself and not necessarily one giant account.

### Domain-Context Voice

The first proof may use a small root plus owner and envelope records. This shape
keeps `{A, B}` easy to prove while leaving later membership growth possible
without redefining the artifact as a fixed-size account.

### Boundary

A Solana Knowledge-Artifact State Aggregate is not a Knowledge Artifact,
Knowledge Artifact Version, ciphertext store, content key, wallet, token, NFT,
license, legal registry, or guarantee that external encrypted bytes remain
available.

### Primary Consumers

- candidate Solana Product Capability
- candidate Solana business ontology
- future DomainSpec v2 state and account nodes

## KEP-SOL-D3: Solana Co-Owner Membership Record

Status: candidate
Term: Solana co-owner membership record
Aliases: co-owner record, owner-membership account

### Normative Definition

A Solana Co-Owner Membership Record is a program-controlled, deterministically
addressed record asserting that one Knowledge Identity is a member of the
Knowledge Co-Ownership set for one exact Knowledge Artifact Version under one
state aggregate and Propagation Policy.

### Formal Model

For program realization `p`, artifact version `v`, and Knowledge Identity `i`,
the record address is derived under an admitted domain-separated scheme such as
`address(p, "coowner", v, i)`. A valid post-grant state from owner set `O` to
`O'` satisfies `O' = O union {recipient}` and preserves every pre-existing
membership record byte-for-byte except fields explicitly allowed by the
admitted revision protocol.

### Operational Interpretation

Use one identity-bound record per membership or another admitted equivalent
that proves the same set semantics. Creating B's record must not close, rewrite,
or invalidate A's record.

### Plain-Language Intuition

It is the on-chain membership card saying this identity belongs to the owner
set for this exact artifact version.

### Domain-Context Voice

The first proof starts with A's valid record and ends with valid records for A
and B. The observable claim is owner-set expansion, not a transfer from A to B.

### Boundary

A Solana Co-Owner Membership Record is not exclusive ownership, legal title,
copyright, custody, a token balance, successful decryption, permission to
publish, a license, or authority over the underlying definitions.

### Primary Consumers

- candidate Solana Product Capability
- candidate Solana business ontology
- future DomainSpec v2 membership nodes and invariants

## KEP-SOL-D4: Solana Recipient-Envelope Commitment Record

Status: candidate
Term: Solana recipient-envelope commitment record
Aliases: envelope commitment record, recipient envelope account

### Normative Definition

A Solana Recipient-Envelope Commitment Record is a program-controlled record
that binds one Recipient Key Envelope commitment to one Knowledge Identity,
Knowledge Artifact Version, Encryption Epoch, and exact Identity
Encryption-Key Binding without placing the plaintext content key, envelope
plaintext, or recipient private key on chain.

### Formal Model

The record commits to
`(recipient_identity_id, artifact_version_id, encryption_epoch,
encryption_key_binding_id, envelope_digest, envelope_locator?, record_version)`.
It is valid only when all identifiers match the state aggregate selected by the
grant and `envelope_digest` commits to the exact externally delivered envelope
bytes.

### Operational Interpretation

Create or select B's envelope commitment in the same atomic grant transition as
B's membership record. Reject a digest or binding prepared for another
identity, artifact version, epoch, or key.

### Plain-Language Intuition

It is the on-chain fingerprint for B's sealed copy of the content key, not the
secret key itself.

### Domain-Context Voice

The first Solana proof can prove that B's membership and B's exact envelope
commitment were recorded together while the encrypted envelope bytes remain in
the separately governed durable-storage layer.

### Boundary

A Solana Recipient-Envelope Commitment Record is not a Recipient Key Envelope
itself, content key, private key, ciphertext custody, availability proof,
decryption acknowledgement, owner membership by itself, or public secret.

### Primary Consumers

- candidate Solana Product Capability
- candidate Solana business ontology
- future DomainSpec v2 envelope commitment nodes

## KEP-SOL-D5: Solana Co-Ownership Grant Instruction

Status: candidate
Term: Solana co-ownership grant instruction
Aliases: Solana owner-set expansion instruction, grant instruction

### Normative Definition

A Solana Co-Ownership Grant Instruction is the program instruction that
realizes one Co-Ownership Grant by consuming an exact artifact pre-state,
authorized grantor signing-key binding, recipient Knowledge Identity,
recipient encryption-key binding, recipient-envelope commitment, Propagation
Policy, and unique operation identity, then requesting the atomic post-state
defined by `KEP-SOL-D6`.

### Formal Model

The minimum logical input is
`(program_realization_id, artifact_version_id, expected_revision,
grantor_identity_id, grantor_signing_binding_version, recipient_identity_id,
recipient_encryption_binding_id, envelope_digest, propagation_policy_id,
operation_id)`. Acceptance requires every referenced identity, binding,
account, and policy to resolve to that same exact transition domain.

### Operational Interpretation

Validate authority, address derivations, binding currency, policy permission,
pre-state revision, recipient non-membership, and replay domain before mutation.
Return one explicit success or typed failure without partially applying state.

### Plain-Language Intuition

It is the exact on-chain request asking the program to add B beside A with B's
sealed-key fingerprint attached.

### Domain-Context Voice

The first instruction has no knowledge price and no seller-payment branch. It
proves only the Solana realization of the already admitted no-payment
Co-Ownership Grant meaning.

### Boundary

A Solana Co-Ownership Grant Instruction is not a Co-Ownership Grant merely
because it was submitted, a payment instruction, token transfer, license,
decryption proof, transaction-finality proof, deployment authorization, or
permission to bypass the admitted Propagation Policy.

### Primary Consumers

- candidate Solana Product Capability
- candidate Solana business ontology
- future DomainSpec v2 instruction and error nodes

## KEP-SOL-D6: Solana Co-Ownership Grant Atomicity

Status: candidate
Term: Solana co-ownership grant atomicity
Aliases: grant atomicity invariant, atomic owner expansion

### Normative Definition

Solana Co-Ownership Grant Atomicity is the invariant that a successful Solana
Co-Ownership Grant Instruction commits the recipient membership, matching
recipient-envelope commitment, state revision, and replay-consumption marker as
one state transition, while any failed instruction commits none of them and
preserves every pre-existing owner membership.

### Formal Model

For pre-state `S`, recipient `b`, and operation `o`, evaluation yields either
`Success(S')` where `owners(S') = owners(S) union {b}`, A and all other prior
owners remain members, `envelope(S', b)` matches the requested commitment,
`revision(S') = revision(S) + 1`, and `consumed(S', o) = true`; or `Failure(S)`
with no protocol-state mutation.

### Operational Interpretation

Place every writable account in one instruction boundary and order validation
before mutation. Tests must compare full protected pre-state after every
rejected authorization, stale revision, invalid binding, malformed account,
and replay attempt.

### Plain-Language Intuition

Either B is added completely and safely, or nothing changes at all.

### Domain-Context Voice

The core test observes `{A}` becoming `{A, B}` together with B's envelope
commitment and replay marker. A failure may charge network fees at the Solana
transaction layer, but it must not partially change protocol ownership state.

### Boundary

Solana Co-Ownership Grant Atomicity is not cross-transaction atomicity,
off-chain storage atomicity, guaranteed transaction inclusion, zero network
fees, decryption success, payment settlement, or rollback of effects outside
the program's declared account set.

### Primary Consumers

- candidate Solana Product Capability
- candidate Solana business ontology
- future DomainSpec v2 invariants and conformance tests

## KEP-SOL-D7: Solana Grant Replay Domain

Status: candidate
Term: Solana grant replay domain
Aliases: grant replay-protection domain, operation-consumption domain

### Normative Definition

A Solana Grant Replay Domain is the exact scope within which a Co-Ownership
Grant operation identity may be consumed at most once. It binds the operation
identity to the program realization, artifact version, expected pre-state
revision, grantor identity, recipient identity, and instruction kind.

### Formal Model

Define `R = H(domain_separator, program_realization_id, artifact_version_id,
expected_revision, grantor_identity_id, recipient_identity_id,
instruction_kind, operation_id)`. A successful transition records `R` as
consumed. Any later transition presenting the same `R` fails before protocol
state mutation.

### Operational Interpretation

Use a deterministic consumption record or an admitted equivalent. Domain
separation must prevent a nonce valid for another program, artifact, revision,
recipient, or instruction kind from being treated as the same operation.

### Plain-Language Intuition

It gives each exact grant request a one-use ticket that cannot be replayed in a
different context.

### Domain-Context Voice

The first proof submits the accepted A-to-B grant once, then demonstrates that
resubmitting its replay identity cannot add B again or mutate the revision.

### Boundary

A Solana Grant Replay Domain is not transaction-signature uniqueness, global
nonce coordination, duplicate-owner policy by itself, protection against every
cross-program attack, or evidence that a rejected transaction paid no fee.

### Primary Consumers

- candidate Solana Product Capability
- candidate Solana business ontology
- future DomainSpec v2 replay records and negative tests

## KEP-SOL-D8: Solana Co-Ownership Evidence

Status: candidate
Term: Solana co-ownership evidence
Aliases: Solana grant evidence, owner-expansion transaction evidence

### Normative Definition

Solana Co-Ownership Evidence is a bounded evidence bundle showing that one
exact Solana Program Realization evaluated a named grant instruction and that
the observed post-state satisfies the admitted owner-set, envelope, revision,
and replay invariants at a declared execution and commitment level.

### Formal Model

The evidence bundle identifies
`(program_realization_id, execution_environment, transaction_or_test_id,
instruction_input_digest, pre_state_digest, post_state_digest,
asserted_invariants, commitment_level, validator_or_harness_identity,
result)`. A claim may not exceed the declared environment or commitment level.

### Operational Interpretation

For a local proof, capture deterministic `solana-program-test` inputs, logs,
account post-state, and negative-test results. For a cluster proof, separately
name the cluster, program deployment, transaction signature, slot, and
commitment level. Never label local simulation as mainnet evidence.

### Plain-Language Intuition

It is the receipt showing which exact program ran, what it received, and how
the owner state changed—with the environment written on the receipt.

### Domain-Context Voice

The first acceptable evidence target is a repeatable local program-test run
showing A preserved, B added, B's envelope commitment bound, and invalid or
replayed grants rejected. Deployment evidence is a later gate.

### Boundary

Solana Co-Ownership Evidence is not ontology admission, implementation
acceptance by itself, cryptographic security proof, mainnet evidence unless it
names mainnet state, decryption proof, legal ownership proof, payment evidence,
publication, or deployment authorization.

### Primary Consumers

- candidate Solana Product Capability
- candidate Solana business ontology
- future conformance and runtime-evidence receipts

## KEP-SOL-D9: No-Price Solana Co-Ownership Grant

Status: candidate
Term: no-price Solana co-ownership grant
Aliases: zero-price protocol grant, non-sale Solana grant

### Normative Definition

A No-Price Solana Co-Ownership Grant is a Solana Co-Ownership Grant Instruction
whose protocol outcome does not require or transfer economic consideration from
the recipient to the originator, grantor, seller, royalty beneficiary, or
protocol treasury. Network transaction fees, account rent, or refundable rent
reserves are infrastructure costs and must remain separately identified rather
than being represented as a knowledge price.

### Formal Model

For the declared economic recipient set `E = {originator, grantor, seller,
royalty_beneficiary, protocol_treasury}`, the grant invariant is
`consideration_delta(e) = 0` for every `e in E`. Any fee-payer or account-funding
delta must be classified as `network_fee`, `rent`, or `refundable_reserve` and
must not satisfy or imply a sale-price obligation.

### Operational Interpretation

Exclude price, escrow, royalty, seller payout, and treasury consideration
accounts from the first capability. Tests may fund accounts and pay validator
fees, but evidence must report those separately and must not call the
instruction economically free when infrastructure costs exist.

### Plain-Language Intuition

B does not buy the knowledge in this proof, even though somebody may still pay
the blockchain's operating costs.

### Domain-Context Voice

This is the bridge between the admitted no-payment business grant and its first
Solana realization. A later paid capability will add an exact SOL amount and an
atomic original-owner payout without rewriting this no-price definition.

### Boundary

A No-Price Solana Co-Ownership Grant is not a promise of zero transaction
fees, zero account rent, free storage, a gift under any legal system, a sale,
barter, royalty settlement, token transfer, or authorization for a later paid
grant.

### Primary Consumers

- candidate Solana Product Capability
- candidate Solana business ontology
- future DomainSpec v2 economic exclusions and tests

## KEP-SOL-D10: Solana Program Realization Identity

Status: candidate
Term: Solana program realization identity
Aliases: exact Solana program realization, program realization binding

### Normative Definition

A Solana Program Realization Identity is the exact identity of one executable
Solana realization of an admitted system ontology, including its source and
build commitments, program identifier, loader and upgrade posture, execution
environment, and deployment or local-fixture identity needed to distinguish it
from every other build or program state.

### Formal Model

Represent the identity as
`(system_ontology_digest, implementation_binding_digest, source_digest,
build_artifact_digest, program_id, loader_kind, upgrade_authority_posture,
execution_environment, deployment_slot_or_fixture_digest)`. Missing or changed
fields produce a different or not-evaluable realization identity.

### Operational Interpretation

Bind conformance evidence to this complete identity. Local program-test may use
a deterministic fixture identity; deployed evidence must use the actual
program ID, loader state, cluster, and deployment slot. Upgradeable and
immutable deployments must not be treated as equivalent.

### Plain-Language Intuition

It is the full fingerprint for exactly which Solana program build ran and
where—not merely its crate name.

### Domain-Context Voice

The first Solana vertical will bind a Rust program-test fixture to the admitted
Solana system ontology. Mainnet or devnet identity remains absent until a
separate deployment decision and evidence bundle exist.

### Boundary

A Solana Program Realization Identity is not a Product Capability, ontology,
program source alone, crate version, program ID alone, deployment approval,
security audit, immutable-code guarantee, mainnet compatibility claim, or
authority to submit transactions.

### Primary Consumers

- candidate Solana Product Capability
- candidate Solana business ontology
- future implementation binding and conformance evidence

## Candidate Claim Ceiling

This set proposes vocabulary only. It does not adopt a Product Capability,
admit an ontology or DomainSpec profile, authorize implementation, establish a
Solana program identity, prove runtime behavior, transfer SOL, grant legal
rights, publish, deploy, or cause any external effect.
