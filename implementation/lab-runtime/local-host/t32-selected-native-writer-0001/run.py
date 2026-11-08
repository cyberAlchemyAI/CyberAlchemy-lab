#!/usr/bin/env python3
"""Selected NativeCandidateStore writer interruption and detached cold recovery."""
import hashlib
import importlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import stat
import subprocess
import sys
import tempfile
import time
import types

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
FACTORY = ROOT / 'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T32/native-original55-execution-preparation-0002/factory'
ADAPTERS = ROOT / 'implementation/lab-ontology/candidates/v1/adapters'
LIFECYCLE = ADAPTERS / 'lifecycle'
NATIVE = ROOT / 'product/lab/release-candidates/v1/interface/native-batch-recovery-v1-completion-0001'
PRODUCTION = NATIVE / 'bin-production/lab-ontology-native'
OBSERVER = NATIVE / 'build-observer/debug/lab-ontology-native'
PINS = {
    'represented_subjects.py': '8aea7147b349a73beebcaefe9bf8fa3ac7e5083ca74bb52962e6e604fd02d9c1',
    'translation.py': 'ee12db294bbf4deff637107635b95ab9f71924f1ae47bc556785875f6798d585',
    'native_store.py': '8d61ae200155fefe4e87c3d303e03a6314465d639089708cef91174efa556138',
    'generation_store.py': '18166ca54455cdaa0005113c07c8e0eabb5369d8431daa204595d5aa0c1e8982',
    'selected_store.py': '4d8f345cd7d4eb27e7dd291bc039197fc90471f1ab762bfa8fba319ffa7487bd',
    'private_io.py': 'b970a0ff9b56f03499f5fb7feb88974a90a029d080a185b417dcb1d03e7b16ec',
    'factory_init.py': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
    'capabilities.py': '9293f3bdb9aefde1e569803140195a457b051115522af2fde6c2593bbe16f944',
    'fixtures.py': '34b260f26d21166b14298d7535e18ad39d60676c08f1590d246e20a03b9f2cbf',
    'production_executable': '57416d01d3479238f9e76a967c0275f1af04466efeb130fc0125bcb94e3a3399',
    'observer_executable': '19cc878e98357a0e23136979c470ef21cf9479287047b8ebfee8139dd5f676d4',
}


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    path = Path(path)
    need(path.is_file() and not path.is_symlink(), 'selected regular file required: ' + str(path))
    return path.read_bytes()


def origin(path, expected):
    raw = read(path)
    need(sha(raw) == expected, 'selected source changed: ' + str(path))
    return raw


def module(name, path, expected, *, package=False):
    raw = origin(path, expected)
    value = types.ModuleType(name)
    value.__file__ = str(path)
    value.__package__ = name if package else name.rsplit('.', 1)[0]
    if package:
        value.__path__ = [str(path.parent)]
    sys.modules[name] = value
    exec(compile(raw, str(path), 'exec'), value.__dict__)
    return value


def binding(path):
    path = Path(path)
    return {'path': str(path.relative_to(ROOT)), 'sha256': sha(read(path))}


def selected(owned_parent):
    # The selected original files execute from their true origins. The test
    # translator itself is intentionally inert; this cut exercises append.
    module('represented_subjects', ADAPTERS / 'represented_subjects.py', PINS['represented_subjects.py'])
    module('translation', LIFECYCLE / 'translation.py', PINS['translation.py'])
    original = module('native_store', LIFECYCLE / 'native_store.py', PINS['native_store.py'])
    package = '_cal_t32_selected_factory'
    module(package, FACTORY / '__init__.py', PINS['factory_init.py'], package=True)
    module(package + '.private_io', FACTORY / 'private_io.py', PINS['private_io.py'])
    generation = module(package + '.generation_store', FACTORY / 'generation_store.py', PINS['generation_store.py'])
    selected_store = module(package + '.selected_store', FACTORY / 'selected_store.py', PINS['selected_store.py'])
    capabilities = module('_cal_t32_capabilities', HERE / 'capabilities.py', PINS['capabilities.py'])
    executable_sha = sha(origin(OBSERVER, PINS['observer_executable']))
    executor = capabilities.FixtureExecutor(OBSERVER, executable_sha)
    parent_stat = owned_parent.stat()
    identity = (parent_stat.st_dev, parent_stat.st_ino, parent_stat.st_uid, stat.S_IMODE(parent_stat.st_mode))
    boundary = capabilities.FixtureBoundary(owned_parent, identity)
    selection = {'schema_version': selected_store.VERSION, 'authority_effect': 'none',
        'original_store_binding': binding(LIFECYCLE / 'native_store.py'),
        'generation_module_binding': binding(FACTORY / 'generation_store.py'),
        'executor_class_binding': {'code_binding': binding(HERE / 'capabilities.py'), 'class_name': 'FixtureExecutor'},
        'boundary_class_binding': {'code_binding': binding(HERE / 'capabilities.py'), 'class_name': 'FixtureBoundary'},
        'owned_parent': str(owned_parent), 'owned_parent_identity': list(identity),
        'retention_policy': 'preserve-all-until-explicit-disposition'}
    factory = selected_store.StoreFactory(original, generation, executor, boundary, selection)
    return factory, capabilities, generation


def fixture(base):
    origin(PRODUCTION, PINS['production_executable'])
    source = module('_cal_t32_fixture', NATIVE / 'fixtures.py', PINS['fixtures.py'])
    request, events = source.sealed_fixture(PRODUCTION, base / 'fixture')
    need(len(events['semantic']) == len(events['governance']) == 3, 'three original sealed event pairs required')
    return events


def production_read(store, cursor):
    head, _, generation = store.head()
    origin(PRODUCTION, PINS['production_executable'])
    result = subprocess.run([str(PRODUCTION), 'read', str(generation / 'semantic'),
                             str(generation / 'governance'), str(cursor)],
                            capture_output=True, timeout=120)
    need(result.returncode == 0, 'production native cold read refused: ' + result.stderr.decode())
    value = json.loads(result.stdout)
    need(value['checkpoint_parity'] == 'PASS', 'production native checkpoint parity failed')
    return value


def child(base, stage, family):
    base = Path(base)
    owned = base / 'owned'
    factory, capabilities, _ = selected(owned)
    events = json.loads(read(base / 'events.json'))
    translator = capabilities.FixtureTranslator()
    store = factory.create(translator, OBSERVER, factory.executor.executable_sha256)
    first = store.append(events['semantic'][:1], events['governance'][:1], {})
    need(len(first['semantic_events']) == len(first['governance_events']) == 1, 'first original selected append failed')
    head = read(store.store_root / 'HEAD.json')
    bootstrap = {'store_root': str(store.store_root), 'store_identity': list(store.committed.identity),
                 'old_head_sha256': sha(head), 'first_control_path': store.commit_receipts[0]['recovery_control_binding']['path']}
    (base / 'bootstrap.json').write_text(json.dumps(bootstrap, sort_keys=True) + '\n')
    if stage in ('before-head-commit', 'after-head-commit'):
        target_line = 171 if stage == 'before-head-commit' else 172
        selected_file = str(FACTORY / 'generation_store.py')
        def trace(frame, event, arg):
            if event == 'line' and frame.f_code.co_filename == selected_file \
                    and frame.f_code.co_name == 'finish_publication' and frame.f_lineno == target_line:
                sys.settrace(None)
                (base / 'kill-ready').write_bytes(stage.encode())
                while True:
                    signal.pause()
            return trace
        sys.settrace(trace)
    else:
        factory.executor.stop_stage = stage
        factory.executor.stop_family = family
        factory.executor.marker = base / 'kill-ready'
    store.append(events['semantic'][1:2], events['governance'][1:2], {})
    raise AssertionError('interrupted original writer returned normally')


def one(stage, family):
    with tempfile.TemporaryDirectory(prefix='cal-t32-selected-writer-') as temporary:
        base = Path(temporary)
        owned = base / 'owned'
        owned.mkdir(mode=0o700)
        events = fixture(base)
        (base / 'events.json').write_text(json.dumps(events, sort_keys=True) + '\n')
        foreign = owned / 'foreign.bin'
        foreign.write_bytes(b'foreign native sibling survives')
        selected_source = globals().get('_SELECTED_RUNNER_RAW')
        need(type(selected_source) is bytes, 'pinning launcher required')
        child_loader = ('import sys\n'
                        'from pathlib import Path\n'
                        'path=sys.argv[1]\n'
                        'raw=sys.stdin.buffer.read()\n'
                        'sys.argv=sys.argv[1:]\n'
                        "scope={'__name__':'__main__','__file__':path,'_SELECTED_RUNNER_RAW':raw}\n"
                        "exec(compile(raw,path,'exec'),scope)\n")
        process = subprocess.Popen([sys.executable, '-I', '-B', '-c', child_loader,
                                    str(Path(__file__).resolve()), '--child', str(base), stage, family],
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, start_new_session=True)
        process.stdin.write(selected_source)
        process.stdin.close()
        process.stdin = None
        try:
            deadline = time.monotonic() + 90
            marker = base / 'kill-ready'
            while not marker.exists():
                if process.poll() is not None:
                    out, err = process.communicate()
                    raise ValueError(f'selected writer exited before checkpoint: {process.returncode} {out!r} {err!r}')
                need(time.monotonic() < deadline, 'native observer checkpoint absent')
                time.sleep(.01)
            need(marker.read_bytes() == stage.encode(), 'wrong native observer stage')
            os.killpg(process.pid, signal.SIGKILL)
            _, err = process.communicate(timeout=10)
            need(process.returncode == -9, f'writer was not SIGKILLed: {err!r}')
        finally:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGKILL)
                process.communicate(timeout=10)
        boot = json.loads(read(base / 'bootstrap.json'))
        store_root = Path(boot['store_root'])
        need(store_root.parent.parent == owned, 'selected store escaped owned parent')
        committed_before_kill = stage == 'after-head-commit'
        need((sha(read(store_root / 'HEAD.json')) != boot['old_head_sha256']) == committed_before_kill,
             'selected commit checkpoint had wrong HEAD state')
        need(foreign.read_bytes() == b'foreign native sibling survives', 'foreign sibling changed')
        controls = [p for p in store_root.parent.glob('recovery-control-*.json') if str(p) != boot['first_control_path']]
        need(len(controls) == 1, 'exact one pending original recovery control required')
        control = {'path': str(controls[0]), 'sha256': sha(read(controls[0]))}
        factory, _, generation = selected(owned)
        store = generation.GenerationStore(store_root, tuple(boot['store_identity']), OBSERVER,
                                           factory.executor.executable_sha256, executor=factory.executor, boundary=factory.boundary)
        before = store.read_committed()
        pre_count = 2 if committed_before_kill else 1
        need(len(before['native_cut']['semantic_events']) == len(before['native_cut']['governance_events']) == pre_count,
             'committed native cut unavailable after kill')
        production_before = production_read(store, pre_count)
        need(production_before['semantic_events'] == events['semantic'][:pre_count]
             and production_before['governance_events'] == events['governance'][:pre_count],
             'production native pre-recovery cut differs')
        refusal = None
        if not committed_before_kill:
            pending = json.loads(read(Path(json.loads(read(controls[0]))['pending_path'])))
            interrupted_stage = store_root / pending['stage']
            if not interrupted_stage.exists():
                interrupted_stage = store_root / 'generations' / ('operation-' + pending['operation'])
            need(interrupted_stage.is_dir(), 'selected interrupted generation is absent')
            foreign_residue = interrupted_stage / 'semantic' / 'unselected-foreign.bin'
            foreign_residue.write_bytes(b'foreign interruption residue must refuse')
            residue_sha = sha(read(foreign_residue))
            old_head = read(store_root / 'HEAD.json')
            try:
                factory.recover_detached(store_root=store_root, store_identity=tuple(boot['store_identity']),
                                         control_binding=control)
            except (ValueError, OSError) as error:
                refusal = {'type': type(error).__name__, 'message': str(error)}
            else:
                raise AssertionError('foreign interrupted-stage residue was accepted')
            need(read(store_root / 'HEAD.json') == old_head and sha(read(foreign_residue)) == residue_sha,
                 'foreign-residue refusal changed committed or foreign bytes')
            foreign_residue.unlink()
        recovered = factory.recover_detached(store_root=store_root, store_identity=tuple(boot['store_identity']),
                                             control_binding=control)
        after = recovered['cold_native']['native_cut']
        need(len(after['semantic_events']) == len(after['governance_events']) == 2, 'detached recovery native cut differs')
        need(after['semantic_events'] == events['semantic'][:2] and after['governance_events'] == events['governance'][:2],
             'recovered native originals differ')
        production_after = production_read(store, 2)
        need(production_after['semantic_events'] == events['semantic'][:2]
             and production_after['governance_events'] == events['governance'][:2],
             'production native recovered cut differs')
        head = read(store_root / 'HEAD.json')
        retry = factory.recover_detached(store_root=store_root, store_identity=tuple(boot['store_identity']),
                                         control_binding=control)
        need(read(store_root / 'HEAD.json') == head and retry['cold_native']['native_cut'] == after,
             'detached exact retry changed committed effect')
        need(foreign.read_bytes() == b'foreign native sibling survives', 'foreign sibling changed after recovery')
        return {'stage': stage, 'family': family, 'child_exit': -9, 'old_head_sha256': boot['old_head_sha256'],
                'new_head_sha256': sha(head), 'control_sha256': control['sha256'],
                'semantic_events': 2, 'governance_events': 2, 'foreign_preserved': True,
                'foreign_residue_refusal': refusal, 'production_cold_read': True,
                'exact_retry_idempotent': True}


def main():
    selected_source = globals().get('_SELECTED_RUNNER_RAW')
    need(type(selected_source) is bytes, 'pinning launcher required')
    if len(sys.argv) == 5 and sys.argv[1] == '--child':
        child(sys.argv[2], sys.argv[3], sys.argv[4])
        return
    need(len(sys.argv) == 1, 'unexpected CLI arguments')
    result = {'result': 'PASS', 'scope': 'selected native lifecycle append and detached recovery technical fixture',
              'cases': ([one(stage, family) for family in ('semantic', 'governance')
                         for stage in ('after-lock', 'after-first-link', 'before-cleanup')]
                        + [one(stage, 'none') for stage in ('before-head-commit', 'after-head-commit')]),
              'selected_factory_sha256': PINS['selected_store.py'], 'generation_store_sha256': PINS['generation_store.py'],
              'original_native_store_sha256': PINS['native_store.py'], 'observer_executable_sha256': PINS['observer_executable'],
              'production_executable_sha256': PINS['production_executable'],
              'capabilities_sha256': PINS['capabilities.py'], 'fixture_sha256': PINS['fixtures.py'],
              'runner_sha256': sha(selected_source),
              'authority_effect': 'none', 'limits': ['No real source/issuer grant', 'No real rich translation',
                  'No API ontology.project writer claim', 'No host power-loss simulation']}
    output = HERE / ('RESULT-OPT-0002.json' if sys.flags.optimize else 'RESULT-0002.json')
    fd = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write((json.dumps(result, sort_keys=True, indent=2) + '\n').encode())
        stream.flush()
        os.fsync(stream.fileno())
    print(json.dumps({'result': result['result'], 'cases': len(result['cases'])}))


if __name__ == '__main__':
    main()
