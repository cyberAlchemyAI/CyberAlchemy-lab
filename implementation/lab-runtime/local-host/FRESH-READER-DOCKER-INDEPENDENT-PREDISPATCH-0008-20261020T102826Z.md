# Independent same-state pre-dispatch: Reader stage 0008

**Verdict at 2026-10-20T10:28:26Z: PASS for one immediate selected stage-only dispatch.** No `--stage-once` command was run by this reviewer. This verdict expires on any selected-byte, attempt, host, or period change; it is not a Reader/Docker effect authorization or a claim that the private archive body was checked.

The exact selected command is:

```sh
/usr/bin/python3 -B /home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host/fresh-reader-docker-0008/stage_only.py --stage-once
```

The frozen `one_shot_argv` equals those four argv members. `/usr/bin/python3` resolves to `/usr/bin/python3.14`, Python 3.14.4, root-owned mode 0755, inode 11370. Freeze `fresh-reader-docker-0008/freeze.json` SHA-256 `7baa002724d031a1225e73518dee282caf3f9d26a914bdc306788c3873917606`; all 24 selected members matched size and SHA-256. The 0007 freeze SHA-256 `3391cd37a4457472534768b9483cab97dbfb375536687684ca44d88d8724f41f` and both independent review digests `8866f60edd3336b2b783c1d54b211060bda008ea3e22a7f818d30bff79041aad` and `1fdf79f37aeb3a0b74f4cf632d7f0343fe765db1e5a55028336f4c8841845340` matched the release bindings. The exact selected stage plan is 986 rows, SHA-256 `82ddcf898953881d49cfb1b99ba0b91f4f9c7393cfde5ae3bb9549b5a769e524`.

Read-only `--preflight` using the selected interpreter and script exited zero immediately before this record. It reported Source audit `PASS_INERT`, 986 selected files/33,411,923 selected bytes, the pinned Source manifest `7e0938e70ac00b5308851b5a5a7c7bdb92041efab3be17296998acb4160395c1`, package manifest `f132b3e1908e9e116464ad29c3db7f56ca17d4dee080e60ffa62547dd9588a5b`, Reader manifest `4b61293453ec763f1c3567d3dac114e0d0782a2c58b85bc941ca34a0c974d251`, selection `073bc2938e30d6d108ed8b22205eed551d3879c1eab4379d0200c4e9f2d90b22`, and current Source period expiring `2026-10-21T08:20:00+00:00`. The selected archive is an owner-1000 `0600` 23,550,300-byte regular leaf by metadata; `archive_current_bytes_checked=false`. Its declared digest is `6d3cfc3f721b9be4fb8a1df14d4f43214709887213eaeae543927f214fdb9323`, to be checked by the one-shot copy. No private archive body was opened in this audit.

The exact new attempt `/tmp/cal-reader-stage-20261020-0001-0008` was absent before and after preflight, including a final `lexists`-equivalent check at 10:28:26Z. The selected controller writes only under that new attempt; its held/no-follow source path is read-only, its marker is durable before first private copy, and an occupied/partial attempt cannot be retried. Its neutral `OBSERVED_STAGE_ONLY` receipt requires selected external exit zero and no UNKNOWN to establish only historical observed copy completion. Any later Reader must freshly revalidate attachment, bytes, and period. No protected or historical Source path was written by this review.
