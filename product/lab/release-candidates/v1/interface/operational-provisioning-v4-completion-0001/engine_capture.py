"""Independently pinned candidate engine loader and original-byte read bridge."""
from contextlib import contextmanager
from dataclasses import dataclass
from . import capture_io
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import uuid

ROOT = Path(__file__).resolve().parents[6]
HERE = ROOT / 'product/lab/release-candidates/v1/interface/custody-correction-v4'
ENGINE = HERE / 'runtime'
MANIFEST = HERE / 'engine-manifest.json'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def require(value, message):
    if not value:
        raise ValueError(message)


def parse(raw):
    def pairs(rows):
        value = {}
        for key, item in rows:
            require(key not in value, 'duplicate JSON key')
            value[key] = item
        return value
    return json.loads(raw, object_pairs_hook=pairs,
        parse_constant=lambda value: (_ for _ in ()).throw(ValueError('nonfinite JSON')))


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False) + '\n').encode()


def bind(path):
    return {'path': Path(path).relative_to(ROOT).as_posix(), 'sha256': sha(Path(path).read_bytes())}


def original(binding):
    require(type(binding) is dict and set(binding) == {'path', 'sha256'}, 'closed original binding required')
    relative = binding['path']; path = ROOT / relative
    require(type(relative) is str and not Path(relative).is_absolute() and '\\' not in relative
        and Path(relative).as_posix() == relative and '..' not in Path(relative).parts,
        'unsafe repository binding')
    return capture_io.capture(path, binding['sha256'])


@dataclass(frozen=True)
class EnginePins:
    manifest_sha256: str
    engine_id: str
    mapping_sha256: str
    profile_sha256: str
    correction_profile_sha256: str


def verify_engine(pins):
    require(type(pins) is EnginePins, 'independent engine pins required')
    manifest = parse(capture_io.capture(MANIFEST, pins.manifest_sha256))
    require(set(manifest) == set('schema_version authority_effect actual_owner_outcome engine_id parent_binding files changed_files profile_binding mapping_binding correction_profile_binding'.split())
        and manifest['schema_version'] == 'lab-R03-correction-engine-manifest/v1-candidate'
        and manifest['authority_effect'] == 'none' and manifest['actual_owner_outcome'] is None,
        'closed candidate engine manifest required')
    require(manifest['engine_id'] == pins.engine_id == 'lab-operator-reference-correction/v1-candidate'
        and manifest['mapping_binding']['sha256'] == pins.mapping_sha256
        and manifest['profile_binding']['sha256'] == pins.profile_sha256
        and manifest['correction_profile_binding']['sha256']==pins.correction_profile_sha256, 'candidate engine identity/profile/mapping pin differs')
    expected = {b['path'] for b in manifest['files']}
    require(len(expected) == len(manifest['files']), 'duplicate executable binding')
    actual = {p.relative_to(ROOT).as_posix() for p in ENGINE.rglob('*')
        if p.is_file() and '__pycache__' not in p.parts}
    require(actual == expected, 'candidate executable closure changed')
    for b in manifest['files']:
        require((ROOT / b['path']).is_relative_to(ENGINE), 'executable binding outside selected engine')
        original(b)
    parent = parse(original(manifest['parent_binding']))
    require(parent['authority_effect'] == 'none' and parent['actual_owner_outcome'] is None,
        'parent source binding cannot grant authority')
    for b in parent['files']:
        original(b)
    original(manifest['profile_binding']); original(manifest['mapping_binding']);original(manifest['correction_profile_binding'])
    return manifest


class LoadedEngine:
    def __init__(self, pins, name, stage, manifest):
        self.pins = pins; self.name = name; self.stage = stage; self.manifest = manifest
        self.closed = False
        self.store_module = importlib.import_module(name + '.store')
        self.operations = importlib.import_module(name + '.operations')
        self.common = importlib.import_module(name + '.common')
        self.mapping = importlib.import_module(name + '.endpoint_mapping')
        self.sources = importlib.import_module(name + '.sources')
        self.corrections=importlib.import_module(name+'.corrections')
        self.custody=importlib.import_module(name+'.custody')

    def guard(self):
        require(not self.closed and verify_engine(self.pins) == self.manifest, 'closed or altered candidate engine handle')
        for b in self.manifest['files']:
            relative = (ROOT / b['path']).relative_to(ENGINE); path = Path(self.stage.name) / relative
            capture_io.capture(path,b['sha256'])

    def create_owned(self, root, store_id, *, selected_project_scope=False,correction_domains=None):
        self.guard(); root = Path(root)
        require(root.is_dir() and root.is_relative_to(Path(tempfile.gettempdir()))
            and not root.is_relative_to(ROOT) and not root.is_symlink(), 'explicit owned temporary root required')
        require(not any((root / p).exists() for p in ('owner.pem', 'owner.pub', 'store')), 'owned branch target already exists')
        self.store_module.keygen(root / 'owner.pem', root / 'owner.pub')
        store = self.store_module.Store(root / 'store', ROOT)
        profile = parse(original(self.manifest['profile_binding']))
        store.initialize(profile, store_id, 'role:R03-controlled-reference-correction-operator', (root / 'owner.pub').read_text().strip(),
            selected_scope_ref=profile['project_ref'] if selected_project_scope else None,
            correction_profile_binding=self.manifest['correction_profile_binding'] if correction_domains is not None else None,
            authorized_domain_scope_refs=correction_domains)
        self.guard()
        return store, root / 'owner.pem'

    def replay_owned(self, store_path, config_sha256, baseline_digest, expected_head):
        self.guard(); path = Path(store_path)
        require(not path.is_symlink() and not any(p.is_symlink() for p in path.parents), 'unsafe signed branch root')
        require(sha((path / 'config.json').read_bytes()) == config_sha256, 'independent configuration pin differs')
        baseline = parse((path / 'baseline.json').read_bytes())
        require(baseline['snapshot_digest'] == baseline_digest, 'independent baseline pin differs')
        head = parse((path / 'HEAD.json').read_bytes())
        require(head['transaction_digest'] == expected_head, 'independent signed branch HEAD pin differs')
        config = parse((path / 'config.json').read_bytes())
        require(config['endpoint_engine_id'] == self.mapping.ENGINE_ID
            and config['endpoint_mapping_binding'] == self.manifest['mapping_binding']
            and config['endpoint_mapping_authority'] == 'isolated-candidate-local-interpretation',
            'selected signed coupling configuration differs')
        if config.get('correction_profile_binding') is not None:
            require(config['correction_profile_binding']==self.manifest['correction_profile_binding']
                and config['correction_engine_id']==self.pins.engine_id,'independent correction configuration pin differs')
        names = {'config.json', 'baseline.json', 'HEAD.json'} | {f'transactions/{i:010d}.json' for i in range(head['sequence'] + 1)}
        actual = {p.relative_to(path).as_posix() for p in path.rglob('*') if p.is_file()}
        require(actual <= names | {'.writer.lock'} and names <= actual, 'signed branch original file closure differs')
        originals = {name: sha((path / name).read_bytes()) for name in names}
        for p in path.rglob('*'):
            require(not p.is_symlink(), 'signed branch entry symlink')
            if p.is_file():
                if p.name != '.writer.lock':
                    parse(p.read_bytes())
        data = self.store_module.Store(path, ROOT).replay()
        require(data['freshness']['status'] == 'current', 'signed branch sources are stale')
        require(all(sha((path / name).read_bytes()) == digest for name, digest in originals.items()),
            'signed branch originals changed during replay')
        self.guard()
        return data


@contextmanager
def engine(pins):
    manifest = verify_engine(pins)
    with tempfile.TemporaryDirectory(prefix='cal-R03-pinned-engine-') as stage_path:
        captured_root = Path(stage_path) / 'captured/implementation/lab-runtime/v2'
        for b in manifest['files']:
            path = captured_root / (ROOT / b['path']).relative_to(ENGINE)
            path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(original(b))
        name = '_cal_T34_captured_original_engine_' + uuid.uuid4().hex
        code_files={}
        for b in manifest['files']:
            relative=(ROOT/b['path']).relative_to(ENGINE).as_posix()
            if relative.startswith('lab_runtime/') and relative.endswith('.py'):
                code_files[relative[len('lab_runtime/'):]]=original(b)
        finder=capture_io.CapturedFinder(name,captured_root/'lab_runtime',code_files)
        sys.meta_path.insert(0,finder)
        try: module=importlib.import_module(name)
        except BaseException:
            sys.meta_path.remove(finder); raise
        stage = type('Stage', (), {'name': str(captured_root)})()
        handle = LoadedEngine(pins, name, stage, manifest)
        try:
            handle.guard(); yield handle; handle.guard()
        finally:
            handle.closed = True
            sys.meta_path.remove(finder)
            for key in list(sys.modules):
                if key == name or key.startswith(name + '.'):
                    sys.modules.pop(key, None)


def selected_pins():
    """Authoring convenience only; acceptance callers receive external pins."""
    m = parse(MANIFEST.read_bytes())
    return EnginePins(sha(MANIFEST.read_bytes()), m['engine_id'],
        m['mapping_binding']['sha256'], m['profile_binding']['sha256'],m['correction_profile_binding']['sha256'])


def selected_engine(plan):
    """Versioned adapter origin; no mutation of an original loader callback."""
    import sys
    loader=sys.modules[__name__]
    return loader,engine(EnginePins(**plan['engine_pins']))
