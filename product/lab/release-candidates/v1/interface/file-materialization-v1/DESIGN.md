# Candidate managed file export kernel

The source of truth remains the selected signed artifact history. This kernel
exports an exact selection to a new independently supplied owned output root.
SQLite and generated files remain derived views. Generated files confer no
admission, release authority or current Agent participation.

## Contract and trust boundaries

Use the unchanged `file-materialization-request` and `file-materialization-receipt`
schemas from proposal 0007 and the `files.materialize` contract from proposal 0008.
The host independently supplies the actor, output scope, current permission
callback, source guard, complete material selection and exact privacy review.
Client path strings never select a filesystem root or establish permission.
An ordered, complete artifact-to-path pairing is required by this implementation.
An empty selection is unsupported. The only supported renderer is the exact
hash-bound JSON pretty renderer in `kernel.py`.

Every source artifact retains its exact artifact reference, byte digest, original
source locator and encoding in the generation manifest. Source and authorization
guards run before effects and before publication. The output budget covers the
complete selection. Nonempty Session memory and known credential fields are
refused using the existing selected privacy implementation.

## Generation publication and retry

The independently owned root contains an immutable directory per exact request
digest. A generation is exclusively claimed with `mkdir`; it contains a pending
claim, `files/`, manifest, receipt and a publication marker. Directory descriptors
and `O_NOFOLLOW` protect path traversal. Output files use `O_EXCL`. The manifest
and receipt are flushed before the publication marker. Readers consider only
complete, verified publication markers published. A possible partial effect
returns an indeterminate receipt and retains the generation for inspection.

An exact retry requires current authorization and source guards, and verifies
the recorded manifest, receipt, marker and every selected output byte. A pending,
tampered or obstructed generation refuses redispatch. This kernel does not delete
or repair generations. Existing unmanaged files remain untouched.

## Verification and remaining integration

Twenty-four checks cover real selected Intent/Goal original body exports,
rendering, exact retry, privacy binding, selection closure, path safety, output
budget, actor/scope mismatch, pending generations and tampered/symlink outputs.
All output workspaces are newly owned development fixtures and are removed by
their fixture owners after checks. The fixture permission callback establishes
no production authentication or governance authority.

Public `files.materialize` dispatch, independently provisioned API export grants,
operation-key conflict/recovery contracts, host policy and integration regressions
remain required. Kernel success alone does not increase the qualified API count.
