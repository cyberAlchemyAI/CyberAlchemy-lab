# Runtime completion audit

Admission update: the exact build documented below was subsequently owner admitted by [Decision 0075](../../decisions/0075-lab-operational-runtime-v1-admission/DECISION.md). The audit remains evidence of the original D74-bound candidate build; the external admission supplies its current implementation status. No reviewed package bytes or validation claims were changed.

Status: complete and verified software candidate, 2026-10-07. All A–L requirements have implementation and verification evidence. This audit covers the complete candidate local runtime in Plan 0008. It does not admit the implementation, promote local operational records into repository authority, or activate a product service.

## Requirement evidence

All implementation paths below are relative to `implementation/lab-runtime/v1/`. Test names refer to `tests/test_runtime.py`; exact results and package hashes are recorded in `receipts/validation.json`.

| DAG node | Delivered evidence | Verification |
| --- | --- | --- |
| A — Requirements and source baseline | `PLAN.md`, machine DAG, source `profile.json`; explicit four D71–D74 roots, current schema bindings, source epoch and independent state tracks. | Real `lab.py status` identifies Decision 0074, 468 subjects, 698 verified materials, current freshness and no initialized default store. `test_real_d74_baseline_and_catalog`. |
| B — Implementation analysis | `IMPLEMENTATION-ANALYSIS.md`: governance projector, D74 builder, v4 immutable ontology store and Rust graph candidate inspected; reuse and adaptation gaps stated. | Concrete inspected paths and schema-fit findings recorded; no Lab Rust adapter claimed. |
| C — Reviewed plan | `PLAN-REVIEW.md`: full scope retained; corrected D74 baseline, schema selectors, local authority, atomicity, closed graph and ephemeral memory. | Written review follows analysis; dependencies and completion criteria match the executable work. |
| D — Closed contracts | `CONTRACT.md`, `profile.json`, six exported interface schemas, `lab_runtime/protocols.py`, current admitted carrier checks in `sources.py`/`operations.py`. | Schema export parity in `validate.py`; tests for malformed records, duplicate JSON keys, remote schema refusal, closed qualifiers, axis collapse and explicit relation extension. |
| E — Effective state resolver | `lab_runtime/sources.py`: immutable capture, all three registries, exact overlays, history validation, historical revisions, carrier selectors and source freshness. | Real D74 counts; `test_snapshot_is_deterministic`, `test_source_candidate_fields_do_not_override_admission`, source-drift and new-repository-epoch tests. |
| F — Immutable store and replay | `lab_runtime/store.py`, `common.py`: complete immutable transaction envelopes, digest chain, one atomic HEAD, configuration/source bindings, deterministic replay. | Atomic-consequence/fresh-process replay, baseline/transaction tampering, configuration/HEAD integrity and idempotency tests. |
| G — Three lenses and bounded queries | `lab_runtime/graph.py`, `cli.py`: source/contract/Decision/implementation trace links, Authority/Provenance/Lifecycle, exact global connections, bounded directed traversal and disposable rebuild. | `test_three_lenses_and_unresolved_versions`, `test_traversal_limits_and_actual_direction`, `test_rebuild_is_disposable_and_deterministic`; real query summaries in `evidence/repository-read.json`. |
| H — Proposals and authorization | `operations.py` and `store.py`: dry review, independent stable Decision cores, complete proposal/base/snapshot/scope/policy/challenge/store/operator signature binding. | Wrong operator/private-key boundary, stale HEAD/tampered approval, target drift, scope/policy rejection and multi-target review tests. Local configuration custody is the trust root. |
| I — Transactions and consequences | `operations.py`, `governance.py`: all five target categories; admit/revise/withdraw; state, both histories, Generated Output, Admission Transaction, Decisions/scopes/bundle/checkpoint/boundary, six declared Typed Relations and receipt. | Definition, new type/instance, Relation Kind revision/extension, Typed Relation, historical revision/withdrawal and multi-target atomic-checkpoint tests. Demo binds 16 generated records for one target. |
| J — Recovery and concurrency | `store.py`: exclusive writer lock, expected HEAD, recognized pending/orphan recovery, unknown future material preservation and committed-history verification. | Three interruption positions, fresh-process replay, declared grant/recovery limits, idempotency and exclusive-writer tests. Scope is process interruption on the inspected filesystem. |
| K — Ephemeral sessions | `session.py`: schema-valid Context/Ontology views and Agent records, source/head/TTL checks, bounded process memory, clear-on-close/expiry and empty next session. | Ephemeral-memory/expiry and changed-HEAD session tests; disposable demo reconstructs context, closes session and erases its note. |
| L — Integration and completion | `lab.py`, operator `README.md`, `validate.py`, `demo.py`, exact receipt, this audit and synchronized DAG. | Full isolated suite and demo; final package hash check, real source verification, repository authority unchanged and Git whitespace check. |

## Real repository read

The read evidence captures `project-state:cyberalchemy-v2-to-lab-migration:decision-0074`, with semantic and governance histories each at cursor 4. Its source snapshot digest is `bf705b1cb60b21069c9175818f5d73cf1babb4c9ca0fff2b747db565ef20ba18`. There are 189 Definition versions / 183 current identities, 143 type contracts / 121 current, and 41 Relation Kinds in the selected registries.

The three default lens queries are **partial**, with explicit bounds and ten diagnostics. Existing ambiguous version references and unresolved Definition bindings are reported; they do not authorize inferred connections. The selected source envelope is not a complete ontology mapping of every repository area. Implementation-symbol links are candidate associations by subject kind, with observed-source/described-candidate posture and unevaluated conformance; they do not establish realization of each linked instance.

## Operational demonstration

The demo provisions an isolated owner key/store, prepares and reviews one planned Work target, signs its exact proposal, applies it, repeats identical bytes idempotently, and verifies replay in a fresh process. Its local successor state is `project-state:operational-demo:1`, with both history cursors at 5. It builds candidate Context/Ontology records and closes the ephemeral Agent session, erasing short memory. The temporary store/key are removed at exit. Repository admission effect, external effects and product runtime activations are zero.

## Verification environment

The initial full 33-test run passed with workspace `jsonschema` 4.19.2, which is below the declared minimum. It was therefore insufficient as the final installation evidence. Final validation uses an isolated environment installed from the package requirements, with `jsonschema` 4.26.0 and `cryptography` 48.0.1. The final receipt supersedes the initial run and binds actual test outcomes, demonstration, dependency versions and unchanged package bytes.

Final result: **PASS**, 33 tests and the disposable demonstration, 499.460 seconds. Package manifest digest: `ed552d46f18becd3e8f6206e0b069e190ff0c489530c70c2ae434a5938748864`. All 24 manifest files remained unchanged during validation. `pip check` reported no broken requirements. The demonstrated source snapshot matches the real D74 read evidence. Repository authority and Decision files have no changes from the checkpoint; the default operational store is uninitialized.

## Delivery boundary

The software candidate supports the complete reviewed local operational scope. Its durable state belongs to an explicitly provisioned local branch. Canonical repository authority remains at D74; adopting this implementation or publishing a local transaction back to repository authority needs an exact admission review. Network services, general organizational permission evaluation, multi-host writes, power-loss validation and the optional Rust graph adapter are outside this implementation contract. New repository authority epochs invalidate a frozen store and require a reviewed source-profile update and fresh store.

No operator key or permanent store was provisioned in this repository by the build. The reproducible operator flow is in the runtime guide. These boundaries do not prevent read commands from inspecting the real admitted baseline immediately.

## Reproduce from repository root

```bash
python3 -m venv .local/lab-runtime/venv
.local/lab-runtime/venv/bin/pip install -r implementation/lab-runtime/v1/requirements.txt
.local/lab-runtime/venv/bin/python implementation/lab-runtime/v1/lab.py status
.local/lab-runtime/venv/bin/python implementation/lab-runtime/v1/validate.py --write-receipt
```

The virtual environment is ignored local setup. The validation command replaces only the candidate validation receipt after repeating the suite and disposable demo. It does not publish an authority admission.
