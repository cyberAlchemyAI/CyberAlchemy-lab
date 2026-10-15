"""Measure original complete guards; no native call, lease, callback or clock patch."""
import hashlib, importlib.util, json, os, stat, sys, time, traceback
from pathlib import Path

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE = Path(__file__).absolute().parent
RUN = ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution'
BASE = ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004'
PROPOSAL = RUN/'T32/native-qualification-bootstrap-independent-review-0001/ROOT-BOOTSTRAP-PROPOSAL.json'
SELECTION = RUN/'T07/ontology-installation-root-0001/execution-selection.json'
SOURCE = 'ee969cc8c6b539aa3247d81c82322cb9e7aefd42188d63db0195e381cdad4cb1'

def need(v, why):
    if not v: raise ValueError(why)

def sha(raw): return hashlib.sha256(raw).hexdigest()

def emit(name, value):
    raw = (json.dumps(value, sort_keys=True, indent=2)+'\n').encode()
    handles = []; links = []; leaf = None
    identity = lambda s: (s.st_dev, s.st_ino, s.st_uid, s.st_gid, s.st_mode)
    def attached():
        for parent, part, child, selected in links:
            need(identity(os.stat(part, dir_fd=parent, follow_symlinks=False)) == identity(os.fstat(child)) == selected, 'measurement ancestor detached')
    try:
        parent = os.open('/', os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC); handles.append(parent)
        for part in HERE.parts[1:]:
            child = os.open(part, os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC, dir_fd=parent); handles.append(child)
            links.append((parent, part, child, identity(os.fstat(child)))); parent = child
        state = os.fstat(parent)
        need(state.st_uid == os.getuid() and stat.S_IMODE(state.st_mode) == 0o700, 'owned700 measurement output changed')
        attached()
        leaf = os.open(name, os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC, 0o600, dir_fd=parent); os.fchmod(leaf, 0o600)
        before = os.fstat(leaf); offset = 0
        while offset < len(raw):
            count = os.write(leaf, raw[offset:]); need(count > 0, 'measurement write stalled'); offset += count
        os.fsync(leaf)
        current = os.stat(name, dir_fd=parent, follow_symlinks=False)
        need(identity(current) == identity(os.fstat(leaf)) == identity(before) and current.st_size == len(raw), 'measurement leaf detached')
        attached(); os.fsync(parent)
    finally:
        if leaf is not None: os.close(leaf)
        for fd in reversed(handles): os.close(fd)


def capture(path, pin):
    if not path.is_absolute() or '..' in path.parts:
        raise ValueError('true absolute selected origin required')
    handles = []
    links = []
    identity = lambda s: (s.st_dev,s.st_ino,s.st_uid,s.st_gid,s.st_mode,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
    try:
        parent = os.open('/', os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
        handles.append(parent)
        for part in path.parts[1:-1]:
            child = os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent)
            handles.append(child)
            links.append((parent,part,child,identity(os.fstat(child))))
            parent = child
        fd = os.open(path.name,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent)
        handles.append(fd)
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or not 0 < before.st_size <= 1024*1024:
            raise ValueError('bounded regular selected launcher/runner required')
        chunks = []
        total = 0
        while total < before.st_size:
            chunk = os.read(fd,min(65536,before.st_size-total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
        raw = b''.join(chunks)
        if len(raw) != before.st_size or os.read(fd,1) or identity(os.fstat(fd)) != identity(before):
            raise ValueError('selected code changed while captured')
        if identity(os.stat(path.name,dir_fd=parent,follow_symlinks=False)) != identity(before):
            raise ValueError('selected code attachment changed')
        for parent_fd,name,child,selected in links:
            if identity(os.stat(name,dir_fd=parent_fd,follow_symlinks=False)) != selected or identity(os.fstat(child)) != selected:
                raise ValueError('selected code ancestor changed')
        if hashlib.sha256(raw).hexdigest() != pin:
            raise ValueError('independent selected code SHA differs')
        return raw
    finally:
        for fd in reversed(handles):
            os.close(fd)

def module(name, row):
    need(name not in sys.modules, 'fresh true-origin namespace required')
    p = ROOT/row['path']; raw = capture(p, row['sha256'])
    need(sha(raw) == row['sha256'], 'independent selected module differs')
    spec = importlib.util.spec_from_file_location(name, p)
    value = importlib.util.module_from_spec(spec); sys.modules[name] = value
    exec(compile(raw, str(p), 'exec'), value.__dict__)
    return value

def main():
    need(Path(sys.executable) == BASE/'bin/python' and sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode, 'selected isolated0004 Python required')
    deps_path = str(BASE/'deps')
    if deps_path in sys.path: sys.path.remove(deps_path)
    sys.path.insert(0, deps_path)
    need(stat.S_IMODE(HERE.stat(follow_symlinks=False).st_mode) == 0o700 and HERE.stat().st_uid == os.getuid(), 'owned700 comparison output required')
    need(set(os.listdir(HERE)) == {'compare.py', 'execution-selection.json'}, 'fresh comparison output leaves required')
    raw = capture(PROPOSAL, '7980f6c77391420036b391c8a2f5931d477c81acc96771d5ed89a23a469ad859')
    bindings = json.loads(raw)['module_bindings']; loaded = {}
    for name in ('checked_io', 'stage_io', 'closure', 'dependencies', 'control', 'executor', 'api_guard'):
        namespace = name if name in ('checked_io', 'stage_io', 'closure') else '_Root_proof_compare_'+name
        loaded[name] = module(namespace, bindings[name])
    old_control = loaded['control']; deps = loaded['dependencies']
    newer = {'path': 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/installed-proof-performance-preparation-0001/control.py', 'sha256': 'a212cf5352ce7994e6a041ccc69f8f5924f01b2be2e9067c066e082ee9a9a5dd'}
    new_control = module('_Root_proof_compare_new_control', newer)
    for row in [*bindings.values(), newer]: old_control.capture(ROOT/row['path'], row['sha256'])
    old_raw = old_control.capture(SELECTION, '3b0c97b2b31363f6d344af10e2dde3281dbffb042a6746e67f0b9fe1795a3bf4')
    new_binding = {"path":"docs/plans/0011-lab-runtime-completion/runs/0001-execution/T07/installed-proof-Root-comparison-0001/execution-selection.json","sha256":"365e3270842dd33e1aa9e5f621f072210d317255155d024078cab049adb20373"}
    new_raw = old_control.capture(ROOT/new_binding['path'], new_binding['sha256'])
    old_value = json.loads(old_raw); new_value = json.loads(new_raw)
    import copy
    permitted = copy.deepcopy(old_value); permitted['module_bindings']['control'] = newer
    need(new_value == permitted, 'only independently reviewed control binding may change')
    old_executor = loaded['executor'].SelectedOntologyExecutor(old_raw, sha(old_raw), deps, old_control)
    new_executor = loaded['executor'].SelectedOntologyExecutor(new_raw, sha(new_raw), deps, new_control)
    need(old_executor.expected == new_executor.expected and len(new_executor.expected) == 1011, 'identical complete1011 proof scope required')
    need(old_value['installation_receipt_binding'] == new_value['installation_receipt_binding'], 'receipt/payloads cannot change')
    entered = False; failure = None; exit_errors = []; phases = []; fd0 = len(os.listdir('/proc/self/fd'))
    def measure(label, fn):
        start = time.perf_counter(); cpu = time.process_time(); ok = False
        try:
            value = fn(); ok = True; return value
        finally:
            row = {'phase': label, 'success': ok, 'elapsed_seconds': time.perf_counter()-start, 'process_cpu_seconds': time.process_time()-cpu}
            phases.append(row); emit('phase-%02d.json'%len(phases), row)
    def enter():
        nonlocal entered
        value = loaded['api_guard'].verify(SOURCE); entered = True; return value
    try:
        measure('original-full28597-Source-entry', enter)
        measure('old-full1011-installed-double-fresh-read', lambda: old_control.installed(old_executor.root, old_executor.expected))
        measure('new-full1011-installed-double-fresh-read', lambda: new_control.installed(new_executor.root, new_executor.expected))
        measure('old-whole720-77ELF-1010-1011-executor-guard', old_executor.guard)
        measure('new-whole720-77ELF-1010-1011-executor-guard', new_executor.guard)
    except BaseException:
        kind, error, tb = sys.exc_info()
        failure = {'exception_class': kind.__name__, 'message': str(error), 'frames': [{'path': f.filename, 'line': f.lineno, 'function': f.name} for f in traceback.extract_tb(tb)]}
    finally:
        if entered:
            try: measure('original-full28597-Source-exit', lambda: loaded['api_guard'].verify(SOURCE))
            except BaseException as error: exit_errors.append({'exception_class': type(error).__name__, 'message': str(error)})
        try:
            for row in [*bindings.values(), newer]: old_control.capture(ROOT/row['path'], row['sha256'])
            old_control.capture(ROOT/new_binding['path'], new_binding['sha256'])
            old_control.capture(SELECTION, '3b0c97b2b31363f6d344af10e2dde3281dbffb042a6746e67f0b9fe1795a3bf4')
        except BaseException as error: exit_errors.append({'exception_class': type(error).__name__, 'message': str(error)})
    delta = len(os.listdir('/proc/self/fd'))-fd0
    passed = failure is None and not exit_errors and delta == 0 and len(phases) == 6 and all(p['success'] for p in phases)
    emit('result.json', {'authority_effect': 'none', 'result': 'PASS-whole-scope-comparison' if passed else 'FAIL-preserved-comparison',
         'phases': phases, 'failure': failure, 'exit_errors': exit_errors, 'FD_delta': delta, 'selection_binding': new_binding,
         'same1011_payloads_and_receipt': True, 'both_fresh_full_byte_passes_retained': True, 'installation_or_native_calls': 0,
         'source_or_ABI_guard_or_clock_callback_suppressed': False, 'runtime_deadline_fit_or_full_task_qualified': False,
         'claim_ceiling': 'One serial comparison on actual identical installed1011 payloads. No repeated-run variance or native deadline-fit claim.'})
    return 0 if passed else 1

if __name__ == '__main__': raise SystemExit(main())
