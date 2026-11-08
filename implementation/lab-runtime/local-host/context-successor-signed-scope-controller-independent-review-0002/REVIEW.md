# Signed-scope controller0002 — independent static review

**PASS_BOUNDED_INERT_HELD_FILE_FIXTURE_ONLY.** Exact freeze `be4fad673eb559ddf810fae4b0bfa8e288c46c8c68b1e90902310d8deb8c8bc7` and three members rehashed unchanged before/after replay. Predecessor controller0001 HOLD `3c3ecf98743f598959d5c8a79b237fe42d72954732282f377b0d5450aaa8cb92` is preserved. Its R01 created-directory adoption defect is closed for this replacement held-file fixture protocol.

## Claim and marker correction

The claim now uses O_RDWR|O_CREAT|O_EXCL|O_NOFOLLOW and retains the descriptor returned for the inode actually created. No mkdir→reopen establishes claim identity. The original descriptor's dev/inode are joined to the named claim before marker write and later retained in both marker and synthetic attestation. Independent successful fixture checks compared the actual os.open-returned inode to those records.

The supplied causal swap immediately after O_EXCL return refuses before marker/Reader activity and leaves both detached original and replacement empty. Post-marker claim replacement and held-marker tampering also refuse before synthetic open. An independent parent-directory detach after marker leaves the replacement directory untouched and refuses. This is a correction to the selected claim-file seam, not a claim of hostile same-UID isolation: a process with the same parent permissions can detach/change names between checks. The fixture intentionally requires an owned, ordinary 0700 /tmp/fixture-signed-scope-* parent.

Claim creation is followed by parent fsync; the marker is written, fsynced and read back through the original held claim FD, joined to its name, then parent-fsynced. Subsequent attachment checks rehash the held marker. Independent regular-file fsync and marker-readback faults retained consumed claims, never called the synthetic Reader, and refused retry. Existing claims/attestations prevent reentry; no cleanup removes consumed attempt evidence during the controller operation.

## Signed-scope and publication sequence

All observations are supplied by the exact SyntheticSelectedReader class. Source/package/adapter basis, expected view/sources scope, selected public review identities, UTC period and final guards/close are checked. Wrong scope/basis, final guard or close failures and expiry retain UNKNOWN without an attestation. Independent public-review drift between initial selection and synthetic open likewise refuses. The fixture close time is explicitly synthetic; it is not a measurement of actual private Reader completion.

After synthetic close, the controller rechecks public selection and writes an exclusive 0600 attestation through a held descriptor, fsyncs, reads back, checks named identity and fsyncs its parent. The attestation remains provisional, authority_effect=none, actual_owner_outcome=null and fixture-only. An independent real-close-then-raise fault on final claim closure produced UNKNOWN, attempted the remaining parent close, did not retry the ambiguous numeric FD, and refused a second run even though provisional attestation bytes existed. Such bytes cannot be accepted without the missing external OS/review conjunction.

## Replay and currentness

All **12 supplied plus 6 independent cases passed normally and with -O (18 each, actual OS0)**. Exact commands, start/end times and raw log digests are retained in execution.json. Tests used only their own disposable public fixture files and synthetic observations; fixture cleanup was confined to those test parents. An audit hook prohibited branch.snapshot, subprocess, socket, fork and exec activity.

Read-only preflight passed with the exact adapter0002 and stage-effect review bindings. Real `context-signed-scope-attempt-0002.claim` and `context-signed-scope-attestation-0002.json` remained absent. Selected Source period ends 2026-10-21T15:00:00Z exclusive. This preflight checks current selected public joins and root metadata; it does not independently rehash the entire staged private family during this review or prove cross-time inode continuity from the earlier stage effect.

## Effect ceiling and remaining integration

run_real_once, issuer/grant, private policy and Docker entrypoints all refuse. No actual Reader, signed view, private archive, issuer, key, grant or AUTH was used or created. The trusted same-UID fixture and direct Python object/callback model are not a security boundary. Public dependencies must be selected again for any real release.

The separate checked Reader loader0001 has now received bounded inert review, but this controller does not compose it into a real effect path. Host jsonschema remains 4.19.2 versus required 4.23.0; a selected matching runtime, full private-read/namespace custody, actual guard/close behavior, external observer and independent effect review remain unresolved. The HANDOFF's Docker-image compatibility statement was not freshly tested here and is not promoted to runtime qualification. This PASS permits continued disjoint construction, not a real signed reopen or original Context acceptance.
