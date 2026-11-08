# Checked staged Reader loader0001 — independent static review

**PASS_BOUNDED_INERT_BUFFER_LOADER_ONLY.** Candidate freeze `34dc11dc1977b47ef67f7ab9b900945e86cb8afa618b8c8845af3b56f90e979c` and all three members rehashed unchanged. No SelectedReader instance was constructed, open_signed was not called, no private archive was opened, and no Docker/key/grant/AUTH effect occurred.

## Evidence and checked closure

Independent isolated normal and optimized Python3.14 replay each passed **15 tests**: nine supplied tests and six independent cases, actual OS exit 0. Exact commands, timestamps and raw streams are retained in execution-0002.json. An audit hook prohibited private archive opening and subprocess/socket/filesystem-mutation effects. Module execution was limited to the captured original import definitions and synthetic scope/copy-name fixtures.

Current capture verified the exact selected Reader manifest and Reader code pins; 940 Source manifest rows join the exact 948 Reader rows. Source package, engine manifest (45 entries) and parent-engine manifest bindings were checked. Capture returned 40 executable buffers and 85 metadata buffers, excluding branch.snapshot. The 85-buffer category includes parent-lineage Python files inspected as manifest evidence; it should not be read as 85 JSON-only configuration files. This is not full verification/virtualization of all 948 bodies.

The first independent probe was deliberately broad and rejected every staged `.py` read, including parent-lineage metadata reads in guard_metadata. Both resulting failures are preserved in check.py/execution.json. Inspection located the failure before imports in the permitted metadata guard, not a pathname executable fallback. The corrected probe resolves descriptor-relative paths and forbids reopening the exact 40 executable-buffer paths; it passes both modes. No candidate change was made to obtain that result.

## Import and substitution checks

Reader/Source package imports execute checked buffers through BufferLoader, with digest validation immediately before compile. Exact Source loader, engine loader and bridge names require their selected origins; unselected staged dynamic origins refuse. Synthetic temporary engine package names are mapped back to original captured runtime modules, not read from the synthetic copied pathname. Missing/changed origin, mutated buffer, stale/mutated metadata and copied-engine mapping cases passed.

Independent tests additionally verified all three named dynamic loader joins, refusal of a preloaded selected-name module while leaving that original object untouched, exact executable-path read denial, hook restoration and selected-module unloading. A metadata mutation during the context caused the final guard to refuse while restoring the finder/spec hook. These demonstrate the intended cooperative import context, not process security against arbitrary code altering sys.modules, meta_path, Capture dictionaries or third-party imports. Capture and its digest dictionaries are ordinary mutable Python objects, not independently authenticated authority.

The original open_signed method is located by exact selected code/module provenance. Synthetic signed scope accepts only the test shape and reports SYNTHETIC_SCOPE_ONLY_NOT_ATTESTED. open_actual_signed unconditionally refuses, and checked_modules requires effect-disabled state. Returning the real class for inspection does not sandbox a caller who invokes it; the review and test harness never do so.

## Explicit unresolved effect gates

The observed host environment is Python 3.14.4 / jsonschema 4.19.2 / cryptography 46.0.5. The Source requires Python 3.14.4 / jsonschema 4.23.0 / cryptography 46.0.5. host_environment_matches=false is truthful; the real Source environment guard would reject this host. No dependency was installed, altered or silently substituted. A future effect must select and qualify a matching runtime/import closure.

The original Reader/Source later open manifest files and the selected private archive by pathname. This unit neither virtualizes those reads nor establishes continuous namespace custody for the whole Source/Reader family. Held nofollow capture checks each selected read's bytes/leaf identity but does not prove hostile same-UID exclusion or immutable ancestor attachment throughout a future Reader invocation. Temporary engine path interception supplies code buffers; it does not qualify engine capture's later I/O, original source currentness, cryptographic signed view or successful private close.

Source currentness was checked during capture and expires 2026-10-21T15:00:00Z exclusive; this is not a lease or later effect authorization. Third-party distributions remain outside the 40-buffer closure. Signed scope, issuer/grant, durable attempt/attestation, issued AUTH and downstream JIT remain separate gaps. This review accepts only the inert loader slice and permits no private reopen or original-task completion claim.
