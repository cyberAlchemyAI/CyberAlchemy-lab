# Hosted Devnet Knowledge Exchange Definitions

Status: authored candidate
Owner: Knowledge Exchange Protocol product owner
Candidate set: `KEP-HOST-DEFINITION-SET-001`

These capability-local terms refine the accepted Knowledge Exchange Protocol
and Solana realization definitions. They do not replace `KEP-D*` or
`KEP-SOL-D*`, and remain candidate-only until an exact digest is accepted.

## KEP-HOST-D1: Hosted Knowledge Exchange Service

### Normative Definition

A Hosted Knowledge Exchange Service is a network-addressable coordinator that
stores and returns encrypted protocol material, verifies scoped participant
authorizations, records workflow state, and reconciles finalized public-chain
observations without becoming a Knowledge Identity, co-owner, wallet custodian,
decryption-key custodian, definition authority, or source of blockchain truth.

### Formal Model

For service `S`, participant set `P`, encrypted material `C`, and public-chain
observation `O`, `S(P,C,O)` may project a protocol transition only when the
required participant signature is valid, `C` matches its byte commitment, and
`O.finality = finalized`. The service state cannot contain plaintext or private
key material.

### Operational Interpretation

Expose HTTPS operations for identity registration, artifact preparation,
grant finalization, recipient retrieval, reissue request and fulfillment.

### Plain-Language Intuition

It coordinates the exchange online, but it is neither an owner nor a vault for
the users' secrets.

### Domain-Context Voice

The first hosted KEP application runs a Rust API behind a VPS reverse proxy and
uses the existing no-price Solana Devnet program only through finalized
observations.

### Boundary

It is not a marketplace, wallet, key manager, plaintext store, Solana validator,
license issuer, production service, or proof that a user understood knowledge.

## KEP-HOST-D2: Wallet Authorization Challenge

### Normative Definition

A Wallet Authorization Challenge is a domain-separated, operation-specific,
replay-bounded canonical byte string whose valid Ed25519 signature proves
control of the currently registered Solana signing key for exactly one hosted
command without equating that key with the Knowledge Identity.

### Formal Model

For domain `d`, operation `op`, identity `i`, payload commitment `h`, and unique
operation identity `n`, the signed bytes are `encode(d,op,i,h,n)`. Verification
requires the exact bytes, registered public key, valid signature, and unused
`n` in the command's replay domain.

### Operational Interpretation

Construct signing messages deterministically and reject wrong signer, changed
payload, stale revision, reused operation identity, or malformed encodings.

### Plain-Language Intuition

It is a one-purpose statement the wallet signs, not permission for the server
to act later on the user's behalf.

### Domain-Context Voice

The Rust API verifies signatures for registration, artifact preparation,
co-owner grants, reissue requests and reissue fulfillment.

### Boundary

It is not a wallet secret, login cookie, universal delegation, legal identity,
encryption-key proof, transaction signature, or authorization for another
payload.

## KEP-HOST-D3: Client-Held Encryption Boundary

### Normative Definition

A Client-Held Encryption Boundary is the invariant that plaintext knowledge,
content-encryption keys, HPKE private keys, and decrypted results are created,
used and retained only in participant-controlled clients, while the hosted
service accepts only ciphertext, public keys, commitments and recipient key
envelopes.

### Formal Model

Let `secret(x)` identify plaintext or private key material. For every persisted
server record `r`, `contains(r, secret(x)) = false`; only public or encrypted
projections of `x` may cross the client-service boundary.

### Operational Interpretation

The API has no plaintext field and no private-key field. Decryption is tested
outside the service using material returned to the intended recipient.

### Plain-Language Intuition

The browser locks and unlocks the knowledge; the server only carries sealed
packages.

### Domain-Context Voice

The hosted vertical stores ciphertext and per-recipient envelopes in its SQL
repository. The test proves recipient-side recovery without giving the API the
content key.

### Boundary

It is not proof that a participant device is safe, browser isolation, digital
rights management, revocation of copied plaintext, or a security certification.

## KEP-HOST-D4: Prepared Hosted Grant

### Normative Definition

A Prepared Hosted Grant is a non-active, originator-authorized record binding
one exact artifact revision, recipient identity, recipient encryption-key
binding, encrypted envelope commitment, and unique operation identity while
awaiting a matching finalized Solana Devnet observation.

### Formal Model

Preparation from state revision `r` creates `g(status=prepared,
expected_revision=r)` but leaves `owners` and `revision` unchanged. Activation
is allowed only after a matching finalized transaction observation and then
produces revision `r+1` with the recipient added beside every existing owner.

### Operational Interpretation

Persist the prepared grant before accepting a transaction signature; never
serve its recipient envelope as active access before finalization.

### Plain-Language Intuition

The grant is packed and waiting, but B is not treated as an owner until Devnet
confirms it.

### Domain-Context Voice

The API separates `POST /grants` from `POST /grants/{id}/finalize` and the test
checks that access remains forbidden between those calls.

### Boundary

It is not an active Co-Ownership Grant, transaction submission, payment,
cross-system atomicity, decryption proof, or publication permission.

## KEP-HOST-D5: Finalized Access Projection

### Normative Definition

A Finalized Access Projection is the hosted read model created only after an
independently queried Solana Devnet transaction has finalized and the expected
grant or reissue transition is reconciled, exposing exact ciphertext and the
requesting current owner's active recipient envelope without exposing another
recipient's envelope or any secret material.

### Formal Model

For artifact `v`, requester `i`, and revision `r`, `access(v,i,r)` exists only
if `i in owners(v,r)` and `finalized(v,r)=true`; its bytes are exactly
`(ciphertext(v), active_envelope(v,i,r))` and their commitments must match.

### Operational Interpretation

Authorize access reads with the recipient's registered wallet and return only
that identity's active envelope.

### Plain-Language Intuition

It is the server's finalized view of the sealed package that this owner may
download.

### Domain-Context Voice

The third-party test proves B cannot retrieve before finalization, can retrieve
afterward, and can decrypt the exact fixture locally.

### Boundary

It is not blockchain consensus, long-term availability, plaintext delivery,
license acceptance, legal title, or proof of comprehension.

## KEP-HOST-D6: Hosted Recovery Topology

### Normative Definition

A Hosted Recovery Topology is the explicit separation of mutable operational
state, append-only recovery evidence, and immutable encrypted-object archive,
including a restore procedure and failure-domain description that does not
misrepresent three logical schemas on one host as three independent backups.

### Formal Model

For encrypted object `c`, readiness requires an operational record `o`, journal
event `j`, archive object `a`, and verified retrieval identities satisfying
`digest(o)=digest(j.object)=digest(a)=digest(c)`. Independent disaster recovery
additionally requires at least one copy outside the primary host failure domain.

### Operational Interpretation

Use PostgreSQL for operational snapshot and append-only journal, export encrypted
archive bytes to a separately configured target, and test restore before a VPS
deployment can claim recovery readiness.

### Plain-Language Intuition

The live database, recovery history and off-server sealed copy are different
jobs; folders in one machine are not three backups.

### Domain-Context Voice

This candidate implements the PostgreSQL snapshot/journal boundary and an
archive table; physical off-VPS archive configuration remains a deployment gate.

### Boundary

It is not guaranteed availability, a backup merely because data was inserted,
cross-provider replication, a service-level agreement, or authorization to use
production credentials.

## Candidate Claim Ceiling

These terms define a candidate hosted realization. They do not adopt the
Product Capability, admit an ontology or DomainSpec source, prove the Rust
binding, authorize a VPS deployment, or expand the no-price Devnet scope.

