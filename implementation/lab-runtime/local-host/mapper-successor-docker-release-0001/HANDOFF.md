# Mapper successor Docker release 0001: one-shot candidate

This disjoint release pins effect-disabled Mapper Docker controller 0002 freeze SHA `4cac02ffa93511633ccdd45f2b0562069225f0e6e7530399ef88f5d2e692da2b` and independent bounded static PASS review SHA `253503d80afaf0d6af0caa2411f38acc96d50fc8b54e70b85dc7efebd84c7bd9`. It also carries the selected independent Mapper stage effect review SHA `bae85fada28780b6bcc88082d2436082402d8acfc25b420328c79df6d2f07406`. The release itself has not been statically reviewed or dispatched, and no Docker Mapper role or native process has run in this successor attempt.

The wrapper checks exact frozen file paths, sizes, and SHA-256 values using nofollow opens. It compiles and executes the captured `anchored_copy`, `held_stage`, `docker_protocol`, `output_verifier`, `root_guard`, and `controller` buffers in dependency order, without importing a second path read or pyc. The captured container entrypoint bytes are syntax-checked; the controller copies the same SHA-256 into the held attempt and verifies the copy before Docker. Host preflight is read-only and does not open the protected archive body. The effect switch exists only inside `execute_reviewed_one_shot()` after that preflight; the frozen controller remains effect disabled.

Current read-only preflight selected the exact 991 staged files and 933 directories, 37 private 0600 rows by metadata only, native ELF SHA `fb8472564c95ba815b4c6192ff2d2dd8a0a49fad83549056f151e820de24aa1c`, Docker image `sha256:7ca5c679c6d8931d268bf5111cb7156a6eeadd9a267bc73f247cd0f0b0428874`, and absent exact container name `cal-mapper-only-20261020-0002-successor-0001`. The `docker-attempt` directory is absent. The stage source-continuity ceiling remains current-snapshot only because original creation/pre-effect per-file inode identities were not externally retained.

The selected effect invocation, **only after independent static PASS review of this frozen release and an external one-shot observer prepared to retain raw intent/stdout/stderr/OS-exit evidence**, is:

```text
/usr/bin/python3 -B /home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host/mapper-successor-docker-release-0001/release.py --execute-reviewed-one-shot
```

It must be dispatched once. Do not re-run the consumed attempt on failure or uncertainty. The controller retains raw consumed/prepared/precreate/terminal/provisional-final evidence and exact 55-leaf package bytes under the selected attempt. A host process OS exit of strict integer zero, exact terminal and package verification, proven exact container absence, and a separate independent effect review are required for downstream selection. The controller's `OBSERVED_DOCKER_ONLY` final cannot promote itself; no synthetic compact review substitutes for actual independent provenance. Container logs are not claimed. No original Source8/G01/G02 or Context qualification follows from this candidate alone.

The release tests pass 6/6 under normal Python and 6/6 under `-O`. They cover exact freeze/review pins, same-buffer module execution with no second source read, read-only preflight, scoped effect switch with an inert controller fake, wrong preflight refusal, and disabled flag refusal. They do not create a Docker attempt, read the private archive body, call Docker create/start, or run Mapper/native code.
