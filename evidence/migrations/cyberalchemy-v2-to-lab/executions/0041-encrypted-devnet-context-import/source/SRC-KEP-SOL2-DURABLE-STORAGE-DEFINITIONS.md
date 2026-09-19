# Durable Knowledge Storage Definitions

Status: candidate capability-local source
Owner: Knowledge Exchange Protocol product owner
Candidate set: `KEP-DST-DEFINITION-SET-001`
Predecessor authority: `KEP-D1` through `KEP-D12` at exact digest `e67deba09ec6df02a4a8542fbf8fbbcb68d27ca87839c5fffe2c1db708df7701`

## Authority Rule

This file proposes provider-neutral durable-storage meanings for the Knowledge
Exchange Protocol. The definitions are candidates until the product owner
accepts one exact digest. They specialize the active `KEP-D*` meanings without
replacing them and do not select a storage provider, network, commercial plan,
credential model, retention period, availability target, or implementation.

A Knowledge Artifact is not a storage object. A content digest is not proof of
availability. A write receipt is not proof of durable retention. A locator is
not byte identity. Provider encryption is not a substitute for recipient-bound
encryption. Downstream capability, ontology, DomainSpec, and implementation
work must preserve these non-collapse boundaries.

Durable storage owns the generic storage contract. A consuming capability does
not redefine that contract: it creates one explicit Durable Storage Capability
Instantiation, specializes only the meanings that are narrower in its domain,
and supplies every required semantic policy value. A later implementation
binding separately supplies provider, adapter, environment, and credential
realization values. Consumer semantics and runtime realization must not be
collapsed into the storage definitions.

## KEP-DST-D1: Durable Knowledge Material Object

Status: candidate
Term: durable knowledge material object
Aliases: durable knowledge object, external encrypted object

### Normative Definition

A Durable Knowledge Material Object is an immutable sequence of externally
stored bytes that carries either encrypted Knowledge Artifact Version material
or one recipient-specific Recipient Key Envelope and is identified independently
from its storage provider and locator.

### Formal Model

Represent object `o` as `(object_kind, bytes, byte_length, digest_algorithm,
byte_digest)`, where `object_kind` is `encrypted-artifact` or
`recipient-envelope`, `byte_length = len(bytes)`, and `byte_digest` is computed
over the exact stored bytes under a versioned domain separator.

### Operational Interpretation

Store and retrieve exact immutable bytes. A change to any byte creates a new
object identity even when the object serves the same artifact, recipient, or
encryption epoch.

### Plain-Language Intuition

It is the sealed package kept outside the blockchain, identified by precisely
what is inside the package.

### Domain-Context Voice

The Knowledge Exchange Protocol uses durable objects for encrypted artifact
material and recipient-envelope material. Each consuming capability selects the
object kinds it needs through an explicit capability instantiation.

### Boundary

A Durable Knowledge Material Object is not a Knowledge Artifact, Knowledge
Artifact Version, plaintext, content key, owner membership, storage locator,
provider account, availability guarantee, or legal record.

### Primary Consumers

- candidate durable-storage Product Capability
- candidate durable-storage business ontology
- future DomainSpec v2 storage entities

## KEP-DST-D2: Content-Addressed Byte Identity

Status: candidate
Term: content-addressed byte identity
Aliases: storage object digest identity, immutable byte address

### Normative Definition

A Content-Addressed Byte Identity is the algorithm- and domain-qualified digest
that identifies one exact Durable Knowledge Material Object by its bytes. It
specializes `KEP-D8` for storage objects and remains stable across provider or
locator changes only when the bytes remain exact.

### Formal Model

For domain `d`, algorithm version `a`, and exact bytes `b`, define
`object_id = (d, a, H_a(d || b))`. Equality requires equality of all three
components; digest text without its algorithm and domain is ambiguous.

### Operational Interpretation

Recompute the qualified digest after every retrieval and before using the bytes
for decryption, acknowledgement, dependent protocol evidence, or reissue.

### Plain-Language Intuition

It is the package's tamper-evident fingerprint, including the rules used to
make that fingerprint.

### Domain-Context Voice

A consumer may bind a protocol commitment to this identity, but that commitment
does not itself store, retrieve, or prove the continued existence of the bytes.

### Boundary

A Content-Addressed Byte Identity is not a locator, provider key, mutable object
name, availability proof, authenticity proof beyond the governed binding,
plaintext commitment, or authorization to retrieve.

### Primary Consumers

- candidate storage integrity rules
- future DomainSpec v2 value objects
- retrieval verification

## KEP-DST-D3: Durable Storage Binding

Status: candidate
Term: durable storage binding
Aliases: provider-neutral storage binding, storage realization binding

### Normative Definition

A Durable Storage Binding is a versioned association between one protocol
storage namespace, one exact Durable Storage Policy, and one identified storage
realization capable of writing and retrieving Durable Knowledge Material
Objects without making provider identity part of object identity.

### Formal Model

Represent binding `s` as `(binding_id, namespace_id, policy_id,
realization_id, valid_from, valid_until?, binding_version, status)`. An operation
may use `s` only when it is active, current, policy-exact, and authorized for the
named namespace and operation.

### Operational Interpretation

Resolve provider adapters and credentials through the current binding. Rotate
or replace a provider by creating a successor binding while preserving object
byte identity and recording migration evidence.

### Plain-Language Intuition

It is the protocol's dated instruction saying which storage system currently
serves a namespace under which rules.

### Domain-Context Voice

The first implementation may use one provider-neutral adapter and local test
realization; neither becomes the permanent identity of the stored envelope or
artifact.

### Boundary

A Durable Storage Binding is not a storage provider, credential, object,
locator, availability guarantee, owner authorization, propagation policy, or
permission to silently migrate or delete bytes.

### Primary Consumers

- candidate durable-storage Product Capability
- future provider-neutral DomainSpec interface
- implementation binding

## KEP-DST-D4: Storage Locator

Status: candidate
Term: storage locator
Aliases: retrieval locator, external object locator

### Normative Definition

A Storage Locator is a provider- or scheme-specific resolution hint used to
attempt retrieval of one content-addressed object under one Durable Storage
Binding. It may change without changing object identity and is never trusted as
proof of returned-byte identity.

### Formal Model

Represent locator `l` as `(scheme, namespace, opaque_address, locator_version,
binding_id)`. Resolution yields either candidate bytes or a typed failure;
successful resolution is complete only after Content-Addressed Byte Identity
verification.

### Operational Interpretation

Treat locator syntax as opaque outside its adapter. Permit locator replacement
only with evidence that the exact object bytes remain retrievable under the
new binding.

### Plain-Language Intuition

It tells the system where to look, not what it should trust when it gets there.

### Domain-Context Voice

A consuming capability may retain an optional locator beside a byte identity,
but retrieval must still use the current binding and verify the returned bytes.

### Boundary

A Storage Locator is not content identity, a public URL requirement,
authorization, availability evidence, a credential, a permanent address, or a
promise that the object exists.

### Primary Consumers

- retrieval operations
- candidate locator integrity rules
- future DomainSpec v2 storage values

## KEP-DST-D5: Stored Recipient Envelope

Status: candidate
Term: stored recipient envelope
Aliases: durable recipient envelope, externally stored key envelope

### Normative Definition

A Stored Recipient Envelope is a Durable Knowledge Material Object whose exact
bytes are a `KEP-D9` Recipient Key Envelope bound to one Knowledge Identity,
Knowledge Artifact Version, Encryption Epoch, and Identity Encryption-Key
Binding, together with its content-addressed identity and retrieval metadata.

### Formal Model

For recipient `i`, version `v`, epoch `e`, key binding `k`, and envelope bytes
`b`, define `E = (i, v, e, k, object_id(b), locator_set, storage_binding_id)`.
`E` is valid only when the cryptographic envelope and every contextual binding
refer to the same tuple `(i, v, e, k)`.

### Operational Interpretation

Persist and verify the recipient envelope before a consuming capability refers
to its commitment. Never reuse the same envelope across identities, versions,
epochs, or key bindings.

### Plain-Language Intuition

It is one recipient's sealed key package after it has been placed in
retrievable storage and tied to that recipient's exact context.

### Domain-Context Voice

The consuming capability may commit to or help locate this external object; it
must not place envelope plaintext or a recipient private key in public state.

### Boundary

A Stored Recipient Envelope is not a content key, recipient private key,
membership record, decryption acknowledgement, proof of long-term availability,
or permission to expose its bytes publicly.

### Primary Consumers

- consuming capability preparation
- future key reissue workflow
- future DomainSpec v2 stored-envelope entity

## KEP-DST-D6: Storage Write Receipt

Status: candidate
Term: storage write receipt
Aliases: object-write receipt, persistence-attempt receipt

### Normative Definition

A Storage Write Receipt is environment-bounded evidence that one identified
storage realization accepted an attempt to persist exact object bytes under a
named binding and returned specified locator or version metadata. It does not
by itself prove later retrieval or retention.

### Formal Model

Represent receipt `w` as `(realization_id, binding_id, object_id,
request_digest, provider_result, locator_set, provider_version?, observed_at,
observer_id)`. A successful provider result remains only a write observation
until a separate Verified Retrieval exists.

### Operational Interpretation

Record the exact request and response without credentials or secret material.
Require a retrieval verification before a workflow treats the object as ready
for any dependent protocol commitment.

### Plain-Language Intuition

It is the storage system saying “I accepted this package,” not proof that the
package will still be there tomorrow.

### Domain-Context Voice

The first storage test should keep the write receipt and then independently
read the same object bytes back before allowing a dependent capability step.

### Boundary

A Storage Write Receipt is not durable retention, availability proof,
retrieval verification, decryption evidence, transaction evidence, provider
trust, or authorization to claim a successful dependent protocol outcome.

### Primary Consumers

- storage workflow evidence
- future DomainSpec v2 events
- conformance tests

## KEP-DST-D7: Verified Retrieval

Status: candidate
Term: verified retrieval
Aliases: byte-verified retrieval, storage retrieval verification

### Normative Definition

A Verified Retrieval is a bounded observation that one locator resolved through
one exact Durable Storage Binding and returned bytes whose Content-Addressed
Byte Identity and required contextual bindings match the requested object.

### Formal Model

For request `(binding_id, locator, expected_object_id, expected_context)` and
returned bytes `b`, verification succeeds exactly when resolution succeeds,
`object_id(b) = expected_object_id`, and decoded context matches
`expected_context`. Otherwise it yields one typed failure and no success claim.

### Operational Interpretation

Verify bytes before decryption or protocol use. Bind evidence to the exact
provider realization, time, request, response, digest algorithm, and context.

### Plain-Language Intuition

It means the system fetched the package and checked that it was exactly the
package requested.

### Domain-Context Voice

Before a consumer records a commitment to stored material, its preparation
workflow can require a current verified retrieval for the exact candidate
bytes.

### Boundary

A Verified Retrieval is not perpetual availability, successful decryption,
recipient acknowledgement, plaintext correctness, storage-provider security,
or proof that another environment can retrieve the bytes.

### Primary Consumers

- consuming capability preparation workflow
- storage evidence
- future DomainSpec v2 verification operation

## KEP-DST-D8: Durable Storage Policy

Status: candidate
Term: durable storage policy
Aliases: storage availability and retention policy, object durability policy

### Normative Definition

A Durable Storage Policy is an immutable rule set for one storage-binding
version that states the required retention, availability-observation,
replication or redundancy, migration, deletion, and evidence behavior for
stored knowledge material without claiming those requirements are satisfied.

### Formal Model

Represent policy `p` as `(policy_id, retention_rule, availability_rule,
redundancy_rule, migration_rule, deletion_rule, evidence_rule, policy_version)`.
A binding conforms only when each required rule has an identified realization
and the required observations exist for the assessed interval.

### Operational Interpretation

Bind every write, retrieval, migration, reissue cleanup, and availability claim
to the exact policy version. Treat missing targets as open design decisions,
not implied defaults.

### Plain-Language Intuition

It is the fixed rulebook saying how the storage layer is expected to keep,
check, move, and eventually remove packages.

### Domain-Context Voice

The first candidate does not yet choose retention duration, replication count,
or availability target; those remain explicit owner decisions before provider
implementation.

### Boundary

A Durable Storage Policy is not a Propagation Policy, provider contract,
service-level proof, monitoring result, legal retention instruction, deletion
proof, or automatically satisfied runtime configuration.

### Primary Consumers

- candidate durable-storage Product Capability
- future storage business ontology
- future DomainSpec v2 policy node

## KEP-DST-D9: Durable Storage Failure

Status: candidate
Term: durable storage failure
Aliases: storage retrieval failure, storage integrity failure

### Normative Definition

A Durable Storage Failure is a typed result stating that a requested storage
operation could not establish its exact postcondition, including absent,
unavailable, unauthorized, expired, context-mismatched, byte-mismatched,
policy-mismatched, or ambiguous outcomes.

### Formal Model

Define failure as `Failure(code, operation_id, binding_id, object_id?,
observed_state_digest, evidence_refs)`, where `code` belongs to a closed failure
set and no success event or dependent effect may be emitted for that operation.

### Operational Interpretation

Fail closed with one explicit code. Never fabricate empty bytes, silently use a
different provider or locator, accept a digest mismatch, or advance a consuming
workflow after storage verification fails.

### Plain-Language Intuition

When storage cannot prove the requested result, it says exactly what failed and
stops dependent work.

### Domain-Context Voice

If a required envelope cannot be written or verified, the consuming capability
must not record a commitment to unavailable or mismatched bytes.

### Boundary

A Durable Storage Failure is not proof of permanent loss, permission to delete
state, automatic provider failover, consumer transition failure, key compromise,
or evidence that no infrastructure cost occurred.

### Primary Consumers

- storage operations and workflow
- failure events
- conformance negative tests

## KEP-DST-D10: Reissue-Safe Envelope Replacement

Status: candidate
Term: reissue-safe envelope replacement
Aliases: durable envelope reissue transition, safe stored-envelope replacement

### Normative Definition

Reissue-Safe Envelope Replacement is the storage transition that persists and
verifies one replacement Recipient Key Envelope before the protocol changes its
active commitment, while preserving owner membership, artifact version,
Encryption Epoch, every other recipient's envelope, and recoverability of the
previous envelope until the replacement transition is committed.

### Formal Model

For old envelope `E0` and replacement `E1`, the allowed sequence is
`write(E1) -> verify(E1) -> commit_active(E1) -> retire(E0)`; `retire(E0)` is
permitted only under the bound Durable Storage Policy after commitment evidence
exists. Any failure before `commit_active(E1)` leaves `E0` active.

### Operational Interpretation

Use a workflow rather than claiming cross-system atomicity. Keep E0 recoverable
until the separately governed commitment update succeeds, then apply retention
or deletion rules explicitly.

### Plain-Language Intuition

Put the new sealed key somewhere safe and check it before pointing the protocol
at it; do not throw away the old one too early.

### Domain-Context Voice

When one recipient requests a lost-key reissue, storage replaces only that
recipient's envelope bytes without changing owner membership, artifact version,
or encryption epoch.

### Boundary

Reissue-Safe Envelope Replacement is not cross-provider atomicity, compromise
recovery, owner-set mutation, artifact-version change, guaranteed deletion,
payment, or proof that the recipient controls the replacement private key.

### Primary Consumers

- future key reissue workflow
- future DomainSpec v2 workflow and state machine
- durable-storage conformance tests

## KEP-DST-D11: Durable Storage Realization Identity

Status: candidate
Term: durable storage realization identity
Aliases: exact storage realization, storage provider realization identity

### Normative Definition

A Durable Storage Realization Identity is the exact, environment-bounded
identity of the adapter, provider or local fixture, configuration schema,
namespace, endpoint class, region or locality, build, and policy-binding version
whose behavior produced storage evidence, excluding credentials and secrets.

### Formal Model

Represent realization `r` as `(adapter_source_digest, adapter_build_digest,
provider_kind, configuration_schema_digest, namespace_id, endpoint_class,
locality, binding_version, environment_id)`. Two observations are comparable
only when their relevant realization components match or a governed migration
relation exists.

### Operational Interpretation

Bind every write, retrieval, migration, and availability observation to `r`.
Record credential references only through a separate secret-management boundary.

### Plain-Language Intuition

It identifies exactly which storage setup produced the evidence without
writing its passwords into the evidence.

### Domain-Context Voice

The first implementation can identify a local deterministic fixture separately
from any later IPFS, object-store, archival, or multi-provider realization.

### Boundary

A Durable Storage Realization Identity is not a credential, provider marketing
name, object identity, storage policy, security proof, deployment authorization,
or evidence that the realization behaved correctly.

### Primary Consumers

- implementation binding
- storage evidence
- conformance environments

## KEP-DST-D12: Durable Storage Evidence

Status: candidate
Term: durable storage evidence
Aliases: storage conformance evidence, durable-object evidence bundle

### Normative Definition

Durable Storage Evidence is an environment- and interval-bounded bundle linking
one exact storage realization and policy to operation inputs, write receipts,
verified retrievals, failures, migrations, observed object state, and costs
without claiming more durability or availability than was observed.

### Formal Model

Represent evidence `e` as `(realization_id, binding_id, policy_id,
environment_id, observation_interval, operation_input_digests,
write_receipts, retrieval_verifications, failure_records, state_digests,
cost_observations, result)`. Every claim is bounded by `observation_interval`
and the named environment.

### Operational Interpretation

Capture deterministic local fixtures first, then separately identify any
external provider observations. Preserve negative cases and never promote one
successful retrieval into a long-term availability claim.

### Plain-Language Intuition

It is the evidence folder showing which storage setup was tested, what it did,
what came back, what failed, and during which period.

### Domain-Context Voice

The first proof should show one exact envelope was written and retrieved with
matching bytes before its consumer used the commitment, while long-term
provider availability remains unproved.

### Boundary

Durable Storage Evidence is not perpetual availability, disaster-recovery
proof, confidentiality proof, provider certification, consumer execution evidence,
deployment, or permission to claim production readiness.

### Primary Consumers

- system-ontology proof obligations
- implementation conformance assessment
- future runtime observations

## KEP-DST-D13: Durable Storage Infrastructure Cost

Status: candidate
Term: durable storage infrastructure cost
Aliases: storage service cost, storage and retrieval cost

### Normative Definition

A Durable Storage Infrastructure Cost is a measured or quoted expense for
writing, retaining, replicating, retrieving, migrating, or deleting stored
objects that remains separate from knowledge price, seller payment, royalty,
license consideration, and owner compensation.

### Formal Model

Represent cost `c` as `(realization_id, operation_kind, object_id?, quantity,
unit, amount, currency_or_token, pricing_basis, observed_or_quoted_at)`. It may
be zero for a fixture while the knowledge consideration remains independently
zero by policy.

### Operational Interpretation

Report infrastructure costs explicitly in evidence and economic boundaries.
Never call the total system cost zero merely because a knowledge exchange has
no knowledge consideration.

### Plain-Language Intuition

The knowledge may be free while keeping and fetching its encrypted packages
still costs money or resources.

### Domain-Context Voice

A no-price knowledge exchange may still incur execution-network and
durable-storage costs, each reported separately by the consuming capability.

### Boundary

A Durable Storage Infrastructure Cost is not knowledge price, consideration,
seller proceeds, royalty, treasury allocation, SOL transfer requirement,
license fee, or evidence that a provider was paid.

### Primary Consumers

- candidate no-price economic boundary
- storage evidence
- future cost policy

## KEP-DST-D14: Durable Storage Confidentiality Boundary

Status: candidate
Term: durable storage confidentiality boundary
Aliases: external secret-material boundary, encrypted-storage boundary

### Normative Definition

The Durable Storage Confidentiality Boundary is the rule that durable storage
may receive only encrypted artifact bytes, recipient-encrypted envelope bytes,
public commitments, and necessary retrieval metadata, while plaintext, content
keys, envelope plaintext, recipient private keys, and credentials remain outside
public or provider-readable protocol state unless a separately admitted secure
realization explicitly proves otherwise.

### Formal Model

Let allowed stored classes be `{ciphertext, recipient_envelope_ciphertext,
public_commitment, locator_metadata}` and forbidden classes be `{plaintext,
content_key, envelope_plaintext, recipient_private_key, credential}`. Every
write must classify its payload and reject any class outside the allowed set.

### Operational Interpretation

Classify payloads before writing, redact evidence, and keep provider credentials
behind a separate secret-management interface. Provider-side encryption may add
defense in depth but cannot replace protocol encryption.

### Plain-Language Intuition

The storage layer may hold sealed packages and labels, never the open knowledge
or the keys that unlock it.

### Domain-Context Voice

A stored recipient envelope is already encrypted for its recipient. A consuming
protocol and external storage may see its digest or ciphertext, but neither
should receive the recipient's private key or the unwrapped content key.

### Boundary

The Durable Storage Confidentiality Boundary is not proof of provider security,
metadata privacy, traffic confidentiality, key management, credential rotation,
legal compliance, or successful encryption implementation.

### Primary Consumers

- storage write rules
- provider-neutral interface
- security and conformance reviews

## KEP-DST-D15: Durable Storage Capability Instantiation

Status: candidate
Term: durable storage capability instantiation
Aliases: storage consumer binding, durable-storage specialization binding

### Normative Definition

A Durable Storage Capability Instantiation is the immutable semantic binding by
which one consuming Product Capability adopts the generic durable-storage
contract, names every definition it reuses or specializes, and supplies all
consumer-owned policy values required before provider realization. It does not
modify the generic definitions and does not select or operate a provider.

### Formal Model

Represent instantiation `i` as `(instantiation_id, consumer_capability_id,
storage_capability_version, reused_definition_ids,
specialized_definition_bindings, object_kind_bindings,
commitment_binding_rule, readiness_rule, failure_effect_rule,
storage_policy_value_binding, infrastructure_cost_classification,
instantiation_version, status)`. It is complete only when every required field
is exact, every specialization points to its generic parent, and no unresolved
semantic slot is treated as a default.

### Operational Interpretation

Author the generic durable-storage Product Capability first. Each consumer then
creates its own instantiation record: reuse unchanged meanings, define narrower
terms in the consumer's definition authority, and fill policy values owned by
that consumer. Provider adapters, endpoints, credentials, and environment
configuration belong to a later implementation binding, not this record.

### Plain-Language Intuition

Durable storage provides a form with required meaning fields. A consuming
capability fills that form and may add narrower labels, but it does not rewrite
the form or choose the storage machinery inside it.

### Domain-Context Voice

Solana Co-Ownership is the first intended consumer. Its successor definition
and Product Capability material must bind envelope commitments, readiness and
failure behavior, policy values, and cost classification to durable storage;
the currently accepted Solana bytes do not yet contain that instantiation.

### Boundary

A Durable Storage Capability Instantiation is not a generic storage definition,
provider binding, credential, deployment, runtime configuration, evidence of
storage behavior, automatic inheritance, Product Capability adoption, or
permission to mutate an already accepted consumer definition set.

### Primary Consumers

- consuming Product Capability definitions and contracts
- capability-local business ontology
- DomainSpec v2 cross-capability bindings
