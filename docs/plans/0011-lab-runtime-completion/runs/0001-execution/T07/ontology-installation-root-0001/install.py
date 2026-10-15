"""Root-owned separate ontology installation; preserve partial output on refusal."""
import hashlib, importlib.util, json, os, stat, sys, tempfile, traceback
from pathlib import Path

ROOT = Path('/home/vlad_/projects/CyberAlchemy-lab')
HERE = Path(__file__).absolute().parent
PROPOSAL = ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T32/native-qualification-bootstrap-independent-review-0001/ROOT-BOOTSTRAP-PROPOSAL.json'
PROPOSAL_SHA = '7980f6c77391420036b391c8a2f5931d477c81acc96771d5ed89a23a469ad859'
BASE = ROOT/'product/lab/release-candidates/v1/interface/runtime-dependencies-v2-completion-0001/installations/0004'

def need(ok, why):
    if not ok: raise ValueError(why)

def digest(raw): return hashlib.sha256(raw).hexdigest()

def write(name, raw):
    fd = os.open(HERE/name, os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC, 0o600)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, 'wb', closefd=False) as stream:
            stream.write(raw); stream.flush(); os.fsync(fd)
    finally: os.close(fd)

def emit(name, value):
    write(name, (json.dumps(value, sort_keys=True, indent=2)+'\n').encode())

def anchor(path):
    need(not any(p.is_symlink() for p in (path, *path.parents)), 'installation path alias')
    s = path.stat()
    need(stat.S_ISDIR(s.st_mode) and s.st_uid == os.getuid() and stat.S_IMODE(s.st_mode) == 0o700, 'private owned installation required')
    return {'path': str(path), 'device': s.st_dev, 'inode': s.st_ino, 'uid': s.st_uid, 'mode': stat.S_IMODE(s.st_mode)}

def main():
    need(Path(sys.executable) == BASE/'bin/python' and sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode, 'selected0004 isolated Python required')
    raw = PROPOSAL.read_bytes(); need(digest(raw) == PROPOSAL_SHA, 'independent bootstrap proposal differs')
    proposal = json.loads(raw)
    launcher = proposal['launcher']; lp = ROOT/launcher['path']
    need(digest(lp.read_bytes()) == launcher['sha256'] == '1be0ac60161c863e44ef9ad6a3711fd3ab671d8f7ae00a06da947491ac386568', 'independent launcher differs')
    # Use reviewed bounded capture, not a path-only import of mutable code.
    capture_binding = proposal['module_bindings']['checked_io']
    cp = ROOT/capture_binding['path']; cr = cp.read_bytes()
    need(digest(cr) == capture_binding['sha256'], 'checked IO bootstrap differs')
    need('checked_io' not in sys.modules, 'fresh bootstrap namespace required')
    spec = importlib.util.spec_from_file_location('checked_io', cp)
    checked = importlib.util.module_from_spec(spec); sys.modules['checked_io'] = checked
    exec(compile(cr, str(cp), 'exec'), checked.__dict__)
    # control.capture provides full held ancestor/leaf attachment checks.
    loaded = {'checked_io': checked}
    for key in ('stage_io', 'closure', 'dependencies', 'control', 'executor'):
        row = proposal['module_bindings'][key]; path = ROOT/row['path']
        code = path.read_bytes(); need(digest(code) == row['sha256'], 'selected module differs')
        name = key if key in ('stage_io', 'closure') else '_Root_ontology_'+key
        need(name not in sys.modules, 'fresh selected module namespace required')
        sp = importlib.util.spec_from_file_location(name, path)
        value = importlib.util.module_from_spec(sp); sys.modules[name] = value
        exec(compile(code, str(path), 'exec'), value.__dict__); loaded[key] = value
    control = loaded['control']
    for row in proposal['module_bindings'].values(): control.capture(ROOT/row['path'], row['sha256'])
    control.capture(PROPOSAL, PROPOSAL_SHA); control.capture(lp, launcher['sha256'])
    base = anchor(BASE); need(base == proposal['base_installation_observation'], 'original0004 anchor changed')
    parent = BASE.parent
    newroot = Path(tempfile.mkdtemp(prefix='ontology-0001-', dir=parent)); os.chmod(newroot, 0o700)
    new = anchor(newroot); need(os.listdir(newroot) == [], 'new root must be empty')
    emit('started.json', {'authority_effect': 'none', 'base_installation': base, 'new_installation': new, 'original0004_mutated': False})
    failure = None; result = None; fd0 = len(os.listdir('/proc/self/fd'))
    try:
        executor_module = loaded['executor']; deps = loaded['dependencies']
        raw = executor_module.prepare_selection(proposal['source_additions_for_prepare_selection'], base, new, proposal['closed_executor_module_bindings'], deps, control)
        write('execution-selection.json', raw)
        pin = digest(raw)
        executor = executor_module.SelectedOntologyExecutor(raw, pin, deps, control)
        need(len(executor.expected) == 1011, 'whole original1010 plus ontology role required')
        result = executor_module.provision(executor)
        executor.guard()
        need(anchor(BASE) == base, 'original installation root changed')
        deps.verify_installed(BASE, executor.base)
        result.update({'selection_binding': {'path': str((HERE/'execution-selection.json').relative_to(ROOT)), 'sha256': pin}, 'installation_receipt_binding': executor.value['installation_receipt_binding'], 'installed_payloads': len(executor.expected), 'original0004_full1010_exit_guard': 'PASS'})
    except BaseException:
        kind, error, tb = sys.exc_info()
        failure = {'exception_class': kind.__name__, 'message': str(error), 'frames': [{'path': f.filename, 'line': f.lineno, 'function': f.name} for f in traceback.extract_tb(tb)]}
    delta = len(os.listdir('/proc/self/fd'))-fd0
    emit('result.json', {'authority_effect': 'none', 'result': result, 'failure': failure, 'FD_delta': delta, 'partial_root_preserved': True, 'native_cases_run': False, 'whole_task_complete': False})
    return 0 if failure is None and delta == 0 else 1

if __name__ == '__main__': raise SystemExit(main())
