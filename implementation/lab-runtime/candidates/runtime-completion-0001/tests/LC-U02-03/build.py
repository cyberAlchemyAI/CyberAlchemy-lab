"""Owned offline build; no ambient Cargo home, registry mutation or network."""
import argparse
import datetime
import time
import hashlib
import json
import os
from pathlib import Path
import stat
import signal
import resource
import re
import subprocess
import sys
import tarfile
import tomllib

sys.dont_write_bytecode = True
S = Path(__file__).absolute().parents[2]
REPO = S.parents[3]
E = REPO / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/runtime-completion-0001/LC-U02-03'
OLD = E.parent / 'LC-U01-02'
PREFIX = OLD / 'python-bytecode-cache-disabled-0002'
PREFIX_SHA = 'a5712f1655f68e6f8fe7cacbfb454dc0be0cd1ad8f22f1788fbad7b8adafae29'
BASELINE_SHA = 'e3541b1f668375686b0c9e6c871acbeb1258830a1ac5ee84f025efd976343b3d'
PREDECESSOR_SHA = '909ab7c0982f1354220ae1ef42faae70007de38a7408d3ca1e980785e502d778'
REGISTRY = Path('/home/vlad_/.cargo/registry')
REGISTRY_ID = 'index.crates.io-1949cf8c6b5b557f'
BASE64_SHA = '72b3254f16251a8381aa12e40e3c4d2f0199f8c6508fbecb9d91f575e0fbb8c6'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def stable(path, expected=None, maximum=128 * 1024 * 1024):
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_size > maximum:
            raise ValueError('input type/size')
        raw = bytearray()
        while True:
            block = os.read(fd, min(1024 * 1024, maximum + 1 - len(raw)))
            if not block:
                break
            raw.extend(block)
            if len(raw) > maximum:
                raise ValueError('input bound')
        after = os.fstat(fd)
        if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (
                after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns):
            raise ValueError('input changed')
        raw = bytes(raw)
        if expected is not None and sha(raw) != expected:
            raise ValueError('input digest')
        return raw
    finally:
        os.close(fd)


def exclusive(path, raw):
    with path.open('xb') as out:
        out.write(raw)
        out.flush()
        os.fsync(out.fileno())


def save(path, value):
    exclusive(path, (json.dumps(value, sort_keys=True, indent=2) + '\n').encode())


def host_inputs():
    stable(PREFIX, PREFIX_SHA, 58)
    if os.environ.get('PYTHONPYCACHEPREFIX') != str(PREFIX) or not sys.flags.no_site or not sys.dont_write_bytecode:
        raise ValueError('guarded Python launch required')
    baseline = json.loads(stable(S / 'control/baseline.json', BASELINE_SHA))
    stable(OLD / 'coordinator-acceptance-0001.json', PREDECESSOR_SHA)
    selected = baseline['toolchain']
    tools = {}
    for name in ('cargo', 'rustc'):
        row = selected[name]['actual_binary']
        stable(Path(row['path']), row['sha256'])
        tools[name] = row['path']
    gcc = selected['gcc']
    stable(Path(gcc['resolved_path']), gcc['sha256'])
    tools['linker'] = gcc['resolved_path']
    # Cargo searches ancestor config even when CARGO_HOME is isolated.
    for parent in [E, *E.parents]:
        for name in ('config', 'config.toml'):
            if (parent / '.cargo' / name).exists() or (parent / '.cargo' / name).is_symlink():
                raise ValueError('unselected Cargo ancestor config')
    return tools


def setup(work):
    tools = host_inputs()
    work.mkdir(mode=0o700)
    for name in ('cargo-home', 'target', 'tmp', 'vendor', 'archives'):
        (work / name).mkdir(mode=0o700)
    predecessor_lock = S / 'tests/LC-U01-02/rust-codec/Cargo.lock'
    postimage = json.loads(stable(OLD / 'implementation-postimage-0002.json',
        '3c994f5ba32485a95a122527d545f12b7b0157ba87695f67aeb1be371ea1063f'))
    pins = [p for p in postimage['files'] if p['path'] == str(predecessor_lock.relative_to(REPO))]
    if len(pins) != 1:
        raise ValueError('predecessor lock pin required')
    lock_raw = stable(predecessor_lock, pins[0]['sha256'])
    packages = [p for p in tomllib.loads(lock_raw.decode())['package'] if 'source' in p]
    packages.append({'name': 'base64', 'version': '0.22.1',
                     'source': 'registry+https://github.com/rust-lang/crates.io-index', 'checksum': BASE64_SHA})
    records = []
    for package in packages:
        if package['source'] != 'registry+https://github.com/rust-lang/crates.io-index':
            raise ValueError('unsupported dependency origin')
        name, version, digest = package['name'], package['version'], package['checksum']
        prefix = f'{name}-{version}'
        archive = REGISTRY / 'cache' / REGISTRY_ID / (prefix + '.crate')
        raw = stable(archive, digest)
        if len(name) == 1:
            index_rel = '1/' + name
        elif len(name) == 2:
            index_rel = '2/' + name
        elif len(name) == 3:
            index_rel = '3/' + name[0] + '/' + name
        else:
            index_rel = name[:2] + '/' + name[2:4] + '/' + name
        index_path = REGISTRY / 'index' / REGISTRY_ID / '.cache' / index_rel
        index_raw = stable(index_path)
        rows = [json.loads(x) for x in index_raw.split(b'\0') if x.startswith(b'{')]
        versions = [r for r in rows if r['vers'] == version]
        if len(versions) != 1 or versions[0]['cksum'] != digest:
            raise ValueError('registry archive/index mismatch')
        exclusive(work / 'archives' / (prefix + '.crate'), raw)
        import io
        files = {}
        with tarfile.open(fileobj=io.BytesIO(raw), mode='r:gz') as tar:
            for member in tar:
                parts = Path(member.name).parts
                if not parts or parts[0] != prefix or any(p in ('', '.', '..') for p in parts):
                    raise ValueError('archive path')
                target = work / 'vendor' / member.name
                if member.isdir():
                    target.mkdir(parents=True, exist_ok=True)
                elif member.isfile():
                    target.parent.mkdir(parents=True, exist_ok=True)
                    body = tar.extractfile(member).read()
                    exclusive(target, body)
                    files['/'.join(parts[1:])] = sha(body)
                else:
                    raise ValueError('archive nonregular member')
        save(work / 'vendor' / prefix / '.cargo-checksum.json', {'files': files, 'package': digest})
        records.append({'name': name, 'version': version, 'archive_sha256': digest,
                        'archive_bytes': len(raw), 'index_path': str(index_path),
                        'index_sha256': sha(index_raw), 'index_bytes': len(index_raw),
                        'selected_index_record': versions[0], 'source_files': files})
    config = ('[source.crates-io]\nreplace-with = "selected-offline"\n'
              '[source.selected-offline]\ndirectory = ' + json.dumps(str(work / 'vendor')) + '\n'
              '[net]\noffline = true\n')
    exclusive(work / 'cargo-home/config.toml', config.encode())
    save(work / 'dependency-inputs.json', {'schema_version': 'lab-broker-offline-inputs/v1',
        'predecessor_lock_sha256': sha(lock_raw), 'tools': tools, 'packages': records,
        'config_sha256': sha(config.encode()), 'authority_effect': 'none'})
    return tools


def environment(work, tools):
    return {'PATH': '/usr/bin:/bin', 'LC_ALL': 'C', 'CARGO_HOME': str(work / 'cargo-home'),
            'CARGO_TARGET_DIR': str(work / 'target'), 'TMPDIR': str(work / 'tmp'),
            'RUSTC': tools['rustc'], 'RUSTDOC': str(Path(tools['rustc']).with_name('rustdoc')),
            'CARGO_TARGET_X86_64_UNKNOWN_LINUX_GNU_LINKER': tools['linker'],
            'CARGO_INCREMENTAL': '0', 'RUST_BACKTRACE': '0', 'SOURCE_DATE_EPOCH': '0',
            'RUST_TEST_THREADS': '1'}


def verify_build_inputs(work, expected):
    if not expected or len(expected) != 64:
        raise ValueError('independent dependency manifest digest required')
    value = json.loads(stable(work / 'dependency-inputs.json', expected))
    if (work / '.cargo').exists() or (work / '.cargo').is_symlink() or (work / 'cargo-home/config').exists() or (work / 'cargo-home/config').is_symlink():
        raise ValueError('unselected Cargo configuration')
    tools = host_inputs()
    if value['tools'] != tools:
        raise ValueError('selected tools changed')
    stable(work / 'cargo-home/config.toml', value['config_sha256'])
    # Effective extracted build scripts/proc macros are checked before Cargo,
    # including exact file inventory and checksums, not just archive ancestry.
    expected_files = set()
    for p in value['packages']:
        name = p['name'] + '-' + p['version']
        stable(work / 'archives' / (name + '.crate'), p['archive_sha256'])
        checksum = json.loads(stable(work / 'vendor' / name / '.cargo-checksum.json'))
        if checksum != {'files': p['source_files'], 'package': p['archive_sha256']}:
            raise ValueError('vendor checksum mapping changed')
        expected_files.add(name + '/.cargo-checksum.json')
        for relative, digest in p['source_files'].items():
            stable(work / 'vendor' / name / relative, digest)
            expected_files.add(name + '/' + relative)
    observed = set()
    for parent, dirs, files in os.walk(work / 'vendor', followlinks=False):
        for name in dirs:
            if not stat.S_ISDIR(os.lstat(Path(parent) / name).st_mode):
                raise ValueError('vendor non-directory')
        for name in files:
            path = Path(parent) / name
            if not stat.S_ISREG(os.lstat(path).st_mode):
                raise ValueError('vendor nonregular file')
            observed.add(path.relative_to(work / 'vendor').as_posix())
    if observed != expected_files:
        raise ValueError('vendor file inventory changed')
    return tools


def verify_toolchain(path, expected):
    if not expected or len(expected) != 64:
        raise ValueError('independent local toolchain manifest digest required')
    value = json.loads(stable(path, expected))
    if value['schema_version'] != 'lab-broker-local-toolchain-inputs/v1' or not value['files']:
        raise ValueError('toolchain manifest')
    seen = set()
    for row in value['locators']:
        if str(Path(row['path']).resolve(strict=True)) != row['resolved_path']:
            raise ValueError('toolchain locator changed')
    for row in value['files']:
        path = row['path']
        if path in seen:
            raise ValueError('duplicate toolchain input')
        seen.add(path)
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(fd, 'rb') as stream:
            before = os.fstat(stream.fileno())
            if not stat.S_ISREG(before.st_mode) or before.st_size != row['size_bytes']:
                raise ValueError('toolchain file type/size')
            actual = hashlib.file_digest(stream, 'sha256').hexdigest()
            after = os.fstat(stream.fileno())
            if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (
                    after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns):
                raise ValueError('toolchain file drift')
            if actual != row['sha256']:
                raise ValueError('toolchain file digest')


def source_snapshot():
    paths=[]
    start=json.loads(stable(E/'coordinator-start-0001.json','a193a49286088c167f860dc0fffbacfcc2c606308f4457f1cdbeb86cdf2fa546'))
    for dep in start['accepted_dependencies']:
        for key in ('acceptance_binding','review_binding','postimage_binding'):
            row=dep[key];stable(REPO/row['path'],row['sha256'])
        post=json.loads(stable(REPO/dep['postimage_binding']['path'],dep['postimage_binding']['sha256']))
        for row in post['files']:
            path=REPO/row['path'];stable(path,row['sha256']);paths.append(path)
    for rel in ('broker/src/main.rs','broker/src/state.rs','broker/src/quota.rs'):
        path=S/rel
        if path.exists(): paths.append(path)
    for path in (S/'tests/LC-U02-03').iterdir():
        if not stat.S_ISREG(path.lstat().st_mode):raise ValueError('nonregular unit source')
        paths.append(path)
    return {str(p.relative_to(S)) if p.is_relative_to(S) else str(p):sha(stable(p)) for p in paths}

def command(work, tools, args, label, test_filter=None):
    if not label or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-' for c in label):
        raise ValueError('evidence label')
    argv = [tools['cargo'], *args, '--manifest-path', str(S / 'tests/LC-U02-03/Cargo.toml')]
    if test_filter is not None:
        if not re.fullmatch(r'[a-zA-Z0-9_:]+', test_filter):
            raise ValueError('closed test filter')
        argv.append(test_filter)
    argv.extend(['--', '--nocapture'])
    before = source_snapshot()
    vector_root=work/(label+'-vectors');vector_root.mkdir(mode=0o700)
    scratch_root=work/(label+'-scratch');scratch_root.mkdir(mode=0o700)
    selected_environment=environment(work,tools);selected_environment['LAB_DISPATCH_VECTOR_DIR']=str(vector_root)
    selected_environment['TMPDIR']=str(scratch_root)
    def limits():
        resource.setrlimit(resource.RLIMIT_FSIZE, (64 * 1024 * 1024, 64 * 1024 * 1024))
    with (work / (label + '.stdout')).open('xb') as out, (work / (label + '.stderr')).open('xb') as err:
        start_utc = datetime.datetime.now(datetime.UTC).isoformat()
        start_monotonic = time.monotonic()
        child = subprocess.Popen(argv, cwd=work, env=selected_environment, stdout=out, stderr=err,
                                 start_new_session=True, preexec_fn=limits)
        try:
            stat_text = Path('/proc', str(child.pid), 'stat').read_text()
            child_start_ticks = int(stat_text.rsplit(')', 1)[1].split()[19])
        except (OSError, ValueError, IndexError):
            child_start_ticks = None
        timed_out = False
        try:
            code = child.wait(timeout=600)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(child.pid, signal.SIGKILL)
            code = child.wait()
        except BaseException:
            os.killpg(child.pid, signal.SIGKILL)
            child.wait()
            raise
    end_utc = datetime.datetime.now(datetime.UTC).isoformat()
    elapsed_seconds = time.monotonic() - start_monotonic
    # Retain the real child terminal even when the accepted log ceiling fails.
    stdout = stable(work / (label + '.stdout'), maximum=64 * 1024 * 1024)
    stderr = stable(work / (label + '.stderr'), maximum=64 * 1024 * 1024)
    logs_within_bound = max(len(stdout), len(stderr)) <= 16 * 1024 * 1024
    after = source_snapshot()
    drift = before != after
    save(work / (label + '.json'), {'argv': argv, 'environment': selected_environment,
         'returncode': code, 'stdout_sha256': sha(stdout), 'stderr_sha256': sha(stderr),
         'source_preimage': before, 'source_postimage': after, 'source_drift': drift,
         'authority_effect': 'none', 'timed_out': timed_out, 'logs_within_accepted_bound': logs_within_bound, 'deadline_seconds': 600,
         'child_pid': child.pid, 'child_start_ticks': child_start_ticks, 'child_reaped': True,
         'start_utc': start_utc, 'end_utc': end_utc, 'elapsed_seconds': elapsed_seconds})
    if timed_out or not logs_within_bound:
        raise ValueError('Bounded child failed; exact terminal and logs retained')
    sys.stderr.buffer.write(stderr)
    if code or drift:
        raise ValueError('Cargo command failed; exact output retained')
    return stdout


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--initialize', action='store_true')
    parser.add_argument('--label', default='build')
    parser.add_argument('--dependency-sha')
    parser.add_argument('--toolchain-manifest', type=Path)
    parser.add_argument('--toolchain-sha')
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--test-filter')
    args = parser.parse_args()
    work = args.work.absolute()
    if work.parent != E or not work.name.startswith(('offline-build-', 'reviewer-offline-build-')):
        raise SystemExit('exact owned build root required')
    if args.prepare_only != args.initialize:
        raise ValueError('initialization is prepare-only; separately select its dependency and toolchain digests before building')
    tools = setup(work) if args.initialize else verify_build_inputs(work, args.dependency_sha)
    if args.prepare_only:
        print(json.dumps({'dependency_manifest': str(work / 'dependency-inputs.json'),
            'sha256': sha(stable(work / 'dependency-inputs.json')), 'result': 'PREPARED', 'authority_effect': 'none'}))
        raise SystemExit(0)
    if args.toolchain_manifest is None:
        raise ValueError('selected toolchain closure required')
    verify_toolchain(args.toolchain_manifest, args.toolchain_sha)
    output = command(work, tools, ['test', '--offline', '--locked', '--all-targets'], args.label, args.test_filter)
    verify_build_inputs(work, args.dependency_sha)
    verify_toolchain(args.toolchain_manifest, args.toolchain_sha)
    checks = sum(int(n) for n in re.findall(rb'test result: ok\. (\d+) passed;', output))
    if checks < 1:
        raise ValueError('no completed Rust tests')
    print(json.dumps({'schema_version': 'lab-case-command-result/v1', 'result': 'PASS',
          'checks': checks, 'effect_state': 'owned-inert', 'cleanup': 'retained-owned'}))
