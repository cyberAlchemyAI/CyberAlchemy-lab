---
title: L1 — faithful baseline and repeatability
status: not-started
dependsOn: [L0]
---

# L1 — faithful baseline and repeatability

**Decision question:** After this layer, we know whether every declaration in a selected authority snapshot is represented faithfully, with repeatable checks and visible semantic gaps.

**Minimum working unit:** import the 41-kind selected snapshot, represent its 550 relation-specific pair entries without widening them, resolve the effective-state overlay, and replay identical normalized inputs deterministically.

## Purpose and boundary

L0 proves a small checker. L1 prevents that checker from becoming unreliable when applied to the real registry. Completeness here means complete declaration coverage for the selected snapshot. It does not mean every prose assertion has a proved mathematical interpretation.

The main concrete compatibility issue is Typed Relation/v2: its 40-kind conditional/enum surface excludes `materializes-consequence`. Treat this as a named coverage mismatch. A future carrier successor or explicit checker profile must account for it; copying or modifying immutable admitted bytes is not a resolution.

## Inputs and outputs

Inputs include the selected registry, its exact referenced kind records, the corresponding artifact-type contracts, effective admission context, selected instance inventory, and L0 semantics/checker modules.

Outputs are a normalized registry snapshot, field-preservation mapping, carrier coverage report, semantic coverage ledger, currentness/dependency inventory, reference-resolution results, and reproducible check receipts.

Every ledger row records the relation/version, exact pairs, qualifier fields, prose semantics, selected executable interpretation, required theorem IDs, evidence, and unresolved obligations. Keep statuses such as imported, structurally checked, semantically defined, proved, and unsupported distinct.

## Snapshot and normalization design

1. Read a selected baseline; verify each referenced record digest.
2. Preserve immutable source posture separately from registry effective state. A candidate source can be the exact payload an admitted registry selects.
3. Record registry selection and admission context; do not guess the newest authority from paths or timestamps.
4. Normalize pair sets without constructing their Cartesian product. Duplicate identical set entries are a source-integrity finding, not a reason to drop evidence silently.
5. Preserve assertion identities and exact versions. Similar names or shared endpoint labels do not imply identity equality.
6. Resolve only within an explicit source envelope. Missing, ambiguous, historical, and withdrawn references have different results.
7. Fail explicitly on an unknown kind or unsupported required semantics.

Start with a self-contained local snapshot adapter. The existing runtime resolver offers useful source-envelope patterns, but its frozen D74 binding is not proof of continuing freshness for every future epoch.

Canonical serialization must specify object-key ordering, array/set ordering, numeric/string handling, and duplicate-key rejection at decoding. A semantic digest includes the normalization version. A content hash can distinguish byte variants while a separately named normalized hash identifies their selected representation; neither should be called the unique semantic truth hash.

## Qualifier and schema alignment

Preserve declared syntactic types before introducing stronger semantics. In the current conformance record, `conformance_evidence_refs` is a nonempty string despite its plural name. Do not reinterpret it as an array silently. Record any desired contract improvement as a future proposal.

Compare registry kinds, carrier enum values, conditional branches, allowed pairs, and qualifier requirements. An enum entry without a semantics branch is also a mismatch even if it passes basic parsing. The report must distinguish rejection of a legitimate registry kind from underconstrained acceptance.

## Proof obligations

Extend the reusable checker theorem to the data-driven supported profile. Establish exact pair projection in both directions: every declared pair appears in normalization, and every normalized pair has a declared source. Analogous obligations cover required qualifiers and identifiers.

Executable round-trip/differential controls support parser fidelity; they do not replace a formal parsing theorem. State this boundary in the receipt. Check that normalization never creates wildcard permission or upgrades a reference to an evidence assessment.

If a prose property lacks a defined profile, import its text and mark its obligation unsupported. Overall readiness for an obligation requiring that property remains unresolved even when structural checks pass.

## Ordered implementation work

1. Build snapshot selection and effective-state resolution.
2. Create the registry/carrier coverage report and choose a scoped successor/profile path.
3. Generalize normalization and checker inputs from the three-kind slice.
4. Implement identity, version, scope, and reference closure.
5. Create the semantic coverage ledger and enforce aggregate obligation coverage.
6. Add deterministic replay and dependency invalidation.
7. Run differential controls against selected existing schemas, without rebuilding historical candidates.

## Validation and acceptance

Required controls include omitted registry entry, unmatched source hash, unknown kind, repeated identity, reversed pair, phantom pair, extra qualifier, ambiguous reference, stale endpoint version, and missing evidence interpretation.

Replay should preserve normalized theory and logical verdict for identical inputs. Execution logs may contain timestamps or resource measurements; compare their semantic portion rather than claiming byte-identical logs.

Completion requires all selected declarations mapped, all coverage discrepancies classified, no invented pair/qualifier, reproducible normalization, and a ledger identifying every unsupported required semantic property. Existing valid L0 cases must continue to work.

## Outcome, cost, and promotion

The operator receives dependable baseline checks and a precise list of what is not yet formalized. Risk reduced: silent omission and misuse of stale or ambiguous source state. Cost is medium to high, dominated by reference semantics and heterogeneous qualifiers.

Proceed to L2 for supported profiles after L1 closure. Do not wait for universal semantic formalization, but do not advertise a structural-only kind as semantically proved.

## Deferred scope

Proof of all prose meanings, optimized incremental decoding/checking, automatic authority discovery across unrelated stores, arbitrary external-reference retrieval, and full live-runtime adoption. Preserve L0 soundness and bind every extension to its selected semantic coverage.
