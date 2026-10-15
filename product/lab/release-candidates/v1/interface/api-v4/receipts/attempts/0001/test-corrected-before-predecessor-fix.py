"""Corrected signed history keeps independent current closure and historical gaps."""
from contextlib import ExitStack
import copy
import tempfile
import unittest
from unittest.mock import patch
from fixtures import *
from service import *
import artifact_model as model


class CorrectedHistoryGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stack=ExitStack();cls.root=Path(cls.stack.enter_context(tempfile.TemporaryDirectory(prefix='cal-R03-corrected-read-tests-')))
        cls.key,cls.policy,cls.pin=provision(cls.root,'reference-corrected');cls.schemas=Schemas()
        cls.view=cls.stack.enter_context(source.replay_source('reference-corrected'))
        cls.members=source.parse(source.original(cls.view.handle.manifest['correction_profile_binding']))['member_bindings']
        cls.corrected=[s for s in cls.view.subjects.values() if s.get('reference_correction_proof')]
        cls.current=cls.corrected[0];cls.prior=cls.view.subjects[cls.current['predecessor_ref']]
    @classmethod
    def tearDownClass(cls):cls.stack.close()
    def setUp(self):
        self.channel=ReaderChannel(self.policy,self.pin,self.schemas);self.channel.authenticate(proof(self.key,self.channel.challenge))
        self.service=Service(self.view,self.channel,self.schemas)
    def tearDown(self):self.service.close()
    def invoke(self,operation,selected=None,**values):
        return self.service.call(compact(call(self.channel.context,operation,selected or cut(self.view),**values)))
    def inspect(self,subject,**values):
        values.setdefault('include',['body','contract','authority','provenance','evidence','lifecycle','gaps'])
        return self.invoke('artifact.inspect',artifact=model.artifact_ref(self.view,subject),**values)
    def query(self,**values):
        values.setdefault('carrier_refs',list(self.view.data['projection']['contracts']));values.setdefault('limit',1000)
        return self.invoke('artifact.query',**values)
    def test_source_selected_independently(self):
        self.assertEqual(self.view.selected,source.source_selection('reference-corrected'))
        self.assertEqual(self.view.handle.pins.__dict__,self.view.selected['engine_pins'])
        self.assertEqual(self.view.data['config']['correction_profile_binding'],self.view.handle.manifest['correction_profile_binding'])
    def test_unknown_source_cannot_select_unpinned_store(self):
        with self.assertRaises(Exception):source.source_selection('arbitrary-live-store')
    def test_preserved_legacy_selection_remains_exact(self):
        for name in ['engineering','research','product']:self.assertEqual(source.source_selection(name),source.legacy.source_selection(name))
    def test_reader_signature_grants_zero_actions(self):
        self.assertEqual(self.channel.context['limits']['max_actions'],0);self.assertIsNone(self.channel.context['agent_instance_ref'])
        self.assertFalse(self.channel.context['accept_client_supplied_authority_context'])
    def test_corrected_status_is_current_and_profile_bound(self):
        r=self.invoke('lab.status');self.assertEqual(r['kind'],'result');self.assertEqual(r['message']['source_cut'],cut(self.view))
        self.assertEqual(r['contract_profile_binding'],self.schemas.profile_binding)
    def test_status_distinguishes_historical_residue(self):
        reasons=' '.join(g['reason'] for g in self.invoke('lab.status')['message']['gaps'])
        self.assertIn('0 current unclosed',reasons);self.assertIn('10 historical unresolved',reasons)
    def test_coverage_accounts_for_all_relations(self):
        c=model.connection_coverage(self.view,self.schemas)
        self.assertEqual(c,{'current':{'closed':60,'unclosed':0},'historical':{'closed':0,'unclosed':10},'excluded':[],'total':70})
    def test_all_ten_original_bodies_preserved(self):
        for b in self.members:
            m=source.parse(source.original(b));old=self.view.subjects[m['predecessor_version_ref']]
            self.assertEqual(old['record'],source.parse(source.original(m['original_source_binding'])))
            self.assertEqual(old['effective_state'],'local-admitted-historical')
    def test_all_ten_current_bodies_match_exact_review(self):
        for b in self.members:
            m=source.parse(source.original(b));new=self.view.subjects[m['version_ref']]
            self.assertEqual(new['record'],source.parse(source.original(m['record_binding'])))
            self.assertEqual(new['effective_state'],'local-admitted-current')
    def test_current_inspection_original_transaction_byte_provenance(self):
        r=self.inspect(self.current);self.assertEqual(r['kind'],'result');m=r['message'];self.assertEqual(m['status_facets']['admission'],'local-admitted-current')
        self.assertEqual(m['envelope']['decoded_artifact']['body'],self.current['record'])
        self.assertIn('inherited-canonical-json',m['envelope']['claim_ceiling']);self.assertTrue(m['provenance_bindings'][0]['ref'].startswith('store:'))
    def test_current_inspection_binds_correction_evidence(self):
        r=self.inspect(self.current);self.assertEqual(r['kind'],'result');actual=r['message']['evidence_bindings']
        for key in ['reference_correction_binding','correction_profile_binding','carrier_schema_binding','carrier_descriptor_binding']:
            b=self.current['reference_correction_proof'][key];self.assertIn({'ref':b['path'],'sha256':b['sha256']},actual)
    def test_historical_inspection_preserves_bad_label_and_admission(self):
        r=self.inspect(self.prior);self.assertEqual(r['kind'],'result');m=r['message'];self.assertEqual(m['status_facets']['admission'],'local-admitted-historical')
        self.assertEqual(m['envelope']['decoded_artifact']['body'],self.prior['record'])
        self.assertTrue(any('Historical exact relation retains unresolved' in g['reason'] for g in m['gaps']))
    def test_body_scope_independent_from_read_namespace(self):
        r=self.inspect(self.current);m=r['message'];self.assertEqual(m['artifact']['scope_ref'],'project:cyberalchemy-v2-to-lab-migration')
        self.assertEqual(m['envelope']['decoded_artifact']['body']['scope_ref'],'scope:cyberalchemy-lab-first-agent-episode')
    def test_historical_carrier_retained_without_current_write_claim(self):
        r=self.inspect(self.current);self.assertEqual(r['message']['artifact']['carrier_ref'],'cal.artifact-type.typed-relation/v2')
        self.assertEqual(self.view.data['projection']['contracts']['cal.artifact-type.typed-relation/v2']['lifecycle_state'],'admitted-historical')
        entries=self.invoke('catalog.get',carrier_refs=['cal.artifact-type.typed-relation/v2'])['message']['contract_entries']
        self.assertEqual(entries[0]['write_posture'],'historical-read-only')
    def test_returned_correction_body_cannot_mutate_verified_source(self):
        expected=copy.deepcopy(self.current['record']);r=self.inspect(self.current);r['message']['envelope']['decoded_artifact']['body']['name']='forged'
        self.assertEqual(self.current['record'],expected)
    def test_excluded_evidence_and_body_do_not_leak(self):
        r=self.inspect(self.current,include=['lifecycle']);m=r['message'];self.assertIsNone(m['envelope'])
        self.assertEqual(m['evidence_bindings'],[]);self.assertEqual(m['authority_bindings'],[]);self.assertEqual(m['provenance_bindings'],[])
    def test_ten_decisions_remain_independent(self):
        cores=self.view.data['transactions'][-1]['decision_cores'];self.assertEqual(len(cores),10);self.assertEqual(len({c['decision_ref'] for c in cores}),10)
        self.assertTrue(all(c['domain_scope_ref']=='scope:cyberalchemy-lab-first-agent-episode' for c in cores))
    def test_full_inventory_canonical_sql_parity(self):
        a=self.query();b=self.query(query_basis='projection');self.assertEqual(a['kind'],b['kind']);self.assertEqual(b['kind'],'result')
        self.assertEqual(a['message']['results'],b['message']['results']);self.assertEqual(len(b['message']['results']),546)
    def test_no_false_current_identity_collision(self):
        self.assertFalse(any('Multiple independently captured' in g['reason'] for g in self.query()['message']['gaps']))
    def test_history_gap_subjects_are_exact_old_revisions(self):
        r=self.query();self.assertEqual(r['kind'],'result')
        gaps=[g for g in r['message']['gaps'] if 'Historical relation remains unresolved' in g['reason']]
        self.assertEqual({g['subject_ref'] for g in gaps},{s['predecessor_ref'] for s in self.corrected})
        self.assertFalse(any('Current relation does not close' in g['reason'] for g in r['message']['gaps']))
    def test_canonical_sql_gap_parity(self):
        a=self.query();b=self.query(query_basis='projection');self.assertEqual(a['message']['gaps'],b['message']['gaps'])
    def test_genesis_contains_originals_and_no_corrections(self):
        old=self.service.handlers.available_views[0];r=self.invoke('artifact.query',cut(old),carrier_refs=list(self.view.data['projection']['contracts']),limit=1000,freshness_requirement='exact-historical')
        self.assertEqual(r['kind'],'result');versions={h['version_ref'] for h in r['message']['results']};self.assertEqual(len(versions),485)
        self.assertTrue({s['predecessor_ref'] for s in self.corrected}<=versions);self.assertFalse({s['version_ref'] for s in self.corrected}&versions)
    def test_setup_prefix_contains_historical_project_without_corrections(self):
        v=self.service.handlers.available_views[1];self.assertEqual(v.subjects['project:cyberalchemy-v2-to-lab-migration@foundation.1']['effective_state'],'local-admitted-historical')
        self.assertFalse({s['version_ref'] for s in self.corrected}&v.subjects.keys())
    def test_historical_prefix_sql_parity(self):
        v=self.service.handlers.available_views[1];values={'carrier_refs':list(self.view.data['projection']['contracts']),'limit':1000,'freshness_requirement':'exact-historical'}
        a=self.invoke('artifact.query',cut(v),**values);b=self.invoke('artifact.query',cut(v),query_basis='projection',**values)
        self.assertEqual(a['kind'],b['kind']);self.assertEqual(b['kind'],'result');self.assertEqual(a['message']['results'],b['message']['results'])
    def test_current_request_refuses_historical_prefix(self):
        r=self.invoke('artifact.query',cut(self.service.handlers.available_views[0]));self.assertEqual(r['message']['code'],'stale-cut')
    def test_corrected_project_tuple_keeps_exact_historical_revision(self):
        relations,_=model.connections(self.view,self.schemas)
        expected={s['version_ref'] for s in self.corrected if s['record']['payload']['target']['kind']=='project'}
        selected=[r for r in relations if r['version_ref'] in expected];self.assertEqual(len(selected),3)
        self.assertTrue(all(r['connection']['target']['semantic_kind']=='project' and r['connection']['target']['artifact']['version_ref']=='project:cyberalchemy-v2-to-lab-migration@foundation.1' for r in selected))
    def test_scope_substitution_refused(self):
        header=model.artifact_ref(self.view,self.current);header['scope_ref']='scope:cyberalchemy-lab-first-agent-episode'
        r=self.invoke('artifact.inspect',artifact=header);self.assertEqual(r['message']['code'],'unauthorized')
    def test_unknown_correction_version_refused(self):
        header=model.artifact_ref(self.view,self.current);header['version_ref']+='-unreviewed'
        r=self.invoke('artifact.inspect',artifact=header);self.assertEqual(r['message']['code'],'not-found')
    def test_current_failure_remains_separate_from_historical_success(self):
        with patch.object(self.service.handlers,'current',return_value=False):
            self.assertEqual(self.query()['message']['code'],'stale-cut')
            r=self.query(freshness_requirement='allow-stale',query_basis='projection');self.assertEqual(r['kind'],'result');self.assertEqual(r['message']['freshness'],'stale')
    def test_source_selection_pin_drift_refused(self):
        with patch.object(source,'SELECTION_SHA','0'*64):
            with self.assertRaises(Exception):source.source_selection('reference-corrected')
    def test_original_operation_scope_not_shrunk(self):self.assertEqual(len(self.schemas.operations),34);self.assertEqual(len(SUPPORTED),4)


if __name__=='__main__':unittest.main()
