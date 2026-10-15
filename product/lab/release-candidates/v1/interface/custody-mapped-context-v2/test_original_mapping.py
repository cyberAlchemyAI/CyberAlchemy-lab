"""Independent mapping/cold native replay checks against actual signed sources."""
import argparse
import copy
import json
import unittest
from .build import *

class MappingChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        guard(PIN);cls.package=load(HERE/'packages/0001/manifest.json')
        require(sha((HERE/'packages/0001/manifest.json').read_bytes())==PACKAGE,'independent mapped package pin differs')
        for row in cls.package['files']:original(row)
        cls.mapping=load(HERE/'packages/0001/mapping.json');cls.output=load(HERE/'packages/0001/native-output.json')
        cls.events=[load(p) for p in sorted((HERE/'packages/0001/semantic').glob('*.json'))]
        cls.gov=[load(p) for p in sorted((HERE/'packages/0001/governance').glob('*.json'))]
        cls.manager=reader.open_signed(SOURCE_PIN,PACKAGE_PIN);cls.source=cls.manager.__enter__()
        cls.nodes=[r for r in cls.mapping['rows'] if r['subject_identity']['subject_kind']=='node']
        cls.edges=[r for r in cls.mapping['rows'] if r['subject_identity']['subject_kind']=='relation']
    @classmethod
    def tearDownClass(cls):cls.manager.__exit__(None,None,None)
    def test_01_actual_same_signed_cut(self):self.assertEqual(self.mapping['source_cut'],self.source.source_cut)
    def test_02_fifteen_mapped_nodes(self):self.assertEqual(len(self.nodes),15);self.assertEqual(len(self.output['governed_nodes']),15)
    def test_03_ten_declared_edges(self):self.assertEqual(len(self.edges),10)
    def test_04_unique_native_identity(self):self.assertEqual(len({r['subject_identity']['subject_id'] for r in self.mapping['rows']}),25)
    def test_05_original_Artifact_References(self):
        for row in self.mapping['rows']:
            s=self.source.view.subjects[row['artifact']['version_ref']]
            self.assertEqual(row['artifact'],reader.adapter.model.artifact_ref(self.source.view,s))
    def test_06_edge_exact_endpoint_closure(self):
        byver={r['artifact']['version_ref']:r for r in self.nodes}
        for row in self.edges:
            for endpoint in [row['source'],row['target']]:
                self.assertEqual(byver[endpoint['version_ref']]['semantic_kind'],endpoint['kind'])
                self.assertEqual(byver[endpoint['version_ref']]['artifact']['identity_ref'],endpoint['ref'])
    def test_07_closed_signature_original_bytes(self):
        for row in self.edges:
            b=row['signature_binding'];self.assertEqual(sha((ROOT/b['ref']).read_bytes()),b['sha256'])
            self.assertEqual(load(ROOT/b['ref'])['payload'],row['closed_signature'])
    def test_08_qualifiers_retained(self):
        for row in self.edges:
            s=self.source.view.subjects[row['artifact']['version_ref']]
            self.assertEqual(row['qualifiers'],s['record']['payload']['qualifiers'])
            self.source.view.handle.operations.validate_relation(s['record'],self.source.view.data['projection'])
    def test_09_each_exact_governance_join(self):
        for e,g in zip(self.events,self.gov):
            self.assertEqual(g['semantic_ref'],{'semantic_event_id':e['event_id'],'semantic_event_digest':e['event_digest'],'semantic_cursor':e['semantic_cursor']})
    def test_10_candidate_governance(self):
        for g in self.gov:
            s=g['complete_resulting_governance_state'];self.assertEqual(s['authority_effect'],'none');self.assertEqual(s['promotion_state_or_handle'],'not-promoted')
    def test_11_no_implicit_edges(self):
        actual={r['artifact']['version_ref'] for r in self.edges}
        expected={s['version_ref'] for s in self.source.view.subjects.values() if s['identity'].startswith('typed-relation:'+records.PREFIX+':') and s['effective_state'] in reader.adapter.CURRENT}
        self.assertEqual(actual,expected)
    def test_12_definition_original_witnesses(self):
        for row in self.nodes:
            for witness in row['definition_witnesses']:
                raw=(ROOT/witness['source_locator']).read_bytes()
                self.assertEqual(sha(raw),witness['selected_original_sha256'])
                self.assertEqual(sha(raw),witness['enclosing_source_sha256'])
    def test_13_source_and_native_cursors_separate(self):
        self.assertEqual(self.mapping['semantic_cursor'],25);self.assertEqual(self.mapping['governance_cursor'],25)
        self.assertNotEqual(self.mapping['source_cut']['commit_sequence'],25)
    def test_14_subject_typed_properties(self):
        for e,row in zip(self.events,self.mapping['rows']):
            p=e['complete_resulting_semantic_state']['typed_properties'];self.assertEqual(p['values']['record_sha256'],row['artifact']['byte_sha256'])
            self.assertEqual(p['values']['mapping_sha256'],sha((HERE/'policy.json').read_bytes()))
    def test_15_actual_native_cold_replay(self):
        raw=call([HERE/'packages/0001/semantic',HERE/'packages/0001/governance',HERE/'packages/0001/request.json'])
        self.assertEqual(raw,(HERE/'packages/0001/native-output.json').read_bytes())
    def test_16_wrong_join_denied_by_native(self):
        with tempfile.TemporaryDirectory(prefix='cal-R03-native-negative-') as tmp:
            r=Path(tmp);semantic=r/'semantic';gov=r/'governance';semantic.mkdir();gov.mkdir()
            for i,e in enumerate(self.events): (semantic/(str(i).zfill(8)+'.json')).write_bytes(native_bytes(e))
            corrupt=copy.deepcopy(self.gov);corrupt[0]['semantic_ref']['semantic_event_digest']='0'*64
            corrupt[0]['complete_resulting_governance_state']['semantic_ref']=copy.deepcopy(corrupt[0]['semantic_ref'])
            # Resealing proves exact-join denial even with a valid event digest.
            corrupt=seal({'semantic':[],'governance':corrupt})['governance']
            for i,e in enumerate(corrupt):(gov/(str(i).zfill(8)+'.json')).write_bytes(native_bytes(e))
            request=r/'request.json';request.write_bytes((HERE/'packages/0001/request.json').read_bytes())
            with self.assertRaisesRegex(ValueError,'GOVERNANCE_REFERENCE_MISMATCH|GOVERNANCE_REFERENCE_MISSING'):call([semantic,gov,request])
    def test_17_wrong_source_manifest_denied(self):
        with self.assertRaises(ValueError):guard('0'*64)
    def test_18_no_view_API_Agent_claim(self):
        for key in ['context_or_ontology_view_carriers_generated','active_Agents_created','public_API_operations_added']:self.assertFalse(self.mapping[key])
        self.assertIsNone(self.mapping['actual_owner_outcome']);self.assertEqual(self.mapping['authority_effect'],'none')
    def test_19_protected_events_and_no_Session_memory(self):
        import stat
        for row in self.package['files']:
            self.assertEqual(stat.S_IMODE((ROOT/row['path']).stat().st_mode),0o600)
            reader.adapter.eligibility.no_private_memory(load(ROOT/row['path']))
    def test_20_mapping_identity_byte_rule(self):
        for row in self.mapping['rows']:
            self.assertEqual(row['subject_identity']['subject_id'],row['subject_identity']['subject_kind']+':'+sha(encoded(row['artifact'])))

