"""Public synthetic 40-leaf packages. No protected Source body or Context effect."""
import copy
import base64
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('context_output_validator_0003', HERE / 'validator.py')
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)
EXPIRY = '2026-10-20T12:10:00Z'
CUT = {'store_ref': 'store:synthetic', 'branch_ref': 'branch:synthetic',
       'commit_sequence': 25, 'commit_sha256': 'a'*64,
       'source_profile_sha256': 'b'*64,
       'streams': [{'stream_ref': 'stream:synthetic', 'cursor': 25, 'head_sha256': 'c'*64}]}


def fixture():
    temp = tempfile.TemporaryDirectory(prefix='context-output-synthetic-')
    root = Path(temp.name) / 'attempt' / 'package'
    root.mkdir(parents=True)
    (root / 'artifacts').mkdir()
    source = {'path': '/synthetic/family/context/source-manifest.json', 'sha256': 'd'*64}
    native_ids = [{'subject_id': f'subject:synthetic-{i:02d}', 'subject_kind':
                   'node' if i < 15 else 'edge'} for i in range(25)]
    source_refs = [{'scope_ref': 'scope:synthetic',
                    'identity_ref': f'source:synthetic-{i:02d}',
                    'version_ref': f'source:synthetic-{i:02d}@v1',
                    'carrier_ref': 'cal.artifact-type.agent-assignment/v1',
                    'byte_sha256': V.sha(f'source-{i}'.encode())} for i in range(25)]
    source_refs[1]['carrier_ref'] = 'cal.artifact-type.work/v1'
    source_refs[2]['carrier_ref'] = 'cal.artifact-type.coordination-context/v2'
    native_rows = [{'native_identity': native_ids[i],
                    'semantic_event_ref': {'semantic_event_id': f'event:{i}',
                                           'semantic_event_digest': V.sha(f'event-{i}'.encode()),
                                           'semantic_cursor': i+1},
                    'governance_event_ref': f'governance:{i}'}
                   for i in range(25)]
    source_material = [
        {'artifact': r,
         'original_material': {'source_ref': f'synthetic-source:{i}',
                               'selector': '#', 'sha256': V.sha(f'enclosing-{i}'.encode())},
         'selected_original_body_sha256': r['byte_sha256'],
         'selected_body_encoding': 'utf-8',
         'visibility': 'selected-body-only; enclosing archives remain private'}
        for i, r in enumerate(source_refs)]
    public_policy = {
        'schema_version': 'lab-context-host-policy/v1-candidate',
        'host_uid': os.getuid(), 'principal_ref': 'principal:synthetic',
        'scope_ref': 'scope:synthetic',
        'reader_public_key': base64.b64encode(b'\x02'*32).decode(),
        'not_before': '2026-10-20T12:00:00Z',
        'expires_at': '2026-10-20T12:10:00Z',
        'max_input_bytes': 1048576, 'max_output_bytes': 2097152,
        'max_session_seconds': 900,
        'period_binding': {'path': V.integration().PERIOD_REL,
                           'sha256': V.integration().PERIOD_SHA},
        'allowed_operations': ['context.get', 'session.open'],
        'authority_effect': 'none', 'actual_owner_outcome': None}
    held = {'held_origin': 'synthetic-held-public-metadata', 'uid': os.getuid(),
            'gid': os.getgid(), 'context_source_binding': source,
            'mapper_package_sha256': 'e'*64, 'native_cut_digest': 'f'*64,
            'source_cut': copy.deepcopy(CUT), 'scope_ref': 'scope:synthetic',
            'native_subject_identities': native_ids,
            'native_rows': native_rows,
            'selected_source_refs': source_refs,
            'source_material_provenance': source_material,
            'native_source_event_set_digest': '1'*64,
            'public_policy': public_policy,
            'principal_ref': 'principal:synthetic',
            'period_binding': public_policy['period_binding'],
            'assignment': source_refs[0], 'work': source_refs[1],
            'coordination_context': source_refs[2],
            'authority_envelope_binding': {'ref': 'host-policy:synthetic',
                                            'sha256': V.sha(V.original_leaf_bytes(
                                                'host-permission-public.json', public_policy))},
            'authority_envelope_ref': 'host-policy:synthetic',
            'observed_at': '2026-10-20T12:00:00Z',
            'source_start': '2026-10-20T08:20:00Z',
            'source_end': '2026-10-21T08:20:00Z',
            'auth_start': '2026-10-20T11:59:00Z',
            'auth_end': '2026-10-20T12:15:00Z',
            'policy_start': '2026-10-20T12:00:00Z',
            'policy_end': '2026-10-20T12:10:00Z',
            'signed_source_guard': True, 'auth_validated': True,
            'policy_validated': True}
    documents = {
        'request.json': {
            'schema_version': 'lab-context-query/v1-candidate',
            'request_ref': 'request:synthetic',
            'actor': {'principal_ref': 'principal:synthetic',
                      'role_assignment_refs': [], 'agent_instance_ref': None,
                      'session_ref': None, 'assignment_ref': None},
            'assignment': source_refs[0], 'work': source_refs[1],
            'coordination_context': source_refs[2], 'source_cut': CUT,
            'intended_use': 'Read current scoped Project State',
            'selectors': [],
            'exclusions': ['historical-session-memory', 'private-source-archives',
                           'external-effects', 'unrelated-work'],
            'freshness_requirement': 'current',
            'budget': {'max_actions': 0, 'max_input_bytes': 1048576,
                       'max_output_bytes': 2097152,
                       'deadline': '2026-10-20T12:05:00Z'},
            'authority_effect': 'none'},
        'authentication-proof.json': {'synthetic': True},
        'trusted-context.json': {'synthetic': True},
        'host-permission-public.json': public_policy,
    }
    order = (['ontology-node']*15 + ['ontology-edge']*10 +
             ['ontology', 'ontology-cut', 'ontology-view', 'context-request', 'context-view'])
    refs = []
    index = []
    bodies = []
    for i, kind in enumerate(order):
        version = V.VERSIONS[kind]
        p = V.REPO / 'authority/artifact-types' / kind / version / 'fixtures/valid/record.json'
        body = json.loads(p.read_bytes())
        body['node_id'] = f'{kind}:synthetic-{i:02d}'
        body['scope_ref'] = held['scope_ref']
        if kind == 'context-view':
            body['expires_at'] = EXPIRY
        if kind == 'ontology-view':
            body['payload']['expires_at'] = EXPIRY
            body['payload']['cut_digest'] = held['native_cut_digest']
            body['payload']['source_event_set_digest'] = held['native_source_event_set_digest']
        if kind == 'ontology-cut':
            body['payload']['calculated_digest'] = held['native_cut_digest']
            body['payload']['source_event_set_digest'] = held['native_source_event_set_digest']
        if i < 15:
            body['payload']['governance_binding']['semantic_event_ref'] = native_rows[i]['semantic_event_ref']
            body['payload']['governance_binding']['governance_event_refs'] = [native_rows[i]['governance_event_ref']]
        elif i < 25:
            body['payload']['semantic_event_ref'] = native_rows[i]['semantic_event_ref']
        if kind == 'context-view':
            body['source_epoch'] = 'protocol:source-cut:' + V.sha(
                V.original_leaf_bytes('context-view.json', CUT))
        leaf = f'artifacts/{i:02d}.json'
        raw = V.original_leaf_bytes(leaf, body)
        ref = {'scope_ref': held['scope_ref'], 'identity_ref': body['node_id'],
               'version_ref': body['node_id'] + '@derived.synthetic',
               'carrier_ref': f'cal.artifact-type.{kind}/{version}',
               'byte_sha256': V.sha(raw)}
        refs.append(ref)
        index.append({'artifact': ref, 'original_binding': V.binding(root, leaf, raw)})
        bodies.append(body)
        documents[leaf] = body
    documents['artifact-index.json'] = index
    lesson = {'schema_version': 'lab-context-lesson-selection/v1-candidate',
              'source_cut': CUT, 'assignment': source_refs[0],
              'current_catalog_lessons': 0, 'selected_lesson_refs': [],
              'selection_rule':
              'Actual current source catalog checked; new lessons require explicit applicability closure.',
              'authority_effect': 'none'}
    documents['lesson-selection.json'] = lesson
    documents['delivery.json'] = {
        'schema_version': 'lab-context-delivery/v1-candidate',
        'request_binding': {'ref': 'request:request:synthetic',
                            'sha256': V.sha(V.wire(documents['request.json']))},
        'source_cut': CUT,
        'context_view': refs[29], 'ontology_view': refs[27],
        'included_refs': source_refs, 'excluded_refs': [],
        'lesson_selection_binding': {'ref': 'protocol:R03-lesson-selection:synthetic',
                                     'sha256': V.sha(V.original_leaf_bytes(
                                         'lesson-selection.json', lesson))},
        'freshness': 'current', 'expires_at': EXPIRY,
        'scope_enforced': True, 'posture': 'ready', 'gaps': [],
        'claim_ceiling': 'Synthetic test only', 'authority_effect': 'none'}
    documents['delivery-provenance.json'] = {
        'schema_version': 'lab-verified-context-delivery-provenance/v1-candidate',
        'source_cut': CUT, 'posture': 'ready', 'scope_enforced': True,
        'freshness': 'current', 'expires_at': EXPIRY,
        'assignment': source_refs[0], 'work': source_refs[1],
        'coordination_context': source_refs[2],
        'authenticated_principal_ref': held['principal_ref'],
        'authority_envelope_binding': held['authority_envelope_binding'],
        'native_cut_digest': held['native_cut_digest'],
        'mapped_package_sha256': held['mapper_package_sha256'],
        'generated_artifact_refs': refs, 'authority_effect': 'none',
        'actual_owner_outcome': None,
        'verified_original_binding': V.binding(root, 'delivery.json',
                                                V.original_leaf_bytes(
                                                    'delivery.json', documents['delivery.json'])),
        'source_material_provenance': source_material,
        'correspondence': [{'native_identity': native_ids[i],
                            'carrier_identity': bodies[i]['node_id'],
                            'semantic_event_ref': native_rows[i]['semantic_event_ref'],
                            'governance_event_ref': native_rows[i]['governance_event_ref']}
                           for i in range(25)]}
    documents['build-result.json'] = {
        'result': 'PASS', 'actual_generated_artifact_carriers': 30,
        'ontology_nodes': 15, 'ontology_edges': 10,
        'context_request_view_and_ontology_cut_view_records': 5,
        'actual_original_schema_validation': True,
        'real_nonce_transport_authentication': True,
        'current_independent_host_permission': True,
        'current_absolute_Assignment_period': True,
        'actual_Context_Delivery_posture': 'ready',
        'native_domain_mapping_supplied': True,
        'source_and_native_cuts_distinct': True,
        'owned_host_policy_and_transport_key_removed': True,
        'active_Agents_created': 0, 'public_API_operations_added': 0,
        'source_sha256': source['sha256'],
        'mapped_package_sha256': held['mapper_package_sha256'],
        'authority_effect': 'none', 'actual_owner_outcome': None,
        'task_complete': False, 'duration_seconds': 1.0,
        'owned_host_root': str(root.parent / 'host-private')}
    materialize(root, documents, held)
    receipt = {'held_origin': 'synthetic-held-os-transport', 'uid': held['uid'],
               'gid': held['gid'], 'manifest_sha256':
               V.sha((root / 'manifest.json').read_bytes()),
               'source_binding': source,
               'output_bytes': sum((root / leaf).stat().st_size for leaf in V.LEAVES),
               'inventory_sha256': V.sha(V.wire([
                   V.binding(root, leaf, (root / leaf).read_bytes()) for leaf in V.LEAVES])),
               'trace': list(V.integration().expected_trace()),
               'writer_closed': True, 'client_closed': True,
               'parent_closed': True, 'child_exited_zero': True,
               'child_stderr': '', 'private_root_absent': True,
               'transport_private_path': str(root.parent / 'private'),
               'host_private_path': str(root.parent / 'host-private')}
    return temp, root, held, receipt


def materialize(root, documents, held):
    os.chmod(root, 0o700)
    os.chmod(root / 'artifacts', 0o700)
    raw = {}
    for leaf in V.LEAVES[:-1]:
        path = root / leaf
        if path.exists():
            os.chmod(path, 0o600)
        value = V.original_leaf_bytes(leaf, documents[leaf])
        path.write_bytes(value)
        os.chmod(path, 0o444)
        raw[leaf] = value
    rows = [V.binding(root, leaf, raw[leaf]) for leaf in V.LEAVES[:-1]]
    manifest = {'schema_version': 'lab-actual-context-delivery-package/v1-candidate',
                'files': sorted(rows, key=lambda r: r['path']),
                'source_manifest_binding': held['context_source_binding'],
                'authority_effect': 'none', 'actual_owner_outcome': None,
                'delivery_binding': rows[V.LEAVES.index('delivery.json')],
                'provenance_binding': rows[V.LEAVES.index('delivery-provenance.json')],
                'claim_ceiling': V.CLAIM}
    target = root / 'manifest.json'
    if target.exists():
        os.chmod(target, 0o600)
    target.write_bytes(V.original_leaf_bytes('manifest.json', manifest))
    os.chmod(target, 0o444)
    os.chmod(root / 'artifacts', 0o500)
    os.chmod(root, 0o500)


def rewrite(root, held, receipt, leaf, change):
    docs = {name: json.loads((root / name).read_bytes()) for name in V.LEAVES[:-1]}
    change(docs[leaf])
    materialize(root, docs, held)
    refresh_receipt(root, receipt)


def rewrite_carrier(root, held, receipt, number, change):
    docs = {name: json.loads((root / name).read_bytes()) for name in V.LEAVES[:-1]}
    leaf = f'artifacts/{number:02d}.json'
    change(docs[leaf])
    digest = V.sha(V.original_leaf_bytes(leaf, docs[leaf]))
    docs['artifact-index.json'][number]['artifact']['byte_sha256'] = digest
    docs['artifact-index.json'][number]['original_binding'] = V.binding(
        root, leaf, V.original_leaf_bytes(leaf, docs[leaf]))
    docs['delivery-provenance.json']['generated_artifact_refs'][number]['byte_sha256'] = digest
    materialize(root, docs, held)
    refresh_receipt(root, receipt)


def refresh_receipt(root, receipt):
    receipt['manifest_sha256'] = V.sha((root / 'manifest.json').read_bytes())
    receipt['output_bytes'] = sum((root / name).stat().st_size for name in V.LEAVES)
    receipt['inventory_sha256'] = V.sha(V.wire([
        V.binding(root, name, (root / name).read_bytes()) for name in V.LEAVES]))


class OutputTests(unittest.TestCase):
    def test_complete_synthetic_package(self):
        temp, root, held, receipt = fixture()
        with temp:
            result = V.check_synthetic(root, held, receipt)
            self.assertEqual(result['status'], 'SYNTHETIC_OUTPUT_CONTRACT_PASS_ONLY')
            self.assertEqual((result['leaves'], result['manifest_rows']), (40, 39))
            self.assertFalse(result['effect_enabled'])

    def test_missing_extra_symlink_and_wrong_mode_refuse(self):
        for fault in ('missing', 'extra', 'symlink', 'mode'):
            with self.subTest(fault=fault):
                temp, root, held, receipt = fixture()
                with temp:
                    os.chmod(root, 0o700)
                    p = root / 'request.json'
                    if fault == 'missing':
                        p.unlink()
                    elif fault == 'extra':
                        (root / 'extra.json').write_text('{}')
                    elif fault == 'symlink':
                        p.unlink(); p.symlink_to(root / 'delivery.json')
                    else:
                        os.chmod(p, 0o600)
                    os.chmod(root, 0o500)
                    with self.assertRaises((V.Refused, OSError)):
                        V.check_synthetic(root, held, receipt)

    def test_manifest_digest_and_result_cut_refuse(self):
        for leaf, change, code in (
            ('manifest.json', lambda d: d['files'].pop(), 'ORIGINAL_MANIFEST_JOIN'),
            ('build-result.json', lambda d: d.update(source_sha256='0'*64), 'RESULT_JOIN'),
            ('delivery-provenance.json', lambda d: d.update(native_cut_digest='0'*64),
             'DELIVERY_CUT_EXPIRY')):
            with self.subTest(leaf=leaf):
                temp, root, held, receipt = fixture()
                with temp:
                    if leaf == 'manifest.json':
                        p=root/leaf; os.chmod(p,0o600)
                        d=json.loads(p.read_bytes()); change(d); p.write_bytes(V.wire(d))
                        os.chmod(p,0o444)
                        receipt['manifest_sha256']=V.sha(p.read_bytes())
                        receipt['output_bytes']=sum((root/name).stat().st_size for name in V.LEAVES)
                        receipt['inventory_sha256']=V.sha(V.wire([
                            V.binding(root,name,(root/name).read_bytes()) for name in V.LEAVES]))
                    else:
                        rewrite(root,held,receipt,leaf,change)
                    with self.assertRaisesRegex(V.Refused, code):
                        V.check_synthetic(root,held,receipt)

    def test_expiry_authority_and_transport_refuse(self):
        for fault in ('expired', 'auth', 'trace', 'exit', 'private'):
            with self.subTest(fault=fault):
                temp, root, held, receipt = fixture()
                with temp:
                    if fault == 'expired':
                        held['observed_at'] = EXPIRY
                    elif fault == 'auth':
                        held['auth_validated'] = False
                    elif fault == 'trace':
                        receipt['trace'].remove('ack:41:FINISH')
                    elif fault == 'exit':
                        receipt['child_exited_zero'] = False
                    else:
                        receipt['private_root_absent'] = False
                    with self.assertRaises(V.Refused):
                        V.check_synthetic(root,held,receipt)

    def test_schema_and_carrier_count_refuse(self):
        temp, root, held, receipt = fixture()
        with temp:
            rewrite(root, held, receipt, 'artifacts/00.json',
                    lambda d: d.update(kind='ontology-edge'))
            with self.assertRaises(V.Refused):
                V.check_synthetic(root, held, receipt)

    def test_receipt_size_digest_and_private_root_refuse(self):
        for fault in ('size', 'inventory', 'host-root'):
            with self.subTest(fault=fault):
                temp, root, held, receipt = fixture()
                with temp:
                    if fault == 'size':
                        receipt['output_bytes'] -= 1
                    elif fault == 'inventory':
                        receipt['inventory_sha256'] = '0'*64
                    else:
                        (root.parent / 'host-private').mkdir()
                    with self.assertRaises(V.Refused):
                        V.check_synthetic(root, held, receipt)

    def test_selected_source_native_and_policy_joins_refuse(self):
        for fault in ('source-ref', 'native-cut', 'public-policy'):
            with self.subTest(fault=fault):
                temp, root, held, receipt = fixture()
                with temp:
                    if fault == 'source-ref':
                        held['selected_source_refs'][0]['byte_sha256'] = '0'*64
                    elif fault == 'native-cut':
                        held['native_cut_digest'] = '0'*64
                    else:
                        held['public_policy']['scope_ref'] = 'scope:foreign'
                    with self.assertRaises(V.Refused):
                        V.check_synthetic(root, held, receipt)

    def test_native_carrier_pair_permutation_refuses(self):
        temp, root, held, receipt = fixture()
        with temp:
            def swap(provenance):
                rows = provenance['correspondence']
                rows[0]['carrier_identity'], rows[1]['carrier_identity'] = (
                    rows[1]['carrier_identity'], rows[0]['carrier_identity'])
            rewrite(root, held, receipt, 'delivery-provenance.json', swap)
            with self.assertRaisesRegex(V.Refused, 'NATIVE_CORRESPONDENCE'):
                V.check_synthetic(root, held, receipt)

    def test_original_envelope_closure_refuses(self):
        probes = (
            ('request.json', 'schema_version', 'QUERY_ENVELOPE'),
            ('host-permission-public.json', 'reader_public_key', 'POLICY_ENVELOPE'),
            ('lesson-selection.json', 'selection_rule', 'LESSON_ENVELOPE'),
            ('delivery-provenance.json', 'assignment', 'PROVENANCE_ENVELOPE'))
        for leaf, field, code in probes:
            with self.subTest(leaf=leaf):
                temp, root, held, receipt = fixture()
                with temp:
                    rewrite(root, held, receipt, leaf, lambda d: d.pop(field))
                    with self.assertRaisesRegex(V.Refused, code):
                        V.check_synthetic(root, held, receipt)

    def test_node_and_edge_body_event_joins_refuse(self):
        for number in (0, 15):
            with self.subTest(number=number):
                temp, root, held, receipt = fixture()
                with temp:
                    if number == 0:
                        def change(body):
                            ref = body['payload']['governance_binding']
                            ref['semantic_event_ref'] = {
                                'semantic_event_id': 'event:foreign',
                                'semantic_event_digest': '9'*64,
                                'semantic_cursor': 999}
                            ref['governance_event_refs'] = ['governance:foreign']
                    else:
                        def change(body):
                            body['payload']['semantic_event_ref'] = {
                                'semantic_event_id': 'event:foreign',
                                'semantic_event_digest': '9'*64,
                                'semantic_cursor': 999}
                    rewrite_carrier(root, held, receipt, number, change)
                    with self.assertRaisesRegex(V.Refused, 'NATIVE_CARRIER_CONTENT_JOIN'):
                        V.check_synthetic(root, held, receipt)

    def test_forged_authority_envelope_digest_refuses(self):
        temp, root, held, receipt = fixture()
        with temp:
            held['authority_envelope_binding']['sha256'] = '0'*64
            rewrite(root, held, receipt, 'delivery-provenance.json',
                    lambda d: d['authority_envelope_binding'].update(sha256='0'*64))
            with self.assertRaisesRegex(V.Refused, 'PROVENANCE_ENVELOPE'):
                V.check_synthetic(root, held, receipt)

    def test_semantically_same_lesson_different_bytes_refuses(self):
        temp, root, held, receipt = fixture()
        with temp:
            path = root / 'lesson-selection.json'
            lesson = json.loads(path.read_bytes())
            os.chmod(path, 0o600)
            path.write_bytes((json.dumps(lesson, sort_keys=True, indent=2) + '\n').encode())
            os.chmod(path, 0o444)
            manifest_path = root / 'manifest.json'
            manifest = json.loads(manifest_path.read_bytes())
            row = next(row for row in manifest['files'] if row['path'] == str(path))
            row['sha256'] = V.sha(path.read_bytes())
            os.chmod(manifest_path, 0o600)
            manifest_path.write_bytes(V.wire(manifest))
            os.chmod(manifest_path, 0o444)
            refresh_receipt(root, receipt)
            with self.assertRaisesRegex(V.Refused, 'REQUEST_POLICY_LESSON_JOIN'):
                V.check_synthetic(root, held, receipt)

    def test_rebound_reformatted_lesson_still_refuses_original_encoding(self):
        temp, root, held, receipt = fixture()
        with temp:
            lesson_path = root / 'lesson-selection.json'
            lesson = json.loads(lesson_path.read_bytes())
            os.chmod(lesson_path, 0o600)
            lesson_path.write_bytes((json.dumps(lesson, sort_keys=True, indent=2) + '\n').encode())
            os.chmod(lesson_path, 0o444)
            delivery_path = root / 'delivery.json'
            delivery = json.loads(delivery_path.read_bytes())
            delivery['lesson_selection_binding']['sha256'] = V.sha(lesson_path.read_bytes())
            os.chmod(delivery_path, 0o600)
            delivery_path.write_bytes(V.original_leaf_bytes('delivery.json', delivery))
            os.chmod(delivery_path, 0o444)
            provenance_path = root / 'delivery-provenance.json'
            provenance = json.loads(provenance_path.read_bytes())
            provenance['verified_original_binding'] = V.binding(
                root, 'delivery.json', delivery_path.read_bytes())
            os.chmod(provenance_path, 0o600)
            provenance_path.write_bytes(V.original_leaf_bytes('delivery-provenance.json',
                                                             provenance))
            os.chmod(provenance_path, 0o444)
            manifest_path = root / 'manifest.json'
            manifest = json.loads(manifest_path.read_bytes())
            for row in manifest['files']:
                if row['path'] in (str(lesson_path), str(delivery_path), str(provenance_path)):
                    row['sha256'] = V.sha(Path(row['path']).read_bytes())
            manifest['delivery_binding'] = V.binding(root, 'delivery.json',
                                                     delivery_path.read_bytes())
            manifest['provenance_binding'] = V.binding(root, 'delivery-provenance.json',
                                                       provenance_path.read_bytes())
            os.chmod(manifest_path, 0o600)
            manifest_path.write_bytes(V.original_leaf_bytes('manifest.json', manifest))
            os.chmod(manifest_path, 0o444)
            refresh_receipt(root, receipt)
            with self.assertRaisesRegex(V.Refused, 'ORIGINAL_EMIT_ENCODING'):
                V.check_synthetic(root, held, receipt)

    def test_delivery_expired_with_authority_still_current(self):
        temp, root, held, receipt = fixture()
        with temp:
            held['observed_at'] = '2026-10-20T12:11:00Z'
            held['policy_end'] = '2026-10-20T12:15:00Z'
            held['public_policy']['expires_at'] = held['policy_end']
            held['authority_envelope_binding']['sha256'] = V.sha(V.original_leaf_bytes(
                'host-permission-public.json', held['public_policy']))
            docs = {name: json.loads((root / name).read_bytes()) for name in V.LEAVES[:-1]}
            docs['host-permission-public.json'] = held['public_policy']
            docs['request.json']['budget']['deadline'] = '2026-10-20T12:12:00Z'
            docs['delivery.json']['request_binding']['sha256'] = V.sha(V.wire(docs['request.json']))
            docs['delivery-provenance.json']['authority_envelope_binding'] = held['authority_envelope_binding']
            docs['delivery-provenance.json']['verified_original_binding'] = V.binding(
                root, 'delivery.json', V.original_leaf_bytes('delivery.json', docs['delivery.json']))
            materialize(root, docs, held)
            refresh_receipt(root, receipt)
            with self.assertRaisesRegex(V.Refused, 'DELIVERY_CUT_EXPIRY'):
                V.check_synthetic(root, held, receipt)

    def test_real_launch_refused(self):
        with self.assertRaisesRegex(V.Refused, 'effect disabled'):
            V.launch()


if __name__ == '__main__':
    unittest.main()
