# P07 owned qualification and repeatability

## What the API adds

`OwnedQualifier(run_root, operator_policy).qualify(raw_request_bytes)` uses the unchanged P06 supervised mathematical pipeline and adds owned phase records, an independently anchored cache key and finalized read-only evidence. Its response uses the distinct `relational.owned-qualification/v3` schema. It carries the qualification result, supervisor report, completion binding, final owned-run binding and observed time including finalization. Application authorization remains false.

`OwnedQualifier.resume(phase_binding, raw_request_bytes)` validates the old phase inside the new supervised worker. It checks the original raw-byte identity, resource policy, exact source fingerprints, owner, chronological previous phases and bound outputs. It then allocates a new job and reruns fresh qualification. It does not resume by relabeling a saved result, reusing an actual witness as fresh compilation or restoring a process-local completion event.

`live_event(result)` requires this instance's exact live P06 completion event and a current completed owned run. A new API instance cannot reconstruct the event from saved files. The final inspector rechecks direct code/output bindings and the bound cache/imported-source references; inspection remains currentness, never a new theorem qualification or application capability.

## Cache authority

The expected local dependency manifest comes from the accepted P02 layout-equivalence report. Its digest is checked before reading the manifest's own declarations. Every one of the 35 retained source/compiled module pairs is checked before reuse. Imported Lean/Std artifacts come from the independently accepted P05 source report: 2,040 distinct toolchain bindings are included in the key and revalidated. A substituted file cannot supply its own new expected digest.

The cache key includes local source and compiled closure, imported toolchain closure, compiler binary, kernel shared library, canonical catalog, structured generator, layout and layout policy. A layout change changes the key. Cache presence never creates a fresh proof event; each successful run still compiles the actual witness and performs the fresh general replay.

The imported binding resolver may skip a repeated content hash only for an unchanged inode, size and modification timestamp with the same independently supplied expected digest. This is an optimization under the existing trusted-host/hash assumption. Final record inspection directly checks current bytes. Neither mechanism claims exclusion of a same-privilege hostile host.

## Records and permissions

An owner record names the unique job and an opaque ownership token. Each phase record is written exclusively, binds its predecessor, raw request, source/policy inputs, available outputs and cache observations, and states fresh_qualification false. A prepared owned-run record is created inside the worker after exact proof inspection. The parent finalizes an owned-run record after successful supervision and public issuance, or records the explicit nonqualified outcome for interrupted work.

Finalized files have mode 0400 and proof/job directories have mode 0500. The mediated API allocates new directories and rejects existing record writes. Byte checks detect later changes when evidence is reread. These are operational ownership/immutability controls; they do not prove filesystem durability or prevent an external writer with equivalent privileges. P08 supplies the transactional shadow head and crash-recovery design.

`inspect_record(binding)` returns recorded-current plus the recorded phase, fresh_qualification false and application_authorized false. It checks ownership, output containment, exact bindings and cache/import currentness. An arbitrary saved completed flag cannot create a live event.

`cleanup_proposal(binding, exact_job)` returns a review-only proposal. It rejects a different run, an escaped path and completed evidence. It performs no deletion. Historical accepted and unrelated directories remain preserved.

## Execution state

Normal execution synchronization writes accepted work, remaining_required, remaining_optional and resolved_optional separately. All seven user-selected extensions remain outstanding optional work until accepted. Only an actually unselected extension may be resolved as not-needed; it then appears in resolved_optional and is excluded from both outstanding lists. Required work cannot be resolved that way.

## CLI

`p07/cli.py --policy POLICY.json --request REQUEST.json --runs OWNED_RUN_DIRECTORY` accepts bounded raw transport files and returns the closed owned response. Mathematical decoding and checking remain inside the fixed supervised worker. A CLI process's saved output does not preserve a reusable live event after the process exits.
