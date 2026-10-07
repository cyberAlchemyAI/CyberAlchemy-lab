# Definitions status

This is a navigation view over the governed Definition registry. The authority
remains [`authority/definitions/registry.json`](../../../authority/definitions/registry.json)
and its generated human projection,
[`DEFINITIONS-INDEX.md`](../../../authority/definitions/DEFINITIONS-INDEX.md).

## Current governed state

- Registry status: `owner-admitted`
- Authority effect: `one-hundred-eighty-eight-exact-definition-versions-canonical`
- Latest admission: [`CAL-DECISION-0072-PROJECT-STATE-BOOTSTRAP-ADMISSION`](../../../docs/decisions/0072-project-state-bootstrap-admission/decision.json)
- Admitted Definition versions: **188**
- Distinct Definition identities: **182**
- Current lookup entries: **182**
- Pending Definition versions in the indexed authority and migration candidate trees: **0**
- Lifecycle state of every registered version: `admitted`

The version suffix `candidate.N` is part of an admitted version identity. It
does not mean the registered version is still unadmitted. Current lifecycle
state comes from the live registry's `lifecycle_state` field.

Six identities retain multiple admitted versions. The current lookup selects
the latest admitted version for each:

| Definition ID | Admitted versions | Current version |
| --- | ---: | --- |
| `cal.definition.artifact-surface-classification` | 2 | `1.0.0-candidate.2` |
| `cal.definition.artifact-type-request` | 2 | `1.0.0-candidate.2` |
| `cal.definition.artifact-type-resolution` | 2 | `1.0.0-candidate.2` |
| `cal.definition.bounded-context` | 2 | `2.0.0-candidate.1` |
| `cal.definition.canonical-package-manifest` | 2 | `1.0.0-candidate.2` |
| `cal.definition.context-map` | 2 | `2.0.0-candidate.1` |

The complete term-by-term table and current lookup are in the
[authoritative Definition index](../../../authority/definitions/DEFINITIONS-INDEX.md).

## Full-queue admission

Decision 0053 admitted the entire previously pending queue through an additive
authority overlay:

| Cohort | Versions admitted | Identities added |
| --- | ---: | ---: |
| Authority Definition candidates | 15 | 11 |
| Reconstructed CyberAlchemy v2 Definitions | 70 | 70 |
| **Total** | **85** | **81** |

The transaction also admitted 58 exact source selections for Definition use.
Fifty-seven selections resolve to current source or concurrently admitted
Definition predecessors. The reconstructed `Axiom` version retains the exact
historical `CAV2-D53` bytes preserved in migration execution 0044 because the
current v2 D53 text has evolved.

`Append-Only Event Ledger` is now admitted as
`cal.definition.append-only-event-ledger-pattern@1.0.0-candidate.1`. Decision
0066 later admitted the broader `cal.definition.ledger` and
`cal.definition.withdrawal-record` meanings. The specific append-only event
pattern and the generic Ledger remain separate current Definitions.

## Admissions after the full queue

The live registry also includes the later Definition decisions that completed
the integrated Lab model and its first Project State transition:

| Decision | Definition effect | Current result |
| --- | ---: | --- |
| [`0064`](../../../docs/decisions/0064-typed-connection-extension-rule-admission/decision.json) | 1 | Typed Connection Extension Rule admitted |
| [`0065`](../../../docs/decisions/0065-integrated-lab-definition-model-admission/decision.json) | 60 | Integrated Lab semantic gaps admitted |
| [`0066`](../../../docs/decisions/0066-definition-specialization-resolution-admission/decision.json) | 7 | Specialization and ledger resolution admitted |
| [`0072`](../../../docs/decisions/0072-project-state-bootstrap-admission/decision.json) | 2 | Project semantic and governance event-history meanings admitted |

Decision 0072 deliberately defines Project-scoped histories separately from
the existing ontology-scoped semantic and governance histories. Its admitted
carriers record the first Project semantic event, the corresponding governance
event, and the successor Project State at Decision 0071. It activates no
runtime.

## Candidate package relationship

Candidate package records preserve their original candidate status even when a
later decision admits exact Definition versions from them. Use the live
registry to determine current authority, and the candidate record to inspect
construction history and claim limits.

| Candidate package or cohort | Versions in live registry | Package-record posture |
| --- | ---: | --- |
| `0001-definition-and-ctx00-v1` | 8 | historical candidate record; selected versions admitted |
| `0002-ctx06-context-map-reference-normalization` | 2 | historical candidate record; selected versions admitted |
| `0003-single-decision-checkpoint` | 8 | historical candidate record; all versions admitted |
| `0004-change-lifecycle-selection` | 0 | orchestration candidate; its referenced Definition versions live in other admitted packages |
| `0005-craft-workflow-interaction` | 5 | historical candidate record; selected versions admitted |
| `0006-craft-identity` | 6 | historical candidate record; selected versions admitted |
| `0007-cml07-semantic-closure` | 8 | historical candidate record; selected versions admitted |
| `0008-canonical-package-home` | 1 | historical candidate record; selected version admitted |
| `0009-artifact-surface-foundation` | 5 | historical candidate record; all versions admitted |
| `0010-artifact-surface-foundation-revision` | 4 | historical candidate record; all successor versions admitted and current |
| `0011-repository-migration-manifest` | 1 | historical candidate record; selected version admitted |
| `0012-typed-connection-extension-rule` | 1 | historical candidate record; selected version admitted by Decision 0064 |
| `0013-integrated-lab-definition-model` | 60 | historical candidate record; all versions admitted by Decision 0065 |
| `0014-definition-specialization-resolution` | 7 | historical candidate record; positive definitions admitted by Decision 0066 |
| `0015-project-state-event-histories` | 2 | historical candidate record; both versions admitted by Decision 0072 |
| Reconstruction pipeline `0004` | 70 | historical migration candidates; all Definition versions admitted |

## Remaining boundaries

Definition admission alone does not admit or activate Artifact Types, profiles,
relation kinds, derived surfaces, carriers, migration consumers, or runtimes.
Decisions 0070 through 0072 separately admit bounded downstream contracts and
instances through their own authority routes. Decision 0072 still creates no
Agent session, evidence claim, ontology projection, implementation adoption,
consumer activation, or runtime activation.

## Status rule

For a Definition, read status in this order:

1. Resolve the identity through `current_lookup` in the live registry.
2. Read the matching registry entry and its `lifecycle_state`.
3. Follow `admission_decision_ref` for the exact authority grant and limits.
4. Treat candidate packages and receipts as construction evidence unless a
   separate decision admits their exact bytes.

This inventory view grants no Definition authority and does not replace the
registry, admission decision, source admission, or drift audit.
