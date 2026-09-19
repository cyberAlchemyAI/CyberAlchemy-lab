# CyberAlchemy Knowledge Exchange Protocol

Status: private product model; Product Capability adopted and business ontology admitted

This package defines the first bounded product slice for a Solana-oriented
knowledge-sharing protocol. The first proof is deliberately smaller than a
marketplace: one originator adds one recipient as an additional co-owner of one
encrypted knowledge-artifact version, gives that recipient a decryptable key
envelope, and receives a signed acknowledgement bound to the exact artifact
version.

The protocol does not custody plaintext, content-encryption keys, or the
encrypted artifact. The artifact is kept at an external content-addressed
location. A stable Knowledge Identity (`KEP-D3`) authorizes actions with a
signing key and binds a separate encryption public key through an Identity
Encryption-Key Binding (`KEP-D4`).

## Definition Authority

The product-local canonical vocabulary is
[authority/definitions/DEFINITIONS.md](authority/definitions/DEFINITIONS.md),
with lookup entries in
[authority/definitions/DEFINITIONS-INDEX.md](authority/definitions/DEFINITIONS-INDEX.md).
`KEP-D1` through `KEP-D12` own the Knowledge Exchange Protocol's business
meaning. CyberAlchemy-v2 contributes shared construction primitives but does
not own these product-local terms.

## First Product Capability

`CA2-CAP-GRANT-ENCRYPTED-KNOWLEDGE-COOWNERSHIP` makes this outcome possible:

```text
owner set {A}
  + A-authorized co-ownership grant for B
  + immutable artifact-version and policy identities
  + encrypted artifact reference
  + recipient-specific key envelope for B
  + B-signed decryption acknowledgement
  = owner set {A, B} with bounded delivery evidence
```

B may later sign a key-reissue request. Reissuing a key envelope does not add
an owner, remove an owner, change the artifact, or create payment. A lost key
may receive the same content key wrapped to a new encryption key. A compromised
key requires a new encryption epoch and new content key; merely rewrapping the
old content key is insufficient.

## D65 Construction State

The product-local definitions, adopted Product Capability, and admitted
business ontology are now the evaluable D65 predecessor chain:

1. `KEP-D1` through `KEP-D12` are canonical product-local definitions;
2. the exact Product Capability is adopted against those definitions;
3. the exact capability-local business ontology is admitted with complete
   definition bindings; and
4. existing DomainSpec-generated and Rust artifacts remain premature candidate
   evidence descended from the earlier unbound model.

The immutable owner decision is
[decisions/ontology-admission.json](decisions/ontology-admission.json). It
supersedes the earlier pre-definition acceptance and grants no successor
execution. DomainSpec admission, implementation conformance, Solana
realization, publication, and deployment remain blocked or `not_evaluable`.

## Validate

```bash
python3 cyberAlchemy-v2/product/knowledge-exchange-protocol/validate.py
python3 cyberAlchemy-v2/product/knowledge-exchange-protocol/tests/test_validate.py
```

## Claim Ceiling

A PASS proves the exact definition bindings, adopted capability postimage,
admitted business-ontology postimage, source currency, graph closure, schema
conformance, decision-digest closure, and current D65 stage posture. It does
not admit DomainSpec or a system ontology, prove implementation conformance or
cryptographic security, prove recipient decryption, implement a Solana
program, authorize a share, transfer SOL, establish licensing or royalties,
publish, release, or deploy anything.
