# Reader successor stage release 0001 — independent static review

**Verdict: PASS for one reviewed, one-shot stage dispatch.** This is a static release verdict; the stage effect and its terminal still require independent observation and review.

The wrapper freeze at SHA-256 `581c68e9c413e8ad9d10032f122f40eb3cccc8b42911ffb185f003e2aa6dc87e` has three member bindings; every size and digest matches. It pins the effect-disabled stage freeze (`1487f1b37d1ce05b45acd9692b4878d5b3f5d78f8046e958942ae62dba9eaf20`), its independent PASS review (`5824eb5ffe42da97a28cd364a26e7f58e1a87e313a7206d27c3a60fd2e4667e1`), and the exact 986-row stage plan (`a5ee5e9812c4ab5d0e37b7fe99aec4f334dcb583668ad0489f267f7e2258478b`). `basis()` rehashes all 14 frozen stage members before loading stage code. A live import resolved the reviewed `stage.py` and its pinned Reader predecessor, with `STAGE_RELEASE_ENABLED` still false and no stage attempt present.

The CLI exposes a read-only `--preflight` and one `--execute-reviewed-one-shot` route. The latter checks the exact frozen basis, runs the no-archive preflight, temporarily enables only that freshly imported stage module, invokes its `execute()`, and restores the disabled flag in `finally`. The stage code itself repeats preflight, claims the exclusive attempt, durably writes the consumed marker before any protected archive read, streams the archive with held no-follow descriptors, and retains UNKNOWN on a covered post-claim fault. The wrapper does not add a bypass or retry route.

Normal and optimized Python tests pass 3/3. A separate live read-only wrapper preflight reports 986 selected files, 33,413,752 bytes, the current Source effect review, no preexisting attempt, and `archive_body_opened: false`. The import test also confirms the stage's Reader predecessor resolves to the frozen selection release rather than the wrapper module.

No stage effect was run for this static review, and the protected archive body was not opened. The subsequent external command observer must capture the one-shot process exit, terminal, and retained attempt. A successful Python return alone is not the independent stage-effect verdict.
