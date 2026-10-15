"""Cold original signed history with separately bound unadmitted evidence.

No projection is augmented. Expired lessons are historical inspection material;
this provider neither constructs an Agent nor grants a lesson application.
"""
import base64
import copy
import hashlib
import importlib
import importlib.util
import json
import platform
import sys
import tempfile
import uuid
from contextlib import contextmanager
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
RECONCILIATION = ROOT / 'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/Genuine-work-learning-reconciliation-0206.json'
RECONCILIATION_SHA = '8716ef1b3b124ffd39d1d06b6c154102f74c174dcbe9787e818f94d157368af1'
LEGACY_MANIFEST = 'implementation/lab-runtime/candidates/repeatable-operation/design/legacy-runtime-bindings.json'
LEGACY_MANIFEST_SHA = '064217cb94e0a97654052338bf8338bb437f3a6311e71061caa2343760d95abe'
READS = ('lab.status', 'catalog.get', 'artifact.inspect', 'artifact.query')


def require(value, reason):
    if not value:
        raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def parse(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'duplicate original JSON key')
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError('nonfinite JSON')))


def original(binding):
    relative = binding['path']
    path = ROOT / relative
    require(type(relative) is str and not Path(relative).is_absolute() and '..' not in Path(relative).parts
            and path.is_file() and not path.is_symlink() and not any(p.is_symlink() for p in path.parents), 'unsafe original material')
    raw = path.read_bytes()
    require(sha(raw) == binding['sha256'], 'original history input changed: ' + relative)
    return raw


def verify(source_pin):
    raw = (HERE / 'source-manifest.json').read_bytes()
    require(sha(raw) == source_pin, 'independent history provider source pin differs')
    manifest = parse(raw)
    require(manifest['authority_effect'] == 'none' and manifest['actual_owner_outcome'] is None
            and manifest['python_version'] == platform.python_version(), 'history provider environment/authority differs')
    proof = parse(original({'path': str(RECONCILIATION.relative_to(ROOT)), 'sha256': RECONCILIATION_SHA}))
    expected = [{'path': r['path'], 'sha256': r['sha256']} for r in proof['material_bindings']]
    require(manifest['retained_proof_files'] == expected, 'complete original 4197-row proof selection differs')
    require(len(expected) == 4197, 'original proof closure cardinality differs')
    names = {'__init__.py', 'provider.py', 'selection.json', 'authentication-case.json'}
    require({Path(r['path']).name for r in manifest['provider_files']} == names, 'mandatory provider inputs missing')
    require({p.name for p in HERE.iterdir() if p.is_file()} == names | {'source-manifest.json'}, 'unselected provider file')
    for row in manifest['provider_files'] + manifest['retained_proof_files']:
        original(row)
    require((HERE / 'source-manifest.json').read_bytes() == raw, 'history source manifest changed during guard')
    return manifest


def selection(source_pin, selection_pin, name):
    verify(source_pin)
    raw = (HERE / 'selection.json').read_bytes()
    require(sha(raw) == selection_pin, 'independent history selection differs')
    selected = parse(raw)
    require(selected['authority_effect'] == 'none' and selected['actual_owner_outcome'] is None
            and selected['allowed_operations'] == list(READS), 'history selection cannot grant an effect')
    matches = [r for r in selected['sources'] if r['name'] == name]
    require(len(matches) == 1, 'unselected original history source')
    return copy.deepcopy(matches[0])


def imported(name, path, package=False):
    spec = importlib.util.spec_from_file_location(name, path / '__init__.py' if package else path,
                                                 submodule_search_locations=[str(path)] if package else None)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class LegacyHandle:
    def __init__(self, source_pin, row):
        self.source_pin, self.row, self.closed = source_pin, row, False
        package = ROOT / 'implementation/lab-runtime/candidates/repeatable-operation/lab_runtime'
        self.bridge_name = '_cal_genuine_original_replay_' + uuid.uuid4().hex
        imported(self.bridge_name, package, True)
        self.replay = importlib.import_module(self.bridge_name + '.replay')
        self.pins = self.replay.ReplayPins(**row['replay_pins'])
        self.name, self.store_module, self.stage = self.replay.legacy_runtime(ROOT, self.pins)
        self.common = importlib.import_module(self.name + '.common')
        self.operations = importlib.import_module(self.name + '.operations')
        self.sources = importlib.import_module(self.name + '.sources')
        selected = parse(original({'path': LEGACY_MANIFEST, 'sha256': LEGACY_MANIFEST_SHA}))
        self.runtime_row = next(r for r in selected['runtimes'] if r['version'] == 'v2')
        self.manifest = {'profile_binding': row['profile_binding'], 'original_runtime_manifest_binding':
                         {'path': LEGACY_MANIFEST, 'sha256': LEGACY_MANIFEST_SHA}}
        self.guard()

    def guard(self):
        require(not self.closed, 'closed original history handle')
        verify(self.source_pin)
        manifest = parse(original({'path': LEGACY_MANIFEST, 'sha256': LEGACY_MANIFEST_SHA}))
        require(self.runtime_row in manifest['runtimes'], 'selected original runtime differs')
        for row in self.runtime_row['files']:
            raw = original(row)
            relative = Path(row['path']).relative_to(self.runtime_row['package_path'])
            require((Path(self.stage.name) / relative).read_bytes() == raw, 'captured original engine code changed')
        require(self.store_module.Store.__module__ == self.name + '.store'
                and Path(self.store_module.__file__).resolve() == Path(self.stage.name) / 'lab_runtime/store.py', 'foreign original Store class')
        return True

    def close(self):
        self.closed = True
        self.stage.cleanup()
        for name in list(sys.modules):
            if name == self.name or name.startswith(self.name + '.') or name == self.bridge_name or name.startswith(self.bridge_name + '.'):
                sys.modules.pop(name, None)


def modules(source_pin):
    verify(source_pin)
    namespace = '_cal_genuine_original_inspection_' + uuid.uuid4().hex
    legacy = imported(namespace, ROOT / 'product/lab/release-candidates/v1/interface/inspection/lab_operator.py')
    require(Path(legacy.__file__).resolve() == ROOT / 'product/lab/release-candidates/v1/interface/inspection/lab_operator.py', 'foreign original Inspection code')
    return legacy


def inspect_view(data, selected, originals, handle, source_pin, selection_pin, legacy=None):
    require(selection(source_pin, selection_pin, selected['name']) == selected, 'history inspection source differs')
    require(data['head']['transaction_digest'] == data['transactions'][-1]['digest']
            and handle.common.digest(data['projection']) == data['transactions'][-1]['projection_digest'], 'unverified original projection')
    legacy = modules(source_pin) if legacy is None else legacy
    view = legacy.Inspection(data, selected, originals, handle)
    # Explicit additive evidence custodian; subjects/projection remain original.
    view.genuine_history = HistoryEvidence(source_pin, selection_pin, selected, data, handle)
    view.genuine_original_projection_digest = handle.common.digest(data['projection'])
    return view


class HistoryEvidence:
    def __init__(self, source_pin, selection_pin, row, data, handle):
        self.source_pin, self.selection_pin, self.row, self.data, self.handle = source_pin, selection_pin, row, data, handle
        self.projection_stamp = handle.common.digest(data['projection'])

    def guard(self):
        require(selection(self.source_pin, self.selection_pin, self.row['name']) == self.row, 'history source selection changed')
        self.handle.guard()
        require(self.handle.common.digest(self.data['projection']) == self.projection_stamp, 'original history projection was grafted or changed')

    def evidence(self, subject):
        self.guard()
        require(subject['version_ref'] in self.row['inspection_subjects'], 'unselected history evidence subject')
        result = []
        for row in self.row['evidence_bindings']:
            raw = original(row)
            require(len(raw) <= 20971520, 'historical evidence byte budget')
            result.append({'ref': row['path'], 'sha256': sha(raw)})
        self.guard()
        return result


@contextmanager
def open_history(source_pin, selection_pin, name):
    row = selection(source_pin, selection_pin, name)
    archive = parse(original(row['archive_binding']))
    require(archive['authority_effect'] == 'none' and archive['actual_owner_outcome'] is None
            and archive['private_key_included'] is False and archive['Session_memory_included'] is False, 'archive contains forbidden authority/private state')
    with tempfile.TemporaryDirectory(prefix='cal-genuine-original-history-0208-') as temporary:
        store = Path(temporary) / 'store'
        store.mkdir(mode=0o700)
        (store / 'transactions').mkdir(mode=0o700)
        originals = {}
        for relative, binding in archive['files'].items():
            require(relative in {'config.json', 'baseline.json', 'HEAD.json', 'transactions/0000000000.json', 'transactions/0000000001.json'}, 'unexpected original archive closure')
            raw = base64.b64decode(binding['base64_original_bytes'], validate=True)
            require(sha(raw) == binding['sha256'], 'embedded original history bytes differ')
            with (store / relative).open('xb') as stream:
                stream.write(raw)
            (store / relative).chmod(0o600)
            originals[relative] = raw
        require(len(originals) == 5 and sha(originals['config.json']) == row['config_sha256'], 'original config/closure differs')
        if row['engine_family'] == 'legacy-v2':
            handle = LegacyHandle(source_pin, row)
            try:
                require(archive['project_pins'] == row['replay_pins'], 'original legacy replay pins differ')
                data = handle.store_module.Store(store, ROOT).replay(require_current=True)
                independent = handle.replay.full_replay(store, ROOT, ROOT, handle.pins, require_current=True)
                require(handle.common.digest(data['projection']) == handle.common.digest(independent['projection'])
                        and data['head'] == independent['head'], 'independent original cold replay differs')
                yield inspect_view(data, row, originals, handle, source_pin, selection_pin)
                handle.guard()
            finally:
                handle.close()
        else:
            legacy = modules(source_pin)
            pins = legacy.EnginePins(**row['engine_pins'])
            with legacy.engine(pins) as handle:
                require(archive['engine_pins'] == row['engine_pins'], 'original coupling engine differs')
                data = handle.replay_owned(store, row['config_sha256'], row['baseline_snapshot_digest'], row['expected_head'])
                expected = parse(original(row['expected_replay_binding']))
                require(handle.common.digest(data['projection']) == expected['projection_sha256']
                        and [handle.common.digest(t) for t in data['transactions']] == expected['transaction_sha256s'], 'original coupling cold projection differs')
                yield inspect_view(data, row, originals, handle, source_pin, selection_pin, legacy)
                handle.guard()
        require(all((store / name).read_bytes() == raw for name, raw in originals.items())
                and {p.relative_to(store).as_posix() for p in store.rglob('*') if p.is_file()} == set(originals), 'history read changed or created committed store bytes')
        verify(source_pin)


def validate_policy(policy, source_pin, selection_pin):
    require(policy['schema_version'] == 'lab-local-genuine-history-read-policy/v1-candidate'
            and policy['allowed_operations'] == list(READS) and policy['session_control'] is None and policy['projection_control'] is None, 'history read policy cannot authorize effects or Sessions')
    row = selection(source_pin, selection_pin, policy['source_name'])
    control = policy['history_control']
    require(control == {'provider_source_binding': {'ref': str((HERE / 'source-manifest.json').relative_to(ROOT)), 'sha256': source_pin},
                        'provider_selection_binding': {'ref': str((HERE / 'selection.json').relative_to(ROOT)), 'sha256': selection_pin},
                        'source_archive_binding': {'ref': row['archive_binding']['path'], 'sha256': row['archive_binding']['sha256']},
                        'source_cut': {'baseline_snapshot_digest': row['baseline_snapshot_digest'], 'signed_head': row['expected_head'], 'sequence': 1},
                        'inspection_only': True, 'expired_lessons_grant_application': False}, 'independent history read scope differs')
    require(policy['scope_refs'] == [row['scope_ref']], 'historical store custody namespace differs')
    authority = ROOT / 'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json'
    require(policy['development_authorization_binding'] == {'ref': str(authority.relative_to(ROOT)), 'sha256': sha(authority.read_bytes())}, 'original development read authorization differs')
    return row
