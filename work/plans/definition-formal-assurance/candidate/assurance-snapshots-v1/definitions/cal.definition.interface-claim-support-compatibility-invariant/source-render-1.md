<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Interface Claim-Support Compatibility Invariant

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.interface-claim-support-compatibility-invariant`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope.ux-ui`
- Lifecycle posture reference: `candidate:artifact-reconstruction-l1/v1`

## Scientific/formal voice

Interface Claim-Support Compatibility Invariant is the normalized invariant identified by semantic.interface-claim-support-compatibility-invariant, owned within scope.ux-ui, and carried by type.invariant. Any canonical instance must preserve that classification and the accepted source relations to CAV2-D47 without silently merging it with another target.

Bound source-semantic basis:

Interface evidence boundary is the CyberAlchemy v2 rule that UX/UI claims must
state which kind of evidence can support them and what that evidence cannot
prove.

At minimum, UX/UI claims must be classified as one of:

- hard gate
- soft flag
- screenshot review
- human study
- not automatable

Browser automation may directly support page-load, accessibility-tree,
keyboard, layout, interaction, screenshot, trace, console/network, and DOM
measurement claims. It may prepare evidence for cognitive, attention,
perception, trust, comprehension, delight, and real-user success claims, but it
must not turn them into deterministic authority without calibrated fixtures and
owner approval.

```text
For UX/UI claim `c`, let:

```text
IEB(c) = (claim_class, evidence_kind, proxy_limit, owner_route, residue)
```

The claim is valid only when `claim_class` matches `evidence_kind` and the
`proxy_limit` states what remains unproven. If the evidence class is weaker than
the claim, `CAV2-D38` requires downgrading, routing, or blocking the claim.
```

### Notation

| Symbol | Meaning |
| --- | --- |
| semantic.interface-claim-support-compatibility-invariant | Stable normalized identity for Interface Claim-Support Compatibility Invariant. |
| CAV2-D47 | Bound CyberAlchemy-v2 source-definition identity. |

### Boundary conditions

- Interface evidence boundary is not a validator implementation, not a complete
accessibility audit, not user research, not a universal UX score, and not a
license to block dense expert interfaces without false-positive calibration.

### Testable conditions

- The candidate identity remains cal.definition.interface-claim-support-compatibility-invariant.
- Every selected source-section digest remains current.
- The machine record validates against Definition/v1.
- The human projection is regenerated exactly from the machine record.

## Plain-language voice

A browser can show what happened on the page. It cannot by itself prove what a
human understood, trusted, felt, or preferred.

## Domain-context voice

Workspace: `/home/vrondelli/projects/CyberAlchemy-lab`

In CyberAlchemy-lab migration work, Interface Claim-Support Compatibility Invariant is a prototype meaning reconstructed from CAL-NORMALIZE-01. It remains non-authoritative until the correct Lab owner admits a fully validated candidate.

Source context retained for reconstruction:

In CyberAlchemy v2, this definition imports the evidence honesty model from
`ux-evidence-validator`: hard gates, soft flags, screenshot review, human
study, and not-automatable residue. It keeps UI validation useful without
collapsing browser evidence, accessibility, UX heuristics, and user research
into one false certainty.

### Examples

- Resolve semantic.interface-claim-support-compatibility-invariant by its machine identity rather than its directory name.
- Challenge source drift through the L1 drift audit before relying on Interface Claim-Support Compatibility Invariant.

## Applicability

Use interface evidence boundary when writing validator specs, Playwright
reports, UI review findings, UX pattern cards, screenshot reviews, or studio
mutation handoffs. Ask whether the claim is deterministic, a risk proxy, a
visual review prompt, a human-study need, or not automatable.

### Exclusions

- Admission, activation, publication, release, deployment, and external effects.
- Meanings assigned to split or reclassified sibling targets unless explicitly referenced.

## Boundaries

- Interface evidence boundary is not a validator implementation, not a complete
accessibility audit, not user research, not a universal UX score, and not a
license to block dense expert interfaces without false-positive calibration.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cyberalchemy-v2:CAV2-D47 | ## CAV2-D47: Interface Evidence Boundary | `f8d187d383d536b6e4271808161e7d103173380b89f3774692faefff76b37e2b` | `candidate-unadmitted` |

## Primary consumers

None declared.

## Lookup and drift

- Index: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/registry.json` / `cal.definition.interface-claim-support-compatibility-invariant@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/drift-audit.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

| Kind | From | To | Owner |
| --- | --- | --- | --- |
| relation.originates-from | cal.definition.interface-claim-support-compatibility-invariant | cyberalchemy-v2:CAV2-D47 | role:definition-owner |

## Evidence

- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0003-review-led-reconstruction/target-candidates/semantic/semantic-interface-claim-support-compatibility-invariant/v1/artifact.json
- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/receipts/validation.json
- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/receipts/validation.json

## Residue

- evidence/migrations/cyberalchemy-v2-to-lab/candidates/0004-artifact-reconstruction-pipeline/layers/l1-semantic-repeatability/drift-audit.json

## Claim ceiling

Candidate Definition reconstructed from an accepted normalization scaffold and exact CyberAlchemy-v2 source sections. It is not admitted and grants no implementation, migration, registry, publication, release, deployment, or external-effect authority.
