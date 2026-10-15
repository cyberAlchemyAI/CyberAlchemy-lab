"""Observe real descriptor custody around the original public catalog replay."""
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

def snapshot():
    rows = []
    for name in os.listdir('/proc/self/fd'):
        try: state = os.fstat(int(name))
        except OSError: continue
        rows.append({'fd': int(name), 'mode': state.st_mode, 'device': state.st_dev, 'inode': state.st_ino, 'uid': state.st_uid})
    return sorted(rows, key=lambda r: r['fd'])

def main():
    need(Path(sys.executable) == BASE/'bin/python' and sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode, 'selected isolated0004 Python required')
    deps_path = str(BASE/'deps')
    if deps_path in sys.path: sys.path.remove(deps_path)
    sys.path.insert(0, deps_path)
    state = HERE.stat(follow_symlinks=False)
    need(stat.S_ISDIR(state.st_mode) and state.st_uid == os.getuid() and stat.S_IMODE(state.st_mode) == 0o700, 'fresh owned700 output directory required')
    need(set(os.listdir(HERE)) == {'probe.py'}, 'fresh exclusive probe output directory required')
    raw = capture(PROPOSAL, '7980f6c77391420036b391c8a2f5931d477c81acc96771d5ed89a23a469ad859')
    bindings = json.loads(raw)['module_bindings']
    guard = module('_Root_catalog_probe_guard', bindings['api_guard'])
    phases = []; entered = False; failure = None; exit_errors = []
    def record(label):
        row = {'phase': label, 'fds': snapshot()}
        phases.append(row); emit('phase-%02d.json'%len(phases), row)
    try:
        guard.verify(SOURCE); entered = True
        record('after-original-fullSource-entry-before-original-catalog-imports')
        lifecycle = ROOT/'implementation/lab-ontology/candidates/v1/adapters/lifecycle'
        sys.path.insert(0, str(lifecycle.parent)); sys.path.insert(0, str(lifecycle))
        sys.path.insert(0, str(ROOT/'implementation/lab-runtime/candidates/repeatable-operation'))
        for name in ('represented_subjects', 'translation', 'native_store'):
            module(name, bindings[name])
        original = sys.modules['native_store']
        record('after-actual-original-module-imports')
        with original.signed_catalog() as (catalog, operations):
            catalog.verify(operations)
            record('inside-original-verified-catalog')
        record('after-original-catalog-exit')
        import gc
        gc.collect()
        record('after-explicit-garbage-collection')
    except BaseException:
        kind, _, tb = sys.exc_info()
        failure = {'exception_class': kind.__name__, 'frames': [{'path': f.filename, 'line': f.lineno, 'function': f.name} for f in traceback.extract_tb(tb)]}
    finally:
        if entered:
            try: guard.verify(SOURCE)
            except BaseException as error: exit_errors.append({'exception_class': type(error).__name__})
        try:
            for row in bindings.values(): capture(ROOT/row['path'], row['sha256'])
        except BaseException as error: exit_errors.append({'exception_class': type(error).__name__})
    record('after-original-fullSource-exit')
    emit('result.json', {'authority_effect': 'none', 'phases': phases, 'failure': failure, 'exit_errors': exit_errors,
         'native_ontology_calls': 0, 'actual_API_Session_Machine_or_owner_effects': False,
         'original_callbacks_and_clocks_modified': False, 'original_native_attempt_FD_delta1_explained': False,
         'claim_ceiling': 'Only real descriptor observations around original catalog import/entry/exit and garbage collection. No invented original leak cause, cleanup, runtime or whole-task qualification.'})
    return 0 if failure is None and not exit_errors else 1

if __name__ == '__main__': raise SystemExit(main())
