# Independent caller integration review

Result: **FLAG — import failure leaves synthetic module registrations behind.** This is a static availability/retry finding, not an integrity bypass claim. No runtime module or callback alteration was performed to reproduce it.

At Source postimage lines 69–71, `_load_selected_capture` registers a deterministic kernel/caller module name before executing the selected module. There is no rollback if execution fails. Successful kernel/caller loading also occurs before the remaining Source native imports at lines 104–105. If later Source initialization fails, those registrations survive. Retrying the same Source name rejects the retained synthetic name at line 70. Normal Python cleanup of a failed outer Source import does not remove independently registered synthetic children.

Stage a new successor that tracks exactly the synthetic modules created by this Source import. On failure, remove a registration only if it still points at the exact created module. Cover both failure within helper execution and failure after successful kernel/caller loading during remaining Source initialization. Preserve the original exception and descriptor cleanup. Retain these frozen reviewed files.

The exact four supplied manifest/handoff identities and 50 nested file digest/size references passed fresh checks. Five selected postimages compiled without execution. Four delegation files remained byte-identical; Source changed only `_load_capture` and `_capture_identity`, added `_load_selected_capture`, and retained all original domain function ASTs. The selected explicit metadata dependency graph was acyclic.

The helper and caller use separately selected actual filenames and exact captured bytes. Source holds companion code/global/default/closure records outside the companion; the companion holds equivalent helper records outside the helper. Successful original capture and whole-input verification are bracketed by held-contract checks. Canonical closed input rows, explicit external inputs, duplicate checks, ordered fresh digests, attachment checks, and invocation-local directory reuse remain present. Ordinary file/open/stat/hash error paths close held file descriptors, and the helper scope clears its active state through saved cleanup primitives.

Existing frozen records report 24 installed helper controls and 11 installed Source-prefix controls with zero descriptor delta. This review checked those records and their exact metadata; it did not rerun them or construct native software. True source closure, role/profile eligibility, new family recipes, native construction, full API or learning qualification, realistic timing calibration, and lease margin remain pending. No old signer, grant, period, authority or qualification transfers.

## Task Session Result

- Task: T03 caller-integration-0001 scoped independent implementation review.
- Result: FLAG, CR01 above.
- Decisions: none; new-candidate correction is recommended to the sole shared writer.
- Context pack: lean read-only context from exact helper/caller Source code, selected preimages/postimages, manifests, handoffs, controls and T03 contract.
- Strict coverage: pass for this bounded static review; full T03 qualification is outside this delegation.
- Runtime: local static checks; no runtime handoff adapter.
- Gate verdict: permitted review and uniquely owned report only.
- Files updated: this directory only; no frozen metadata or shared status edits.
- Validation: 50 nested digest/size bindings, selected top-level identities, five compile-only postimage checks, Source AST preservation, four byte equality checks and acyclic explicit metadata references passed.
- Experiment harness: not_run; prohibited broader experiment was not repeated.
- Synchronized records: none; root coordinator owns shared synchronization.
- Follow-up: stage and review import-failure rollback correction, then continue separate recipe/native/profile/learning/performance gates.

Machine-readable evidence is in `review.json`. Its static compiled metadata fingerprints identify the review interpreter's compile output only and do not establish installed runtime eligibility.
