# Original-role Reader successor release 0001 — stage selection only

Status: **effect disabled, ready for independent static review**. This is a
separate candidate for the original Reader role `docker-reader-20261020-0002`.
It does not reuse the consumed historical `/tmp` Source or Reader attempts.
The Source one-shot on 2026-10-20 reported a PASS terminal with package
manifest SHA-256 `bdb5eac92cbb3f96857c4d2ccb00880441d55fb8f1dbbeb5cdaae8d81c720653`
and terminal SHA-256 `66c51614278e38e061eac7cc195288444efa176f36f13dd4243462faaa34c7b9`.
Those actual Source bytes are **not** selected by this frozen candidate until
their independent effect review is complete and its exact SHA-256 has been
chosen outside the selector. The protected archive body was not read here.

`release.py` verifies the frozen `reader-successor-recovery-0001` selector and
its independent static review before import. Given public Source manifest,
actual package manifest, PASS terminal, current period, independently authored
Source effect review and outside-pinned review digest, `select_stage()` invokes
that selector and builds an exact 986-row plan: 940 public Source rows, 36
package rows, the public Source manifest, the private package manifest, seven
projected Reader role files, and the dynamic Reader manifest. Its returned
Reader bytes are only in memory. All Source pathnames are relative to the
durable Source attempt root; the public manifest includes repository-wide
paths outside the Source role directory. Package members and their manifest
require mode 0600, while public and projected Reader files require 0444.
The plan binds the exact dynamic Source package, terminal, effect review,
archive digest, Reader manifest, selector freeze, and selector review.

Selected future attempt paths are
`/home/vlad_/.local/state/cyberalchemy-lab/context-successor-20261020-0001/reader-stage-attempt`
and
`/home/vlad_/.local/state/cyberalchemy-lab/context-successor-20261020-0001/reader-attempt`.
The distinct Docker name is
`cal-reader-only-20261020-0002-successor-0001`. The selected image is
`sha256:7ca5c679c6d8931d268bf5111cb7156a6eeadd9a267bc73f247cd0f0b0428874`.
`docker_envelope()` records a read-only/no-network/cap-drop-all/UID-1000
container envelope and an exact future stage dev:ino binding. It intentionally
does not produce runnable argv: no new Reader entrypoint or controller is
bound to the dynamic Reader and package yet. `execute_stage()` and
`execute_reader()` always refuse.

Before any private stage effect, a separate release must bind the *actual*
Source effect review digest, verify current Source package bytes and metadata
through no-follow held descriptors, write a 986-file owner-only stage in a
durably claimed no-retry attempt, and independently review its full inventory,
hashes, modes, identities, exact directory set, terminal, and external OS
observation. The archive must be copied opaquely in that separately released
effect; this selector does not read it. Before Reader Docker effect, a further
release must bind a compatible cold-open entrypoint and controller, freshly
observe the exclusive container name and image/UID/mount feasibility through
the external OS, hold and reverify mount-source identities, apply the selected
no-network envelope, capture bounded daemon create/start/wait/inspect and
external exit, enforce current period through terminal publication, and obtain
independent postclose review. Neither synthetic tests nor an in-memory plan
are authority to run the protected Reader.

Normal and optimized synthetic suites each pass **5/5**. They cover the exact
986-row closure, package/private modes, dynamic archive/package/Reader binding,
review pin and expiry refusal, Docker envelope non-executability, and both
effect refusals. They use synthetic package digests and do not open a private
archive, copy a stage, create a container, or cold-open Reader. Original
Source8 authority and the complete runtime qualification remain separate.
