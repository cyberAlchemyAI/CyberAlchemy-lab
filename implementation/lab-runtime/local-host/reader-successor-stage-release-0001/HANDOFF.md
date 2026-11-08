# Reader successor stage release 0001 — one-shot private copy candidate

Status: **effect enabled only by this disjoint wrapper; not yet run**. This
release pins `reader-successor-stage-0001/freeze.json` SHA-256
`1487f1b37d1ce05b45acd9692b4878d5b3f5d78f8046e958942ae62dba9eaf20`
and its independent static PASS review SHA-256
`5824eb5ffe42da97a28cd364a26e7f58e1a87e313a7206d27c3a60fd2e4667e1`.
It verifies all 14 frozen bindings before importing the effect-disabled stage
module. Only `--execute-reviewed-one-shot` temporarily enables that exact
module, calls its no-archive preflight again, and restores the disabled
literal on return or error. No predecessor files were changed.

The selected actual Source review is
`599d7cca4b87b98809e33636ad1326bc60ddba589123ec5a0a0c5e00b58a4440`;
Reader stage plan is
`a5ee5e9812c4ab5d0e37b7fe99aec4f334dcb583668ad0489f267f7e2258478b`.
The exclusive, unoccupied future attempt is
`/home/vlad_/.local/state/cyberalchemy-lab/context-successor-20261020-0001/reader-stage-attempt`.
The one-shot will durably claim it before copying the protected archive,
stream and hash the selected 986 files through held no-follow descriptors,
and write a stage-only terminal. Ambiguity leaves the attempt consumed with
UNKNOWN where possible; no retry is selected.

Normal and optimized tests each pass **3/3**. Read-only live preflight passes
with 986 files, 33,413,752 selected bytes, archive body unopened and current
period. No stage effect was run by this construction. An independent static
review of this exact wrapper and freeze, followed by same-state predispatch,
must precede the single command below. Capture its external OS exit code and
retain stdout/stderr without printing private bodies. Then independently
review the consumed marker, exact staged inventory and hashes, terminal,
UNKNOWN precedence, current period, and Source retention before Reader use.

```sh
/usr/bin/python3 -B /home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host/reader-successor-stage-release-0001/release.py --preflight
/usr/bin/python3 -B /home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host/reader-successor-stage-release-0001/release.py --execute-reviewed-one-shot
```

This stage release does not cold-open Reader, create a Docker container, or
qualify original Source8 authority. The later Reader effect requires a
separate exact stage review and compatible controller/entrypoint release.
