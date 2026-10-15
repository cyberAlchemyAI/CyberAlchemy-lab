"""Rich source bindings and actual native rejection guards."""
import copy
import os
import unittest
from unittest.mock import patch

from native_store import *


class LifecycleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manager = signed_catalog();cls.catalog,cls.operations = cls.manager.__enter__()
        cls.adapter = CandidateRepresentationAdapter(cls.catalog,cls.operations)
        cls.translator = RichTranslation(cls.adapter,bind(PROFILE))
        p = ROOT/'implementation/lab-work/candidates/v1/packages/0002/work.json'
        cls.work = cls.adapter.represent({**bind(p),'kind':'work','version_ref':'work:lab-development:c12-source-audit-0002@candidate.1'})
        cls.spec = cls.translator.node_spec(cls.work)
        cls.record = cls.translator.rich_record(cls.spec,{'semantic_event_id':'ontology-semantic:O02:1','semantic_event_digest':'0'*64,'semantic_cursor':1},[])
        cls.executable = Path(os.environ['O02_NATIVE_EXECUTABLE']);cls.exe_sha = os.environ['O02_NATIVE_SHA256']
    @classmethod
    def tearDownClass(cls):cls.manager.__exit__(None,None,None)
    def bad(self,fn,*args):
        with self.assertRaises(RepresentationFault):fn(*args)
    def changed(self,fn):
        record = copy.deepcopy(self.record);fn(record)
        self.bad(self.translator.translate_node,record,self.spec)

    def test_real_signed_source_effect_is_resolved(self):
        proof = self.translator.signed_source_effect(self.work)
        self.assertEqual(proof['source_effect'],'admit');self.assertEqual(proof['source_posture'],'local-admitted-current')
        self.assertFalse(proof['source_admission_is_repository_admission'])
    def test_rich_fields_survive_translation(self):
        state,witness = self.translator.translate_node(self.record,self.spec)
        self.assertTrue(state['semantic_components'] and state['use_obligations'] and state['forbidden_collapse'])
        self.assertEqual(state['typed_properties']['values'],self.record['payload']['semantic_state']['typed_properties'])
        self.assertEqual(len(witness['definition_witnesses']),2)
    def test_definition_selectors_are_actual_original_digests(self):
        d = self.translator.definition('cal.definition.work@1.0.0-candidate.1')
        raw = parse(original(d['witness']['source_binding']))
        self.assertEqual(d['reference']['selector_sha256'],sha(canonical(pointer(raw,d['witness']['selector']))))
    def test_missing_definition_cannot_be_invented(self):
        self.bad(self.translator.definition,'definition:invented@1')
    def test_exact_historical_revision_not_latest(self):
        self.bad(self.translator.definition,'cal.definition.work@invented')
    def test_missing_components_rejected(self):self.changed(lambda r:r['payload']['semantic_state'].update(semantic_components=[]))
    def test_missing_properties_rejected(self):self.changed(lambda r:r['payload']['semantic_state'].update(typed_properties={}))
    def test_missing_obligations_rejected(self):self.changed(lambda r:r['payload']['semantic_state'].update(use_obligations=[]))
    def test_missing_collapse_boundary_rejected(self):self.changed(lambda r:r['payload']['semantic_state'].update(forbidden_collapse=[]))
    def test_source_revision_poison_rejected(self):self.changed(lambda r:r['payload']['represented_subject'].update(version_ref='work:other@1'))
    def test_source_digest_poison_rejected(self):self.changed(lambda r:r['payload']['represented_subject'].update(digest='0'*64))
    def test_undeclared_profile_rejected(self):self.changed(lambda r:r['payload'].update(profile_ref='test-empty-profile/v1'))
    def test_changed_definition_witness_rejected(self):
        spec = copy.deepcopy(self.spec);next(iter(spec['definitions'].values()))['reference']['selector_sha256']='0'*64
        self.bad(self.translator.translate_node,self.record,spec)
    def test_identity_label_is_not_identity(self):
        source = copy.deepcopy(self.spec['subject']);profile=self.translator.profile
        first=node_id(source,profile);source['version_ref']+='-different';self.assertNotEqual(node_id(source,profile),first)
    def test_confidence_is_explicitly_not_assessed(self):
        store = NativeCandidateStore(self.translator,self.executable,self.exe_sha)
        try:
            store.map_node(self.work);view=store.read();g=view['governed_nodes'][0]['governance_state']
            self.assertEqual(g['evidence_confidence']['level'],'not-assessed')
            self.assertEqual(g['commitment_confidence']['level'],'not-assessed')
        finally:store.close()
    def test_native_typed_profile_rejects_unknown_property(self):
        store=NativeCandidateStore(self.translator,self.executable,self.exe_sha)
        state,_=self.translator.translate_node(self.record,self.spec)
        state['typed_properties']['values']['undeclared']='value'
        try:
            semantic=store.seal([store.semantic_draft(state)])['semantic'][0]
            self.bad(store.append,[semantic],[],{'synthetic_negative':True})
            self.assertEqual(store.files(),{})
        finally:store.close()
    def test_native_requires_rich_semantic_components(self):
        store=NativeCandidateStore(self.translator,self.executable,self.exe_sha)
        state,_=self.translator.translate_node(self.record,self.spec);state['semantic_components']=[]
        try:
            semantic=store.seal([store.semantic_draft(state)])['semantic'][0]
            self.bad(store.append,[semantic],[],{'synthetic_negative':True})
        finally:store.close()
    def test_native_project_event_relabel_cannot_replay(self):
        store=NativeCandidateStore(self.translator,self.executable,self.exe_sha)
        state,_=self.translator.translate_node(self.record,self.spec)
        draft=store.semantic_draft(state);draft['source_kind']='project-semantic-event-history'
        try:self.bad(store.seal,[draft])
        finally:store.close()
    def test_governance_wrong_exact_tuple_rejected(self):
        store=NativeCandidateStore(self.translator,self.executable,self.exe_sha)
        try:
            node,_=store.map_node(self.work);semantic=store.latest_semantic(node)
            gs=copy.deepcopy(store.latest_governance(semantic)['complete_resulting_governance_state'])
            draft=store.governance_draft(semantic,gs);draft['semantic_ref']['semantic_event_digest']='0'*64
            draft['complete_resulting_governance_state']['semantic_ref']=copy.deepcopy(draft['semantic_ref'])
            event=store.seal(governance=[draft])['governance'][0];before=store.files()
            self.bad(store.append,[],[event],{'synthetic_negative':True});self.assertEqual(store.files(),before)
        finally:store.close()
    def test_removed_representation_is_terminal(self):
        store=NativeCandidateStore(self.translator,self.executable,self.exe_sha)
        try:
            node,_=store.map_node(self.work);store.change_lifecycle(node,'removed')
            self.bad(store.change_lifecycle,node,'active')
        finally:store.close()
    def test_original_event_byte_drift_rejected(self):
        store=NativeCandidateStore(self.translator,self.executable,self.exe_sha)
        try:
            store.map_node(self.work);path=next(store.semantic.iterdir());path.write_bytes(path.read_bytes()+b' ')
            self.bad(store.read)
        finally:store.close()
    def test_closed_store_rejected(self):
        store=NativeCandidateStore(self.translator,self.executable,self.exe_sha);store.close();self.bad(store.guard)
    def test_expired_store_rejected(self):
        store=NativeCandidateStore(self.translator,self.executable,self.exe_sha);store.expires=0
        try:self.bad(store.guard)
        finally:store.close()
    def test_project_cursor_cannot_become_native_cursor(self):
        store=NativeCandidateStore(self.translator,self.executable,self.exe_sha)
        state,_=self.translator.translate_node(self.record,self.spec)
        source=self.translator.signed_source_effect(self.work)
        draft=store.semantic_draft(state);draft['semantic_cursor']=source['project_histories']['project-semantic-event-history']['cursor']
        try:
            semantic=store.seal([draft])['semantic'][0]
            self.bad(store.append,[semantic],[],{'synthetic_negative':True});self.assertEqual(store.files(),{})
        finally:store.close()
    def challenge_inputs(self):
        p=ROOT/'implementation/lab-workflows/candidates/v1/receipts/integration/W07/0001/scenarios/failure/case.json'
        case=parse(p.read_bytes())
        contract=next(r for r in case['records'] if r['kind']=='challenge-contract')
        event=next(r for r in case['records'] if r['kind']=='challenge-event' and r['version_ref'].endswith('@candidate.4'))
        implementation=next(r for r in case['records'] if r['version_ref']=='implementation:lab-W05:historical-builder@candidate.1')
        return contract,event,implementation
    def test_challenge_wrong_subject_revision_rejected(self):
        contract,event,_=self.challenge_inputs()
        store=NativeCandidateStore(self.translator,self.executable,self.exe_sha)
        try:
            node,_=store.map_node(self.work)
            self.bad(store.map_challenge,node,event,contract)
        finally:store.close()
    def test_resolved_challenge_requires_exact_source_decision(self):
        contract,event,row=self.challenge_inputs()
        view=self.adapter.represent({k:row[k] for k in ['path','sha256','kind','version_ref']})
        store=NativeCandidateStore(self.translator,self.executable,self.exe_sha)
        try:
            node,_=store.map_node(view)
            self.bad(store.map_challenge,node,event,contract)
        finally:store.close()


if __name__=='__main__':unittest.main()
