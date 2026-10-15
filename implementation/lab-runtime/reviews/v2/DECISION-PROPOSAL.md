# Proposed admission: Lab Operational Runtime/v2

Status: candidate proposal; no owner authorization is recorded by this document.

## Review

- [Revised implementation and example](../../v2/REVIEW.md)
- [Candidate Implementation record](implementation.json)
- [Exact target and evidence bindings](target.json)
- [Validation receipt](../../v2/receipts/validation.json)
- [Repository source inspection](../../v2/receipts/source-inspection.json)

## Proposed decision

Admit Lab Operational Runtime/v2, with its frozen D75 source profile, as an implementation for local repository inspection, explicitly authorized local transactions, verified local replay/recovery and ephemeral Agent context, bound to its exact reviewed target and validation evidence. Preserve the exact admitted v1 implementation and separate implementation admission from source-profile selection, operator provisioning, capability adoption and runtime activation.

## Effect boundary

One implementation admission can produce its declared deterministic governance, Project State, history, index and relation consequences. No additional bookkeeping approval is required. Provisioning a permanent operator/store, changing canonical vocabulary, asserting product realization, publishing or starting a service is outside this proposed admission.

The executable is frozen to D75. A repository admission advances the repository epoch; operating from that later State needs an explicitly reviewed source-profile selection/update and a fresh local baseline. This candidate does not silently discover or adopt future admission roots. Its package release label and the eventual admitted artifact revision remain distinct.

Validation demonstrates local process interruption and verified replay on this filesystem. It does not establish power-loss durability, multi-host writing or complete ontology coverage. Earlier unresolved source references remain diagnostics.

## Observed performance boundary

The complete 38-check suite and demonstration took 1102.787 seconds with six isolated workers. The longest check, `test_runtime.RuntimeTests.test_revision_and_withdrawal_keep_old_bytes`, took 534.455 seconds; it repeatedly verifies a three-transaction revision/withdrawal history. These are integration-check timings, not per-operation latency benchmarks.

Full replay regenerates and validates each committed transaction's consequences on every read. The candidate has passing correctness evidence within its declared local scope, but replay performance and scaling remain a hardening frontier. Admission should not assert production throughput.
