# Numbered LC-U02-05 evidence

`evidence_guard.publish_numbered` creates a new numbered evidence leaf only under the exact LC-U02-05 evidence directory, using nofollow `O_EXCL`, file and directory `fsync`, and a final held-parent and leaf-identity check. `audit_evidence` checks an explicit list of canonical repository-relative evidence, log, and review bindings. Candidate source files are intentionally excluded because later revisions can evolve them; each construction packet pins its own source bytes.

An interrupted write or `fsync` failure can leave a partial exclusive leaf. The publisher does not delete or retry it; the next author must use a new revision name and record the failed attempt. No filesystem check gives continuous custody after return or authority for a protected runtime effect. Historical `construction-0007` and `construction-0008` remain superseded drafts; `construction-0009` is the corrected prior packet. Never reuse any numbered path.
