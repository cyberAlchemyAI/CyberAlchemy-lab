"""Owned technical custody fixtures; never genuine owner/source approval."""
import base64
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import time
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
RUN = ROOT/'docs/plans/0011-lab-runtime-completion/runs/0001-execution/T08'
name = '_cal_completion_protected_inputs'
spec = importlib.util.spec_from_file_location(name, HERE/'__init__.py',
                                            submodule_search_locations=[str(HERE)])
component = importlib.util.module_from_spec(spec); sys.modules[name] = component
spec.loader.exec_module(component)
P = sys.modules[name+'.protected_inputs']; G = sys.modules[name+'.semantic_graph']

def save(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    path.write_bytes(raw); path.chmod(0o600)

def locator(path, root_id='scratch'):
    info = path.stat()
    return dict(root_id=root_id, path=path.name, size=info.st_size, **P.metadata(info))

class Fixture:
    def __init__(self, parent):
        self.root = parent; self.payloads = {}; self.kinds = {}; self.tables = []
        self.private = Ed25519PrivateKey.generate()  # Own ephemeral technical key only.
        self.public = base64.b64encode(self.private.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw)).decode()
        self.principal = 'technical-principal:T08-owned-custody'
        source_raw = P.canonical({'schema_version': 'technical-source-table/v1', 'files': []})
        profile_raw = P.canonical({'schema_version': 'technical-profile-table/v1', 'files': []})
        self.add('source', 'source-manifest', source_raw)
        self.add('profile', 'contract-profile', profile_raw)
        self.source = {'ref': 'technical:owned/source', 'sha256': P.digest(source_raw)}
        self.profile = {'ref': 'technical:owned/profile', 'sha256': P.digest(profile_raw)}
        self.cut = {'branch_ref': 'technical:branch', 'store_ref': 'technical:owned-store',
            'commit_sequence': 1, 'commit_sha256': P.digest(b'technical-own-cut'),
            'source_profile_sha256': P.digest(profile_raw), 'streams': []}
        self.add('state', 'custody-state', P.canonical({
            'schema_version': 'lab-protected-input-custody-state/v1-candidate',
            'principal_ref': self.principal, 'revoked': False, 'authority_effect': 'none'}))

    def add(self, identity, kind, raw):
        self.payloads[identity] = raw; self.kinds[identity] = kind
        save(self.root/identity, raw)

    def reader(self, seconds=300, selector_edit=None, signer=None):
        rows = []
        for identity in sorted(self.payloads):
            path = self.root/identity; info = path.stat()
            rows.append(dict(id=identity, root_id='scratch', path=identity,
                logical_path='technical:owned/'+identity, kind=self.kinds[identity],
                sha256=P.digest(path.read_bytes()), size=info.st_size, **P.metadata(info)))
        selector = {'schema_version': 'lab-protected-input-selector/v1-candidate',
            'source_binding': self.source, 'profile_binding': self.profile,
            'source_cut': self.cut, 'principal_ref': self.principal,
            'operation': 'release.prepare',
            'roots': [dict(id='scratch', path=str(self.root), **P.metadata(self.root.stat()))],
            'files': rows, 'proof_tables': self.tables + [
                {'file_id': 'source', 'row_selector': '/files', 'coverage_file_ids': []},
                {'file_id': 'profile', 'row_selector': '/files', 'coverage_file_ids': []}],
            'custody_state_file_id': 'state',
            'authority_effect': 'none'}
        if selector_edit: selector_edit(selector)
        raw = P.canonical(selector); save(self.root/'selector-control', raw)
        selected = {'ref': 'technical:owned/selector-control', 'sha256': P.digest(raw)}
        clock = datetime.now(timezone.utc)
        payload = {'schema_version': 'lab-protected-input-custody-grant/v1-candidate',
            'selector_binding': selected, 'source_binding': self.source,
            'profile_binding': self.profile, 'source_cut': self.cut,
            'principal_ref': self.principal, 'operation': 'release.prepare',
            'not_before': (clock-timedelta(seconds=1)).isoformat(),
            'expires_at': (clock+timedelta(seconds=seconds)).isoformat(), 'authority_effect': 'none'}
        grant = P.canonical({'payload': payload, 'signature_b64': base64.b64encode(
            (signer or self.private).sign(P.canonical(payload))).decode()})
        save(self.root/'grant-control', grant)
        anchor = P.CustodyAnchor(self.principal, self.public, self.source, self.profile,
            self.cut, 'release.prepare', selected,
            {'ref': 'technical:owned/grant-control', 'sha256': P.digest(grant)},
            locator(self.root/'selector-control'), locator(self.root/'grant-control'))
        return P.ProtectedReader(raw, grant, anchor)

    def graph(self, cycle=False, omitted_field=False):
        for identity, relative, kind in (
            ('schema', 'authority/artifact-types/governed-model/v1/schema.json', 'governed-schema'),
            ('descriptor', 'authority/artifact-types/governed-model/v1/artifact.json', 'governed-descriptor')):
            self.add(identity, kind, (ROOT/relative).read_bytes())
        for identity, other, direction in [('A', 'B', 'source'), ('B', 'A', 'source' if cycle else 'target')]:
            value = {'schema_version': 'cyberalchemy-lab-governed-model/v1',
                'node_id': identity, 'kind': 'governed-model', 'name': 'Owned technical '+identity,
                'lifecycle_state': 'candidate', 'authority_effect': 'none',
                'owner_ref': 'role:technical-fixture-only', 'scope_ref': 'scope:T08-owned',
                'evidence_refs': [], 'challenge_route': 'technical:challenge', 'successor_refs': [],
                'relation_refs': [{'relation_kind_ref': 'relation.successor-of',
                    'direction': direction, 'counterpart_kind': 'governed-model',
                    'counterpart_ref': other}],
                'payload': {'model_kind': 'technical-fixture', 'contract_ref': 'proof:schema',
                    'version_ref': identity+'@technical.1', 'rule_refs': ['proof:schema'],
                    'extension_policy_ref': 'proof:descriptor'},
                'claim_ceiling': 'Original schema/role validation of technical graph; no actual owner or admission.'}
            self.add(identity, 'governed-record', P.canonical(value))
        fields = []
        mapping = {'/owner_ref': 'current-context', '/scope_ref': 'current-context',
            '/evidence_refs': 'verified-proof', '/successor_refs': 'semantic-node',
            '/payload/contract_ref': 'verified-proof', '/payload/version_ref': 'self-identity',
            '/payload/rule_refs': 'verified-proof', '/payload/extension_policy_ref': 'verified-proof'}
        for pointer, disposition in mapping.items():
            fields.append({'instance_pointer': pointer,
                'schema_pointer': G.expected_schema_pointer(pointer), 'disposition': disposition})
        if omitted_field: fields.pop()
        policy = {'schema_version': 'lab-schema-declared-semantic-graph/v1-candidate',
            'profiles': [{'kind': 'governed-model', 'schema_file_id': 'schema',
                          'descriptor_file_id': 'descriptor', 'fields': fields}],
            'node_file_ids': ['A', 'B'], 'proof_references': [
                {'reference': 'proof:schema', 'file_id': 'schema'},
                {'reference': 'proof:descriptor', 'file_id': 'descriptor'}],
            'context_references': ['role:technical-fixture-only', 'scope:T08-owned'],
            'authority_effect': 'none'}
        self.add('policy', 'semantic-policy', P.canonical(policy))
        return self.reader()

class ReaderCases(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='owned-reader-', dir=RUN)
        self.root = Path(self.temp.name); self.fixture = Fixture(self.root)
        self.fixture.add('body', 'host-dependency', b'exact owned technical host bytes')
    def tearDown(self): self.temp.cleanup()
    def test_signed_positive_and_fresh_full_pre_post_boundary(self):
        reader = self.fixture.reader()
        with reader.boundary(): self.assertEqual(reader.read('body', 'host-dependency'), self.fixture.payloads['body'])
        self.assertFalse(reader.verify()['public_export_allowed'])
    def test_closed_published_selector_and_grant_schema_contracts(self):
        from jsonschema import Draft202012Validator, FormatChecker
        reader = self.fixture.reader()
        for file, value in [('protected-selector.schema.json', reader.selector),
                            ('custody-grant.schema.json', reader.grant)]:
            schema = json.loads((HERE/file).read_text())
            Draft202012Validator.check_schema(schema)
            Draft202012Validator(schema, format_checker=FormatChecker()).validate(value)
            wrong = dict(value, extra=True)
            self.assertFalse(Draft202012Validator(schema).is_valid(wrong))
    def test_other_key_signature_cannot_create_custody(self):
        with self.assertRaisesRegex(P.Refusal, 'signature'):
            self.fixture.reader(signer=Ed25519PrivateKey.generate())
    def test_equal_size_tamper_refused(self):
        reader = self.fixture.reader(); path = self.root/'body'; raw = path.read_bytes()
        save(path, raw[:-1]+b'X')
        with self.assertRaisesRegex(P.Refusal, 'bytes'): reader.verify()
    def test_mode_refused(self):
        reader = self.fixture.reader(); (self.root/'body').chmod(0o644)
        with self.assertRaisesRegex(P.Refusal, 'mode'): reader.verify()
    def test_same_bytes_new_inode_refused(self):
        reader = self.fixture.reader(); body = self.root/'body'
        save(self.root/'replacement', body.read_bytes()); os.replace(self.root/'replacement', body)
        with self.assertRaisesRegex(P.Refusal, 'identity'): reader.verify()
    def test_symlink_refused(self):
        reader = self.fixture.reader(); (self.root/'body').unlink()
        (self.root/'body').symlink_to(self.root/'state')
        with self.assertRaisesRegex(P.Refusal, 'no-follow'): reader.verify()
    def test_current_custody_revocation_and_control_tamper_refused(self):
        reader = self.fixture.reader()
        save(self.root/'grant-control', b'{}')
        with self.assertRaises(P.Refusal): reader.read('body')
        reader = self.fixture.reader()
        state = P.parse((self.root/'state').read_bytes()); state['revoked'] = True
        save(self.root/'state', P.canonical(state))
        with self.assertRaises(P.Refusal): reader.read('body')
    def test_real_expiry_between_entry_and_exit(self):
        reader = self.fixture.reader(seconds=1)
        with self.assertRaisesRegex(P.Refusal, 'expired'):
            with reader.boundary(): time.sleep(1.1)
    def test_unknown_kind_duplicate_and_parent_escape_refused(self):
        for edit in (lambda s: s['files'][0].update(kind='unrestricted-private-key'),
                     lambda s: s['files'].append(s['files'][0].copy()),
                     lambda s: s['files'][0].update(path='../outside')):
            with self.assertRaises(P.Refusal): self.fixture.reader(selector_edit=edit)
    def test_runtime_selector_and_index_mutation_refused(self):
        reader = self.fixture.reader(); reader.files.pop('body')
        with self.assertRaisesRegex(P.Refusal, 'indices'): reader.verify()
    def test_missing_original_proof_row_refused(self):
        value = {'files': [{'path': 'technical:owned/body', 'sha256': P.digest(self.fixture.payloads['body'])}]}
        self.fixture.add('table', 'source-manifest', P.canonical(value))
        self.fixture.tables = [{'file_id': 'table', 'row_selector': '/files', 'coverage_file_ids': ['body']}]
        self.assertEqual(self.fixture.reader().verify()['proof_rows'], 1)
        self.fixture.add('table', 'source-manifest', P.canonical({'files': []}))
        with self.assertRaisesRegex(P.Refusal, 'omitted'): self.fixture.reader().verify()
    def test_mandatory_source_profile_coverage_cannot_be_removed(self):
        def edit(selector):
            selector['proof_tables'] = [t for t in selector['proof_tables'] if t['file_id'] != 'source']
        with self.assertRaisesRegex(P.Refusal, 'mandatory complete'):
            self.fixture.reader(selector_edit=edit)
    def test_three_actual_composite_environment_tables_verified(self):
        row = {'path': 'technical:owned/body', 'sha256': P.digest(self.fixture.payloads['body'])}
        document = {'schema_version': 'technical-composite-environment/v1',
            'complete_source_bindings': [row], 'complete_profile_bindings': [row],
            'schema_execution_bindings': [row]}
        self.fixture.add('environment', 'environment-contract', P.canonical(document))
        self.fixture.tables = [{'file_id': 'environment', 'row_selector': key,
                               'coverage_file_ids': ['body']} for key in
            ('/complete_source_bindings', '/complete_profile_bindings', '/schema_execution_bindings')]
        self.assertEqual(self.fixture.reader().verify()['proof_rows'], 3)
        self.fixture.tables.pop()
        with self.assertRaisesRegex(P.Refusal, 'complete composite'):
            self.fixture.reader()
    def test_full_size_closed_24497_row_technical_table(self):
        ids = []; rows = []
        for i in range(24497):
            identity = 'row-'+str(i).zfill(5); raw = ('technical-proof-row:'+str(i)).encode()
            self.fixture.add(identity, 'history-proof', raw); ids.append(identity)
            rows.append({'path': 'technical:owned/'+identity, 'sha256': P.digest(raw)})
        value = {'schema_version': 'technical-full-size-proof-table/v1', 'files': rows,
            'size_padding_reason': 'Technical size stress only; no historical source claim.',
            'opaque_history_cycle_annotations': [{'source': 'technical:A', 'dependency': 'technical:B'},
                                                {'source': 'technical:B', 'dependency': 'technical:A'}],
            'technical_padding': 'x'*(27*1024*1024)}
        raw = P.canonical(value); self.fixture.add('table', 'source-manifest', raw)
        self.fixture.tables = [{'file_id': 'table', 'row_selector': '/files', 'coverage_file_ids': ids}]
        reader = self.fixture.reader()
        with reader.boundary():
            observed = reader.verify()
            self.assertEqual(observed['proof_rows'], 24497)
            self.assertGreater(len(reader.read('table')), 27*1024*1024)
        self.assertEqual((self.root/'table').read_bytes(), raw)

class GraphCases(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='owned-graph-', dir=RUN)
        self.fixture = Fixture(Path(self.temp.name))
    def tearDown(self): self.temp.cleanup()
    def test_actual_original_schema_and_roles_acyclic_graph(self):
        reader = self.fixture.graph()
        result = G.verify_graph(reader, 'policy', [{'source': 'A', 'dependency': 'B'}], ['A'])
        self.assertEqual((result['nodes'], result['edges']), (2, 1))
        self.assertFalse(result['admission_or_owner_authority'])
        from jsonschema import Draft202012Validator
        Draft202012Validator(json.loads((HERE/'semantic-policy.schema.json').read_text())).validate(
            P.parse(self.fixture.payloads['policy']))
    def test_actual_semantic_cycle_refused(self):
        reader = self.fixture.graph(cycle=True)
        with self.assertRaisesRegex(P.Refusal, 'cycle'):
            G.verify_graph(reader, 'policy', [{'source': 'A', 'dependency': 'B'},
                {'source': 'B', 'dependency': 'A'}], ['A'])
    def test_omitted_edge_and_duplicate_edge_refused(self):
        reader = self.fixture.graph()
        for edges in ([], [{'source': 'A', 'dependency': 'B'}]*2):
            with self.assertRaisesRegex(P.Refusal, 'edges'):
                G.verify_graph(reader, 'policy', edges, ['A'])
    def test_missing_schema_reference_classification_refused(self):
        reader = self.fixture.graph(omitted_field=True)
        with self.assertRaisesRegex(P.Refusal, 'slot omitted'):
            G.verify_graph(reader, 'policy', [{'source': 'A', 'dependency': 'B'}], ['A'])
    def test_proof_kind_spoof_cannot_be_graph_node(self):
        self.fixture.graph(); self.fixture.kinds['A'] = 'history-proof'
        reader = self.fixture.reader()
        with self.assertRaisesRegex(P.Refusal, 'kind spoofed'):
            G.verify_graph(reader, 'policy', [{'source': 'A', 'dependency': 'B'}], ['A'])
    def test_duplicate_semantic_identity_refused(self):
        self.fixture.graph(); value = P.parse(self.fixture.payloads['B']); value['node_id'] = 'A'
        self.fixture.add('B', 'governed-record', P.canonical(value)); reader = self.fixture.reader()
        with self.assertRaisesRegex(P.Refusal, 'duplicate semantic'):
            G.verify_graph(reader, 'policy', [], ['A'])
    def test_missing_pinned_proof_reference_refused(self):
        self.fixture.graph(); value = P.parse(self.fixture.payloads['policy'])
        value['proof_references'].pop()
        self.fixture.add('policy', 'semantic-policy', P.canonical(value)); reader = self.fixture.reader()
        with self.assertRaisesRegex(P.Refusal, 'proof reference omitted'):
            G.verify_graph(reader, 'policy', [{'source': 'A', 'dependency': 'B'}], ['A'])
    def test_undeclared_direction_and_real_schema_refused(self):
        self.fixture.graph(); value = P.parse(self.fixture.payloads['A'])
        value['relation_refs'][0]['counterpart_kind'] = 'implementation'
        self.fixture.add('A', 'governed-record', P.canonical(value)); reader = self.fixture.reader()
        with self.assertRaisesRegex(P.Refusal, 'declared pair'):
            G.verify_graph(reader, 'policy', [{'source': 'A', 'dependency': 'B'}], ['A'])
        value['relation_refs'] = []
        self.fixture.add('A', 'governed-record', P.canonical(value)); reader = self.fixture.reader()
        with self.assertRaisesRegex(P.Refusal, 'original record schema'):
            G.verify_graph(reader, 'policy', [], ['A'])

if __name__ == '__main__': unittest.main(verbosity=2)
