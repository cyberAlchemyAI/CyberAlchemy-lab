# Reader successor container entrypoint release 0001

Status: **one-shot container entrypoint candidate, not run**. This disjoint
tool bundle copies the three exact execution inputs from the independently reviewed,
effect-disabled Reader entrypoint 0001 (freeze SHA-256
`850978c56a3c8f1d9523f1a67f69e1f62a58b17db39143d5c209ed56e2e81919`,
static review SHA-256
`8d2457f66c668b557549ee026525cdd23c0080d29ccbc6221bb6764213a45bd2`).
`reader_entry.py` verifies the original `reader_once.py`, selection and
stage-plan byte digests before import; the reviewed tool's
`EFFECT_ENABLED` remains false on disk. Only the exact one-shot invocation
temporarily enables it in memory, calls `run()`, restores the flag, and
prints the bounded result on success. An exception prints no PASS.

The selected Reader manifest is
`048ef6c1f54387fc6e593f38b29723cb06f84649f12e9c75a0340d389b0f5756`,
selection is
`a5fea0a94c27900c4975d11924c7ba0abcb7e118d8795c721e5a6c9cefc4cab7`,
and 986-row stage plan is
`a5ee5e9812c4ab5d0e37b7fe99aec4f334dcb583668ad0489f267f7e2258478b`.
The controller release must mount this exact frozen tool bundle read-only,
bind its independent static review, enforce single UID-1000 process/private
tmpfs/no-network image and stage identity, and observe external Docker exit
and postclose state. No direct host Reader effect is selected.

Normal and optimized wrapper tests pass **3/3**. The underlying reviewed
cold-open tests pass **21/21** in both modes. These are synthetic; no
protected archive body was opened or Reader cold-open run while constructing
this release. Independent static review of this exact freeze is required
before the controller can select it.
