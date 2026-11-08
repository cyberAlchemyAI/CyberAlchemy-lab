# T19 two-root local fixture install and restore

`run.py` rebuilds the exact pinned T25 candidate archive, extracts it into two separate empty private roots, and builds/runs each installed fixture through unique Docker project and image names. Each root must pass the Source→Reader→Mapper→Context chain and Work journey. It then extracts the same archive into a third empty root and repeats both journeys. Every run checks that its containers, volumes, networks and image are removed. The temporary roots are removed after verification.

`RUN-0001.json` records all three installations and six successful journeys, with command exit codes, output hashes, durations and resource postchecks. `RUN-0001.err` is empty. The runner SHA-256 is `fbf381eb77465f2d3a2bc8b54037aabbcdb1350ab40a496fbcbf71abccee679a`; the result SHA-256 is `877d357909e1a967a280241fcb705450ff0585178993a8cc1c955e9d21bfc4fd`. This is a **fixture package** install/restore exercise. The integrated API Service is not installed from this archive, so T19 remains open for that closure, source-backed composite operation and rollback.

The first run's `failed_restore_refused_without_change` field is too strong: it tested the corrupt bytes with in-memory replay only. [The independent review](../working/t19-two-root-fixture-independent-review-0001/REVIEW.md) held that subclaim. `restore_negative.py` now calls the real `extract_verified` entrypoint with corrupt bytes and with a valid archive against a nonempty installed root. [Its result](RESTORE-NEGATIVE-0001.json) records both refusals, no change to any of 1,675 installed file/directory entries, and byte-identical extraction into a clean restoration root. It pins the six-journey result but does not rerun those Docker journeys.

The [independent re-review](../working/t19-two-root-fixture-independent-review-0001/REVIEW-0002.md) reran that successor cold and passed its bounded claim. The tree comparison covers paths and regular-file bytes; ownership, modes, timestamps and xattrs are outside this slice.

Run from the repository root:

```sh
python3 -B implementation/lab-runtime/local-host/t19-two-root-fixture-0001/run.py
python3 -B implementation/lab-runtime/local-host/t19-two-root-fixture-0001/restore_negative.py
```
