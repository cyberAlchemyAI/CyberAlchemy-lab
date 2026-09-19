# Knowledge Exchange Protocol Definitions Index

Status: active
Canonical source: [DEFINITIONS.md](DEFINITIONS.md)

## Terms

| ID | Term | Status | Canonical section | Plain-language intuition |
| --- | --- | --- | --- | --- |
| KEP-D1 | knowledge artifact | active | [Knowledge Artifact](DEFINITIONS.md#kep-d1-knowledge-artifact) | It is the named piece of knowledge being governed, not the file that happens to carry it today. |
| KEP-D2 | knowledge artifact version | active | [Knowledge Artifact Version](DEFINITIONS.md#kep-d2-knowledge-artifact-version) | It is the exact edition everyone is talking about, even if its encrypted packaging changes. |
| KEP-D3 | knowledge identity | active | [Knowledge Identity](DEFINITIONS.md#kep-d3-knowledge-identity) | It is who the protocol recognizes over time, not whichever key they use today. |
| KEP-D4 | identity encryption-key binding | active | [Identity Encryption-Key Binding](DEFINITIONS.md#kep-d4-identity-encryption-key-binding) | It is the dated receipt saying which lock currently belongs to this identity. |
| KEP-D5 | knowledge co-ownership | active | [Knowledge Co-Ownership](DEFINITIONS.md#kep-d5-knowledge-co-ownership) | The artifact gains another recognized owner; the original owner does not lose their place. |
| KEP-D6 | co-ownership grant | active | [Co-Ownership Grant](DEFINITIONS.md#kep-d6-co-ownership-grant) | It is the governed act that changes `{A}` into `{A, B}`—not a handover from A to B. |
| KEP-D7 | propagation policy | active | [Propagation Policy](DEFINITIONS.md#kep-d7-propagation-policy) | It is the original creator's fixed rulebook for how this exact edition may spread. |
| KEP-D8 | content-addressed ciphertext reference | active | [Content-Addressed Ciphertext Reference](DEFINITIONS.md#kep-d8-content-addressed-ciphertext-reference) | It is a tamper-evident address for the encrypted package, not a promise that the package will always be there. |
| KEP-D9 | recipient key envelope | active | [Recipient Key Envelope](DEFINITIONS.md#kep-d9-recipient-key-envelope) | It is one sealed copy of the artifact key made for one recipient's current lock. |
| KEP-D10 | encryption epoch | active | [Encryption Epoch](DEFINITIONS.md#kep-d10-encryption-epoch) | It is one complete generation of locks and sealed keys for the same exact knowledge edition. |
| KEP-D11 | key reissue | active | [Key Reissue](DEFINITIONS.md#kep-d11-key-reissue) | It gives the same owner a new sealed key without changing who owns what. |
| KEP-D12 | decryption acknowledgement | active | [Decryption Acknowledgement](DEFINITIONS.md#kep-d12-decryption-acknowledgement) | It is B's signed receipt for this exact encrypted delivery, not proof of everything that happened afterward. |

## Alias Lookup

| Alias | Definition ID |
| --- | --- |
| knowledge artifact | KEP-D1 |
| governed knowledge artifact | KEP-D1 |
| tradable knowledge artifact | KEP-D1 |
| knowledge artifact version | KEP-D2 |
| artifact version | KEP-D2 |
| immutable knowledge version | KEP-D2 |
| knowledge identity | KEP-D3 |
| protocol knowledge identity | KEP-D3 |
| knowledge subject identity | KEP-D3 |
| identity encryption-key binding | KEP-D4 |
| encryption-key binding | KEP-D4 |
| recipient key binding | KEP-D4 |
| knowledge co-ownership | KEP-D5 |
| artifact co-ownership | KEP-D5 |
| co-owner membership | KEP-D5 |
| co-ownership grant | KEP-D6 |
| knowledge co-ownership grant | KEP-D6 |
| owner-set expansion | KEP-D6 |
| propagation policy | KEP-D7 |
| artifact propagation policy | KEP-D7 |
| originator propagation rules | KEP-D7 |
| content-addressed ciphertext reference | KEP-D8 |
| ciphertext reference | KEP-D8 |
| external ciphertext commitment | KEP-D8 |
| recipient key envelope | KEP-D9 |
| key envelope | KEP-D9 |
| wrapped content key | KEP-D9 |
| encryption epoch | KEP-D10 |
| artifact encryption epoch | KEP-D10 |
| content-key epoch | KEP-D10 |
| key reissue | KEP-D11 |
| recipient key reissue | KEP-D11 |
| lost-key reissue | KEP-D11 |
| decryption acknowledgement | KEP-D12 |
| recipient decryption acknowledgement | KEP-D12 |
| delivery acknowledgement | KEP-D12 |

## Governance Notes

- Product-local terms remain owned here until a separate CyberAlchemy-v2
  promotion decision says otherwise.
- Business ontology records must bind exact definition IDs and a digest of the
  canonical definition set before admission.
- Withdrawn parent IDs `CAV2-D70` through `CAV2-D81` are migration
  tombstones, not aliases for these product-local IDs.

