# Reader successor controller 0003 — exact enabled tool mount, effect disabled

Status: **effect disabled, ready for independent static review**. This
disjoint successor retains the reviewed controller 0002 logic and binds its
immutable freeze SHA-256
`107c6c0ea60402101559eb6d7ee858975d887e976600d10aacf745d8411701a9`
and independent static PASS review SHA-256
`ab1766c3c709f69d768c1e6c986938e433ab74a1a5ce8eac21765f26206e396b`.
The causal change is the exact tool mount: it selects
`reader-successor-entrypoint-release-0001` freeze SHA-256
`a19e831559804d397cc9131b0594f1385fad55f41381139196e5490bf4af52fc`
and independent static PASS review SHA-256
`835545402292e828507987ea35aaba09cba0c2091b22d18db39e64ea551b5c8c`.
The Docker command invokes `/tool/reader_entry.py --execute-reviewed-one-shot`;
the predecessor controller's disabled `/tool/reader_once.py` command is not
selected. The new tool bundle copies the exact reviewed cold-open code and
enables it only in memory inside the container after verifying the code,
selection and stage-plan bytes.

All earlier Source, 986-file Reader stage, stage effect review, Reader role,
manifest, period, image, UID, mount, no-retry, daemon evidence and finalization
checks remain selected. A provisional terminal cannot authorize PASS;
the final file is fsynced and the finalization marker must be observed in the
same run. Its parent directory is not fsynced; marker loss after a crash
leaves retained evidence UNKNOWN. The exclusive Reader attempt is
`/home/vlad_/.local/state/cyberalchemy-lab/context-successor-20261020-0001/reader-attempt`,
and exact Docker name is `cal-reader-only-20261020-0002-successor-0001`.

Normal and optimized fake-daemon suites each pass **42/42**. Live read-only
preflight passes with 986 staged files, exact stage and tool pins, current
Source period, and fresh Reader attempt. It hashes the private staged archive
without printing its body. No Reader attempt or Docker container was created.
An effect-enabled release must pin this freeze and its independent static
review, re-observe exclusive name and image/UID/mount feasibility immediately
before the single one-shot, capture external OS exit, and obtain independent
postclose effect review. This is a disposable local Reader cold-open only,
not original protected Source8 or full runtime qualification.
