"""Causal role/current-boundary tests using exclusive owned fixture directories."""
import bootstrap
from bootstrap import E
import argparse, copy, json, os, tempfile, time, traceback, unittest
from unittest.mock import patch
from pathlib import Path
from lab_contracts.codec import canonical, sha, Refusal
from lab_selectors.anchors import AnchoredReader, RootAnchor, identity
from dependency_graph.reader import RoleReader, ReaderSelection, FixturePermission, MAX_READ, PUBLIC_CODES

TEMP_ROOT = E
OWNED = []

class Fixture:
    def __init__(self, root):
        self.root = root
        self.bindings = []
        self.source = self.write('source.json', {'files': []})
        self.profile = self.write('profile.json', {'profile': 'fixture'})
        self.cut = {'branch_ref': 'fixture-branch', 'store_ref': 'fixture-store',
                    'commit_sequence': 7, 'commit_sha256': 'a'*64,
                    'source_profile_sha256': self.profile['sha256'], 'streams': []}
        self.table_rows = [{'path': 'NEVER-OPEN-THIS-PROTECTED-LOCATOR', 'sha256': 'b'*64,
                            'identity': 'same', 'extra': {'order': 1}},
                           {'identity': 'second', 'extra': {'order': 2}},
                           {'path': 'NEVER-OPEN-THIS-PROTECTED-LOCATOR', 'sha256': 'b'*64,
                            'identity': 'same', 'extra': {'order': 1}}]
        self.table = self.write('table.json', {'files': self.table_rows})
        self.body = self.write('protected.json', {'private_fixture_body': 'DO-NOT-DISCLOSE'}, 'protected-input')
        self.public = self.write('schema.json', {'type': 'object'}, 'execution')
        self.descriptors = [{'document_binding': self.table, 'selector': '/files', 'row_count': 3,
                             'classification': 'original-proof-metadata'}]
        self.policy = {'schema_version': 'lab-original-role-selection/v1',
            'source_binding': self.source, 'profile_binding': self.profile, 'source_cut': self.cut,
            'table_descriptors': self.descriptors, 'authority_effect': 'none', 'files': [
                {'file_id': 'proof', 'logical_path': 'proof/original.json', 'kind': 'history-proof', 'binding': self.table},
                {'file_id': 'body', 'logical_path': 'private/original.json', 'kind': 'governed-record', 'binding': self.body},
                {'file_id': 'schema', 'logical_path': 'schemas/original.json', 'kind': 'governed-schema', 'binding': self.public}]}
        self.policy_binding = self.write('policy.json', self.policy, 'execution')
        self.grant = {'schema_version': 'lab-fixture-reader-permission/v1', 'posture': 'owned-fixture',
            'subject': 'fixture-owner', 'source_binding': self.source, 'profile_binding': self.profile,
            'source_cut': self.cut, 'allowed_bindings': [self.body], 'not_before_ns': 0,
            'expires_ns': time.time_ns()+120_000_000_000, 'authority_effect': 'none'}
        self.grant_binding = self.write('permission.json', self.grant)
        self.calls = 0
        self.after_read = None
        self.expected_root = identity(os.stat(root))

    def write(self, path, value, kind='evidence'):
        raw = canonical(value)
        with (self.root/path).open('xb') as f: f.write(raw)
        result = {'kind': kind, 'root_id': 'fixture', 'relative_path': path,
                  'sha256': sha(raw), 'size_bytes': len(raw)}
        self.bindings.append(result)
        return result

    def reader(self):
        outer = self
        class Provider:
            def read(self, binding, *, max_bytes):
                outer.calls += 1
                public = {**binding, 'kind': 'public-package'}
                raw = AnchoredReader([RootAnchor('fixture', str(outer.root), outer.expected_root)], [public]).read(public, max_bytes)
                if outer.after_read: outer.after_read()
                return raw
        return AnchoredReader([RootAnchor('fixture', str(self.root), self.expected_root)], self.bindings,
                              protected_provider=Provider())

    def selection(self, **overrides):
        return ReaderSelection(**({'policy_binding': self.policy_binding, 'source_binding': self.source,
            'profile_binding': self.profile, 'source_cut': self.cut, 'table_descriptors': self.descriptors} | overrides))

    def role(self, fixture=False, selection=None):
        reader = self.reader()
        return RoleReader(reader, selection or self.selection(),
            posture='owned-fixture' if fixture else 'public-metadata',
            permission=FixturePermission(reader,self.grant_binding,'fixture-owner') if fixture else None)

    def substitute(self, path, value):
        (self.root/path).write_bytes(canonical(value))

class ReaderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='owned-test-reader-', dir=TEMP_ROOT)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name);OWNED.append(self.root)
        self.f = Fixture(self.root)

    def test_public_schema_selected_role(self):
        self.assertEqual(self.f.role().read('schema', 'governed-schema'), canonical({'type':'object'}))

    def test_protected_read_only_fixture(self):
        self.assertEqual(self.f.role(True).read('body', 'governed-record'), canonical({'private_fixture_body':'DO-NOT-DISCLOSE'}))
        self.assertEqual(self.f.calls,1)

    def test_public_posture_refuses_protected_before_provider(self):
        with self.assertRaisesRegex(Refusal,'ACTUAL_PROTECTED_READ_GATED'): self.f.role().read('body')
        self.assertEqual(self.f.calls,0)

    def test_actual_posture_cannot_be_enabled_by_fixture_grant(self):
        with self.assertRaisesRegex(Refusal,'ACTUAL_HOST_PROVIDER_REQUIRED'):
            RoleReader(self.f.reader(),self.f.selection(),posture='actual')

    def test_wrong_role_not_inferred_from_file_name(self):
        for role in ['governed-record','governed-schema']:
            with self.subTest(role=role),self.assertRaisesRegex(Refusal,'ORIGINAL_ROLE_MISMATCH'):
                self.f.role().read('proof',role)

    def test_no_implicit_proof_promotion(self):
        p=copy.deepcopy(self.f.policy);p['files'][0]['kind']='governed-record'
        b=self.f.write('independently-selected-invalid-role.json',p,'execution')
        with self.assertRaisesRegex(Refusal,'ROLE_BINDING_KIND'):
            self.f.role(selection=self.f.selection(policy_binding=b))

    def test_invalid_limits_before_provider_even_expired_grant(self):
        r=self.f.role(True)
        self.f.substitute('permission.json',{})
        for limit in [0,-1,True,MAX_READ+1,1]:
            with self.subTest(limit=limit),self.assertRaisesRegex(Refusal,'READ_LIMIT'):
                r.read('body',max_bytes=limit)
        self.assertEqual(self.f.calls,0)

    def test_current_permission_revocation_before_read(self):
        r=self.f.role(True);self.f.substitute('permission.json',{})
        with self.assertRaises(Refusal):r.read('body')
        self.assertEqual(self.f.calls,0)

    def test_permission_revoked_during_read_returns_no_body(self):
        r=self.f.role(True);self.f.after_read=lambda:self.f.substitute('permission.json',{})
        with self.assertRaises(Refusal):r.read('body')
        self.assertEqual(self.f.calls,1)

    def test_expired_independently_selected_permission(self):
        b=self.f.write('expired.json',self.f.grant|{'expires_ns':1})
        rd=self.f.reader()
        with self.assertRaisesRegex(Refusal,'FIXTURE_PERMISSION_EXPIRED'):
            RoleReader(rd,self.f.selection(),posture='owned-fixture',permission=FixturePermission(rd,b,'fixture-owner'))

    def test_current_permission_scope(self):
        b=self.f.write('empty-grant.json',self.f.grant|{'allowed_bindings':[]})
        rd=self.f.reader()
        r=RoleReader(rd,self.f.selection(),posture='owned-fixture',permission=FixturePermission(rd,b,'fixture-owner'))
        with self.assertRaisesRegex(Refusal,'FIXTURE_PERMISSION_SCOPE'):r.read('body')
        self.assertEqual(self.f.calls,0)

    def test_permission_cross_cut(self):
        b=self.f.write('wrong-cut-grant.json',self.f.grant|{'source_cut':self.f.cut|{'commit_sequence':8}})
        rd=self.f.reader()
        with self.assertRaisesRegex(Refusal,'FIXTURE_PERMISSION_SELECTION'):
            RoleReader(rd,self.f.selection(),posture='owned-fixture',permission=FixturePermission(rd,b,'fixture-owner'))

    def test_coherent_repin_does_not_replace_independent_policy(self):
        p=copy.deepcopy(self.f.policy);p['files']=[]
        self.f.substitute('policy.json',p)
        with self.assertRaises(Refusal):self.f.role()

    def test_policy_cannot_replace_independent_source_cut(self):
        p=copy.deepcopy(self.f.policy);p['source_cut']['commit_sequence']=8
        b=self.f.write('changed-cut-policy.json',p,'execution')
        with self.assertRaisesRegex(Refusal,'INDEPENDENT_ROLE_SELECTION'):
            self.f.role(selection=self.f.selection(policy_binding=b))

    def test_source_profile_cross_cut_refused(self):
        with self.assertRaisesRegex(Refusal,'SOURCE_PROFILE_CUT'):
            self.f.role(selection=self.f.selection(source_cut=self.f.cut|{'source_profile_sha256':'f'*64}))

    def test_accepted_source_drift_during_boundary_refuses(self):
        r=self.f.role()
        with self.assertRaises(Refusal):
            with r.boundary():
                self.f.substitute('source.json',{'changed':True})

    def test_symlink_member_refuses(self):
        r=self.f.role();(self.root/'schema.json').rename(self.root/'moved.json')
        (self.root/'schema.json').symlink_to('moved.json')
        with self.assertRaises(Refusal):r.read('schema')

    def test_root_identity_drift_refuses(self):
        r=self.f.role();os.chmod(self.root,0o755)
        with self.assertRaises(Refusal):r.read('schema')

    def test_duplicate_file_or_binding_refuses(self):
        for mode in ['id','binding']:
            p=copy.deepcopy(self.f.policy);row=copy.deepcopy(p['files'][0])
            if mode=='binding':row['file_id']='second-id'
            p['files'].append(row)
            b=self.f.write('duplicate-'+mode+'.json',p,'execution')
            with self.subTest(mode=mode),self.assertRaises(Refusal):
                self.f.role(selection=self.f.selection(policy_binding=b))

    def test_unknown_kind_refuses(self):
        p=copy.deepcopy(self.f.policy);p['files'][0]['kind']='invented'
        b=self.f.write('unknown-role.json',p,'execution')
        with self.assertRaisesRegex(Refusal,'ROLE_BINDING_KIND'):
            self.f.role(selection=self.f.selection(policy_binding=b))

    def test_full_occurrences_retained_no_row_member_reads(self):
        r=self.f.role();result=r.inventory(self.f.descriptors)
        self.assertEqual(result['tables'][0]['rows'],self.f.table_rows)
        self.assertEqual(result['occurrences'],3)
        self.assertEqual(result['member_bodies_read'],0)
        self.assertFalse((self.root/'NEVER-OPEN-THIS-PROTECTED-LOCATOR').exists())

    def test_complete_row_corruption_refuses_selected_document(self):
        r=self.f.role()
        for rows in [self.f.table_rows[:-1],list(reversed(self.f.table_rows[:2])),
                     [self.f.table_rows[0]]*3, [self.f.table_rows[1],*self.f.table_rows[:2]]]:
            self.f.substitute('table.json',{'files':rows})
            with self.assertRaises(Refusal):r.inventory(self.f.descriptors)

    def test_independent_table_descriptor_omission_refuses(self):
        with self.assertRaisesRegex(Refusal,'INDEPENDENT_TABLE_SELECTION'):
            self.f.role().inventory([])

    def test_no_protected_inventory_bypass(self):
        descriptors=[dict(self.f.descriptors[0],document_binding=self.f.body)]
        p=self.f.policy|{'table_descriptors':descriptors}
        b=self.f.write('protected-table.json',p,'execution')
        with self.assertRaisesRegex(Refusal,'PROTECTED_TABLE_DOCUMENT_GATED'):
            self.f.role(selection=self.f.selection(policy_binding=b,table_descriptors=descriptors))

    def test_summary_contains_no_body_or_locator(self):
        raw=canonical(self.f.role(True).public_summary())
        for value in [b'DO-NOT-DISCLOSE',b'private/original',b'NEVER-OPEN',b'fixture-owner']:
            self.assertNotIn(value,raw)

    def test_returned_selection_and_file_maps_are_defensive_copies(self):
        r=self.f.role();r.files['schema']['kind']='governed-record';r.selection['source_cut']['commit_sequence']=99
        self.assertEqual(r.read('schema','governed-schema'),canonical({'type':'object'}))

    def public_refusal(self, action, *private_values):
        try:
            action()
        except Refusal as error:
            rendered=''.join(traceback.format_exception(error))
            self.assertIn(str(error),PUBLIC_CODES)
            self.assertIsNone(error.__cause__)
            self.assertTrue(error.__suppress_context__)
            for value in private_values:self.assertNotIn(value,rendered)
        else:self.fail('expected bounded refusal')

    def test_provider_message_and_private_traceback_are_suppressed(self):
        r=self.f.role(True);marker='INERT_'+'PRIVATE_PROVIDER_MARKER'
        def fail():raise RuntimeError(marker)
        self.f.after_read=fail
        self.public_refusal(lambda:r.read('body'),marker)
        self.assertEqual(self.f.calls,1)

    def test_provider_refusal_type_does_not_trust_its_message(self):
        r=self.f.role(True);marker='INERT_'+'PRIVATE_REFUSAL_MARKER'
        def fail():raise Refusal(marker)
        self.f.after_read=fail
        self.public_refusal(lambda:r.read('body'),marker)

    def test_arbitrary_exception_rendering_is_never_invoked(self):
        r=self.f.role(True);calls=[]
        class Hostile:
            def __str__(self):calls.append('str');return 'private'
            def __repr__(self):calls.append('repr');return 'private'
        def fail():raise Refusal(Hostile())
        self.f.after_read=fail
        self.public_refusal(lambda:r.read('body'))
        self.assertEqual(calls,[])

    def test_missing_root_constructor_suppresses_os_locator(self):
        rd=self.f.reader();moved=self.root.with_name(self.root.name+'-held')
        self.root.rename(moved)
        try:self.public_refusal(lambda:RoleReader(rd,self.f.selection()),str(self.root),self.root.name)
        finally:moved.rename(self.root)

    def test_permission_direct_check_suppresses_io_exception(self):
        rd=self.f.reader();permission=FixturePermission(rd,self.f.grant_binding,'fixture-owner')
        marker='INERT_'+'PRIVATE_PERMISSION_LOCATOR'
        with patch.object(rd,'read',side_effect=OSError(marker)):
            self.public_refusal(lambda:permission.check(self.f.selection().__dict__,self.f.body),marker)

    def test_inventory_parser_exception_is_suppressed(self):
        r=self.f.role();marker='INERT_'+'PRIVATE_PARSE_INPUT'
        with patch('dependency_graph.reader.retain',side_effect=ValueError(marker)):
            self.public_refusal(lambda:r.inventory(self.f.descriptors),marker)

    def test_boundary_enter_and_exit_errors_are_suppressed(self):
        r=self.f.role();marker='INERT_'+'PRIVATE_BOUNDARY_LOCATOR'
        def enter():
            with r.boundary():pass
        with patch.object(r,'_guard',side_effect=OSError(marker)):
            self.public_refusal(enter,marker)
        self.assertEqual(r._depth,0)
        with patch.object(r,'_guard',side_effect=[None,OSError(marker)]):
            self.public_refusal(enter,marker)
        self.assertEqual(r._depth,0)

    def test_boundary_body_exception_is_suppressed_but_interrupt_propagates(self):
        r=self.f.role();marker='INERT_'+'PRIVATE_CALLER_CONTEXT'
        def body():
            with r.boundary():raise RuntimeError(marker)
        self.public_refusal(body,marker)
        with self.assertRaises(KeyboardInterrupt):
            with r.boundary():raise KeyboardInterrupt()
        self.assertEqual(r._depth,0)

    def test_permission_cannot_cross_same_named_roots_even_with_equal_bindings(self):
        a=self.f.reader();permission=FixturePermission(a,self.f.grant_binding,'fixture-owner')
        b=copy.copy(self.f);b.root=self.root/'second-root';b.root.mkdir(mode=0o700)
        for path in self.root.iterdir():
            if path.is_file():(b.root/path.name).write_bytes(path.read_bytes())
        b.expected_root=identity(os.stat(b.root));b.calls=0
        self.assertNotEqual(b.expected_root,self.f.expected_root)
        b.substitute('permission.json',{})
        reader_b=b.reader()
        with patch.object(reader_b,'read',wraps=reader_b.read) as observed:
            with self.assertRaisesRegex(Refusal,'PERMISSION_READER_DOMAIN'):
                RoleReader(reader_b,b.selection(),posture='owned-fixture',permission=permission)
            self.assertEqual(observed.call_count,0)
        self.assertEqual(b.calls,0)

    def test_permission_reader_replacement_after_construction_refuses(self):
        r=self.f.role(True);r._permission._reader=self.f.reader()
        with self.assertRaisesRegex(Refusal,'PERMISSION_READER_DOMAIN'):r.read('body')
        self.assertEqual(self.f.calls,0)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--temp-root',type=Path,required=True);args=p.parse_args()
    TEMP_ROOT=args.temp_root
    if not TEMP_ROOT.is_dir():raise ValueError('owned existing temp root required')
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ReaderTests))
    clean=not any(p.exists() for p in OWNED)
    print(json.dumps({'schema_version':'lab-case-command-result/v1','result':'PASS' if result.wasSuccessful() and clean else 'FAIL',
        'checks':result.testsRun,'effect_state':'owned-inert','cleanup':'clean' if clean else 'retained-owned'}))
    raise SystemExit(0 if result.wasSuccessful() and clean else 1)
