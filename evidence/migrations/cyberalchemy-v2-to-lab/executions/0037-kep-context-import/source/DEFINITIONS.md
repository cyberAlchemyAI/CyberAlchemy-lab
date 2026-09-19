# Knowledge Exchange Protocol Definitions

Status: active product-local source
Owner: Knowledge Exchange Protocol product owner
Canonical source: `authority/definitions/DEFINITIONS.md`
Lookup index: `authority/definitions/DEFINITIONS-INDEX.md`

## Authority Rule

Only this file defines normative Knowledge Exchange Protocol business terms.
CyberAlchemy-v2 supplies shared construction primitives, including
[CAV2-D33 Definition](../../../../authority/definitions/DEFINITIONS.md#cav2-d33-definition),
[CAV2-D63 Product Thesis](../../../../authority/definitions/DEFINITIONS.md#cav2-d63-product-thesis),
[CAV2-D65 DomainSpec-Governed Construction Invariant](../../../../authority/definitions/DEFINITIONS.md#cav2-d65-domainspec-governed-construction-invariant),
and [CAV2-D67 Product Capability](../../../../authority/definitions/DEFINITIONS.md#cav2-d67-product-capability).
Those imports do not make this product's vocabulary CyberAlchemy-v2 authority.

Downstream product artifacts may apply or reference these definitions but may
not redefine them. Promotion into shared CyberAlchemy-v2 vocabulary requires a
separate evidence-backed owner decision.

## KEP-D1: Knowledge Artifact

Status: active
Term: knowledge artifact
Aliases: governed knowledge artifact, tradable knowledge artifact
Adopted: 2026-08-31 by explicit owner direction as product-local definition authority

### Normative Definition

A Knowledge Artifact is a governed, identifiable body of knowledge that can be
referenced, versioned, related to origin and contribution evidence, and made the
subject of access, co-ownership, or licensing rules without equating the
knowledge with any one file, ciphertext, storage location, token, or legal
right.

### Operational Interpretation

Use Knowledge Artifact for ontology packages, definition sets, or other bounded
knowledge products whose identity must survive changes in encoding, storage, or
encryption. Address exchange and authorization against an exact Knowledge
Artifact Version rather than against the mutable artifact identity alone.

### Plain-Language Intuition

It is the named piece of knowledge being governed, not the file that happens to
carry it today.

### Domain-Context Voice

In the Knowledge Exchange Protocol, an artifact may contain ontology knowledge
or definitions. The first proof governs one encrypted version and does not yet
claim that the protocol transfers copyright, verifies truth, or stores the
artifact.

### Boundary

A Knowledge Artifact is not a Knowledge Artifact Version, ciphertext, storage
object, key, token, account, ontology admission, definition authority, license,
copyright interest, or proof that the knowledge is correct or novel.

### Primary Consumers

- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- [Knowledge Exchange Protocol](../..)

## KEP-D2: Knowledge Artifact Version

Status: active
Term: knowledge artifact version
Aliases: artifact version, immutable knowledge version
Adopted: 2026-08-31 by explicit owner direction as product-local definition authority

### Normative Definition

A Knowledge Artifact Version is one immutable semantic snapshot of a Knowledge
Artifact, identified by an exact content commitment and the propagation-policy
identity that governs that snapshot. Changing its committed content or policy
creates a successor version; changing only ciphertext or recipient access
material does not.

### Operational Interpretation

Bind every grant, owner membership, key envelope, acknowledgement, and reissue
to one exact version identity. Keep plaintext-content identity separate from
encryption epochs so compromised keys can be rotated without pretending the
knowledge changed.

### Plain-Language Intuition

It is the exact edition everyone is talking about, even if its encrypted
packaging changes.

### Domain-Context Voice

The first Knowledge Exchange proof uses an immutable version as the unit whose
owner set expands from one identity to two. Later payment or licensing rules
must name the same exact version or an explicit successor.

### Boundary

A Knowledge Artifact Version is not a mutable document, ciphertext blob,
storage locator, encryption epoch, owner set, license, or assertion that two
different encodings have the same meaning without a governed canonicalization
rule.

### Primary Consumers

- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- [Knowledge Exchange Protocol](../..)

## KEP-D3: Knowledge Identity

Status: active
Term: knowledge identity
Aliases: protocol knowledge identity, knowledge subject identity
Adopted: 2026-08-31 by explicit owner direction as product-local definition authority

### Normative Definition

A Knowledge Identity is a stable protocol subject that can be named in
knowledge-origin, co-ownership, authorization, and evidence relationships while
remaining distinct from any wallet address, signing key, encryption key,
account, Person, Team, or session that represents or controls it.

### Operational Interpretation

Resolve authorization through independently evidenced bindings from the stable
identity to current signing and encryption keys. Key loss, key rotation, or a
new wallet must not silently create a new owner or erase the old identity's
history.

### Plain-Language Intuition

It is who the protocol recognizes over time, not whichever key they use today.

### Domain-Context Voice

The initial protocol calls the originator A and recipient B, but both are
Knowledge Identities. Whether either identity maps to a Person, Team, wallet, or
later decentralized identifier remains a separate integration decision.

### Boundary

A Knowledge Identity is not proof of legal identity, a Person, Team, wallet,
public key, credential, permission, owner membership, authority grant, or right
to process personal data.

### Primary Consumers

- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- [Knowledge Exchange Protocol](../..)

## KEP-D4: Identity Encryption-Key Binding

Status: active
Term: identity encryption-key binding
Aliases: encryption-key binding, recipient key binding
Adopted: 2026-08-31 by explicit owner direction as product-local definition authority

### Normative Definition

An Identity Encryption-Key Binding is a time-bounded, challengeable assertion
that one public encryption key is controlled for a named Knowledge Identity and
may receive newly issued access material during the binding's valid interval.
It is independently versioned from the identity and from owner membership.

### Operational Interpretation

Verify a current binding before creating or reissuing a Recipient Key Envelope.
Preserve superseded bindings for provenance, reject ambiguous or stale
bindings, and treat suspected private-key compromise as an Encryption Epoch
rotation problem rather than merely a binding update.

### Plain-Language Intuition

It is the dated receipt saying which lock currently belongs to this identity.

### Domain-Context Voice

For recipient B, the protocol binds the envelope to B's current encryption
public key. A replacement key may support a lost-key reissue without changing
B's co-owner membership.

### Boundary

An Identity Encryption-Key Binding is not the private key, a signing-key
binding, identity proof by itself, owner membership, authorization to grant
access, successful decryption, or evidence that the old private key is safe.

### Primary Consumers

- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- [Knowledge Exchange Protocol](../..)

## KEP-D5: Knowledge Co-Ownership

Status: active
Term: knowledge co-ownership
Aliases: artifact co-ownership, co-owner membership
Adopted: 2026-08-31 by explicit owner direction as product-local definition authority

### Normative Definition

Knowledge Co-Ownership is an explicit, non-exclusive membership relationship
between two or more Knowledge Identities and one exact Knowledge Artifact
Version under its Propagation Policy. Adding a member preserves all existing
members unless a separately governed successor operation says otherwise.

### Operational Interpretation

Represent ownership as a set of explicit memberships, not a single transferable
owner field. Validate additions by set inclusion: the post-state contains every
pre-state owner and the newly authorized identity. Keep access delivery,
economic allocation, licensing, and legal title as separate relations.

### Plain-Language Intuition

The artifact gains another recognized owner; the original owner does not lose
their place.

### Domain-Context Voice

The first protocol proof changes the owner set from `{A}` to `{A, B}`. It does
not implement resale, royalties, licenses, reputation, or removal of either
identity.

### Boundary

Knowledge Co-Ownership is not exclusive ownership, transfer, copyright title,
custody, possession, decryption success, a key envelope, a payment claim, a
license, authority over definitions, or permission to publish.

### Primary Consumers

- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- [Knowledge Exchange Protocol](../..)

## KEP-D6: Co-Ownership Grant

Status: active
Term: co-ownership grant
Aliases: knowledge co-ownership grant, owner-set expansion
Adopted: 2026-08-31 by explicit owner direction as product-local definition authority

### Normative Definition

A Co-Ownership Grant is an authorized, replay-safe state transition that adds
one Knowledge Identity to the Knowledge Co-Ownership membership of one exact
Knowledge Artifact Version without removing or silently changing any existing
member, version, or Propagation Policy.

### Operational Interpretation

Require an authorized grantor, the exact pre-state, recipient identity, current
recipient encryption-key binding, immutable policy reference, and unique
operation identity. Record access delivery and recipient acknowledgement as
separate evidence rather than folding them into the grant.

### Plain-Language Intuition

It is the governed act that changes `{A}` into `{A, B}`—not a handover from A
to B.

### Domain-Context Voice

The Knowledge Exchange Protocol first proves a no-payment grant. A later Solana
transaction may condition the grant, but payment is not part of this term and
must not be inferred from owner-set expansion.

### Boundary

A Co-Ownership Grant is not a sale, transfer, payment, token mint, license,
publication, successful decryption, key reissue, or proof of off-chain legal
rights.

### Primary Consumers

- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- [Knowledge Exchange Protocol](../..)

## KEP-D7: Propagation Policy

Status: active
Term: propagation policy
Aliases: artifact propagation policy, originator propagation rules
Adopted: 2026-08-31 by explicit owner direction as product-local definition authority

### Normative Definition

A Propagation Policy is the originator-selected, version-bound rule set that
governs who may add co-owners, who may authorize access-material reissue, and
which later economic or licensing obligations may attach to propagation. The
policy is immutable for its Knowledge Artifact Version.

### Operational Interpretation

Resolve every grant and reissue against the exact policy identity stored with
the version. A material policy change creates a successor Knowledge Artifact
Version and does not retroactively rewrite prior memberships or evidence.

### Plain-Language Intuition

It is the original creator's fixed rulebook for how this exact edition may
spread.

### Domain-Context Voice

The first proof needs only grant and reissue authority rules. Royalty shares,
prices, licenses, and downstream propagation obligations are reserved fields of
future policy versions, not behavior already implemented.

### Boundary

A Propagation Policy is not a license by itself, legal advice, runtime code,
owner membership, payment settlement, universal authority of the originator,
or permission to change canonical CyberAlchemy definitions.

### Primary Consumers

- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- [Knowledge Exchange Protocol](../..)

## KEP-D8: Content-Addressed Ciphertext Reference

Status: active
Term: content-addressed ciphertext reference
Aliases: ciphertext reference, external ciphertext commitment
Adopted: 2026-08-31 by explicit owner direction as product-local definition authority

### Normative Definition

A Content-Addressed Ciphertext Reference is a commitment to exact encrypted
bytes, together with sufficient location information to attempt retrieval,
without making the protocol the custodian of those bytes or promising their
continued availability.

### Operational Interpretation

Verify retrieved ciphertext against the committed digest. Bind the reference to
one Knowledge Artifact Version and Encryption Epoch, and surface missing or
mismatched bytes as delivery blockers rather than fabricating availability.

### Plain-Language Intuition

It is a tamper-evident address for the encrypted package, not a promise that the
package will always be there.

### Domain-Context Voice

The first protocol stores commitments and locators on the governed state while
encrypted knowledge remains in durable external storage selected later by the
product's storage capability.

### Boundary

A Content-Addressed Ciphertext Reference is not plaintext, a content key,
storage custody, replication, availability proof, decryption proof, owner
membership, or a Solana account containing the whole artifact.

### Primary Consumers

- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- [Knowledge Exchange Protocol](../..)

## KEP-D9: Recipient Key Envelope

Status: active
Term: recipient key envelope
Aliases: key envelope, wrapped content key
Adopted: 2026-08-31 by explicit owner direction as product-local definition authority

### Normative Definition

A Recipient Key Envelope is recipient-specific encrypted access material that
wraps one Encryption Epoch's content key for one Knowledge Identity's current
Identity Encryption-Key Binding and binds that wrapping to one exact Knowledge
Artifact Version.

### Operational Interpretation

Create a distinct envelope for every current recipient binding, commit to its
bytes, and reject reuse across identities, versions, keys, or epochs. Keep the
content key and recipient private key outside public protocol state.

### Plain-Language Intuition

It is one sealed copy of the artifact key made for one recipient's current
lock.

### Domain-Context Voice

When B becomes a co-owner, B receives an envelope tied to B, B's current key,
the exact artifact version, and the current epoch. The envelope can exist before
B acknowledges successful use.

### Boundary

A Recipient Key Envelope is not the plaintext content key, private key,
identity, owner membership, authorization grant, acknowledgement, proof of
decryption, or guarantee of ciphertext availability.

### Primary Consumers

- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- [Knowledge Exchange Protocol](../..)

## KEP-D10: Encryption Epoch

Status: active
Term: encryption epoch
Aliases: artifact encryption epoch, content-key epoch
Adopted: 2026-08-31 by explicit owner direction as product-local definition authority

### Normative Definition

An Encryption Epoch is one immutable generation of ciphertext and recipient
access material for a Knowledge Artifact Version, using one content key and a
complete set of Recipient Key Envelopes for the identities meant to retain
access in that generation.

### Operational Interpretation

Create a successor epoch with a new content key, ciphertext reference, and
replacement envelopes when a prior encryption private key may be compromised.
A lost, non-compromised recipient key may instead use Key Reissue within the
same epoch.

### Plain-Language Intuition

It is one complete generation of locks and sealed keys for the same exact
knowledge edition.

### Domain-Context Voice

The first proof separates ordinary B key loss from suspected compromise. Loss
can rewrap the existing content key; compromise requires a new epoch covering
every identity that should keep access.

### Boundary

An Encryption Epoch is not a Knowledge Artifact Version, time period by itself,
blockchain epoch, ownership era, partial key update, key reissue, or evidence
that every intended recipient actually decrypted the artifact.

### Primary Consumers

- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- [Knowledge Exchange Protocol](../..)

## KEP-D11: Key Reissue

Status: active
Term: key reissue
Aliases: recipient key reissue, lost-key reissue
Adopted: 2026-08-31 by explicit owner direction as product-local definition authority

### Normative Definition

A Key Reissue is an authorized replacement of one Knowledge Identity's
Recipient Key Envelope within the same Encryption Epoch after the identity
binds a new encryption key. It changes only that identity's access material and
must preserve owner membership, artifact version, policy, economic state, and
every other recipient's envelope.

### Operational Interpretation

Allow the affected identity to request reissue through stable identity
authorization and a current replacement key binding. Reject replay, stale
bindings, protected-state mutation, and reissue when compromise of the prior
private key cannot be excluded; suspected compromise requires a successor
Encryption Epoch.

### Plain-Language Intuition

It gives the same owner a new sealed key without changing who owns what.

### Domain-Context Voice

Recipient B may ask for reissue after losing a key. That request does not add B
again, remove A, change the propagation rules, charge SOL, or create a new
artifact version.

### Boundary

Key Reissue is not identity recovery by itself, ownership transfer, new
co-ownership, revocation, compromise recovery, artifact-version change,
payment, or proof that the requester still controls every earlier key.

### Primary Consumers

- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- [Knowledge Exchange Protocol](../..)

## KEP-D12: Decryption Acknowledgement

Status: active
Term: decryption acknowledgement
Aliases: recipient decryption acknowledgement, delivery acknowledgement
Adopted: 2026-08-31 by explicit owner direction as product-local definition authority

### Normative Definition

A Decryption Acknowledgement is recipient-authorized evidence that binds one
Knowledge Identity to one exact Knowledge Artifact Version, Encryption Epoch,
Recipient Key Envelope, ciphertext commitment, and fresh delivery challenge,
without claiming more than the recipient attests.

### Operational Interpretation

Require recipient authorization and replay protection, and store the
acknowledgement separately from the Co-Ownership Grant. Use it as bounded
delivery evidence; do not infer confidentiality, comprehension, truth,
licensing compliance, or long-term availability.

### Plain-Language Intuition

It is B's signed receipt for this exact encrypted delivery, not proof of
everything that happened afterward.

### Domain-Context Voice

The first protocol can require B to acknowledge the exact version, epoch, and
envelope. A missing acknowledgement leaves delivery unconfirmed but does not
silently erase an already admitted owner membership.

### Boundary

A Decryption Acknowledgement is not plaintext disclosure, cryptographic proof
of correct decryption unless a later scheme supplies one, acceptance of legal
terms, payment confirmation, ownership creation, knowledge validation, or proof
of durable storage.

### Primary Consumers

- [DEFINITIONS-INDEX.md](DEFINITIONS-INDEX.md)
- [Knowledge Exchange Protocol](../..)

