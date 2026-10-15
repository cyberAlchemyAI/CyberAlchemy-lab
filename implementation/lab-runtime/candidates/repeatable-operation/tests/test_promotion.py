"""Actual signed local results and independently authorized isolated publication."""
import copy
from dataclasses import asdict, replace
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

PACKAGE = Path(__file__).resolve().parents[1]; ROOT = PACKAGE.parents[3]
sys.path.insert(0, str(PACKAGE)); sys.path.insert(0, str(PACKAGE / 'tests'))
import test_transition
from transition_fixture_v1.store import Store, keygen
from transition_fixture_v1.cli import example
from lab_runtime.common import RuntimeFault, byte_digest, digest, encoded, load
from lab_runtime.profiles import select
from lab_runtime.sources import capture
from lab_runtime.replay import ReplayPins
from lab_runtime.store import VerifiedLegacyReadStore
from lab_runtime.promotion import RepositoryAuthority, prepare_promotion, public_material
from lab_runtime.publisher import (PublicationPins, owner_response, verify_response, render_bundle,
                                   verify_bundle, publish, repair_publication, _lock)


class PromotionTests(unittest.TestCase):
    observed = None

    @classmethod
    def setUpClass(cls):
        cls.temp = TemporaryDirectory(prefix='lab-promotion-fixture-'); cls.root = Path(cls.temp.name)
        cls.repository = cls.root / 'repository'; cls.repository.mkdir()
        row = next(r for r in load(PACKAGE / 'profiles/selections.json')['selections'] if r['name'] == 'd75')
        cls.args = {k:v for k,v in row.items() if k not in ['name', 'source_bytes', 'source_materials']}
        snap = capture(select(ROOT, **cls.args))
        from transition_fixture_v1.sources import capture as legacy_capture
        old = legacy_capture(ROOT, load(test_transition.LEGACY / 'profile.json'))
        paths = set(snap['materials']) | set(old['materials']) | {r['path'] for r in snap['controls'].values()} | {r['path'] for r in snap['executable_materials']}
        for names in snap['epoch_inventory'].values(): paths.update(names)
        for name in paths:
            p = cls.repository / name; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes((ROOT / name).read_bytes())
        cls.private = cls.root / 'local.pem'; public = cls.root / 'local.pub'; keygen(cls.private, public)
        cls.owner_private = cls.root / 'repository-owner.pem'; owner_public = cls.root / 'repository-owner.pub'; keygen(cls.owner_private, owner_public)
        cls.public_key = owner_public.read_text().strip()
        cls.fixture = cls.root / 'local-store'; store = Store(cls.fixture, cls.repository)
        store.initialize(load(test_transition.LEGACY / 'profile.json'), 'promotion-source-d74', 'role:local-test-operator', public.read_text().strip())
        proposal = example(store, 'selected-work'); proposal['targets'].append(example(store, 'unselected-work')['targets'][0])
        data = store.replay(); work = next(e for e in data['projection']['subjects'].values() if e['kind'] == 'work' and e['effective_state'] == 'admitted-current')
        r = copy.deepcopy(work['record']); r['scope_ref'] = proposal['scope_ref']; r['name'] = 'Isolated local revision'; r['payload']['work_statement'] = 'Fixture-only local revision; no actual Work satisfaction.'
        proposal['targets'].append({'category': 'artifact-instance', 'operation': 'revise', 'version_ref': r['node_id'] + '@publisher-fixture.1',
            'carrier_ref': work['carrier_ref'], 'record': r, 'predecessor_ref': work['version_ref'], 'decision_ref': 'decision:local:fixture-revision', 'contract': None})
        carrier = next(ref for ref,c in data['projection']['contracts'].items() if c['semantic_kind'] == 'definition' and c['lifecycle_state'] == 'admitted-current')
        # D74 preserves v1 definitions while its current write carrier is v2;
        # construct a labeled v2 fixture rather than inventing a revision alias.
        d = load(ROOT / 'authority/artifact-types/definition/v2/fixtures/valid/definition.json')
        d['definition_id'] = 'cal.definition.publisher-fixture'; d['term'] = 'Publisher fixture definition'
        proposal['targets'].append({'category': 'definition', 'operation': 'admit', 'version_ref': d['definition_id'] + '@' + d['version'],
            'carrier_ref': carrier, 'record': d, 'predecessor_ref': None, 'decision_ref': 'decision:local:fixture-definition', 'contract': None})
        schema = {'$schema': 'https://json-schema.org/draft/2020-12/schema', 'type': 'object', 'additionalProperties': False,
            'required': ['node_id', 'schema_version'], 'properties': {'node_id': {'type': 'string', 'minLength': 1}, 'schema_version': {'const': 'lab-fixture-result/v1'}}}
        schema_path = 'runtime/schemas/publisher-fixture-result.json'; type_ref = 'cal.artifact-type.publisher-fixture-result/v1'
        contract = {'semantic_kind': 'publisher-fixture-result', 'schema_path': schema_path, 'schema_sha256': byte_digest(encoded(schema)),
            'schema_selector': None, 'instance_discriminator': {'path': '/schema_version', 'value': 'lab-fixture-result/v1'}, 'identity_field': 'node_id',
            'allowed_relation_kinds': [], 'relation_roles': []}
        descriptor = {k:contract[k] for k in ['semantic_kind', 'schema_path', 'schema_sha256', 'schema_selector']}
        descriptor.update(artifact_type_ref=type_ref, semantic_definition_refs=[d['definition_id'] + '@' + d['version']], distinct_validation_purpose='Isolated minimal fixture result validation')
        meta = next(ref for ref,c in data['projection']['contracts'].items() if c['semantic_kind'] == 'artifact-type' and c['lifecycle_state'] == 'admitted-current')
        proposal['schemas'][schema_path] = schema
        proposal['targets'].append({'category': 'artifact-type', 'operation': 'admit', 'version_ref': type_ref, 'carrier_ref': meta,
            'record': descriptor, 'predecessor_ref': None, 'decision_ref': 'decision:local:fixture-type', 'contract': contract})
        proposal['targets'].append({'category': 'artifact-instance', 'operation': 'admit', 'version_ref': 'fixture-result:publisher@1', 'carrier_ref': type_ref,
            'record': {'node_id': 'fixture-result:publisher', 'schema_version': 'lab-fixture-result/v1'}, 'predecessor_ref': None, 'decision_ref': 'decision:local:fixture-result', 'contract': None})
        approval = store.authorize(proposal, cls.private); store.apply(proposal, approval)
        cls.local_approval = approval
        cls.targets = proposal['targets']; manifest = PACKAGE / 'design/legacy-runtime-bindings.json'
        cls.pins = ReplayPins('v1', manifest.relative_to(ROOT).as_posix(), byte_digest(manifest.read_bytes()),
            byte_digest((cls.fixture / 'config.json').read_bytes()), load(cls.fixture / 'baseline.json')['snapshot_digest'])
        cls.mapping_path = PACKAGE / 'design/contract-impact.json'; cls.mapping_sha = byte_digest(cls.mapping_path.read_bytes())
        # Unrelated private/session state is deliberately present but unselected.
        private = cls.fixture / '.local/session-notes.json'; private.parent.mkdir(); private.write_text('{"short_memory":"never-export-this-secret"}')

    @classmethod
    def tearDownClass(cls): cls.temp.cleanup()

    def setUp(self):
        self.temp = TemporaryDirectory(prefix='lab-promotion-case-'); self.root = Path(self.temp.name)
        self.repo = self.root / 'repository'; shutil.copytree(self.repository, self.repo)
        self.selection = select(self.repo, **self.args)
        self.parent = VerifiedLegacyReadStore(self.fixture, self.repository, ROOT, self.pins)
        self.authority = RepositoryAuthority(str(self.repo), 'principal:test-only-repository-owner', self.public_key,
            'scope:isolated-publisher', 'policy:cyberalchemy-lab-operational-foundation', 'challenge-contract:cyberalchemy-lab-operational-foundation',
            '2099-01-01T00:00:00Z', 'isolated-publisher-fixture', 'authority/admissions/isolated-publisher-fixture/v1',
            (('artifact-instance','role:repository-owner'), ('definition','role:definition-owner'), ('artifact-type','role:artifact-type-owner'),
             ('typed-relation','role:relation-owner'), ('relation-kind','role:relation-owner')), 'fixture:independent-role-resolution',
            claim_ceiling='Isolated publisher fixture only; no authority outside this temporary repository or actual human admission.')
        self.selected = self.select_rows([0, 3])
        self.mirrors = [{'path': 'docs/decisions/fixture-publisher/decision.json', 'source': 'instances/governance/decision-0000.json', 'before_sha256': None}]

    def tearDown(self): self.temp.cleanup()

    def select_rows(self, indexes):
        return [{'version_ref': self.targets[i]['version_ref'], 'carrier_ref': self.targets[i]['carrier_ref'],
            'operation': self.targets[i]['operation'], 'predecessor_ref': self.targets[i]['predecessor_ref'],
            'decision_ref': 'decision:repository-fixture:' + str(i), 'evidence_selectors': ['/decision_cores/' + str(i)]} for i in indexes]

    def prepare(self, *, selected=None, mirrors=None):
        return prepare_promotion(self.parent, self.selection, selected or self.selected, self.mapping_path, self.mapping_sha,
            self.authority, mirrors=self.mirrors if mirrors is None else mirrors)

    def apply(self, prepared, response, **kw):
        return publish(self.parent, self.selection, self.selected, self.mapping_path, self.mapping_sha,
            self.authority, prepared, response, mirrors=self.mirrors, **kw)

    def test_selected_export_and_private_exclusion(self):
        p = self.prepare(); raw = b'\n'.join(p['materials'].values())
        self.assertNotIn(b'never-export-this-secret', raw); self.assertNotIn(self.targets[1]['record']['node_id'].encode(), raw)
        self.assertNotIn(self.local_approval['signature'].encode(), raw)
        self.assertEqual(p['review']['local_approvals_exported'], 0)
        self.assertEqual({c['owner_ref'] for c in p['review']['independent_cores']}, {'role:repository-owner', 'role:definition-owner'})

    def test_one_response_complete_carriers_and_cold_replay(self):
        p = self.prepare(); response = owner_response(p, self.authority, self.owner_private)
        cores = copy.deepcopy(p['review']['independent_cores'])
        result = self.apply(p, response); self.assertTrue(result['committed'])
        pins = PublicationPins(**result['pins']); final = self.repo / self.authority.bundle_path
        verified = verify_bundle(final, pins, self.authority)
        self.assertEqual(len(verified['review']['independent_cores']), 2)
        self.assertEqual(verified['review']['independent_cores'], cores)
        state = load(final / 'instances/project-state.json'); self.assertEqual(state['payload']['cursor'], 'repository-admission:' + self.authority.bundle_id)
        self.assertEqual(load(final / 'receipts/application.json')['semantic_cursor'], 6)
        pointer = load(self.repo / self.authority.current_pointer_path); self.assertFalse(pointer['replay_source'])
        self.assertTrue(self.apply(p, response)['idempotent'])
        self.assertFalse(repair_publication(pins, self.authority)['new_owner_response_required'])
        code = 'import json,sys;from lab_runtime.publisher import *;from lab_runtime.promotion import RepositoryAuthority;x=json.loads(sys.argv[1]);a=x["authority"];a["owner_roles"]=tuple(tuple(r) for r in a["owner_roles"]);v=verify_bundle(x["path"],PublicationPins(**x["pins"]),RepositoryAuthority(**a));print(v["manifest"]["bundle_id"])'
        args = {'path': str(final), 'pins': asdict(pins), 'authority': asdict(self.authority)}
        child = subprocess.run([sys.executable, '-c', code, json.dumps(args)], cwd=PACKAGE, capture_output=True, text=True, timeout=30)
        self.assertEqual(child.returncode, 0, child.stderr); self.assertEqual(child.stdout.strip(), self.authority.bundle_id)
        PromotionTests.observed = {'fixture_only': True, 'review': p['review'], 'result': result,
            'owner_response_count': 1, 'fresh_process_verified': True, 'recorded_human_outcome': None,
            'parent_committed_bytes_preserved': all(byte_digest((self.fixture/n).read_bytes()) == sha for n,sha in p['review']['parent']['committed_files'].items()),
            'generated_carrier_postimages': len([n for n in verified['files'] if n.startswith('instances/')]),
            'mirror_repair_requires_new_response': False}

    def test_local_signature_is_not_repository_authority(self):
        p = self.prepare()
        with self.assertRaises(RuntimeFault): self.apply(p, self.local_approval)
        with self.assertRaisesRegex(RuntimeFault, 'key mismatch'): owner_response(p, self.authority, self.private)

    def test_invalid_repository_signature(self):
        p = self.prepare(); r = owner_response(p, self.authority, self.owner_private); r['signature'] = '0' * 128
        with self.assertRaisesRegex(RuntimeFault, 'signature'): verify_response(r, p['review'], self.authority)

    def test_local_decision_identity_reuse_rejected(self):
        selected = copy.deepcopy(self.selected); selected[0]['decision_ref'] = self.targets[0]['decision_ref']
        with self.assertRaisesRegex(RuntimeFault, 'independent new identity'): self.prepare(selected=selected)

    def test_unselected_and_approval_evidence_rejected(self):
        for selector in ['/approval', '/proposal/targets/1/record', '/config/private_key', '/consequences/receipt']:
            selected = copy.deepcopy(self.selected); selected[0]['evidence_selectors'] = [selector]
            with self.assertRaisesRegex(RuntimeFault, 'evidence selector'): self.prepare(selected=selected)

    def test_explicit_repository_revision_and_collision(self):
        selected = self.select_rows([2]); p = self.prepare(selected=selected)
        self.assertEqual(p['review']['independent_cores'][0]['selected_outcome'], 'revise')
        selected[0].update(operation='admit', predecessor_ref=None)
        with self.assertRaisesRegex(RuntimeFault, 'already present'): self.prepare(selected=selected)

    def test_new_contract_and_coeval_instance(self):
        selected = self.select_rows([3, 4, 5]); schema_sha = self.targets[4]['contract']['schema_sha256']
        mirrors = [{'path': self.targets[4]['contract']['schema_path'], 'source': 'validation/schemas/' + schema_sha + '.json', 'before_sha256': None}]
        p = self.prepare(selected=selected, mirrors=mirrors); r = owner_response(p, self.authority, self.owner_private)
        files, _ = render_bundle(p, r, self.authority)
        self.assertIn('validation/schemas/' + schema_sha + '.json', files)
        result = publish(self.parent, self.selection, selected, self.mapping_path, self.mapping_sha, self.authority, p, r, mirrors=mirrors)
        self.assertTrue(result['committed']); self.assertEqual(byte_digest((self.repo / mirrors[0]['path']).read_bytes()), schema_sha)

    def test_unselected_definition_cannot_authorize_coeval_type(self):
        with self.assertRaisesRegex(RuntimeFault, 'Definition binding'):
            self.prepare(selected=self.select_rows([4, 5]), mirrors=[])

    def test_reviewed_generator_pin_rejected(self):
        from lab_runtime.publisher import verify_generator
        p = self.prepare(); p['review']['generator_binding']['files'][0]['sha256'] = '0' * 64
        with self.assertRaisesRegex(RuntimeFault, 'generator bytes changed'): verify_generator(p['review'])

    def test_local_source_writer_exclusion(self):
        import fcntl
        p = self.prepare(); r = owner_response(p, self.authority, self.owner_private)
        fd = os.open(self.fixture / '.writer.lock', os.O_RDONLY)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            with self.assertRaisesRegex(RuntimeFault, 'local source writer active'): self.apply(p, r)
        finally: os.close(fd)

    def test_exact_owner_core_selection_rejected(self):
        p = self.prepare(); r = owner_response(p, self.authority, self.owner_private)
        r['decision_core_sha256s'] = r['decision_core_sha256s'][:1]
        with self.assertRaisesRegex(RuntimeFault, 'exact independent'): self.apply(p, r)

    def test_stale_repository_sources_block_before_commit(self):
        p = self.prepare(); r = owner_response(p, self.authority, self.owner_private)
        pointer = self.repo / self.authority.current_pointer_path; raw = pointer.read_bytes(); pointer.write_bytes(raw + b'\n')
        with self.assertRaises(RuntimeFault): self.apply(p, r)
        self.assertFalse((self.repo / self.authority.bundle_path).exists())

    def test_changed_export_postimage_rejected(self):
        p = self.prepare(); r = owner_response(p, self.authority, self.owner_private)
        name = p['review']['targets'][0]['record_path']; p['materials'][name] += b'\n'
        with self.assertRaisesRegex(RuntimeFault, 'closure changed'): self.apply(p, r)

    def test_unknown_existing_final_bundle_preserved(self):
        p = self.prepare(); r = owner_response(p, self.authority, self.owner_private)
        final = self.repo / self.authority.bundle_path; final.mkdir(parents=True); (final / 'unrelated').write_text('retain')
        with self.assertRaisesRegex(RuntimeFault, 'incomplete'): self.apply(p, r)
        self.assertEqual((final / 'unrelated').read_text(), 'retain')

    def test_writer_exclusion(self):
        lock = _lock(self.authority)
        try:
            with self.assertRaisesRegex(RuntimeFault, 'writer active'): _lock(self.authority)
        finally: os.close(lock)

    def test_expired_owner_authority(self):
        p = self.prepare(); a = replace(self.authority, expires_at='2000-01-01T00:00:00Z')
        p['review']['authority'] = a.core()
        with self.assertRaisesRegex(RuntimeFault, 'expired'): owner_response(p, a, self.owner_private)

    def test_private_record_or_unmanaged_path_rejected(self):
        for value in [{'private_key':'secret'}, {'short_memory':['secret']}, '.local/operator/key.pem', '-----BEGIN PRIVATE KEY-----']:
            with self.assertRaises(RuntimeFault): public_material(value)
        with self.assertRaisesRegex(RuntimeFault, 'mirror scope'):
            self.prepare(mirrors=[{'path':'README.md','source':'instances/project-state.json','before_sha256':None}])

    def test_mirror_conflict_after_commit_is_recovery_required(self):
        p = self.prepare(); r = owner_response(p, self.authority, self.owner_private)
        # Conflict is introduced after exact staging/commit in the crash test below;
        # a managed postcommit repair never overwrites unexpected user bytes.
        result = self.apply(p, r); path = self.repo / self.mirrors[0]['path']; path.write_text('unrelated edited mirror')
        with self.assertRaisesRegex(RuntimeFault, 'preserve unrelated'): repair_publication(PublicationPins(**result['pins']), self.authority)
        self.assertEqual(path.read_text(), 'unrelated edited mirror')
        verify_bundle(self.repo / self.authority.bundle_path, PublicationPins(**result['pins']), self.authority)

    def child(self, p, r, hook):
        x = {'parent_path': str(self.fixture), 'parent_repository': str(self.repository), 'executable_repo': str(ROOT), 'parent_pins': asdict(self.pins),
            'repository': str(self.repo), 'selection_args': self.args, 'selections': self.selected,
            'identity_path': str(self.mapping_path), 'identity_sha256': self.mapping_sha, 'authority': asdict(self.authority),
            'mirrors': self.mirrors, 'response': r, 'review': p['review'],
            'materials': {name: __import__('base64').b64encode(raw).decode() for name,raw in p['materials'].items()}, 'crash_at': hook}
        arg = self.root / 'fixture-child-input.json'; arg.write_bytes(encoded(x))
        return subprocess.run([sys.executable, str(Path(__file__).resolve()), '--child', str(arg)], cwd=PACKAGE, capture_output=True, text=True, timeout=120)

    def test_crash_before_and_after_commit_and_cold_repair(self):
        p = self.prepare(); r = owner_response(p, self.authority, self.owner_private); files,_ = render_bundle(p,r,self.authority)
        pins = PublicationPins(digest(p['review']), byte_digest(files['bundle.json']), digest(self.authority.core()))
        child = self.child(p,r,'after-stage'); self.assertEqual(child.returncode,75,child.stderr)
        self.assertFalse((self.repo / self.authority.bundle_path).exists())
        child = self.child(p,r,'after-commit'); self.assertEqual(child.returncode,76,child.stderr)
        self.assertEqual(byte_digest((self.repo / self.authority.current_pointer_path).read_bytes()),p['review']['expected_pointer_sha256'])
        final = self.repo / self.authority.bundle_path; verify_bundle(final,pins,self.authority)
        # Failure after the first mirror leaves a committed complete bundle; retry
        # needs the same response and no mutable current-source recapture.
        child = self.child(p,r,'after-first-mirror'); self.assertEqual(child.returncode,77,child.stderr)
        outcome = repair_publication(pins,self.authority); self.assertTrue(outcome['committed']); self.assertFalse(outcome['new_owner_response_required'])
        self.assertTrue(self.apply(p,r)['idempotent'])
        (final / 'instances/project-state.json').write_bytes((final / 'instances/project-state.json').read_bytes()+b'\n')
        with self.assertRaisesRegex(RuntimeFault,'original bytes changed'): verify_bundle(final,pins,self.authority)


if __name__ == '__main__':
    if len(sys.argv)>1 and sys.argv[1]=='--child':
        import base64
        x=load(sys.argv[2]); a=x['authority']; a['owner_roles']=tuple(tuple(r) for r in a['owner_roles']); authority=RepositoryAuthority(**a)
        parent=VerifiedLegacyReadStore(x['parent_path'],x['parent_repository'],x['executable_repo'],ReplayPins(**x['parent_pins']))
        selection=select(x['repository'],**x['selection_args'])
        prepared={'review':x['review'],'materials':{p:base64.b64decode(raw) for p,raw in x['materials'].items()}}
        outcome=publish(parent,selection,x['selections'],x['identity_path'],x['identity_sha256'],authority,prepared,x['response'],mirrors=x['mirrors'],crash_at=x['crash_at'])
        print(json.dumps(outcome))
    else: unittest.main()
