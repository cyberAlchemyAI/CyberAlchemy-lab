# Mapper successor direct actual Reader adapter 0002 — effect disabled

Status: **exact actual Reader result selected into public Mapper plans; no
Mapper effect**. This is a disjoint successor to the synthetic future Reader
contract in `mapper-successor-stage-adapter-0001`. It preserves the frozen,
independently PASS-reviewed `mapper-successor-release-0002` as its source for
role projection, stage paths and confinement selection. This release has not
yet received its own independent static review.

`adapter.select_actual()` pins and directly validates the original
independently authored Reader Docker effect review, SHA-256
`c2f9d0307610d281784c4d3c86211dbc37bd6a5843130647ff1718561957f295`
(`lab-reader-successor-docker-effect-review/v1`, verdict
`PASS_BOUNDED_READER_ONLY_EFFECT`). It does **not** manufacture or use a
replacement nine-field Reader review. The actual review binds the reviewed
Reader one-shot release freeze, actual Source package, 986-file Reader stage
effect review, original receipt, provisional and final terminal, consumed
marker and external observer result. This adapter also pins the review
narrative, external intent/result/stdout/stderr, retained create response and
observation, CID receipt, pre-removal record and their exact digests. It
checks exact one-shot argv, release/review identity, no retry, strict JSON
integer OS/client/daemon/pre-removal exit zero, empty stderr, shared CID and
attempt label, image/name, terminal PASS and postclose checks, and current
finalization marker with no release UNKNOWN receipt. The observer's raw
stdout digest is **different** from the final file digest because its JSON
formatting differs; the adapter verifies the parsed stdout object equals the
final object and retains both original hashes.

The final Reader file is SHA-256
`8a4a1bf63afe5351e1f6184038e2ec13cf30e855d85c51b145122a19efcb21aa`,
joining the original provisional UNKNOWN/PENDING file
`5d8748a5efc5e2108c477263797bec3282968d1bb9fdfb36f2e0a8efd151bd9f`
and original receipt
`d389c46467b2cbac48e6cec3ec9a8d58c7f036516576b718c6f796a1586eedf2`.
The external result is
`5c421de1f92545ba29efaa2cb5d49d8f51ff8773a979173f8ef21bee4e3b95c5`.
The finalization marker is present at selection time; its parent was not
fsynced by the Reader release, so this is **not** a crash-durability claim.
The Reader attempt is consumed and must not run again.

The Source manifest SHA is derived only from the separately pinned Source
and Reader public selection and joined to the actual Reader receipt. The
original Reader effect review does not contain that field. The adapter uses
the frozen original Mapper role projector for four files, with dynamic Source
manifest, actual Source package and Reader manifest pins. It checks the
Reader stage selector yields the exact retained Reader manifest. The Mapper
source manifest SHA-256 is
`bad889d50a0ba302ae83c9f4d5d9b664417af50cf4a6e4c408dfb50f8680d947`,
matching the reviewed predecessor's projection for the same bindings.

Four public, effect-disabled artifacts are saved beside this handoff:

- `stage-plan.json` SHA-256 `9041aeedc8b349f6d7315e7ac2544aabda85afdb748663010e00af25e0b9ca2e` — exactly 991 input rows: 986 retained Reader-stage rows and five projected Mapper files. It pins the **actual** independent Reader review, not a compatibility projection.
- `copy-plan.json` SHA-256 `76bfc24841d652cbae039d666bcde80d7899b3b978ebd0291443705543d3dd95` — 931 Reader-stage source directories, including the intentionally empty Source `receipts` directory; 933 target directories after adding Mapper and empty owner-only `packages`; 37 private `0600` Source rows. A future exclusive `0700`, no-retry attempt must perform held no-follow copy with pre/post inventory, hash, mode and identity checks and attach the pinned native executable. This plan performs no copy.
- `verifier-plan.json` SHA-256 `e45ba0c5ba2797b2e7ed564caa4528fbf8d79c8b1f42d95f36783ec59cf94416` — original native ELF SHA-256 `fb8472564c95ba815b4c6192ff2d2dd8a0a49fad83549056f151e820de24aa1c` and historical verifier template SHA-256 `aa883d697a9cfec02a4671da2a76d10c5c4b23ef0a93e63c78f31ac0667ff23b`. It preserves the exact 55 leaves, 15 nodes, 10 edges, 25 joins, two seals and two cold reads, byte parity, signed source cut and no authority effect. The verifier is **not rebound or run**.
- `actual-selection.json` summarizes original provenance and the three plan digests, with the selection-only claim ceiling.

Normal and optimized suites pass **8/8**. They exercise actual 991/933
closure, archive-body non-access, strict scalar exits, original review and
swapped terminal drift, changed stdout with coherently changed derived
hashes, wrong CID, wrong attempt, cross-family package, missing finalization
marker, UNKNOWN receipt, period expiry and effect refusal. No protected
`branch.snapshot` body was opened, printed or copied, and no Mapper stage,
Docker or native effect ran.

An independent static reviewer must challenge the direct Reader schema
translation, exact artifact digests, empty directory accounting and
55-leaf verifier selection before any effect release. A later disjoint
Mapper stage release must implement the private copy and receive an
independent stage effect review. A separate Mapper Docker release must bind
an actual entrypoint and rebounded output verifier, run once under external
observation, and receive its own independent effect review. No Mapper effect
review schema or protected Source8 authority is claimed here.
