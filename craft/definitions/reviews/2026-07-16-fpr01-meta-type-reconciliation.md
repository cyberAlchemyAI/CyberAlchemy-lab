# Definitions Governance Result — FPR01 Meta-Type Reconciliation

Date: 2026-07-16
Status: completed-with-external-residue
Owner route: definitions-governance
Trigger: `BLK-FPR01003-001`
Canonical machine source: `definitions/meta-types/meta-types.yml`
Human companion: `definitions/meta-types/meta-types.md`
Accepted decision: `development/first-production-release/evidence/FPR01-OWNER-DISPOSITIONS-DECISION.md`

## Outcome

The canonical DS-D1 machine registry, three-voice human companion, definition summary,
index, drift audit, and learning projection now agree on the accepted FPR-01 baseline:

- 24 staged labels;
- 13 active backend IDs: `DS-D1.1..9` plus `DS-D1.11..14`;
- one explicit, superseded, non-reusable `DS-D1.10` stable ID;
- nine non-active UI candidates: `DS-D1.15..23`;
- `DS-D1.24` as `deferred/merge-candidate` toward Mapping;
- `DS-D1.25` as `deferred/split-candidate`; and
- 30 active relationship signatures described as a typed composable graph fragment.

`BLK-FPR01003-001` is resolved at the definitions and validator surfaces. Continuation
state was not synchronized by this run, and `SWU-FPR01-003` remains blocked by its two
other owner-routed blockers.

## Definitions Updated

- `DS-D1` registry status and maturity partition;
- `DS-D1.1..9` and `DS-D1.11..14` current status;
- `DS-D1.10` stable superseded-ID card;
- `DS-D1.15..23` candidate cards;
- `DS-D1.24` deferred merge-candidate card;
- `DS-D1.25` deferred split-candidate card;
- `domainspec-v2-D6` and `domainspec-v2-D7` staged-count wording;
- `domainspec-v2-D9` and `domainspec-v2-D19` relationship-count wording; and
- the `DS-D1` summary in `DEFINITIONS.md`.

Every new or reconciled DS-D1 human entry carries a formal voice, plain-language
voice, DomainSpec-context voice, and explicit misuse/promotion boundary. Candidate and
deferred entries remain visibly non-active.

## Index And Drift

`DEFINITIONS-INDEX.md` now contains one row for every stable ID `DS-D1.1..25`, with
the active set intentionally non-contiguous. Its status vocabulary includes explicit
deferred and superseded states.

`DEFINITION-DRIFT-AUDIT.md` now checks the machine/human DS-D1 pair and records the
13/1/9/1/1 maturity partition plus the 30-signature DS-D8 baseline. The focused live
scan found no remaining 25-label, 14-backend, uniform-UI, or 31-signature claim in the
owned definition/index/audit/learning surfaces.

## Downstream Consumer Synchronization

Changing the canonical registry bytes invalidated the minted-project supported-profile
binding. The following live projections were rebound and their deterministic expected
graph, provenance, Markdown metadata, and receipt digests were cascaded:

- `definitions/minted-project/supported-profiles.yml`;
- the Key-and-Door positive contract fixture;
- the Message-Delivery positive conformance fixture; and
- the source-path-escape negative fixture.

Historical receipts, context packs, preregistrations, and research artifacts retain
their original digests and were not rewritten as current evidence.

## Undefined Critical Terms

No new undefined term was used as authority. `feature / bounded context` and `concept
individuation cue` remain explicitly proposed, non-canonical learning terms in
`impl/spec/meta-types/LEARNING-ORDER.md`; they are follow-up definition candidates, not
FPR01 authority inputs.

## Conflicting Consumers And Residue

1. The retired-reference guard still fails on seven exact files: four canonical
   superseded-ID surfaces that require narrow reviewed classification, plus three
   pre-existing evidence/research files. No allowlist or broad exception was added.
2. The sample engine lint still rejects two missing normalized tables in
   `impl/spec/features/sample/SPEC.md`.
3. `impl/spec/TAXONOMY.md` remains a transitional non-authority with retirement
   conditions still open. Backend-card references and the agent-execution fixture must
   be repointed or removed before its deletion gate can pass.

## Concept Registry Aggregation

Not applicable. This run reconciled the DS-D1 type registry; it did not aggregate or
mutate feature-level Concept Registry tables.

## Validation

- FPR01 canonical validator: PASS twice with identical normalized SHA-256
  `91de9e042b564e1bf85582e8ac360e55e1cafde101f960cbabfb231444b9df7c`.
- FPR01 mutant suite: PASS; all five fixtures killed.
- Documentation links: PASS.
- Relationship validation: PASS, 30 canonical signatures.
- Content validation: PASS, 20 concepts / 14 edges / 13 schemas.
- Instance validation: PASS, 13 instances.
- Meta-type non-collapse: PASS, 13 types / 78 pairs / zero collapse candidates.
- TypeScript typecheck: PASS.
- Minted-project focused suite: PASS, 30/30.
- Full tools suite: 99/101; the two failures are both the known retired-reference
  guard condition.
- Sample engine lint: expected FAIL on the separate two-table normalization blocker.

## Boundary

This result does not ratify FPR-01, grant production authority, select FPR01-004,
delete the transitional taxonomy, classify retired references, repair the sample
feature, or synchronize Craft/roadmap continuation state.
