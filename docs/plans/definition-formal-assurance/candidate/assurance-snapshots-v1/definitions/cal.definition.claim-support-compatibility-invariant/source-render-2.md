<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Claim-Support Compatibility Invariant

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.claim-support-compatibility-invariant`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope.shared-authority`
- Lifecycle posture reference: `candidate:artifact-reconstruction-l1/v1`

## Scientific/formal voice

Claim-Support Compatibility Invariant is the normalized invariant identified by semantic.claim-support-compatibility-invariant, owned within scope.shared-authority, and carried by type.invariant. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D38 without silently merging it with another target.

Bound source-semantic basis:

Claim <= proof is the CyberAlchemy v2 epistemic invariant that a claim's
asserted strength, authority effect, validation status, or publication posture
must not exceed the proof, evidence, witness, validation result, owner decision,
or accepted premise cited for it.

If support is absent, partial, private, indirect, disputed, or weaker than the
claim, the claim must be downgraded, marked as hypothesis or candidate,
flagged with residue, routed through a gate, or blocked from governing work.

```text
For claim `c`, asserted strength `S(c)`, and support package `P(c)`:

```text
S(c) <= strength(P(c))
```

where `strength(P(c))` is interpreted by the relevant domain, validator,
research standard, owner decision, or constitution. If no support package is
declared, `S(c)` defaults to candidate or hypothesis.
```

### Notation

| Symbol | Meaning |
| --- | --- |
| semantic.claim-support-compatibility-invariant | Stable normalized identity for Claim-Support Compatibility Invariant. |
| CAV2-D38 | Bound CyberAlchemy-v2 source-definition identity. |

### Boundary conditions

- Proof does not mean only formal mathematical proof. It can be a source citation,
validation run, witness, owner decision, accepted premise, or formal proof,
depending on the claim type. The invariant does not require maximal certainty;
it requires honest wording relative to declared support.

### Testable conditions

- The candidate identity remains cal.definition.claim-support-compatibility-invariant.
- Every selected source-section digest remains current.
- The machine record validates against Definition/v1.
- The human projection is regenerated exactly from the machine record.

## Plain-language voice

Do not say more than the evidence can carry.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

In CyberAlchemy-lab migration work, Claim-Support Compatibility Invariant is a prototype meaning reconstructed from CAL-NORMALIZE-01. It remains non-authoritative until the correct Lab owner admits a fully validated candidate.

Source context retained for reconstruction:

In CyberAlchemy v2, claim <= proof prevents research synthesis, inventory
cards, ontology projections, generated indexes, successful commands, or owner
intuition from hardening into stronger authority than they earned. It is the
epistemic companion to provenance and gates: provenance shows the support
trail, gates decide movement, and claim <= proof bounds what the project is
allowed to say.

### Examples

- Resolve semantic.claim-support-compatibility-invariant by its machine identity rather than its directory name.
- Challenge source drift through the L1 drift audit before relying on Claim-Support Compatibility Invariant.

## Applicability

Use claim <= proof when writing research findings, definitions, constitutions,
validation reports, ontology projections, public statements, or implementation
readiness notes. The invariant forces the project to ask: what exactly supports
this claim, and how strong may the wording be?

### Exclusions

- Admission, activation, publication, release, deployment, and external effects.
- Meanings assigned to split or reclassified sibling targets unless explicitly referenced.

## Boundaries

- Proof does not mean only formal mathematical proof. It can be a source citation,
validation run, witness, owner decision, accepted premise, or formal proof,
depending on the claim type. The invariant does not require maximal certainty;
it requires honest wording relative to declared support.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cyberalchemy-v2:CAV2-D38 | ## CAV2-D38: Claim-Proof Bound | `de58dbca26577af6e991dca7f30a1b7dc41069c147532289777284d0d8b7d39a` | `candidate-unadmitted` |

## Primary consumers

- semantic.authority-promotion
- semantic.discipline
- semantic.interface-claim-support-compatibility-invariant
- semantic.invariant

## Lookup and drift

- Index: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/registry.json` / `cal.definition.claim-support-compatibility-invariant@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/drift-audit.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.originates-from | cal.definition.claim-support-compatibility-invariant | cyberalchemy-v2:CAV2-D38 | role:definition-owner |

## Evidence

- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0003-review-led-reconstruction/target-candidates/semantic/semantic-claim-support-compatibility-invariant/v1/artifact.json
- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/receipts/validation.json
- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/receipts/validation.json

## Residue

- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/drift-audit.json

## Claim ceiling

Candidate Definition reconstructed from an accepted normalization scaffold and exact CyberAlchemy-v2 source sections. It is not admitted and grants no implementation, migration, registry, publication, release, deployment, or external-effect authority.
