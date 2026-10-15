"""Hostile candidate import checks without mutating external source trees."""
import unittest
from .validate import *
from . import migration as selected_migration

def publish(files, destination):
    return selected_migration.publish(files, destination, execution_contract=ImportGuards.execution_contract)


class ImportGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        require(type(cls.execution_contract) is MigrationExecutionContract, 'independently suppliedv2 test contract required')
        cls.catalog_context = signed_catalog()
        catalog, operations = cls.catalog_context.__enter__()
        cls.translator = SourceTranslation(catalog, operations,
            producer_bindings=runtime_producers(cls.execution_contract), execution_contract=cls.execution_contract)
        cls.files = cls.selected_package_bytes
        cls.pin = cls.independent_manifest_sha256
        require(sha(cls.files['manifest.json']) == cls.pin, 'independently selected test package differs')

    @classmethod
    def tearDownClass(cls):
        cls.catalog_context.__exit__(None, None, None)

    def setUp(self):
        self.data = copy.deepcopy(self.files)

    def check(self, native=False):
        return validate_payload(self.data, self.translator, sha(self.data['manifest.json']), native=native)

    def reseal(self):
        """Update byte hashes to exercise semantic checks past generic envelopes."""
        index = parse(self.data['record-index.json'])
        for row in index:
            if row['path'] in self.data:
                row['sha256'] = sha(self.data[row['path']])
        self.data['record-index.json'] = record_bytes(index)
        core = parse(self.data['core.json'])
        core['record_index'] = [r for r in index if r['kind'] != 'generated-output']
        by_path = {r['path']: r for r in index}
        for d in core['dispositions']:
            d['outputs'] = [by_path.get(r['path'], r) for r in d['outputs']]
        self.data['core.json'] = record_bytes(core)
        manifest = parse(self.data['manifest.json'])
        manifest['core_sha256'] = sha(self.data['core.json'])
        manifest['files'] = [{'path': p, 'sha256': sha(raw)}
            for p, raw in sorted(self.data.items()) if p != 'manifest.json']
        self.data['manifest.json'] = record_bytes(manifest)

    def alter_core(self, function):
        core = parse(self.data['core.json']); function(core)
        self.data['core.json'] = record_bytes(core); self.reseal()

    def alter_record(self, kind, function):
        row = next(r for r in parse(self.data['record-index.json']) if r['kind'] == kind)
        value = parse(self.data[row['path']]); function(value)
        self.data[row['path']] = record_bytes(value); self.reseal()

    def reject(self, expression):
        with self.assertRaisesRegex(ValueError, expression):
            self.check()

    def test_exact_carriers_and_native_replay(self):
        result = self.check(native=True)
        self.assertEqual(result['carriers_checked'], 220)
        self.assertEqual(result['items_reconciled'], 140)
        self.assertTrue(result['native_replay_verified'])

    def test_original_manifest_pin(self):
        self.alter_core(lambda c: c.update(domain_instances_conformed=1))
        with self.assertRaisesRegex(ValueError, 'independently pinned'):
            validate_payload(self.data, self.translator, self.pin, native=False)

    def test_generated_output_cannot_infer_admission(self):
        self.alter_record('generated-output', lambda r: r.update(lifecycle_state='active'))
        self.reject('generated output candidate identity/posture')

    def test_reproduction_cannot_fabricate_proof(self):
        r = parse(self.data['reproducibility.json']); r['independent_rebuild_verified'] = True
        self.data['reproducibility.json'] = record_bytes(r); self.reseal()
        self.reject('reproduction inputs or proof ceiling')

    def test_native_memory_is_not_long_term_state(self):
        archive = parse(self.data['native.snapshot']); archive['Session_memory_included'] = True
        self.data['native.snapshot'] = record_bytes(archive)
        self.alter_core(lambda c: c.update(native_archive_sha256=sha(self.data['native.snapshot'])))
        self.reject('forbidden native archive content')

    def test_native_governance_confidence_not_inferred(self):
        archive = parse(self.data['native.snapshot'])
        key = 'governance/00000001-ontology-governance:O05:1.json'
        event = parse(base64.b64decode(archive['files'][key]['base64_original_bytes']))
        event['complete_resulting_governance_state']['commitment_confidence']['level'] = 'accepted'
        raw = canonical(event)
        archive['files'][key] = {'sha256':sha(raw),'base64_original_bytes':base64.b64encode(raw).decode()}
        self.data['native.snapshot'] = record_bytes(archive)
        self.alter_core(lambda c: c.update(native_archive_sha256=sha(self.data['native.snapshot'])))
        self.reject('native governance exact tuple, confidence')

    def test_native_semantic_node_mapping_exact(self):
        archive = parse(self.data['native.snapshot'])
        key = 'semantic/00000001-ontology-semantic:O05:1.json'
        event = parse(base64.b64decode(archive['files'][key]['base64_original_bytes']))
        event['complete_resulting_semantic_state']['typed_properties']['values']['represented_kind'] = 'product'
        raw = canonical(event)
        archive['files'][key] = {'sha256':sha(raw),'base64_original_bytes':base64.b64encode(raw).decode()}
        self.data['native.snapshot'] = record_bytes(archive)
        self.alter_core(lambda c: c.update(native_archive_sha256=sha(self.data['native.snapshot'])))
        self.reject('native semantic state/source/endpoint tuple')

    def test_private_body_file_rejected(self):
        self.data['raw-private-source.txt'] = b'not an allowed carrier'
        self.reseal(); self.reject('private body or unselected file')

    def test_unbound_file_rejected(self):
        self.data['extra.json'] = b'{}'; self.reject('file closure')

    def test_duplicate_manifest_entry(self):
        m = parse(self.data['manifest.json']); m['files'].append(m['files'][0])
        self.data['manifest.json'] = record_bytes(m); self.reject('duplicate package binding')

    def test_manifest_authority_rejected(self):
        m = parse(self.data['manifest.json']); m['actual_owner_outcome'] = 'approved'
        self.data['manifest.json'] = record_bytes(m); self.reject('posture')

    def test_public_export_posture_rejected(self):
        m = parse(self.data['manifest.json']); m['visibility'] = 'public'
        self.data['manifest.json'] = record_bytes(m); self.reject('posture')

    def test_raw_core_body_rejected(self):
        self.alter_core(lambda c: c.update(source_body='new field')); self.reject('closed adaptation core')

    def test_generic_envelope_not_domain_conformance(self):
        self.alter_core(lambda c: c.update(domain_instances_conformed=38)); self.reject('unauthorized adaptation effect')

    def test_global_axis_not_inferred(self):
        self.alter_core(lambda c: c.update(global_typed_relations_created=50)); self.reject('unauthorized adaptation effect')

    def test_source_effect_not_inferred(self):
        self.alter_core(lambda c: c.update(source_effects_applied=1)); self.reject('unauthorized adaptation effect')

    def test_source_prose_not_copied(self):
        self.alter_core(lambda c: c.update(source_bodies_copied=1)); self.reject('unauthorized adaptation effect')

    def test_changed_epoch_not_selected(self):
        self.alter_core(lambda c: c['deferred_source_epoch'].update(disposition='import'))
        self.reject('source gaps/epochs dropped')

    def test_excluded_package_preserved(self):
        self.alter_core(lambda c: c['excluded_packages'].pop()); self.reject('source gaps/epochs dropped')

    def test_unresolved_questions_preserved(self):
        self.alter_core(lambda c: c.update(outside_references=[])); self.reject('source gaps/epochs dropped')

    def test_selector_observation_not_fabricated(self):
        self.alter_core(lambda c: c['selector_observations'][0].update(status='resolved-semantic-authority'))
        self.reject('literal selector evidence')

    def test_disposition_partition_closed(self):
        self.alter_core(lambda c: c['dispositions'].pop()); self.reject('accounting incomplete')

    def test_blocked_revision_not_replaced(self):
        self.alter_core(lambda c: next(d for d in c['dispositions'] if d['disposition'] == 'block')
            .update(blocked_expected_sha256='0'*64)); self.reject('blocked expected revision')

    def test_blocked_dependencies_not_dropped(self):
        self.alter_core(lambda c: next(d for d in c['dispositions'] if d['blocked_dependency_ids'])
            .update(blocked_dependency_ids=[])); self.reject('dependencies or posture collapsed')

    def test_disposition_body_field_rejected(self):
        self.alter_core(lambda c: c['dispositions'][0].update(source_record={})); self.reject('closed source disposition')

    def test_source_bytes_digest_preserved(self):
        self.alter_record('source', lambda r: r['payload'].update(content_digest='file-sha256:'+'0'*64))
        self.reject('source metadata carrier differs')

    def test_source_locator_no_alias(self):
        self.alter_record('source', lambda r: r['payload'].update(locator='legacy-source://different-root/file'))
        self.reject('source metadata carrier differs')

    def test_source_observation_time_pinned(self):
        self.alter_record('source', lambda r: r['payload'].update(captured_at='invented timestamp'))
        self.reject('source metadata carrier differs')

    def test_source_schema_extra_field_rejected(self):
        self.alter_record('source', lambda r: r['payload'].update(source_record={}))
        self.reject('selected schema violation')

    def test_source_actual_derivation_required(self):
        self.alter_record('source', lambda r: r.update(relation_refs=[]))
        self.reject('selected schema violation')

    def test_source_product_kind_not_inferred(self):
        self.alter_record('source', lambda r: r.update(kind='product'))
        self.reject('selected schema violation')

    def test_node_represented_subject_digest_preserved(self):
        self.alter_record('ontology-node', lambda r: r['payload']['represented_subject'].update(digest='0'*64))
        self.reject('rich ontology carrier differs')

    def test_node_domain_kind_not_inferred(self):
        self.alter_record('ontology-node', lambda r: r['payload']['represented_subject'].update(kind='product'))
        self.reject('rich ontology carrier differs')

    def test_definition_revision_must_resolve(self):
        self.alter_core(lambda c: next(iter(c['definition_witnesses'].values()))['witness'].update(selector_sha256='0'*64))
        self.reject('Definition or adapter byte closure')

    def test_node_replay_source_false(self):
        self.alter_record('ontology-node', lambda r: r['payload'].update(replay_source=True))
        self.reject('selected schema violation')

    def test_edge_requires_local_vocabulary(self):
        self.alter_record('ontology-edge', lambda r: r['payload'].update(relation_type_ref='relation.member-of'))
        self.reject('rich ontology carrier differs')

    def test_edge_endpoint_tuple_not_reversed(self):
        def reverse(r):
            p = r['payload']; p['source_node_ref'], p['target_node_ref'] = p['target_node_ref'], p['source_node_ref']
        self.alter_record('ontology-edge', reverse); self.reject('rich ontology carrier differs')

    def test_edge_qualifiers_closed(self):
        self.alter_record('ontology-edge', lambda r: r['payload']['closed_qualifiers'].update(undeclared=True))
        self.reject('rich ontology carrier differs')

    def test_edge_cannot_acquire_global_binding(self):
        self.alter_record('ontology-edge', lambda r: r['payload'].update(global_typed_relation_binding={
            'typed_relation_ref':'relation:invented','typed_relation_version_ref':'relation:invented@v1',
            'typed_relation_digest':'0'*64}))
        self.reject('selected schema violation')

    def test_profile_tamper_rejected(self):
        saved = copy.deepcopy(self.translator.profile)
        try:
            self.translator.profile['namespace'] = 'different'
            with self.assertRaisesRegex(ValueError, 'source profile changed'):
                self.translator.guard()
        finally:
            self.translator.profile = saved

    def test_scope_execution_not_authorized(self):
        saved = copy.deepcopy(self.translator.scope)
        try:
            self.translator.scope['source_execution_allowed'] = True
            with self.assertRaisesRegex(ValueError, 'build scope changed'):
                self.translator.guard()
        finally:
            self.translator.scope = saved

    def test_unknown_source_read_rejected(self):
        item = copy.deepcopy(self.translator.selection['items'][0]); item['source_binding']['path'] = 'unknown/file'
        with self.assertRaisesRegex(ValueError, 'unselected source item'):
            self.translator.selected_bytes(item)

    def test_blocked_source_read_rejected(self):
        item = next(i for i in self.translator.selection['items'] if i['disposition'] == 'block')
        with self.assertRaisesRegex(ValueError, 'blocked revision'):
            self.translator.selected_bytes(item)

    def test_duplicate_json_key_rejected(self):
        with self.assertRaisesRegex(ValueError, 'duplicate JSON key'):
            parse(b'{"id":1,"id":2}')

    def test_json_pointer_array_positions(self):
        self.assertEqual(pointer({'a':[{'b':1}]}, '/a/0/b'), 1)
        with self.assertRaisesRegex(ValueError, 'invalid array position'):
            pointer({'a':[1]}, '/a/00')

    def test_json_pointer_escape_closed(self):
        with self.assertRaisesRegex(ValueError, 'invalid pointer escape'):
            pointer({'a':1}, '/a~2')

    def test_existing_package_no_overwrite(self):
        with self.assertRaisesRegex(ValueError, 'cannot be overwritten'):
            publish(self.files, ROOT / self.translator.scope['output_root'])

    def test_unselected_output_root_rejected(self):
        with self.assertRaisesRegex(ValueError, 'unselected output root'):
            publish(self.files, ROOT / 'different-output')


if __name__ == '__main__':
    raise SystemExit('Trusted Root supplies explicitv2 contract and independently pinned produced package; no legacy direct-host test bootstrap.')
