# Canonical event-file process recovery result

Status: **PASS** for two fresh-process recoveries of the frozen W7 event-file
fixture, with the transitive event-store runtime source included in the
implementation digest.

The release binary was built once outside the timed region. Two independent
child processes then loaded 47 semantic and 47 governance event files,
calculated the ontology projection, built the graph read model, and verified
the expected source envelope and index digest. The current epoch completed in
28.73 ms and 29.06 ms. Event loading and validation took 22.18 ms and 23.96 ms;
calculation plus graph rebuild took 2.55 ms and 1.89 ms. Their normalized
recovery receipts were identical.

The failure controls also passed:

- a missing semantic event directory failed with
  `EVENT_DIRECTORY_READ_FAILED`;
- a changed expected index digest failed with
  `RECOVERY_INDEX_DIGEST_MISMATCH`.

The source-bound machine report is
[`runs/latest-w7-event-files.json`](runs/latest-w7-event-files.json), and
[`validation.json`](validation.json) rechecks the evidence hashes, current
runtime bytes, and current event-directory digests.

This is local prototype evidence for the 47-event W7 fixture only. Separate
experiments establish synthetic 250,000-subject event-file parity and a
disposable checkpoint-plus-canonical-tail strategy at 50,000 subjects. This W7
result does not establish crash consistency, durability, product approval,
ontology admission, runtime activation, publication, or cutover. Generated
5,000- and 50,000-subject canonical-format profiles are measured separately.
