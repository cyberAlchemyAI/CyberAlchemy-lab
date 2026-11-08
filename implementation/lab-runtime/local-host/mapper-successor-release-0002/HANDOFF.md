# Original-role Mapper successor release 0002 — corrected stage selection only

Status: **effect disabled; ready for separate independent static review**. This is a
new candidate for the original Mapper role
`docker-mapped-20261020-0002`. It is not a Mapper stage, container run,
output verification, Source8 authority qualification, or completed runtime.
The current Source effect was independently reviewed PASS at review SHA-256
`599d7cca4b87b98809e33636ad1326bc60ddba589123ec5a0a0c5e00b58a4440`.
The Reader stage and effect are still outside this release's evidence.
It supersedes the frozen 0001 release for future selection because the 0001
independent review reproduced HOLD R01: JSON `false` and `0.0` were accepted
as integer-zero Reader exit status by the frozen predecessor selector.
That review is `MAPPER-SUCCESSOR-RELEASE-INDEPENDENT-STATIC-REVIEW-0001.md`
at SHA-256 `a95f78e6558f913f6550ccf72541e239421c6e8e12cf40deeb3fec9c2a025ade`.
The 0001 files and predecessor selector remain unchanged.

`release.py` verifies the frozen `mapper-successor-recovery-0001` selector,
its independent static review, the frozen `reader-successor-release-0001`
stage selector, and its independent static review before importing either.
`select_stage()` requires the exact actual Source effect review digest and
fresh, independently reviewed Reader receipt, PASS terminal, external OS
exit 0, and Reader effect review pinned outside the call. The predecessor
Mapper selector proves the dynamic Source package and Reader manifest joins
and projects four exact original Mapper role files. The separate Reader
release regenerates the same Reader manifest and 986-file stage plan.
Before delegating to the frozen Mapper selector, this corrected release parses
the Reader external OS record with duplicate-key rejection and requires
`type(exit_code) is int and exit_code == 0`. A matching digest or otherwise
coherent Reader review cannot turn JSON `false` or `0.0` into an integer OS
status.
The new plan contains **991 distinct files**: the 986 Reader-stage files plus
the four Mapper roles and their dynamic source manifest. Private Source
package members remain `0600`; public and generated files are `0444`.
The protected `branch.snapshot` is only a pathname and digest in this plan;
its body was not opened, hashed, copied, or printed here.

The selected future attempt is
`/home/vlad_/.local/state/cyberalchemy-lab/context-successor-20261020-0001/mapper-attempt`.
Its source is the distinct durable Reader stage root under
`reader-stage-attempt/root`. The unique Docker name is
`cal-mapper-only-20261020-0002-successor-0001`. The selected image is
`sha256:7ca5c679c6d8931d268bf5111cb7156a6eeadd9a267bc73f247cd0f0b0428874`.
The native ELF remains pinned to SHA-256
`fb8472564c95ba815b4c6192ff2d2dd8a0a49fad83549056f151e820de24aa1c`.
`docker_envelope()` records an identity-bound, no-network, read-only-root,
cap-drop-all, UID/GID 1000 with host user namespace, 16 PID, 1 GiB, one-CPU
container. It selects a read-only workspace bind, a narrow writable empty
Mapper `packages` bind, a read-only native input, and owner-only scratch
tmpfs. It deliberately provides no runnable argv or entrypoint.

The exact historical `verify_mapped_output` template is pinned by SHA-256
`aa883d697a9cfec02a4671da2a76d10c5c4b23ef0a93e63c78f31ac0667ff23b`
and not dynamically rebound. The output acceptance contract retains all
55 expected leaves, including 25 semantic and 25 governance leaves, 15
nodes, 10 edges, 25 exact joins, two native seals, two actual cold native
reads, byte parity, one signed source cut, the source-package binding,
native-domain mapping, and `authority_effect: none`. It rejects an owner
outcome, task completion, and generated Context/ontology carriers. The
separate effect release must implement and independently review those
checks against actual new output; listing the contract here does not verify
any output.

Before private stage effect, bind an independently reviewed actual Reader
stage and effect digest, verify its exact 986-file inventory, identities,
hashes, modes, and current period through held no-follow descriptors, then
copy into a newly exclusive owner-only `mapper-attempt` with no retry.
Create the empty Mapper package directory, copy the five generated Mapper
files, and attach the pinned native ELF without mounting the checkout. A
separate independent stage review must verify the complete post-copy
inventory, exact directory set, identities, modes, hashes, terminal, and
external OS observation. Before Docker effect, bind a new Mapper entrypoint
and a rebounded output verifier, reobserve the exclusive Docker name and
mount-source identities, enforce the current period through terminal
publication, and obtain independent postclose review. Neither old `/tmp`
attempts nor synthetic Reader test metadata are effect authority.

Normal and optimized tests pass **5/5** each. They exercise the actual Source
metadata with synthetic future Reader metadata, exact 991-file closure,
native and output-contract pins, private modes, refusal on stale review,
Reader exit, manifest, and period, archive-body non-access during selection,
Docker envelope non-executability, and unconditional stage/Mapper effect
refusal. The inverted causal Reader-exit tests update the external digest in
the synthetic Reader review and the outside review pin, then reject `false`,
`0.0`, integer 1 and `true`; integer 0 succeeds. `execute_stage()` and
`execute_mapper()` always refuse. This corrected candidate needs its own
independent static review before any further release consumes it.
