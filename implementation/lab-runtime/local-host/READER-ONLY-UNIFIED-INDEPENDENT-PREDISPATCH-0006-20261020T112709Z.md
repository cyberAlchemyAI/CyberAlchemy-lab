# Reader unified 0006 immediate predispatch

Observed 2026-10-20T11:26:49Z–11:27:09Z UTC. Verdict: **PASS for one exact, fresh local-fixture dispatch while the observed state remains unchanged.** This is a read-only predispatch, not a Reader or Docker effect result. No Docker create/start or Reader call was made by this review.

The enabled 0006 freeze SHA-256 `a4d424959bf6846194ca101f6ac2f80b4d6fbf91e35e7db835de157c61c845df` matched all **17/17** bound member hashes and sizes. The independent static PASS review at `reader-only-unified-0006-independent-architecture-review-0001/review.json` matched SHA-256 `c1106aa6d9a9964d9f46772987b07f1638ce3795b8f0f8cf81ce3b5e338d10c3`. Its selected image and tool/source bindings remain unchanged. The prior consumed 0003 UNKNOWN is not retried.

The exact read-only command was:

```sh
/usr/bin/python3 -B /home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host/reader-only-unified-0006/controller.py --preflight
```

OS exit was **0**, with `status=PASS_INERT`, `effect=NOT_RUN`, `attempt_fresh=true`, `selected_files=986`, `host_tmp_available_bytes=574181376`, stage freeze SHA-256 `7baa002724d031a1225e73518dee282caf3f9d26a914bdc306788c3873917606`, stage terminal SHA-256 `bd45626107f1754b9d108e138fdf3a85dc3b4ed0ffa00cfb1fc304f7974093cd`, selection SHA-256 `073bc2938e30d6d108ed8b22205eed551d3879c1eab4379d0200c4e9f2d90b22`, and Reader manifest SHA-256 `4b61293453ec763f1c3567d3dac114e0d0782a2c58b85bc941ca34a0c974d251`. The preflight hashed all 986 selected staged files, including the private archive **hash-only** without parsing or printing its contents; it checked owner/group/mode/link count, directory inventory, held/path attachment, stage neutral terminal/consumed marker/reviews, selected Source/package/Reader bindings, host binaries, and the current signed participation period ending `2026-10-21T08:20:00+00:00`. Neither stage UNKNOWN path existed. The stage attempt root was UID/GID 1000 mode 0700 and staged root UID/GID 1000 mode 0755. Host `/tmp` exceeded the selected 512 MiB floor by 37,310,464 bytes at preflight.

Read-only Docker image inspection returned the exact selected image ID `sha256:7ca5c679c6d8931d268bf5111cb7156a6eeadd9a267bc73f247cd0f0b0428874`, Linux amd64. Exact-name Docker inspect reported no such object for `cal-reader-only-20261020-0001-unified-0006`; `/tmp/cal-reader-only-dev-20261020-0001-unified6` remained absent. Docker CLI help lists selected network, read-only, IPC, process-limit, UID, mount and tmpfs options. The previously frozen create-only diagnostic 0004 returned create exit 0, exact identity match and confirmed removal with the selected image, UID, process limit and tmpfs flags, without private mounts or start. The 0006 full mount graph and cold-open remain effect/post-effect observations, not proven by this predispatch.

The exact eligible one-shot command is:

```sh
/usr/bin/python3 -B /home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host/reader-only-unified-0006/controller.py --execute-reviewed-one-shot
```

Dispatch it at most once while the pinned state is unchanged and the period current. Any consumed failure or UNKNOWN is retained without retry. The result remains a disposable Reader fixture only; it is not protected Source8, Mapper/Context, G01/G02 or original-plan acceptance.
