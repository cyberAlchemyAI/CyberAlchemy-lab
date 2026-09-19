# Solana Co-Ownership Completion Definitions

Status: candidate capability-local successor source
Owner: Knowledge Exchange Protocol product owner
Candidate set: `KEP-SOL-DEFINITION-SET-002`
Accepted predecessor: `KEP-SOL-D1` through `KEP-SOL-D10` at exact digest `4bd06cf89baf081cbd404c1bad55378c47a14cdeb2029b0cf41d4ad49e133365`
Accepted storage dependency: `KEP-DST-D1` through `KEP-DST-D15` at exact digest `4edb03caab66af2eedf79ad31a47d09b19aec0d975deccfd217195046258c4df`

## Authority Rule

This file proposes only the additional meanings required to complete the first
encrypted, durable, no-price Solana co-ownership vertical. It does not alter or
replace the accepted `KEP-SOL-D1` through `KEP-SOL-D10` bytes. The predecessor
and this extension form a successor definition set only if the product owner
later accepts this extension's exact digest.

Generic storage meaning remains owned by the accepted `KEP-DST-D*` definitions.
This consumer may specialize and instantiate that contract, but it may not
redefine storage, select a provider, or treat provider behavior as authority.
Cryptographic algorithms, libraries, providers, endpoints, credentials, wallet
keys, and deployment values remain implementation or later policy bindings.

## KEP-SOL-D11: Solana Co-Ownership Cryptographic Profile

Status: candidate
Term: Solana co-ownership cryptographic profile
Aliases: protocol cryptographic profile, encrypted-grant cryptographic suite

### Normative Definition

A Solana Co-Ownership Cryptographic Profile is an immutable, versioned semantic
contract that identifies the complete algorithm, parameter, encoding, domain-
separation, nonce, associated-data, and key-compatibility rules used to encrypt
one Knowledge Artifact Version and create or verify its Recipient Key Envelopes,
without collapsing encryption keys into Solana signing keys.

### Formal Model

Represent profile `c` as `(profile_id, profile_version, content_encryption,
recipient_key_agreement_or_wrapping, kdf, digest_suite, serialization,
domain_separators, nonce_rule, associated_data_schema, key_length_rules,
compatibility_status)`. A ciphertext or envelope is profile-valid only when all
named components and contextual bindings match exactly; an absent or ambiguous
component makes cryptographic use `not_evaluable`.

### Operational Interpretation

Bind every ciphertext, envelope, acknowledgement, reissue, and decryption
observation to one exact profile version. Reject silent algorithm fallback,
nonce reuse where uniqueness is required, unbound contextual data, ambiguous
serialization, and mixing a recipient encryption-key binding with a Solana
signing-key binding.

### Plain-Language Intuition

It is the complete recipe for sealing and opening the knowledge, including all
the small choices that must match for the recipe to be safe and repeatable.

### Domain-Context Voice

The first Devnet vertical will choose one concrete profile in a later Product
Capability or implementation binding. This definition supplies the required
shape now without pretending that naming an algorithm proves secure use.

### Boundary

A Solana Co-Ownership Cryptographic Profile is not a private key, content key,
Solana wallet, implementation library, security audit, proof of confidentiality,
successful encryption, key custody policy, credential store, or authorization
to select a production cryptographic suite.

### Primary Consumers

- successor no-price Solana Product Capability
- successor Solana business ontology and DomainSpec source
- cryptographic implementation binding and conformance evidence

## KEP-SOL-D12: Solana Co-Ownership Durable Storage Instantiation

Status: candidate
Term: Solana co-ownership durable storage instantiation
Aliases: Solana storage consumer binding, encrypted-grant storage instantiation

### Normative Definition

A Solana Co-Ownership Durable Storage Instantiation is the immutable consumer
binding that specializes `KEP-DST-D15` for the no-price Solana capability by
naming its encrypted-artifact and recipient-envelope object kinds, commitment
rule, pre-grant readiness rule, failure effect, three-layer durability posture,
policy-value bindings, confidentiality boundary, and infrastructure-cost class,
without selecting storage machinery.

### Formal Model

Represent instantiation `s` as `(instantiation_id, consumer_capability_id,
storage_capability_version, reused_definition_ids,
object_kind_bindings={encrypted_artifact, recipient_envelope},
commitment_binding_rule, readiness_rule, failure_effect_rule,
three_layer_posture={live_registry, append_only_journal, immutable_archive},
storage_policy_value_binding, confidentiality_rule,
infrastructure_cost_classification, instantiation_version, status)`. Readiness
requires every declared storage obligation and a Verified Retrieval for each
object required by the grant; an unmet obligation blocks the Solana mutation.

### Operational Interpretation

Prepare and verify the ciphertext and B's envelope before submitting the grant.
Require evidence for the live registry, append-only journal, and immutable
archive obligations selected by the policy. If preparation or verification
fails, emit a typed storage failure and do not submit or advance the grant.

### Plain-Language Intuition

It is the filled-in storage form for this Solana grant: what must be stored,
checked, backed up, and proven before the blockchain step may begin.

### Domain-Context Voice

The first realization may use PostgreSQL for its SQL adapter, but PostgreSQL is
not part of this definition. Another SQL realization may conform when a later
implementation binding proves the same semantic obligations.

### Boundary

A Solana Co-Ownership Durable Storage Instantiation is not a provider, SQL
dialect, database schema, endpoint, credential, backup execution, availability
proof, runtime configuration, deployment, or claim of cross-system atomicity.

### Primary Consumers

- successor no-price Solana Product Capability
- storage-aware Solana DomainSpec source
- Durable Storage and Solana implementation bindings

## KEP-SOL-D13: Solana Key-Reissue Request

Status: candidate
Term: Solana key-reissue request
Aliases: recipient reissue request instruction, B key-reissue request

### Normative Definition

A Solana Key-Reissue Request is a recipient-authorized, replay-safe request for
replacement Recipient Key Envelope material for the same Knowledge Identity,
Knowledge Artifact Version, Encryption Epoch, and owner membership after a new
Identity Encryption-Key Binding becomes current. The request records intent
only and does not change active access material.

### Formal Model

Represent request `q` as `(request_id, artifact_version_id, recipient_identity,
owner_membership_ref, encryption_epoch_id, active_envelope_commitment,
replacement_encryption_key_binding_ref, nonce, valid_until_slot?,
recipient_signing_binding_ref, recipient_authorization, status)`. Creation is
valid only when the recipient controls an authorized signing binding, remains a
co-owner, names the exact current state, and the replay identity is fresh.

### Operational Interpretation

Allow B to request reissue without re-adding B or changing A. Reject a stale
state, inactive membership, invalid replacement key binding, expired request,
identity mismatch, or replay. Keep the request pending until separately
authorized fulfillment succeeds or an explicit terminal result is recorded.

### Plain-Language Intuition

It is B's signed request for a new sealed key, not the new sealed key itself.

### Domain-Context Voice

The first protocol lets B ask after losing a non-compromised key. Suspected
compromise remains an Encryption Epoch rotation, not ordinary reissue.

### Boundary

A Solana Key-Reissue Request is not fulfillment, a new envelope, ownership
creation, owner removal, identity recovery by itself, compromise recovery,
payment, acknowledgement, or proof that the replacement private key is safe.

### Primary Consumers

- successor reissue Product Capability behavior
- Solana reissue request account and instruction model
- negative and replay conformance tests

## KEP-SOL-D14: Solana Key-Reissue Fulfillment

Status: candidate
Term: Solana key-reissue fulfillment
Aliases: envelope reissue fulfillment instruction, authorized reissue commit

### Normative Definition

A Solana Key-Reissue Fulfillment is the propagation-policy-authorized,
replay-safe transition that consumes one valid Solana Key-Reissue Request and
atomically replaces only that recipient's active envelope commitment after the
replacement envelope has satisfied Reissue-Safe Envelope Replacement, while
preserving owner memberships, artifact version, Encryption Epoch, policy,
economic state, and every other recipient's envelope.

### Formal Model

For state `S`, request `q`, verified replacement `E1`, and authorization `a`,
`Fulfill(S,q,E1,a)=S'` exactly when `q` is pending and current, `a` satisfies the
bound Propagation Policy, `E1` matches the recipient, version, epoch, replacement
key binding, cryptographic profile, and durable-storage instantiation, and the
replay identity is fresh. Then only the recipient envelope commitment, envelope
revision, request status, state revision, and replay record may change.

### Operational Interpretation

Write and verify the replacement envelope first. Submit fulfillment with the
exact request and state revisions. On success, consume the request and update
the active commitment in one Solana transition; on failure, leave the old
commitment active and preserve the replacement as non-active stored material.

### Plain-Language Intuition

It is the authorized step that points B to the checked replacement envelope
without changing who owns the artifact or creating a new knowledge edition.

### Domain-Context Voice

B may ask, but the exact Propagation Policy decides who may fulfill. The first
test can bind that role to A without making A universally authoritative.

### Boundary

A Solana Key-Reissue Fulfillment is not a new Co-Ownership Grant, identity
recovery, compromise recovery, Encryption Epoch rotation, payment, owner-set
mutation, cross-system atomicity, deletion proof, or decryption acknowledgement.

### Primary Consumers

- successor no-price Solana Product Capability
- reissue state transition and account constraints
- storage/chain coordination tests

## KEP-SOL-D15: Solana Finalized Delivery Activation

Status: candidate
Term: Solana finalized delivery activation
Aliases: finalized grant activation boundary, chain-storage delivery activation

### Normative Definition

Solana Finalized Delivery Activation is the confirmation-bounded rule that
prepared durable ciphertext or envelope material becomes protocol-active for a
recipient only after an exact Solana grant or reissue transaction reaches the
configured activation commitment and the finalized on-chain commitment matches
the verified stored bytes and expected state revision.

### Formal Model

For prepared material `m`, transaction `t`, expected post-state `S'`, activation
commitment `k`, and observed chain state `C`, define `active(m,t)` exactly when
`storage_ready(m)`, `commitment_status(t) >= k`, `C.state = S'`, and
`C.material_commitment = digest(m)` under the bound cryptographic profile.
Otherwise the material remains prepared, rejected, expired, or reconciliation-
required, but not active.

### Operational Interpretation

Persist first, submit second, then observe the configured commitment and fetch
the program-owned state independently. Serve B only after both sides match.
Record orphaned prepared material and ambiguous transaction outcomes for
reconciliation; never invent atomicity between Solana and external storage.

### Plain-Language Intuition

The sealed package may be ready on the shelf, but B gets the green light only
after the blockchain record is final enough and points to that exact package.

### Domain-Context Voice

The first Devnet trial is expected to select `finalized` as its activation
commitment. A different environment must declare its own exact policy rather
than silently weakening the boundary.

### Boundary

Solana Finalized Delivery Activation is not storage write success, transaction
submission, optimistic UI state, universal chain finality, cross-system atomic
commit, perpetual availability, decryption success, or deployment authority.

### Primary Consumers

- Rust client orchestration and reconciliation
- Devnet end-to-end trial
- grant and reissue evidence rules

## KEP-SOL-D16: Solana Devnet Protocol Trial

Status: candidate
Term: Solana Devnet protocol trial
Aliases: real-Devnet co-ownership trial, public test-cluster protocol run

### Normative Definition

A Solana Devnet Protocol Trial is an explicitly non-production experiment that
executes the bound Solana program and off-chain encrypted-delivery workflow
against the public Solana Devnet cluster using test identities and test SOL,
while preserving exact program, cluster, commitment, storage, cryptographic,
fixture, and observation boundaries.

### Formal Model

Represent trial `d` as `(trial_id, cluster_identity, genesis_hash,
rpc_endpoint_class, program_realization_id, cryptographic_profile_id,
storage_instantiation_id, storage_realization_id, fixture_digest,
test_identity_refs, activation_commitment, started_at, ended_at, result,
evidence_bundle_ref)`. Missing or changed identity fields create a distinct or
not-evaluable trial.

### Operational Interpretation

Use disposable non-repository key material, test SOL, an exact program build,
an exact encrypted fixture, and the complete positive and negative scenario.
Label resets, rate limits, RPC failures, and cluster observations honestly.

### Plain-Language Intuition

It is a real run on Solana's public developer network, but still a laboratory
trial rather than a production launch.

### Domain-Context Voice

This is the first acceptable external runtime target for `{A} -> {A,B}` plus
retrieval, decryption, replay rejection, and reissue. Mainnet remains separate.

### Boundary

A Solana Devnet Protocol Trial is not Mainnet evidence, production readiness,
security certification, economic validation, legal transfer, service-level
proof, deployment approval, or permission to use real customer keys or funds.

### Primary Consumers

- Devnet evidence runner
- conformance review
- later Mainnet-readiness planning

## KEP-SOL-D17: Solana End-to-End Protocol Evidence Bundle

Status: candidate
Term: Solana end-to-end protocol evidence bundle
Aliases: encrypted co-ownership trial evidence, Devnet grant evidence bundle

### Normative Definition

A Solana End-to-End Protocol Evidence Bundle is an immutable, environment-
bounded evidence aggregate that connects one exact D65 construction chain to
the cryptographic preparation, Durable Storage observations, Solana program
identity and transactions, pre/post account bytes, recipient decryption result,
reissue result, negative cases, and separately classified infrastructure costs
observed in one local or Devnet trial.

### Formal Model

Represent bundle `e` as `(definition_digests, product_capability_digest,
business_ontology_digest, domainspec_source_digest, system_ontology_digest,
implementation_binding_digest, program_realization_id,
cryptographic_profile_id, storage_instantiation_id, storage_evidence_ref,
trial_environment_id, transaction_signatures, slots, commitment_observations,
pre_post_account_digests, ciphertext_and_envelope_commitments,
plaintext_fixture_digest, decrypted_plaintext_digest, acknowledgement_ref?,
reissue_evidence_ref?, negative_case_results, network_cost_observations,
storage_cost_observations, result)`. Every success claim must resolve to exact
members of this tuple.

### Operational Interpretation

Capture the complete positive path and all required failures without secrets.
Require the source and decrypted plaintext digests to match, preserve raw
account and transaction evidence, and identify local versus Devnet runs. Report
missing dependent evidence as `not_evaluable`, never as an omitted success.

### Plain-Language Intuition

It is the receipt folder that ties the meaning, code, chain events, stored
packages, decrypted result, failures, and costs into one checkable trial.

### Domain-Context Voice

The first Devnet bundle should prove A remains an owner, B is added, B decrypts
the exact fixture, replay and wrong-signer cases fail, and B's reissue path works
under the declared storage and finalization rules.

### Boundary

A Solana End-to-End Protocol Evidence Bundle is not definition acceptance,
Product Capability adoption, ontology admission, implementation authority,
security audit, proof of long-term availability, production readiness, Mainnet
evidence, legal title, publication, release, or deployment authorization.

### Primary Consumers

- conformance reviewer
- protocol trial report
- successor planning and challenge routes

## Candidate Claim Ceiling

This extension proposes vocabulary and dispositions only. It does not accept
the successor definition set, revise the accepted predecessor, adopt a Product
Capability, instantiate Durable Storage with authority, admit an ontology or
DomainSpec source, authorize cryptographic choices or implementation, submit a
transaction, use credentials, publish, release, deploy, or cause any external
effect.
