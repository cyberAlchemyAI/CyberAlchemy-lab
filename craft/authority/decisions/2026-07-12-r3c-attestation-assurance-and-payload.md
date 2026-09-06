---
node_type: decision
is_session: false
status: pass
boundary: INTERNAL — DomainSpec v2 authority attestation route
created: 2026-07-12
timestamp: 2026-07-12T19:24:49Z
decision_id: DEC-R3C-ATTESTATION-ASSURANCE-PAYLOAD
target_scope: BLK-DSV2-L2-ATTESTATION / SWU-R3C-010
source: operator choices in decision-gate, 2026-07-12
---

# Decision: R3C Attestation Assurance And Payload

## Consequential work

SWU-R3C-010 cannot produce an honest attestation handoff until the accepted
assurance rung and exact sealed payload are explicit. The repository already
has a demonstrated L1 integrity-seal capability, but its L2 external
actor-identity signature remains intended-not-shipped.

## Decision 1: assurance rung for R3 closeout

### Considered options

1. Use the demonstrated L1 integrity seal now and track L2 external signature
   separately.
2. Require the full L2 external actor-identity signature before R3 closeout.
3. Defer all attestation and produce only a blocked handoff.

### Selected option

**Option 1 — use L1 now; track L2 separately.**

### Rationale and consequence

The L1 capability has a real discriminating witness: the untampered fixture
verifies as `valid`, while a content mutation verifies as `tampered`. It can
therefore produce an honest integrity seal for SWU-R3C-010. It cannot prove who
signed the tuple. The R3 closeout may proceed with an L1 seal and an explicit
FLAG, while `BLK-DSV2-L2-ATTESTATION` is refined to the remaining external
actor-identity signature capability rather than falsely closed.

This decision does not authorize the words “externally signed,” “actor
authenticated,” or “L2 sealed” for the L1 result.

## Decision 2: exact L1 payload

### Considered options

1. Seal only the owner-ratification record.
2. Seal a deterministic manifest binding the mint proposal and owner
   ratification records.
3. Seal a full authority-state manifest.

### Selected option

**Option 2 — deterministic proposal→ratification manifest.**

### Rationale and consequence

The manifest must bind both governance acts without copying the broader
authority tree: the mint proposal states the three proposed domain-local kinds,
and the owner record ratifies those exact kinds. A deterministic manifest keeps
that provenance edge explicit while avoiding the unrelated-drift and snapshot
fragility of a full authority bundle.

SWU-R3C-010 must make the manifest independently checkable against both source
records before sealing it. Verifying only a manifest whose source digests were
never recomputed would be vacuous.

## Assumptions recorded

- The L1 `actor` field uses the stable role label
  `domainspec-v2-authority-owner`, matching the ratification record. At L1 this
  is metadata, not cryptographic identity proof.
- The manifest records repository-relative source paths, canonical content
  digests under `attest.canon.v1`, the three ratified kind names, and the
  proposal→ratification relation.
- The attestation artifact lives with the private DomainSpec v2 authority
  evidence and must never be copied to public `arcanum/`.
- Implementation-level filename and JSON field ordering are reversible details,
  provided the manifest is deterministic and source verification is runnable.

## Remaining blocker

`BLK-DSV2-L2-ATTESTATION` remains open but narrows to the genuinely unbuilt L2
capability: an external actor-identity signature, key/identity model, and
third-party verification procedure. It blocks a full L2 authority seal, not the
R3 backend graph-verification closeout or the L1 integrity receipt.

## Validation and next route

- Decision Gate: **PASS** — two blocker decisions resolved by the operator.
- Deferred decision: L2 identity/signing scheme; not needed for the selected L1
  SWU-R3C-010 route.
- Next: execute SWU-R3C-010 with `task-session`: build and verify the
  deterministic two-record manifest, produce the L1 attestation artifact and
  tamper-control receipt, refine the blocker without closing it, then route to
  SWU-R3C-011 final verification.

## Source evidence

- `cyberAlchemy-v2/development/attestation-capability/development/TASK-SESSION-L1.md`
- `cyberAlchemy-v2/development/attestation-capability/development/specimen/DEMO.md`
- `cyberAlchemy-v2/development/attestation-capability/SPEC.md`
- `cyberAlchemy-v2/authority/decisions/2026-06-29-mint-signer-and-boundary.md`
- `projects/domainspec-v2/authority/decisions/2026-06-29-mint.md`
- `projects/domainspec-v2/authority/decisions/2026-06-29-ratify-governance-kinds.md`
- `projects/domainspec-v2/authority/AUTHORITY-MODEL.md`
