"""Synthetic pure closure fixtures. No authenticated host or admission evidence."""
import base64
import copy
from dataclasses import replace
import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('_cal_package_transfer_pure', HERE / 'transfer.py')
T = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = T
spec.loader.exec_module(T)


class Packages(unittest.TestCase):
    def setUp(self):
        self.engine = T.Transfer(json.loads((HERE / 'source-manifest.json').read_bytes())['source_sha256'])
        self.actor = {'principal_ref': 'principal:synthetic-transfer', 'role_assignment_refs': [],
                      'agent_instance_ref': None, 'session_ref': None, 'assignment_ref': None}
        self.cut = {'store_ref': 'store:synthetic-source', 'branch_ref': 'branch:synthetic-source',
                    'commit_sequence': 1, 'commit_sha256': 'a' * 64, 'source_profile_sha256': 'b' * 64, 'streams': []}
        self.target_cut = {**self.cut, 'store_ref': 'store:synthetic-target', 'branch_ref': 'branch:synthetic-target'}
        self.original = b'{ "node_id": "hypothesis:one", "kind": "hypothesis", "payload": {"synthetic": true} }\n'
        self.header = {'scope_ref': 'project:synthetic', 'identity_ref': 'hypothesis:one',
                       'version_ref': 'hypothesis:one@1', 'carrier_ref': 'cal.artifact-type.hypothesis/v1',
                       'byte_sha256': T.sha(self.original)}
        self.root_binding = T.pin('source:one', self.original)
        self.dependency = b'{"synthetic_dependency":true}'
        self.dependency_binding = T.pin('dependency:one', self.dependency)
        self.materials = (
            T.Material(T.encoded(self.root_binding), self.original, T.encoded([self.dependency_binding]), T.encoded(self.header)),
            T.Material(T.encoded(self.dependency_binding), self.dependency, T.encoded([])))
        self.contract = {'schema_version': 'lab-package-export-contract/v1-candidate', 'source_cut': self.cut,
            'artifact_refs': [self.header], 'dependency_bindings': [self.dependency_binding], 'source_admission_basis': [],
            'source_posture': 'controlled-candidate', 'maximum_package_bytes': T.MAX_BYTES,
            'authority_effect': 'none', 'actual_owner_outcome': None}
        self.sync_export_controls()

    def sync_export_controls(self):
        self.contract_raw = T.encoded(self.contract)
        self.contract_binding = T.pin('contract:synthetic', self.contract_raw)
        bindings = sorted((T.parse(m.binding_json) for m in self.materials), key=lambda row: row['ref'])
        self.review = {'schema_version': 'lab-package-privacy-review/v2-candidate', 'source_cut': self.cut,
            'export_contract_binding': self.contract_binding, 'materials': bindings,
            'material_encodings': [{'binding': T.parse(m.binding_json), 'encoding': m.encoding} for m in sorted(self.materials, key=lambda m: T.parse(m.binding_json)['ref'])],
            'include_session_memory': False, 'include_private_credentials': False,
            'authority_effect': 'none', 'actual_owner_outcome': None}
        self.sync_review()

    def sync_review(self):
        self.review_raw = T.encoded(self.review)
        self.review_binding = T.pin('privacy:synthetic', self.review_raw)
        self.facts = T.ExportFacts(T.encoded(self.actor), T.encoded(self.cut), T.encoded(self.contract_binding),
                                  T.encoded(self.review_binding), self.materials)
        self.request = {'schema_version': 'lab-package-export-request/v1-candidate', 'request_ref': 'export:synthetic',
            'actor': self.actor, 'source_cut': self.cut, 'artifact_refs': self.contract['artifact_refs'],
            'dependency_bindings': self.contract['dependency_bindings'], 'export_contract_binding': self.contract_binding,
            'privacy_review_binding': self.review_binding, 'include_session_memory': False,
            'include_private_credentials': False, 'authority_effect': 'none'}

    def export(self):
        return self.engine.export(T.encoded(self.request), self.facts, self.contract_raw, self.review_raw)

    def refuse_export(self):
        with self.assertRaises(Exception):
            self.export()

    def import_setup(self, disposition='import-exact'):
        self.package_raw = self.export()
        self.package_binding = T.pin('package:synthetic', self.package_raw)
        target_bytes = self.original if disposition == 'import-exact' else T.encoded({
            'node_id': 'hypothesis:one', 'kind': 'hypothesis', 'payload': {'synthetic': True, 'adapted': True}})
        target = {**self.header, 'byte_sha256': T.sha(target_bytes),
                  'candidate_contract_binding': T.pin('contract:synthetic-candidate', b'{"synthetic":true}')}
        self.mapping = {'schema_version': 'lab-package-import-mapping/v1-candidate',
            'source_package_binding': self.package_binding, 'target_base_cut': self.target_cut,
            'items': [{'source': self.header, 'target': target,
                       'target_bytes_b64': base64.b64encode(target_bytes).decode()}],
            'authority_effect': 'none', 'actual_owner_outcome': None}
        self.dispositions = {'schema_version': 'lab-package-import-disposition/v1-candidate',
            'source_package_binding': self.package_binding, 'target_base_cut': self.target_cut,
            'items': [{'source': self.header, 'disposition': disposition, 'reason': 'Synthetic unit fixture only.'}],
            'authority_effect': 'none', 'actual_owner_outcome': None}
        self.workspace = T.pin('workspace:synthetic', b'{"synthetic":true}')
        self.sync_import()

    def sync_import(self):
        self.mapping_raw, self.disposition_raw = T.encoded(self.mapping), T.encoded(self.dispositions)
        mapping_binding = T.pin('mapping:synthetic', self.mapping_raw)
        disposition_binding = T.pin('disposition:synthetic', self.disposition_raw)
        self.import_facts = T.ImportFacts(T.encoded(self.actor), T.encoded(self.target_cut), T.encoded(self.package_binding),
            T.encoded(mapping_binding), T.encoded(disposition_binding), T.encoded(self.workspace), 'project:synthetic', ())
        self.import_request = {'schema_version': 'lab-package-import-request/v1-candidate', 'request_ref': 'import:synthetic',
            'actor': self.actor, 'source_package_binding': self.package_binding, 'source_admission_basis': [],
            'target_base_cut': self.target_cut, 'mapping_binding': mapping_binding, 'disposition_binding': disposition_binding,
            'candidate_workspace_binding': self.workspace, 'automatic_admission': False, 'authority_effect': 'none'}

    def account(self):
        return self.engine.account_import(T.encoded(self.import_request), self.import_facts,
            self.package_raw, self.mapping_raw, self.disposition_raw)

    def refuse_import(self):
        with self.assertRaises(Exception):
            self.account()

    def verify_changed_archive(self, edit):
        value = T.parse(self.export())
        edit(value)
        raw = T.encoded(value)
        with self.assertRaises(Exception):
            self.engine.verify_archive(raw, T.pin('package:changed-synthetic', raw))

    def test_export_preserves_whitespace_and_original_bytes(self):
        package = T.parse(self.export())
        row = next(row for row in package['materials'] if row['artifact'])
        self.assertEqual(base64.b64decode(row['original_bytes_b64']), self.original)
        self.assertFalse(package['target_admission_granted'])

    def test_deterministic_order(self):
        original = self.export()
        self.facts = replace(self.facts, materials=tuple(reversed(self.materials)))
        self.assertEqual(original, self.export())

    def test_cycles_are_complete_finite_closure(self):
        self.materials = (self.materials[0], replace(self.materials[1], dependencies_json=T.encoded([self.root_binding])))
        self.sync_export_controls()
        self.assertEqual(len(T.parse(self.export())['materials']), 2)

    def test_missing_request_dependency_refused(self):
        self.request['dependency_bindings'] = []
        self.refuse_export()

    def test_dependency_hash_conflict_refused(self):
        altered = {**self.dependency_binding, 'sha256': 'f' * 64}
        self.facts = replace(self.facts, materials=(replace(self.materials[0], dependencies_json=T.encoded([altered])), self.materials[1]))
        self.refuse_export()

    def test_missing_dependency_material_refused(self):
        self.facts = replace(self.facts, materials=(self.materials[0],))
        self.refuse_export()

    def test_unreachable_extra_material_refused(self):
        extra = T.Material(T.encoded(T.pin('extra:synthetic', b'{}')), b'{}', b'[]')
        self.materials += (extra,)
        self.sync_export_controls()
        self.refuse_export()

    def test_duplicate_material_reference_refused(self):
        self.facts = replace(self.facts, materials=self.materials + (self.materials[0],))
        self.refuse_export()

    def test_duplicate_artifact_identity_revision_refused(self):
        extra = replace(self.materials[0], binding_json=T.encoded(T.pin('source:duplicate', self.original)))
        self.facts = replace(self.facts, materials=self.materials + (extra,))
        self.refuse_export()

    def test_unknown_root_refused(self):
        self.request['artifact_refs'] = [{**self.header, 'identity_ref': 'hypothesis:missing'}]
        self.refuse_export()

    def test_duplicate_root_refused(self):
        self.contract['artifact_refs'] = [self.header, self.header]
        self.sync_export_controls()
        self.request['artifact_refs'] = self.contract['artifact_refs']
        self.refuse_export()

    def test_original_byte_drift_refused(self):
        self.facts = replace(self.facts, materials=(replace(self.materials[0], original=b'{}'), self.materials[1]))
        self.refuse_export()

    def test_partial_privacy_review_refused(self):
        self.review['materials'] = [self.root_binding]
        self.sync_review()
        self.refuse_export()

    def test_private_json_material_refused(self):
        raw = b'{"short_memory":"private synthetic sentinel"}'
        item = T.Material(T.encoded(T.pin('private:synthetic', raw)), raw, b'[]')
        with self.assertRaisesRegex(ValueError, 'Session memory'):
            self.engine.graph((item,))

    def test_private_key_string_refused(self):
        raw = b'{"document":"-----BEGIN PRIVATE KEY-----"}'
        item = T.Material(T.encoded(T.pin('private:synthetic', raw)), raw, b'[]')
        with self.assertRaisesRegex(ValueError, 'private key'):
            self.engine.graph((item,))

    def test_encoded_package_budget_refused(self):
        self.contract['maximum_package_bytes'] = 1
        self.sync_export_controls()
        self.refuse_export()

    def test_actor_spoof_refused(self):
        self.request['actor'] = {**self.actor, 'principal_ref': 'principal:spoof'}
        self.refuse_export()

    def test_source_cut_drift_refused(self):
        self.request['source_cut'] = {**self.cut, 'commit_sequence': 2}
        self.refuse_export()

    def test_control_not_independently_selected_refused(self):
        self.request['export_contract_binding'] = {**self.contract_binding, 'ref': 'contract:caller-selected'}
        self.refuse_export()

    def test_admitted_source_without_basis_refused(self):
        self.contract['source_posture'] = 'admitted-source'
        self.sync_export_controls()
        self.refuse_export()

    def test_complete_basis_bytes_retained_without_target_authority(self):
        self.contract['source_admission_basis'] = [self.dependency_binding]
        self.contract['source_posture'] = 'admitted-source'
        self.sync_export_controls()
        package = T.parse(self.export())
        self.assertEqual(package['source_admission_basis'], [self.dependency_binding])
        self.assertFalse(package['target_admission_granted'])

    def test_archive_metadata_tamper_refused(self):
        self.verify_changed_archive(lambda value: value.update(source_posture='admitted-source'))

    def test_archive_original_tamper_refused(self):
        self.verify_changed_archive(lambda value: value['materials'][0].update(original_bytes_b64=base64.b64encode(b'{}').decode()))

    def test_archive_control_tamper_refused(self):
        self.verify_changed_archive(lambda value: value.update(export_contract_bytes_b64=base64.b64encode(b'{}').decode()))

    def test_archive_unknown_field_refused(self):
        self.verify_changed_archive(lambda value: value.update(automatic_admission=True))

    def test_import_exact_preserves_original_and_retains_dependencies(self):
        self.import_setup()
        plan = self.account()
        self.assertEqual(base64.b64decode(plan['items'][0]['target_bytes_b64']), self.original)
        self.assertEqual(plan['accounted_source_materials'], 2)
        self.assertEqual(plan['retained_dependency_bindings'], [self.dependency_binding])
        self.assertFalse(plan['automatic_admission'])
        self.assertTrue(plan['target_model_validation_pending'])

    def test_explicit_adaptation_preserves_source_provenance(self):
        self.import_setup('adapt')
        plan = self.account()
        self.assertEqual(plan['items'][0]['source_binding'], self.root_binding)
        self.assertNotEqual(base64.b64decode(plan['items'][0]['target_bytes_b64']), self.original)

    def test_missing_source_accounting_refused(self):
        self.import_setup()
        self.mapping['items'] = []
        self.sync_import()
        self.refuse_import()

    def test_duplicate_source_accounting_refused(self):
        self.import_setup()
        self.mapping['items'] *= 2
        self.dispositions['items'] *= 2
        self.sync_import()
        self.refuse_import()

    def test_unknown_source_accounting_refused(self):
        self.import_setup()
        self.mapping['items'][0]['source'] = {**self.header, 'identity_ref': 'hypothesis:unknown'}
        self.sync_import()
        self.refuse_import()

    def test_existing_target_collision_refused(self):
        self.import_setup()
        self.import_facts = replace(self.import_facts, existing_identity_refs=('hypothesis:one',))
        self.refuse_import()

    def test_target_scope_spoof_refused(self):
        self.import_setup()
        self.mapping['items'][0]['target']['scope_ref'] = 'project:foreign'
        self.sync_import()
        self.refuse_import()

    def test_target_byte_hash_spoof_refused(self):
        self.import_setup()
        self.mapping['items'][0]['target']['byte_sha256'] = 'f' * 64
        self.sync_import()
        self.refuse_import()

    def test_exact_disposition_for_changed_bytes_refused(self):
        self.import_setup('adapt')
        self.dispositions['items'][0]['disposition'] = 'import-exact'
        self.sync_import()
        self.refuse_import()

    def test_adaptation_disposition_for_unchanged_bytes_refused(self):
        self.import_setup()
        self.dispositions['items'][0]['disposition'] = 'adapt'
        self.sync_import()
        self.refuse_import()

    def test_excluded_source_cannot_hide_target(self):
        self.import_setup()
        self.dispositions['items'][0]['disposition'] = 'exclude'
        self.sync_import()
        self.refuse_import()

    def test_empty_target_plan_refused(self):
        self.import_setup()
        self.dispositions['items'][0]['disposition'] = 'retain-source'
        self.mapping['items'][0].update(target=None, target_bytes_b64=None)
        self.sync_import()
        self.refuse_import()

    def test_import_actor_spoof_refused(self):
        self.import_setup()
        self.import_request['actor'] = {**self.actor, 'principal_ref': 'principal:spoof'}
        self.refuse_import()

    def test_import_target_cut_drift_refused(self):
        self.import_setup()
        self.import_request['target_base_cut'] = {**self.target_cut, 'commit_sequence': 2}
        self.refuse_import()

    def test_import_source_proof_spoof_refused(self):
        self.import_setup()
        self.import_request['source_admission_basis'] = [self.dependency_binding]
        self.refuse_import()

    def test_import_workspace_spoof_refused(self):
        self.import_setup()
        self.import_request['candidate_workspace_binding'] = {**self.workspace, 'ref': 'workspace:foreign'}
        self.refuse_import()

    def test_import_control_original_hash_drift_refused(self):
        self.import_setup()
        self.mapping_raw += b' '
        self.refuse_import()

    def test_import_private_target_refused(self):
        self.import_setup('adapt')
        raw = T.encoded({'node_id': 'hypothesis:one', 'short_memory': 'private synthetic sentinel'})
        self.mapping['items'][0]['target']['byte_sha256'] = T.sha(raw)
        self.mapping['items'][0]['target_bytes_b64'] = base64.b64encode(raw).decode()
        self.sync_import()
        self.refuse_import()

    def test_import_target_identity_spoof_refused(self):
        self.import_setup()
        self.mapping['items'][0]['target']['identity_ref'] = 'hypothesis:claimed'
        self.sync_import()
        self.refuse_import()

    def test_automatic_import_admission_refused(self):
        self.import_setup()
        self.import_request['automatic_admission'] = True
        self.refuse_import()

    def test_json_duplicate_fields_refused(self):
        with self.assertRaisesRegex(ValueError, 'duplicate JSON'):
            T.parse(b'{"scope":"one","scope":"two"}')

    def test_json_nonfinite_refused(self):
        with self.assertRaisesRegex(ValueError, 'nonfinite'):
            T.parse(b'{"datum":NaN}')

    def test_json_nesting_budget(self):
        with self.assertRaisesRegex(ValueError, 'nesting budget'):
            T.parse(b'[' * 33 + b'0' + b']' * 33)

    def test_json_whole_input_budget(self):
        with self.assertRaisesRegex(ValueError, 'bounded original'):
            T.parse(b' ' * (T.MAX_BYTES + 1))

    def test_original_facts_remain_unchanged(self):
        before = copy.deepcopy(self.facts)
        self.export()
        self.assertEqual(before, self.facts)

    def change_dependency(self, raw, encoding):
        self.dependency = raw
        self.dependency_binding = T.pin('dependency:one', raw)
        self.materials = (
            replace(self.materials[0], dependencies_json=T.encoded([self.dependency_binding])),
            T.Material(T.encoded(self.dependency_binding), raw, b'[]', encoding=encoding))
        self.contract['dependency_bindings'] = [self.dependency_binding]
        self.sync_export_controls()

    def add_second_artifact(self):
        raw = T.encoded({'node_id': 'hypothesis:two', 'kind': 'hypothesis', 'payload': {'synthetic': True}})
        header = {**self.header, 'identity_ref': 'hypothesis:two', 'version_ref': 'hypothesis:two@1', 'byte_sha256': T.sha(raw)}
        self.materials += (T.Material(T.encoded(T.pin('source:two', raw)), raw, b'[]', T.encoded(header)),)
        self.contract['artifact_refs'] = [self.header, header]
        self.sync_export_controls()
        return header

    def test_raw_text_dependency_bytes_survive_archive(self):
        raw = b'# Original document\n\nThis is a raw dependency.\n'
        self.change_dependency(raw, 'text-utf8')
        package_raw = self.export()
        package = self.engine.verify_archive(package_raw, T.pin('package:raw-text', package_raw))
        row = next(row for row in package['materials'] if row['binding'] == self.dependency_binding)
        self.assertEqual(base64.b64decode(row['original_bytes_b64']), raw)
        self.assertEqual(row['encoding'], 'text-utf8')

    def test_raw_binary_dependency_bytes_survive_archive(self):
        raw = b'\x00\xff\xfe\x80synthetic-binary\x00'
        self.change_dependency(raw, 'binary')
        package_raw = self.export()
        package = self.engine.verify_archive(package_raw, T.pin('package:raw-binary', package_raw))
        row = next(row for row in package['materials'] if row['binding'] == self.dependency_binding)
        self.assertEqual(base64.b64decode(row['original_bytes_b64']), raw)
        self.assertEqual(row['encoding'], 'binary')

    def test_binary_label_cannot_hide_json_session_memory(self):
        self.change_dependency(b'{"short_memory":"private synthetic sentinel"}', 'binary')
        self.refuse_export()

    def test_binary_label_cannot_hide_private_key_marker(self):
        self.change_dependency(b'\x00-----BEGIN PRIVATE KEY-----', 'binary')
        self.refuse_export()

    def test_unknown_dependency_encoding_refused(self):
        self.facts = replace(self.facts, materials=(self.materials[0], replace(self.materials[1], encoding='caller-defined')))
        self.refuse_export()

    def test_non_json_artifact_carrier_body_refused(self):
        self.facts = replace(self.facts, materials=(replace(self.materials[0], encoding='binary'), self.materials[1]))
        self.refuse_export()

    def test_privacy_review_encoding_mismatch_refused(self):
        self.review['material_encodings'][0]['encoding'] = 'binary'
        self.sync_review()
        self.refuse_export()

    def test_duplicate_source_basis_refused(self):
        self.contract['source_admission_basis'] = [self.dependency_binding, self.dependency_binding]
        self.sync_export_controls()
        self.refuse_export()

    def test_complete_plan_output_budget_refused(self):
        self.import_setup()
        self.dispositions['items'][0]['reason'] = 'r' * (T.MAX_BYTES - len(T.encoded(self.dispositions)) - 20)
        self.sync_import()
        self.assertLess(len(self.disposition_raw), T.MAX_BYTES)
        with self.assertRaisesRegex(ValueError, 'complete import plan byte budget'):
            self.account()

    def test_retained_source_accounted_alongside_real_candidate_target(self):
        second = self.add_second_artifact()
        self.import_setup()
        self.mapping['items'].append({'source': second, 'target': None, 'target_bytes_b64': None})
        self.dispositions['items'].append({'source': second, 'disposition': 'retain-source', 'reason': 'Keep this exact source.'})
        self.sync_import()
        plan = self.account()
        self.assertEqual(plan['accounted_source_artifacts'], 2)
        self.assertEqual(plan['accounted_source_materials'], 3)
        self.assertEqual(plan['items'][1]['disposition'], 'retain-source')
        self.assertIsNone(plan['items'][1]['target'])
        self.assertFalse(plan['source_retirement'])

    def test_excluded_source_accounted_alongside_real_candidate_target(self):
        second = self.add_second_artifact()
        self.import_setup()
        self.mapping['items'].append({'source': second, 'target': None, 'target_bytes_b64': None})
        self.dispositions['items'].append({'source': second, 'disposition': 'exclude', 'reason': 'Explicitly exclude this exact source.'})
        self.sync_import()
        plan = self.account()
        self.assertEqual(plan['accounted_source_artifacts'], 2)
        self.assertEqual(plan['items'][1]['disposition'], 'exclude')
        self.assertIsNone(plan['items'][1]['target'])
        self.assertFalse(plan['automatic_admission'])
