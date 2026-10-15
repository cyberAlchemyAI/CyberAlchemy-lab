"""Actual isolated D74->D75 candidate reconstruction and adversarial checks."""
import copy
from dataclasses import asdict, replace
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

PACKAGE = Path(__file__).resolve().parents[1]; ROOT = PACKAGE.parents[3]
sys.path.insert(0, str(PACKAGE))
from lab_runtime.common import RuntimeFault, byte_digest, digest, encoded, load
from lab_runtime.profiles import select
from lab_runtime.sources import capture
from lab_runtime.replay import ReplayPins
from lab_runtime.store import VerifiedLegacyReadStore
from lab_runtime.transition import (LocalPolicy, BranchPins, prepare_transition, authorize_transition,
    apply_transition, replay_successor, classify, committed_files, _publish)

LEGACY = ROOT / 'implementation/lab-runtime/v1'
spec = importlib.util.spec_from_file_location('transition_fixture_v1', LEGACY / 'lab_runtime/__init__.py',
                                             submodule_search_locations=[str(LEGACY / 'lab_runtime')])
mod = importlib.util.module_from_spec(spec); sys.modules[spec.name] = mod; spec.loader.exec_module(mod)
from transition_fixture_v1.store import Store, keygen
from transition_fixture_v1.cli import example


class TransitionTests(unittest.TestCase):
    observed = None

    @classmethod
    def setUpClass(cls):
        cls.temp = TemporaryDirectory(prefix='lab-transition-isolated-'); cls.root = Path(cls.temp.name)
        cls.repository = cls.root / 'repository'; cls.repository.mkdir()
        row = next(r for r in load(PACKAGE / 'profiles/selections.json')['selections'] if r['name'] == 'd75')
        cls.args = {k:v for k,v in row.items() if k not in ['name', 'source_bytes', 'source_materials']}
        initial = capture(select(ROOT, **cls.args))
        names = set(initial['materials']) | {r['path'] for r in initial['controls'].values()} | {r['path'] for r in initial['executable_materials']}
        for paths in initial['epoch_inventory'].values(): names.update(paths)
        # The old D74 fixture uses its own exact fixed capture adapter.
        from transition_fixture_v1.sources import capture as old_capture
        old = old_capture(ROOT, load(LEGACY / 'profile.json')); names.update(old['materials'])
        for paths in old['epoch_inventory'].values(): names.update(paths)
        for name in names:
            path = cls.repository / name; path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((ROOT / name).read_bytes())
        cls.selection = select(cls.repository, **cls.args); cls.snapshot = capture(cls.selection)
        cls.private = cls.root / 'test-only.pem'; public = cls.root / 'test-only.pub'; keygen(cls.private, public)
        cls.public_key = public.read_text().strip()
        cls.fixture = cls.root / 'old'; store = Store(cls.fixture, cls.repository)
        store.initialize(load(LEGACY / 'profile.json'), 'transition-parent-d74', 'role:test-only', cls.public_key)
        proposal = example(store, 'carry-work'); second = example(store, 'exclude-work')['targets'][0]
        proposal['targets'].append(second); store.apply(proposal, store.authorize(proposal, cls.private))
        manifest = PACKAGE / 'design/legacy-runtime-bindings.json'
        cls.pins = ReplayPins('v1', manifest.relative_to(ROOT).as_posix(), byte_digest(manifest.read_bytes()),
            byte_digest((cls.fixture / 'config.json').read_bytes()), load(cls.fixture / 'baseline.json')['snapshot_digest'])
        cls.parent = VerifiedLegacyReadStore(cls.fixture, cls.repository, ROOT, cls.pins)
        cls.data = cls.parent.verify_full(); cls.bindings = committed_files(cls.parent, cls.data)
        cls.mapping_path = PACKAGE / 'design/contract-impact.json'; cls.mapping_bytes = cls.mapping_path.read_bytes()
        cls.mapping_sha = byte_digest(cls.mapping_bytes); cls.mapping = load(cls.mapping_path)
        cls.selections = [{'version_ref': t['version_ref'], 'new_carrier_ref': t['carrier_ref'],
                          'disposition': 'carry' if i == 0 else 'exclude', 'reason': 'isolated test explicit selection'}
                          for i,t in enumerate(proposal['targets'])]

    @classmethod
    def tearDownClass(cls): cls.temp.cleanup()

    def setUp(self):
        self.temp = TemporaryDirectory(prefix='lab-transition-case-'); self.root = Path(self.temp.name)
        self.destination = self.root / 'successor'
        self.policy = LocalPolicy('role:test-only', self.public_key, 'candidate-successor', str(self.destination),
                                  'scope:isolated-c05', '2099-01-01T00:00:00Z')

    def tearDown(self): self.temp.cleanup()

    def prepare(self, **kw):
        return prepare_transition(self.parent, self.selection, kw.get('selections', self.selections),
                                  self.mapping_path, self.mapping_sha, kw.get('policy', self.policy))

    def pure(self, snapshot=None, selections=None, data=None):
        return classify(data or self.data, snapshot or self.snapshot,
                        selections or self.selections, self.mapping, self.bindings)

    def apply(self, prepared, approval, **kw):
        return apply_transition(self.parent, self.selection, prepared, approval, self.mapping_path, self.policy, **kw)

    def test_eligible_and_explicit_exclusion(self):
        rows, records = self.pure()
        self.assertEqual([r['classification'] for r in rows], ['eligible', 'excluded'])
        self.assertEqual(set(records), {self.selections[0]['version_ref']})

    def test_already_promoted_blocks_carry(self):
        snap = copy.deepcopy(self.snapshot); version = self.selections[0]['version_ref']
        snap['subjects'][version] = copy.deepcopy(self.data['projection']['subjects'][version])
        self.assertEqual(self.pure(snapshot=snap)[0][0]['classification'], 'already-promoted')

    def test_same_revision_different_content_conflicts(self):
        snap = copy.deepcopy(self.snapshot); version = self.selections[0]['version_ref']
        snap['subjects'][version] = copy.deepcopy(self.data['projection']['subjects'][version])
        snap['subjects'][version]['record']['label'] = 'different'
        self.assertEqual(self.pure(snapshot=snap)[0][0]['classification'], 'conflicting')

    def test_identity_collision_blocks(self):
        snap = copy.deepcopy(self.snapshot); version = self.selections[0]['version_ref']
        e = copy.deepcopy(self.data['projection']['subjects'][version]); e['version_ref'] += '.other'
        snap['subjects'][e['version_ref']] = e
        self.assertEqual(self.pure(snapshot=snap)[0][0]['classification'], 'conflicting')

    def test_incompatible_new_schema_blocks(self):
        snap = copy.deepcopy(self.snapshot); ref = self.selections[0]['new_carrier_ref']
        path = snap['contracts'][ref]['schema_path']; snap['documents'][path] = {'not': {}}
        self.assertEqual(self.pure(snapshot=snap)[0][0]['classification'], 'conflicting')

    def test_historical_and_unknown_carriers_block(self):
        for ref in [self.selections[0]['new_carrier_ref'], 'unknown/carrier']:
            snap = copy.deepcopy(self.snapshot); selected = copy.deepcopy(self.selections)
            selected[0]['new_carrier_ref'] = ref
            if ref in snap['contracts']: snap['contracts'][ref]['lifecycle_state'] = 'admitted-historical'
            self.assertEqual(self.pure(snapshot=snap, selections=selected)[0][0]['classification'], 'conflicting')

    def test_withdrawn_result_requires_exclusion(self):
        data = copy.deepcopy(self.data); data['projection']['subjects'][self.selections[0]['version_ref']]['effective_state'] = 'local-withdrawn'
        self.assertEqual(self.pure(data=data)[0][0]['classification'], 'conflicting')

    def test_duplicate_selection_rejected(self):
        with self.assertRaisesRegex(RuntimeFault, 'duplicate'): self.pure(selections=[self.selections[0]] * 2)

    def test_raw_artifact_type_uses_registered_descriptor_selector(self):
        from lab_runtime.transition import _validate
        c = self.snapshot['contracts']['cal.artifact-type.work/v1']
        record = {'artifact_type_ref': 'cal.artifact-type.c05-fixture/v1', 'semantic_kind': 'work',
                  'semantic_definition_refs': c['semantic_definition_refs'], 'schema_path': c['schema_path'],
                  'schema_selector': None, 'schema_sha256': c['schema_sha256'],
                  'distinct_validation_purpose': 'Isolated exact raw descriptor conformance'}
        identity, kind = _validate(record, 'artifact-type', 'cal.artifact-type.artifact-type/v3',
                                   self.snapshot, self.mapping, self.snapshot['subjects'])
        self.assertEqual(identity, 'cal.artifact-type.c05-fixture'); self.assertEqual(kind, 'artifact-type')

    def test_exact_historical_relation_endpoint_retains_valid_reference(self):
        from lab_runtime.transition import _validate
        record = self.data['transactions'][1]['consequences']['typed_relations'][0]
        carrier = next(r for r,c in self.snapshot['contracts'].items() if c['semantic_kind'] == 'typed-relation' and c['lifecycle_state'] == 'admitted-current')
        endpoint = self.data['projection']['subjects'][record['payload']['target']['version_ref']]
        self.assertIn(endpoint['effective_state'], ['admitted-historical', 'local-admitted-historical'])
        identity, kind = _validate(record, 'typed-relation', carrier, self.snapshot, self.mapping, self.data['projection']['subjects'])
        self.assertEqual(identity, record['node_id']); self.assertEqual(kind, 'typed-relation')

    def test_baseline_subject_is_not_committed_result(self):
        selected = copy.deepcopy(self.selections); selected[0]['version_ref'] = next(iter(self.snapshot['subjects']))
        with self.assertRaisesRegex(RuntimeFault, 'committed local'): self.pure(selections=selected)

    def test_full_apply_restart_and_exact_preservation(self):
        prepared = self.prepare(); self.assertTrue(prepared['plan']['applicable'])
        approval = authorize_transition(prepared, self.policy, self.private)
        outcome = self.apply(prepared, approval); pins = BranchPins(**outcome['pins'])
        replayed = replay_successor(self.destination, pins, self.policy)
        self.assertEqual(set(replayed['records']), {self.selections[0]['version_ref']})
        e = replayed['subjects'][self.selections[0]['version_ref']]
        self.assertEqual(e['effective_state'], 'candidate-reconstructed'); self.assertIsNone(e['decision_ref'])
        self.assertFalse(e['provenance']['signatures_copied'])
        self.assertEqual(committed_files(self.parent, self.data), self.bindings)
        args = {'path': str(self.destination), 'pins': asdict(pins), 'policy': asdict(self.policy)}
        code = 'import json,sys;from lab_runtime.transition import *;from lab_runtime.common import digest;x=json.loads(sys.argv[1]);r=replay_successor(x["path"],BranchPins(**x["pins"]),LocalPolicy(**x["policy"]));print(digest(r["records"]))'
        process = subprocess.run([sys.executable, '-c', code, json.dumps(args)], cwd=PACKAGE, capture_output=True, text=True, timeout=45)
        self.assertEqual(process.returncode, 0, process.stderr); self.assertEqual(process.stdout.strip(), digest(replayed['records']))
        self.assertTrue(self.apply(prepared, approval)['idempotent'])
        TransitionTests.observed = {'plan': prepared['plan'], 'outcome': outcome,
            'parent_committed_files_unchanged': True, 'fresh_process_replay_digest': process.stdout.strip(),
            'raw_new_source_bytes_preserved': replayed['baseline']['byte_contents'] == prepared['baseline']['byte_contents']}
        # Self-seals do not bypass externally pinned original bytes.
        recordfile = next((self.destination / 'records').glob('*.json'))
        recordfile.write_bytes(recordfile.read_bytes() + b'\n')
        with self.assertRaisesRegex(RuntimeFault, 'bytes changed'): replay_successor(self.destination, pins, self.policy)

    def test_stale_approval_and_private_permissions(self):
        prepared = self.prepare(); approval = authorize_transition(prepared, self.policy, self.private)
        wrong = copy.deepcopy(approval); wrong['plan_digest'] = '0' * 64
        with self.assertRaisesRegex(RuntimeFault, 'different exact effects'): self.apply(prepared, wrong)
        os.chmod(self.private, 0o644)
        try:
            with self.assertRaisesRegex(RuntimeFault, '0600'): authorize_transition(prepared, self.policy, self.private)
        finally: os.chmod(self.private, 0o600)

    def test_unreviewed_plan_change_rejected(self):
        prepared = self.prepare(); approval = authorize_transition(prepared, self.policy, self.private)
        prepared['plan']['effects']['reconstructed_count'] = 999
        with self.assertRaisesRegex(RuntimeFault, 'stale transition'): self.apply(prepared, approval)

    def test_parent_writer_lock_blocks(self):
        import fcntl
        fd = os.open(self.fixture / '.writer.lock', os.O_RDONLY)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            with self.assertRaisesRegex(RuntimeFault, 'writer active'):
                self.apply({'plan': {}}, {})
        finally: os.close(fd)

    def test_no_replace_directory_publish(self):
        fd = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY)
        try:
            (self.root / 'stage').mkdir(); self.destination.mkdir()
            with self.assertRaisesRegex(RuntimeFault, 'no-replace'): _publish(fd, 'stage', 'successor')
            self.assertTrue((self.root / 'stage').is_dir()); self.assertEqual(list(self.destination.iterdir()), [])
        finally: os.close(fd)

    def test_unreviewed_existing_branch_rejected(self):
        prepared = self.prepare(); approval = authorize_transition(prepared, self.policy, self.private)
        self.destination.mkdir(); (self.destination / 'unrelated').write_text('retain')
        with self.assertRaisesRegex(RuntimeFault, 'incomplete genesis'): self.apply(prepared, approval)
        self.assertEqual((self.destination / 'unrelated').read_text(), 'retain')

    def test_expired_policy_rejected(self):
        from lab_runtime.transition import _approval
        policy = replace(self.policy, expires_at='2000-01-01T00:00:00Z')
        prepared = self.prepare(policy=policy)
        with self.assertRaisesRegex(RuntimeFault, 'interval'): authorize_transition(prepared, policy, self.private)

    def child(self, prepared, approval, hook):
        args = {'fixture': str(self.fixture), 'repository': str(self.repository), 'executable_repo': str(ROOT),
                'pins': asdict(self.pins), 'selection_args': self.args, 'policy': asdict(self.policy),
                'mapping_path': str(self.mapping_path), 'mapping_sha': self.mapping_sha,
                'selections': self.selections, 'plan_digest': digest(prepared['plan']), 'approval': approval, 'hook': hook}
        argfile = self.root / 'child-input.json'; argfile.write_bytes(encoded(args))
        return subprocess.run([sys.executable, str(Path(__file__).resolve()), '--child', str(argfile)],
                              cwd=PACKAGE, capture_output=True, text=True, timeout=90)

    def test_interrupted_stage_recovery_and_postpublish_retry(self):
        prepared = self.prepare(); approval = authorize_transition(prepared, self.policy, self.private)
        child = self.child(prepared, approval, 'after-stage'); self.assertEqual(child.returncode, 75, child.stderr)
        self.assertFalse(self.destination.exists()); self.assertEqual(len(list(self.root.glob('.successor.transition-*'))), 1)
        child = self.child(prepared, approval, 'after-publish'); self.assertEqual(child.returncode, 76, child.stderr)
        self.assertTrue(self.destination.is_dir()); self.assertEqual(list(self.root.glob('.successor.transition-*')), [])
        outcome = self.apply(prepared, approval); self.assertTrue(outcome['idempotent'])
        replay_successor(self.destination, BranchPins(**outcome['pins']), self.policy)
        self.assertEqual(committed_files(self.parent, self.data), self.bindings)

    def test_incomplete_stage_is_retained(self):
        prepared = self.prepare(); approval = authorize_transition(prepared, self.policy, self.private)
        stage = self.root / ('.successor.transition-' + digest(prepared['plan'])); stage.mkdir()
        (stage / 'unknown').write_text('retain')
        with self.assertRaisesRegex(RuntimeFault, 'incomplete genesis'): self.apply(prepared, approval)
        self.assertEqual((stage / 'unknown').read_text(), 'retain'); self.assertFalse(self.destination.exists())


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--child':
        x = load(sys.argv[2]); parent = VerifiedLegacyReadStore(x['fixture'], x['repository'], x['executable_repo'], ReplayPins(**x['pins']))
        selection = select(x['repository'], **x['selection_args']); policy = LocalPolicy(**x['policy'])
        prepared = prepare_transition(parent, selection, x['selections'], x['mapping_path'], x['mapping_sha'], policy)
        if digest(prepared['plan']) != x['plan_digest']: raise RuntimeFault('fresh process plan mismatch')
        outcome = apply_transition(parent, selection, prepared, x['approval'], x['mapping_path'], policy, crash_at=x['hook'])
        print(json.dumps(outcome))
    else:
        unittest.main()
