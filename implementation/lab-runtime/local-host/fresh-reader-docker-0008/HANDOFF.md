# Fresh Reader stage-only release candidate 0008

Status: **READY_FOR_INDEPENDENT_STATIC_AND_SAME_STATE_PREDISPATCH_REVIEW; EFFECT NOT RUN**. This is a disjoint successor to frozen `fresh-reader-docker-0007`, with a new selected attempt `/tmp/cal-reader-stage-20261020-0001-0008`. The 0007 neutral-stage controller passed two independent bounded reviews: `FRESH-READER-DOCKER-INDEPENDENT-STATIC-REVIEW-0007.md` SHA-256 `1fdf79f37aeb3a0b74f4cf632d7f0343fe765db1e5a55028336f4c8841845340` and `independent-fresh-reader-docker-review-0007/review.json` SHA-256 `8866f60edd3336b2b783c1d54b211060bda008ea3e22a7f818d30bff79041aad`. The reviewed 0007 freeze SHA-256 is `3391cd37a4457472534768b9483cab97dbfb375536687684ca44d88d8724f41f`. The 0001–0007 attempts and Source-only PASS are preserved.

Only the stage-only release gate is enabled here. The separate Reader cold-open and Docker controller remain effect-disabled. The release candidate binds the exact 0007 freeze and both reviews, preserves the 0005 predecessor/source/Reader selections, and changes the eight generated Reader source paths in a newly pinned 986-row copy plan. The Source episode expires `2026-10-21T08:20:00+00:00`; no historical protected Source8 authority is claimed.

Read-only preflight (safe to repeat until the attempt is consumed):

```sh
/usr/bin/python3 -B /home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host/fresh-reader-docker-0008/stage_only.py --preflight
```

**Exact one-shot command after independent review of this freeze and a same-state predispatch:**

```sh
/usr/bin/python3 -B /home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host/fresh-reader-docker-0008/stage_only.py --stage-once
```

Run that selected one-shot at most once. If any attempt directory or consumed marker exists, stop and inspect; do not reuse, remove, or retry it. Capture the command's external OS exit as well as the terminal output. The controller durably creates a 0700 attempt and no-replace consumed marker before the first private source read. It copies exactly 986 selected files through held no-follow descriptors with no-replace destination creation, digest/readback and fsync. The original Source archive is never written. It checks the staged tree, Source predecessor, original archive attachment and current period both before and after writing a neutral `OBSERVED_STAGE_ONLY` receipt. A nonzero exit or any `UNKNOWN` receipt supersedes that neutral receipt; any partial stage remains private under the consumed attempt. A successful exit records observed copy completion only. It does not certify immutable retained stage custody or authorize Reader use; a later Reader must independently revalidate the stage and period at use time.

Normal and `-O` suites each passed 35/35; all effect tests used disposable synthetic bytes. Live preflight passed read-only with 986 selected rows, 33,411,923 selected bytes, and the 0008 attempt absent. The selected private archive body has **not** been opened, copied, or cold-read by this candidate. No Reader cold-open, Docker, Mapper, Context, protected qualification, G01/G02, human outcome, or original-plan acceptance is claimed.
