# T06 current composite local prerequisites

`entrypoint.py` checks the selected API33 Source/profile/member, the historical SDK manifest and all 17 of its selected files, and the branch preparer against exact current profile pins. It also pins the reviewed Craft bridge freeze before running check, build, verify, generated Rule and Query, and one in-memory Operation in a fresh scratch directory. The selected bridge remains inactive and does not dispatch into the Lab API.

Run from this directory with the current independently selected Source/profile digests:

```bash
python3 -B entrypoint.py \
  --api-source-sha256 ceae2efe1a93e7041b83a5f7d3efa32085383beb061459e0568ebb5536e168aa \
  --api-profile-sha256 62cf46ffc5a01cc0009a4675ce265a45037104b3e64da0f022aaf2b2d3e75ec9 \
  --craft
```

The initial [RUN-0001.json](RUN-0001.json) predates the exact SDK/preparer and bridge-freeze checks. The repaired [RUN-0002.json](RUN-0002.json) records the rerun against the same API33 pins. It reports `BLOCKED_CURRENT_COMPOSITE_INTEGRATION` because the maintained revision-0003 composite SDK and branch fixture preparer use API17. API33 profile still selects those historical bytes; it does not select a true-origin API33 successor SDK/preparer/driver. No Base, Action or Governance branch was constructed in this run.

`python3 -B -m unittest test_entrypoint -v` exercises current selection, changed Source/profile/SDK/preparer/freeze refusal, matching-byte symlink refusal, the original revision-0003 `software_guard` rejecting an API33 directory, and the rule that a Craft pass cannot become full34 readiness. Seven tests pass normally and under `-O`; [independent review](../working/t06-current-composite-independent-review-0001/REVIEW.md) reproduced the behavior. No original API, SDK, private source or policy files are changed.
