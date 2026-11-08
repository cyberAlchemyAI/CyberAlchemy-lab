# Mapper-only Docker release candidate 0003 — held before effect

This is a fresh, disjoint, **effect-enabled** one-shot candidate derived from the independently PASS-reviewed controller0004 (`freeze.json` SHA-256 `34f71af3ff57941083c3e2c159ed7a25fbe975e0d17a248b4f6f2e4ca2aca788`; review SHA-256 `0142efe21a2965ad4c4e8a938ea5572117743ef8eb59a7615eec905470a4931d`). The release is **not authorized or executed** at this freeze. The code requires a separate static PASS review, same-state predispatch PASS review, and their pinned authorization JSON before it can copy the private Source archive or create a container. Do not call `--execute-reviewed-one-shot` during static review.


Release0001 was independently **FAIL** at SHA-256 `57c092cd5d2ea8507cf8fde215fa02372051e3c684f02b9bbb20cdc907fe21ed`; its frozen release SHA-256 is `e358a9cc908fb69514a15985b776f0a36306adaf77916c12a85a3069d9feb7cd`. This disjoint successor fixes both causal findings. R01 uses the same `evidence_json_bytes` encoder for durable terminal writing and controller hash/readback, then the full synthetic controller path checks PASS and terminal-byte drift. R02 accepts only the read-only probed Docker absence grammar: exit 1, stdout `[]\n`, and stderr `Error response from daemon: No such container: <exact CID>\n`; wrong CID, substring, transport and return-code variants remain UNKNOWN. The selected read-only probe is frozen as `docker-absence-observation.json` SHA-256 `3a9aebfcbf4a1cacacb795ccb38e230265ca0befca67f5608ebcc3ae1acda760`, with `/usr/bin/docker` SHA-256 `999189864fcf5cbda492d1fcb790044a6f152e2d0a7e49308d1c21ff4146bd00`. It observed the new name absent. This probe did not create, run, or remove a container.

Release0002 was independently **FAIL** at SHA-256 `0aeef2a7a805b4636edb328892f01fd55bc2d1030d17343d05ad3c780654e743`; its freeze SHA-256 is `03aa1bc26c03700240b00117845f9f9fcc110863b6c1ad9e0512ce80c097cb08`. R01 and R02 are closed within their tested scope. This new release fixes R03: the pinned original Mapper `build.py` assigns `build-result.json.source_sha256` from the `build(pin)` argument, which is the **Mapper source-manifest pin** despite the legacy field name. The output verifier now compares that field to `mapper_manifest_sha256`; it independently checks the output manifest’s Mapper source binding and the mapping’s Source package binding. A 55-leaf inert fixture executes only the pinned original result-assignment AST, then runs the real output verifier. The original-compatible output passes; substituting the Source pin for the result, the Mapper pin for the Source package, or the Source pin for the output manifest independently fails. The fixture never imports/runs the Mapper builder, Source, Reader, native ELF or Docker.

The selected fresh attempt is `/tmp/cal-mapper-only-dev-20261020-0001-release3`, and the selected name is `cal-mapper-only-20261020-0001-release3`; both must remain absent before dispatch. The separate consumed Reader stage `/tmp/cal-reader-stage-20261020-0001-0008/root` is copied held no-follow into the new attempt, never modified. The exact Source archive is 23,550,300 bytes, UID/GID 1000, mode 0600, with its SHA-256 in the selected stage plan; **static review must not open its body**. The private copy is the first effect and is one-shot even if it fails. Source period is `[2026-10-20T08:20:00+00:00, 2026-10-21T08:20:00+00:00)` and is checked again immediately before Docker create. An expired period requires a new Source→Reader→Mapper selection, not a retry.

The Source predecessor is the independently reviewed disposable Source-only Docker0006 effect review SHA-256 `69483a1cd55d55b9813a47537a1f2c71f4d7f4d786924e1a43d2007d84dfdf27`, terminal SHA-256 `4b39cf98a4b9964becac7aa90086e0e77fe41c68addd6b67262544a0db47abdd`, and package manifest SHA-256 `f132b3e1908e9e116464ad29c3db7f56ca17d4dee080e60ffa62547dd9588a5b`. Its terminal observes Docker client and daemon exit 0; **no separate Source external-OS-exit artifact is claimed**. The Reader predecessor is the independently reviewed unified0006 effect review SHA-256 `80886da75c0849f123365d1ac6adcc5b0eea4927d9b268352c4c7c2261c2be39`, final SHA-256 `42550aa40ea1b3a69e97809f3ba91e36f2fb8aa193636c98d3f99e725e184b6c`, receipt SHA-256 `51a06890a9b5d120409127989578fdb944fccc2f02776fcd89b1713041cd978d`, and separate external OS-exit-0 observation SHA-256 `68035fae0b759b635c6ae8b3d0d686dc92be98c88eb60fec30b7512cecbcb6b3`. All are rechecked without opening the archive body.

The Docker vector is closed by `docker_create_argv` and independently recomputed in `docker_protocol.exact_create_argv`. Image ID is `sha256:7ca5c679c6d8931d268bf5111cb7156a6eeadd9a267bc73f247cd0f0b0428874`; UID/GID is 1000:1000 with host user namespace, no network, read-only root, cap drop, pids 16, 1 GiB memory, CPU 1, exact root/package/native/tool mounts and 512 MiB private scratch tmpfs. The public native ELF SHA-256 is `fb8472564c95ba815b4c6192ff2d2dd8a0a49fad83549056f151e820de24aa1c`; the separately selected image probe proves `PASS_LOAD_ONLY`, not protocol success. Mapper `build.py` is the reviewed five-file projection, with exact original Source/Reader/Mapper pins and 55-leaf expected output. Post-effect output verification checks all 55 leaves, manifest and 15-node/10-edge/25-join result, two declared native seal and two cold-read processes, native cut, Source package binding and authority-none fields. The original native builder protocol must still be observed on the real effect and independently reviewed.

Static checks already run with normal and `-O` Python: 10/10 each, including full synthetic controller-to-production-absence-parser composition and public predecessor evidence. They do not call `preflight`, perform a real private copy, run real Docker create/start/remove, or run the Mapper entrypoint. The one-shot protocol records `prepared.json`, `precreate.json`, `terminal.json`, and `final.json` under the new attempt's 0700 evidence directory. A Docker ambiguity, cleanup failure, output mismatch, evidence-path custody failure, or missing external observation is UNKNOWN; no in-place retry is permitted. A Docker terminal PASS alone is not Mapper PASS. The real Python process OS exit must be captured separately at dispatch and included in post-effect review.

## Exact future dispatch sequence — not run at this freeze

1. Independently review this exact `freeze.json` and its members. Write `MAPPER-ONLY-DOCKER-RELEASE-INDEPENDENT-STATIC-REVIEW-0003.md` with literal `Verdict: PASS` and the exact release freeze SHA-256 only if it passes. Then perform a separate same-state predispatch review, checking fresh attempt/name absence, selected file bytes, Source period, Docker/image/UID/mount feasibility, stage metadata without archive-body read, and release authorization shape. Write `MAPPER-ONLY-DOCKER-RELEASE-INDEPENDENT-SAME-STATE-PREDISPATCH-REVIEW-0003.md` with literal `Verdict: PASS` and the same release freeze SHA-256 only if it passes.
2. Only after both PASS reviews, create `implementation/lab-runtime/local-host/mapper-only-docker-release-0003-authorization.json` as mode 0600, owned by UID/GID 1000. Its exact JSON fields are `schema_version: lab-mapper-release-authorization/v1`, `status: PASS_STATIC_AND_SAME_STATE_PREDISPATCH`, `freeze_sha256: <exact release freeze SHA-256>`, `static: {path: <absolute static review path>, sha256: <hash>}`, and `predispatch: {path: <absolute predispatch review path>, sha256: <hash>}`. Do not place this changing authorization in the frozen release directory.
3. From this directory, dispatch **once** before period expiry using the pinned `/usr/bin/python3.14 -B -S` command below. Capture its actual external process OS exit, stdout and stderr bytes/hashes in a separate observation. If the process fails, retain the entire attempt and observed evidence; do not rerun this attempt/name or rewrite authorization as a retry mechanism.
4. After exit 0, independently inspect final/terminal and output through their exact frozen selection, verify Docker ID/name absence, native protocol output and all 55 leaf bindings, post-close Source/Reader stage invariance, and effect evidence attachment. Only then issue a narrow Mapper candidate PASS review. A later Context phase needs its own source/package selection and independent review.

Exact read-only static commands from the release directory:

```bash
sha256sum freeze.json
/usr/bin/python3.14 -B -S -m unittest -v test_release_static
/usr/bin/python3.14 -B -S -O -m unittest -v test_release_static
/usr/bin/python3.14 -B -S -c 'import controller; print(controller.release_freeze_gate())'
```

Once both named independent review files for release0003 exist and contain `Verdict: PASS` plus the exact freeze SHA-256, create the authorization **once** with this command from the repository root:

```bash
python3 - <<'PY'
from pathlib import Path
import hashlib, json, os
local = Path('/home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host')
release = local / 'mapper-only-docker-release-0003'
freeze_sha = hashlib.sha256((release / 'freeze.json').read_bytes()).hexdigest()
reviews = {
    'static': local / 'MAPPER-ONLY-DOCKER-RELEASE-INDEPENDENT-STATIC-REVIEW-0003.md',
    'predispatch': local / 'MAPPER-ONLY-DOCKER-RELEASE-INDEPENDENT-SAME-STATE-PREDISPATCH-REVIEW-0003.md',
}
bound = {}
for key, path in reviews.items():
    raw = path.read_bytes()
    if b'Verdict: PASS' not in raw or freeze_sha.encode() not in raw:
        raise SystemExit('selected review does not approve exact freeze: ' + str(path))
    bound[key] = {'path': str(path), 'sha256': hashlib.sha256(raw).hexdigest()}
value = {'schema_version': 'lab-mapper-release-authorization/v1',
         'status': 'PASS_STATIC_AND_SAME_STATE_PREDISPATCH',
         'freeze_sha256': freeze_sha, **bound}
target = local / 'mapper-only-docker-release-0003-authorization.json'
fd = os.open(target, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
with os.fdopen(fd, 'wb') as handle:
    handle.write((json.dumps(value, sort_keys=True, indent=2) + '\n').encode())
    handle.flush()
    os.fsync(handle.fileno())
PY
```

Then dispatch once and capture the external Python OS exit with this command from the release directory. It creates a separate 0700 observer directory exclusively before the effect, so a second dispatch attempt stops before launching the controller:

```bash
python3 - <<'PY'
from pathlib import Path
import hashlib, json, os, subprocess
here = Path('/home/vlad_/projects/CyberAlchemy-lab/implementation/lab-runtime/local-host/mapper-only-docker-release-0003')
out = Path('/tmp/cal-mapper-only-dev-20261020-0001-release3-external-observation')
out.mkdir(mode=0o700)
env = os.environ.copy()
env.pop('PYTHONPATH', None)
env.pop('PYTHONHOME', None)
env['PATH'] = '/usr/bin:/bin'
env['PYTHONPYCACHEPREFIX'] = '/home/vlad_/projects/CyberAlchemy-lab/docs/plans/0011-lab-runtime-completion/runs/0001-execution/runtime-completion-0001/LC-U01-02/python-bytecode-cache-disabled-0002'
result = subprocess.run(['/usr/bin/python3.14', '-B', '-S', str(here / 'controller.py'),
                         '--execute-reviewed-one-shot'], cwd=here,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                        check=False, env=env)
for name, raw in (('stdout.bin', result.stdout), ('stderr.bin', result.stderr)):
    fd = os.open(out / name, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())
record = {'schema_version': 'lab-mapper-external-exec/v1',
          'tool_exit_code': result.returncode,
          'stdout_sha256': hashlib.sha256(result.stdout).hexdigest(),
          'stderr_sha256': hashlib.sha256(result.stderr).hexdigest(),
          'attempt': '/tmp/cal-mapper-only-dev-20261020-0001-release3'}
fd = os.open(out / 'external-exec.json', os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
with os.fdopen(fd, 'wb') as handle:
    handle.write((json.dumps(record, sort_keys=True, indent=2) + '\n').encode())
    handle.flush()
    os.fsync(handle.fileno())
print(json.dumps(record, sort_keys=True))
PY
```

At this freeze, the claim is **release candidate constructed and statically tested, effect held**. No private Source archive body was opened by this task, no Mapper Docker effect occurred, no Mapper package exists, and no Source8 protected authority or original runtime qualification is claimed.
