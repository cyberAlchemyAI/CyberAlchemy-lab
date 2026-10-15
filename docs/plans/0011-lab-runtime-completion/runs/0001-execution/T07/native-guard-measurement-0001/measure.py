"""Measure original complete guards; no native call, lease, callback or clock patch."""
import hashlib, importlib.util, json, os, sys, time, traceback
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
    fd = os.open(HERE/name, os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC, 0o600)
    try:
        with os.fdopen(fd, 'wb', closefd=False) as stream:
            stream.write(raw); stream.flush(); os.fsync(fd)
    finally: os.close(fd)

def module(name, row):
    need(name not in sys.modules, 'fresh true-origin namespace required')
    p = ROOT/row['path']; raw = p.read_bytes()
    need(sha(raw) == row['sha256'], 'independent selected module differs')
    spec = importlib.util.spec_from_file_location(name, p)
    value = importlib.util.module_from_spec(spec); sys.modules[name] = value
    exec(compile(raw, str(p), 'exec'), value.__dict__)
    return value

def main():
    need(Path(sys.executable) == BASE/'bin/python' and sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode, 'selected isolated0004 Python required')
    pr = PROPOSAL.read_bytes()
    need(sha(pr) == '7980f6c77391420036b391c8a2f5931d477c81acc96771d5ed89a23a469ad859', 'independent bootstrap proposal differs')
    bindings = json.loads(pr)['module_bindings']; loaded = {}
    for name in ('checked_io', 'stage_io', 'closure', 'dependencies', 'control', 'executor', 'api_guard'):
        namespace = name if name in ('checked_io', 'stage_io', 'closure') else '_Root_guard_measure_'+name
        loaded[name] = module(namespace, bindings[name])
    control = loaded['control']; deps = loaded['dependencies']
    for row in bindings.values(): control.capture(ROOT/row['path'], row['sha256'])
    raw = control.capture(SELECTION, '3b0c97b2b31363f6d344af10e2dde3281dbffb042a6746e67f0b9fe1795a3bf4')
    executor = loaded['executor'].SelectedOntologyExecutor(raw, sha(raw), deps, control)
    fd0 = len(os.listdir('/proc/self/fd')); phases = []; failure = None; exit_errors = []
    def measured(label, callback):
        started = time.perf_counter(); cpu = time.process_time(); ok = False
        try:
            value = callback(); ok = True
            return value
        finally:
            row = {'phase': label, 'success': ok, 'elapsed_seconds': time.perf_counter()-started, 'process_cpu_seconds': time.process_time()-cpu}
            phases.append(row); emit('phase-%02d.json'%len(phases), row)
    entered = False
    try:
        measured('original-full28597-API-Source-entry', lambda: loaded['api_guard'].verify(SOURCE)); entered = True
        measured('original-full720-source-wheel77ELF-ABI-preflight', lambda: deps.preflight(ROOT/executor.value['base_dependency_selection_binding']['path'], executor.value['base_dependency_selection_binding']['sha256']))
        measured('original-strict1010-base-installation', lambda: deps.verify_installed(BASE, executor.base))
        measured('original-double-read1011-extension-installed', lambda: control.installed(executor.root, executor.expected))
        measured('whole-selected-ontology-executor-guard', executor.guard)
    except BaseException:
        kind, error, tb = sys.exc_info()
        failure = {'exception_class': kind.__name__, 'message': str(error), 'frames': [{'path': f.filename, 'line': f.lineno, 'function': f.name} for f in traceback.extract_tb(tb)]}
    finally:
        if entered:
            try: measured('original-full28597-API-Source-exit', lambda: loaded['api_guard'].verify(SOURCE))
            except BaseException as error: exit_errors.append({'exception_class': type(error).__name__, 'message': str(error)})
        try:
            for row in bindings.values(): control.capture(ROOT/row['path'], row['sha256'])
            control.capture(SELECTION, '3b0c97b2b31363f6d344af10e2dde3281dbffb042a6746e67f0b9fe1795a3bf4')
        except BaseException as error: exit_errors.append({'exception_class': type(error).__name__, 'message': str(error)})
    delta = len(os.listdir('/proc/self/fd'))-fd0
    emit('result.json', {'authority_effect': 'none', 'phases': phases, 'failure': failure, 'exit_errors': exit_errors, 'FD_delta': delta, 'native_calls': 0, 'guards_callbacks_or_clocks_modified': False, 'full_runtime_qualification': False, 'claim_ceiling': 'One same-process guard measurement; no repeated-run variance, guard optimization, runtime speedup or task completion claimed.'})
    return 0 if failure is None and not exit_errors and delta == 0 else 1

if __name__ == '__main__': raise SystemExit(main())
