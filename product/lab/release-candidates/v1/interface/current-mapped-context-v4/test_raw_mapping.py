"""Original-body/native identity separation and complete captured diagnostics."""
import copy,unittest
from .build import *
class OriginalMappingChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        guard(PIN);require(sha((HERE/'packages/0001/manifest.json').read_bytes())==PACKAGE,'independent mapped package differs')
        cls.mapping=load(HERE/'packages/0001/mapping.json');cls.events=[load(p) for p in sorted((HERE/'packages/0001/semantic').glob('*.json'))]
        cls.manager=reader.open_signed(SOURCE_PIN,PACKAGE_PIN);cls.source=cls.manager.__enter__()
    @classmethod
    def tearDownClass(cls):cls.manager.__exit__(None,None,None)
    def test_21_explicit_new_original_source_branch(self):
        self.assertEqual(self.mapping['source_name'],'custody-participation')
        self.assertEqual(self.mapping['source_package_binding'],binding(reader.HERE/'packages/0001/manifest.json'))
    def test_22_all23authored_raw_target_hashes_enter_native_properties(self):
        raw_count=0
        for row,event in zip(self.mapping['rows'],self.events):
            s=self.source.view.subjects[row['artifact']['version_ref']];raw,locator,encoding,enclosing=reader.adapter.model.record_bytes(self.source.view,s)
            self.assertEqual(sha(raw),row['artifact']['byte_sha256']);self.assertEqual(sha(raw),event['complete_resulting_semantic_state']['typed_properties']['values']['record_sha256'])
            self.assertEqual((locator,encoding,enclosing),(row['origin']['source_locator'],row['origin']['encoding'],row['origin']['enclosing_source_sha256']))
            if encoding==self.source.view.handle.custody.ENCODING:self.assertNotEqual(raw,encoded(s['record']));raw_count+=1
        self.assertEqual(raw_count,23)
    def test_23_native_header_identity_is_separate_from_actual_body_hash(self):
        for row in self.mapping['rows']:
            self.assertNotEqual(row['subject_identity']['subject_id'].split(':',1)[1],row['artifact']['byte_sha256'])
        self.assertFalse(self.mapping['native_representation_is_artifact_instance'])
    def test_24_current_captured_source_dispositions_are_retained(self):
        self.assertEqual(self.mapping['source_closure'],self.source.closure_report())
        dispositions=self.mapping['projection_dispositions'];self.assertEqual(len(dispositions),len(self.source.view.subjects))
        self.assertEqual(len(dispositions),len(self.source.view.subjects));self.assertEqual({r['version_ref'] for r in dispositions},set(self.source.view.subjects))
        actual={r['version_ref'] for r in dispositions if r['disposition']=='mapped-exact-context-representation'}
        self.assertEqual(actual,{r['artifact']['version_ref'] for r in self.mapping['rows']})
        self.assertEqual(len(actual),25)
    def test_25_old_instance_assignment_diagnostic_not_mapped_as_new_participant(self):
        closure=self.mapping['source_closure'];self.assertEqual(len(closure['instance_bound_assignments']),1)
        versions={r['artifact']['version_ref'] for r in self.mapping['rows']}
        for row in closure['instance_bound_assignments']:self.assertNotIn(row['assignment']['version_ref'],versions)
        self.assertIn(records.ASSIGNMENT+'@'+records.VERSION,versions)
        self.assertFalse(self.mapping['projection_is_host_permission'])
    def test_26_source_and_native_profile_and_cursor_coordinates_are_explicit(self):
        self.assertEqual(self.mapping['source_cut']['source_profile_sha256'],self.source.view.handle.manifest['profile_binding']['sha256'])
        self.assertEqual(self.mapping['source_cut']['commit_sequence'],2)
        self.assertEqual(self.mapping['semantic_cursor'],25);self.assertEqual(self.mapping['governance_cursor'],25)
        self.assertEqual(self.events[0]['subject_identity']['ontology_id'],ONTOLOGY)
    def test_27_original_absolute_period_is_not_reset_or_extended(self):
        b=self.mapping['source_assignment_interval_binding'];period=load(ROOT/b['path']);original(b)
        declared=load(reader.HERE/'episode-contract.json')
        old=load(ROOT/period['original_expired_period_binding']['path']);original(period['original_expired_period_binding'])
        self.assertEqual((period['not_before'],period['expires_at']),(declared['not_before'],declared['expires_at']))
        self.assertEqual(period['assignment_version_ref'],records.ASSIGNMENT+'@'+records.VERSION)
        self.assertEqual(period['principal_ref'],records.PRINCIPAL)
        self.assertNotEqual(period['principal_ref'],old['principal_ref'])
        self.assertNotEqual(period['assignment_version_ref'],old['assignment_version_ref'])
        from datetime import datetime
        self.assertGreaterEqual(datetime.fromisoformat(period['not_before']),datetime.fromisoformat(old['expires_at']))
        self.assertFalse(declared['original_Assignment_renewed'])
        self.assertFalse(declared['original_signer_restored'])
        self.assertFalse(declared['Session_memory_rehydrated'])
    def test_28_schema_definition_signature_qualifier_witnesses_remain_distinct(self):
        for row,event in zip(self.mapping['rows'],self.events):
            values=event['complete_resulting_semantic_state']['typed_properties']['values']
            if row['subject_identity']['subject_kind']=='node':
                self.assertEqual(row['schema_binding']['sha256'],values['schema_sha256'])
                self.assertTrue(row['definition_witnesses'])
            else:
                self.assertEqual(row['axis_ref'],row['closed_signature']['axis_id'])
                self.assertEqual(values['relation_kind_ref'],row['closed_signature']['relation_kind_id'])
                self.assertEqual(values['qualifiers_sha256'],sha(encoded(row['qualifiers'])))
    def test_29_current_ontology_representation_and_represented_carrier_qualification(self):
        ontology_refs=set(self.source.view.data['projection']['contracts']['cal.artifact-type.ontology-node/v2']['semantic_definition_refs'])
        for row,event in zip(self.mapping['rows'],self.events):
            if row['subject_identity']['subject_kind']!='node':continue
            state=event['complete_resulting_semantic_state'];components=state['semantic_components']
            self.assertEqual(len(components),2)
            self.assertEqual(components[0]['type_ref'],'cal.artifact-type.ontology-node/v2')
            self.assertEqual(components[1]['type_ref'],row['artifact']['carrier_ref'])
            self.assertTrue(ontology_refs <= {w['version_ref'] for w in row['definition_witnesses']})
            for component in components:self.assertIn(component['definition_ref'],state['semantic_definition_refs'])
