# Reader successor entrypoint 0001 — dynamic Source cold-open tool

Status: **effect disabled, ready for independent static review**. This adapts
the previously reviewed `reader-only-unified-0006/reader_once.py` to the
new `docker-source-20261020-0002` and `docker-reader-20261020-0002` roles.
It binds actual Reader selection SHA-256
`a5fea0a94c27900c4975d11924c7ba0abcb7e118d8795c721e5a6c9cefc4cab7`,
Reader manifest SHA-256
`048ef6c1f54387fc6e593f38b29723cb06f84649f12e9c75a0340d389b0f5756`,
and exact 986-row stage-plan SHA-256
`a5ee5e9812c4ab5d0e37b7fe99aec4f334dcb583668ad0489f267f7e2258478b`.
Its selection binds the independently reviewed Source effect SHA-256
`599d7cca4b87b98809e33636ad1326bc60ddba589123ec5a0a0c5e00b58a4440`,
current Source terminal/package, archive digest, signed expected head, and
period end. These tool files are public metadata; no protected archive body
was read while preparing them.

The adapted `selected()` accepts only the new stage-plan schema and binds
its Reader manifest, package manifest, Source effect review, and exact 986
path/hash rows to the selected Reader/Source manifests. It retains the
original held no-follow input verification, exact namespace and modes,
single-process UID-1000 tmpfs topology, sealed code snapshot loader,
selected Reader cold-open, current-period checks before/inside/after use,
bounded body-free aggregate receipt, and postreceipt full rehash. Its
`EFFECT_ENABLED` remains false. A later independent release must bind the
reviewed stage effect, this exact entrypoint freeze and review, a matching
Docker controller, image/UID/mount feasibility, exclusive attempt and name,
external OS observation, and independent postclose review before one-shot.

Normal and optimized synthetic tests pass **21/21**. They cover the exact
986-file synthetic stage, manifest and plan joins, mutations and extra
entries, private mode, wrong carrier, stale module origin, period expiry,
report bounds, symlink ancestors, tmpfs copy/readback, swap-and-restore,
faulted cleanup and no-replace snapshot, and effect refusal. They do not
constitute an actual protected Reader cold-open. The Reader stage one-shot
has external OS exit zero, but its independent effect review was pending at
this freeze; this entrypoint does not select that result yet.
