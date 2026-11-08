---
artifact_role: authority-attestation-result
task: SWU-R3C-010
result: pass-l1-integrity
created: 2026-07-12
boundary: private
---

# DomainSpec v2 Governance Kinds — L1 Integrity Result

## Result

**PASS at L1 integrity.** A deterministic manifest binds the 2026-06-29 mint
proposal to the separate owner-ratification act for Validation governance,
Layering governance, and Drift governance.

Both live sources match their pinned `attest.canon.v1` digests. Regenerating
the attestation produces the same artifact. The exact manifest verifies
`valid`; a content-mutated relation verifies `tampered`.

## Evidence

- [manifest](manifest.json)
- [L1 attestation artifact](attestation.json)
- [machine verification receipt](verification-receipt.json)
- [content-mutated control](controls/manifest.content-mutated.json)
- [private source verifier](verify_manifest.py)

## Claim boundary

The `actor` value is stable role metadata. L1 proves tamper-evident integrity
of the sealed tuple; it does **not** cryptographically authenticate an external
actor. `BLK-DSV2-L2-ATTESTATION` remains active for actor identity, key custody,
signature production, and `bad-signature` / `unknown-actor` verification.

The original mint and ratification decisions were not edited. No private
mechanism or DomainSpec authority prose was copied into public `arcanum/`.
