# Reader-only unified 0003 immediate predispatch

Observed 2026-10-20T10:56:30Z–10:57:03Z UTC. Verdict: **PASS, bounded same-state local fixture predispatch**. This is a short-lived observation for one exact launch, not a continuing approval or effect result. No Docker container or Reader was started by this review.

The enabled 0003 freeze SHA-256 was `f7174803cb9951718ef304d9cf7b96d87294cf7918dd3e49616b533b0c90ec29`; all nine recorded member sizes and hashes matched. Independent static release review SHA-256 was `7fa54597d6b650014cb60c76bf2b3d6b20d10778291af30329a0a40043900ff9`, with bounded PASS. The controller's read-only preflight rechecked pinned 0001/0002 unified reviews, stage 0008 freeze, neutral terminal, consumed marker, both stage effect reviews, Reader 0004/0005, controller 0003, and mount audit. It verified the exact 986-file selected stage including the private archive by SHA-256 only, without parsing or printing its body; owner/group/modes/single-link counts, exact directory inventory and private directory modes, held/named attachment, selected Source/package/Reader manifests, and current signed participation period. It found no stage UNKNOWN at the attempt root or evidence path. Selected stage root was 1000:1000 mode 0700, staged root 1000:1000 mode 0755.

Exact read-only invocation:

```sh
/usr/bin/python3 -B /home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host/reader-only-unified-0003/controller.py --preflight
```

It exited 0 with `status=PASS_INERT`, `effect=NOT_RUN`, `attempt_fresh=true`, `selected_files=986`, `host_tmp_available_bytes=574210048`, stage freeze `7baa002724d031a1225e73518dee282caf3f9d26a914bdc306788c3873917606`, stage terminal `bd45626107f1754b9d108e138fdf3a85dc3b4ed0ffa00cfb1fc304f7974093cd`, selection `073bc2938e30d6d108ed8b22205eed551d3879c1eab4379d0200c4e9f2d90b22`, and Reader manifest `4b61293453ec763f1c3567d3dac114e0d0782a2c58b85bc941ca34a0c974d251`. The selected period ends `2026-10-21T08:20:00+00:00`. The preflight also pins host Docker and Python binaries.

Read-only Docker image inspection returned exact image `sha256:7ca5c679c6d8931d268bf5111cb7156a6eeadd9a267bc73f247cd0f0b0428874`, Linux amd64; selected container inspection returned the exact absent-object diagnostic. The selected attempt `/tmp/cal-reader-only-dev-20261020-0001-unified3` was absent before and after preflight. The selected container name is `cal-reader-only-20261020-0001-unified-0003`. The reviewed static command requests UID/GID 1000, private PID/IPC/UTS, `--pids-limit 1`, network none, read-only stage/tool binds, and owner-1000 mode-0700 512 MiB `/attempt/tmp` tmpfs; runtime mount behavior remains an effect/post-effect fact, not proven by this read-only predispatch.

Exact one-shot command eligible **only while the observed state remains unchanged and current**:

```sh
/usr/bin/python3 -B /home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host/reader-only-unified-0003/controller.py --execute-reviewed-one-shot
```

The one-shot itself consumes the attempt no-retry. A later failure/UNKNOWN must be preserved. This predispatch does not establish Reader effect, daemon mount custody against a privileged or joined same-UID actor, protected Source8 authority, Mapper, Context, or original-plan acceptance.
