<!-- GENERATED FILE: edit definition.json and run the bound generator. -->

# Withdrawal Record

> Human projection generated from the machine-canonical `definition.json`.

- Definition ID: `cal.definition.withdrawal-record`
- Version: `1.0.0-candidate.1`
- Semantic owner: `role:definition-owner`
- Authority scope: `scope:withdrawal-record-definition`
- Lifecycle posture reference: `CAL-LIFECYCLE-DEFINITION-V1:candidate-authored`

## Scientific/formal voice

A Withdrawal Record is a permanent governance and lineage record that reserves one retired or rejected identifier, binds the exact withdrawn subject and digest when available, states the reason and effective time, names any successor authority, preserves evidence and owner decision, and exposes a challenge route. It does not delete history, erase prior references, reuse the identifier, imply a successor exists, or automatically supersede another subject.

```text
WithdrawalRecord(x) => governed(x) and bounded(x); WithdrawalRecord(x) =/=> authority_effect(x).
```

### Notation

| Symbol | Meaning |
| --- | --- |
| x | One subject evaluated under the Withdrawal Record contract. |

### Boundary conditions

- The withdrawn identifier remains permanently reserved unless an explicit higher-order recovery rule permits restoration.
- A successor reference states lineage or replacement routing and does not merge identities.
- The record remains resolvable for historical consumers after the withdrawn subject becomes inactive.

### Testable conditions

- Every Withdrawal Record names one exact identifier, withdrawal posture, reason, effective time, owner Decision, evidence, and challenge route.
- Identifier reuse is rejected while the Withdrawal Record is effective.
- A claimed successor resolves independently and retains its own identity and admission state.
- Historical references can resolve the withdrawal disposition without loading a deleted subject.

## Plain-language voice

A Withdrawal Record is a permanent governance and lineage record that reserves one retired or rejected identifier, binds the exact withdrawn subject and digest when available, states the reason and effective time, names any successor authority, preserves evidence and owner decision, and exposes a challenge route. It does not delete history, erase prior references, reuse the identifier, imply a successor exists, or automatically supersede another subject.

## Domain-context voice

Workspace: `/home/vlad_/projects/CyberAlchemy-lab`

Withdrawal Record receives its own positive meaning so its carrier no longer borrows a broader Definition as its primary semantic identity.

### Examples

- withdrawal:CAV2-D70 permanently reserves CAV2-D70, binds its last known digest and owner decision, and routes consumers to a named successor only when that successor is independently admitted.

## Applicability

A Withdrawal Record is a permanent governance and lineage record that reserves one retired or rejected identifier, binds the exact withdrawn subject and digest when available, states the reason and effective time, names any successor authority, preserves evidence and owner decision, and exposes a challenge route.

### Exclusions

- It does not delete history, erase prior references, reuse the identifier, imply a successor exists, or automatically supersede another subject.
- Withdrawal is distinct from deprecation, rejection, suspension, deletion, archival, and ordinary lifecycle closure.
- This Definition does not admit a carrier, instance, relation, runtime, consumer, publication, or deployment.

## Boundaries

- The withdrawn identifier remains permanently reserved unless an explicit higher-order recovery rule permits restoration.
- A successor reference states lineage or replacement routing and does not merge identities.
- The record remains resolvable for historical consumers after the withdrawn subject becomes inactive.

## Sources

| Source | Selector | Digest | Admission posture |
| --- | --- | --- | --- |
| cal.source.step3.normalization | whole-file | `c1021431d8d33ee1e7c8bc6caf3ca0e89cba20e840a9360a2cefbff240cb5016` | `candidate-unadmitted` |

## Primary consumers

- CAL-DEFINITION-SPECIALIZATION-RESOLUTION-0014

## Lookup and drift

- Index: `authority/definitions/candidates/0014-definition-specialization-resolution/DEFINITIONS-INDEX.md` / `cal.definition.withdrawal-record@1.0.0-candidate.1`
- Drift owner: `role:definition-owner`
- Audit: `authority/definitions/candidates/0014-definition-specialization-resolution/drift-audit-postimage.json`
- Challenge route: `CA2-ROUTE-DEFINITIONS`

## Typed relations

No typed relations declared.

## Evidence

- docs/normalizations/0001-definition-migration-model/normalization.json
- .arcanum/ontology-vault/2026-10-06-lab-semantic-gap-audit.md

## Residue

- Definition-owner admission remains required.
- Artifact Type rebinding and admission remain separate.

## Claim ceiling

This candidate defines Withdrawal Record for Step 3 review only and has no admission or downstream activation effect.
