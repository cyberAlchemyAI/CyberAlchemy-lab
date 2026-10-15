"""Disposable explicit candidate scope; no caller-selected live store destination."""
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import shutil
import sys
from tempfile import TemporaryDirectory

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[3]
RUNTIME = ROOT / 'implementation/lab-runtime/candidates/repeatable-operation'
BOOTSTRAP = ROOT / 'implementation/lab-bootstrap/candidates/v1'
sys.path.insert(0, str(RUNTIME)); sys.path.insert(0, str(BOOTSTRAP))
import bootstrap
from lab_runtime.common import RuntimeFault, byte_digest, digest, encoded, load, require
from lab_runtime.replay import ReplayPins, legacy_runtime, full_replay
from lab_runtime.profiles import select

BINDINGS = 'implementation/lab-runtime/candidates/repeatable-operation/design/legacy-runtime-bindings.json'
MANIFEST = ROOT / BINDINGS
RUN = ROOT / 'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction'


def verify_inputs():
    for row in load(RUN / 'context-C11.json')['source_bindings']:
        require(byte_digest((ROOT / row['path']).read_bytes()) == row['sha256'], 'C11 selected input changed')
    for path in ['implementation/lab-review/candidates/v1/receipts/C10/0001.json',
                 'implementation/lab-integration/candidates/v1/receipts/C09/0001/receipt.json']:
        receipt = load(ROOT / path)
        require(receipt['result'] == 'PASS' and receipt['task_complete'] is True, 'candidate prerequisite incomplete')
        for row in receipt['files']:
            require(byte_digest((ROOT / row['path']).read_bytes()) == row['sha256'], 'candidate prerequisite source drift')


@dataclass(frozen=True)
class CandidateScope:
    store_id: str
    operator_ref: str
    scope_ref: str
    allowed_categories: tuple = ('work',)
    allowed_effects: tuple = ('admit',)
    candidate_only: bool = True

    def check(self):
        require(self.candidate_only is True, 'only candidate rehearsal scope supported')
        require(bool(self.store_id) and all(c.isalnum() or c == '-' for c in self.store_id), 'explicit store identity required')
        require(self.operator_ref.startswith('role:candidate-') and len(self.operator_ref) > len('role:candidate-'), 'explicit candidate operator required')
        require(self.scope_ref == 'scope:lab-runtime-local:' + self.store_id, 'explicit exact local scope required')
        require(self.allowed_categories == ('work',) and self.allowed_effects == ('admit',), 'only declared bounded candidate Work effects supported')


class CandidateBranch:
    """Owns its disposable root and key; closes them together."""
    def __init__(self, scope):
        require(isinstance(scope, CandidateScope), 'explicit CandidateScope required')
        scope.check(); verify_inputs(); self.scope = scope; self.closed = False
        self.owned = TemporaryDirectory(prefix='lab-C11-owned-candidate-')
        self.root = Path(self.owned.name)
        require(not self.root.is_relative_to(ROOT), 'fixture root must be outside repository')
        self.store_path = self.root / 'project'; self.key_path = self.root / 'candidate-only.pem'
        self.catalog_path = self.root / 'catalog'
        pins = ReplayPins('v2', BINDINGS, byte_digest(MANIFEST.read_bytes()), '', '')
        self.module_name, self.engine, self.stage = legacy_runtime(ROOT, pins)
        try:
            public_path = self.root / 'candidate-only.pub'
            self.engine.keygen(self.key_path, public_path); self.public_key = public_path.read_text().strip()
            self.store = self.engine.Store(self.store_path, ROOT)
            profile = load(Path(self.stage.name) / 'profile.json')
            self.store.initialize(profile, scope.store_id, scope.operator_ref, self.public_key,
                                  list(scope.allowed_categories), list(scope.allowed_effects))
            baseline = load(self.store_path / 'baseline.json'); head = load(self.store_path / 'HEAD.json')
            self.pins = ReplayPins('v2', BINDINGS, pins.manifest_sha256,
                byte_digest((self.store_path / 'config.json').read_bytes()), baseline['snapshot_digest'], head['transaction_digest'])
            self.initial = full_replay(self.store_path, ROOT, ROOT, self.pins, require_current=True)
            require(self.initial['config']['scope_ref'] == scope.scope_ref, 'provisioned scope differs from explicit selection')
            require(self.key_path.stat().st_mode & 0o777 == 0o600, 'private key custody mode changed')
            require(not self.key_path.is_relative_to(self.store_path), 'private key inside store')
        except BaseException:
            self.close(); raise

    def live(self):
        require(not self.closed, 'candidate branch closed')

    def bootstrap_catalog(self):
        self.live()
        package = BOOTSTRAP / 'packages/0004'
        manifest = load(package / 'PACKAGE-MANIFEST.json')
        require(manifest['actual_owner_outcome'] is None and manifest['authority_effect'] == 'none', 'catalog package claims actual authority')
        for row in manifest['file_bindings']:
            require(byte_digest((ROOT / row['path']).read_bytes()) == row['sha256'], 'catalog package bytes changed')
        self.catalog_selection = select(ROOT, **load(package / 'selection.json'))
        self.catalog_policy = bootstrap.RehearsalPolicy('fixture:C11:catalog-operator', self.public_key,
            self.scope.store_id + '-catalog', str(self.catalog_path), 'scope:C11:isolated-catalog',
            (datetime.now(timezone.utc) + timedelta(minutes=20)).isoformat())
        plan = bootstrap.prepare(self.catalog_selection, self.catalog_policy)
        response = bootstrap.sign(plan, self.catalog_policy, self.key_path)
        outcome = bootstrap.apply(self.catalog_selection, plan, response, self.catalog_policy)
        self.catalog_pins = bootstrap.CatalogPins(**outcome['pins'])
        result = bootstrap.replay(self.catalog_path, self.catalog_pins, self.catalog_policy)
        require(response['human_outcome'] is None and response['fixture_only'], 'fixture response claims human outcome')
        require(all(row['effective_state'] == 'candidate-unadmitted' for row in result['catalog']['candidate_subjects'].values()), 'bootstrap admitted a candidate')
        return result

    def export_project(self):
        self.live(); full_replay(self.store_path, ROOT, ROOT, self.pins, require_current=True)
        destination = self.root / 'exported-project'
        require(not destination.exists(), 'export destination already exists')
        destination.mkdir(mode=0o700); (destination / 'transactions').mkdir()
        # Genesis rehearsal export deliberately has no operational notes or private key.
        paths = ['config.json', 'baseline.json', 'HEAD.json', 'transactions/0000000000.json']
        before = {p: byte_digest((self.store_path / p).read_bytes()) for p in paths}
        for p in paths: shutil.copyfile(self.store_path / p, destination / p)
        require(before == {p: byte_digest((destination / p).read_bytes()) for p in paths}, 'export changed original committed bytes')
        after = full_replay(destination, ROOT, ROOT, self.pins, require_current=True)
        require(after['head'] == self.initial['head'], 'export HEAD differs')
        return destination, before

    def close(self):
        if self.closed: return
        self.closed = True
        if hasattr(self, 'stage'): self.stage.cleanup()
        if hasattr(self, 'module_name'):
            for key in list(sys.modules):
                if key == self.module_name or key.startswith(self.module_name + '.'):
                    sys.modules.pop(key, None)
        if hasattr(self, 'owned'): self.owned.cleanup()

    def __enter__(self): return self
    def __exit__(self, *args): self.close()
