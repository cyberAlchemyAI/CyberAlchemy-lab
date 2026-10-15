"""Strict signed joins and independent candidate/source status guard checks."""
import unittest
from unittest.mock import patch
from successor import *


class SignedJoinGuards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stack=ExitStack();cls.addClassCleanup(cls.stack.close);cls.selected=selection();cls.cases0=original_cases(cls.selected)
        cls.witnesses={r['domain']:cls.stack.enter_context(signed_witness(r,cls.selected)) for r in cls.selected['signed_coupling_witnesses']}
        cls.baseline=parent.audit_join(cls.cases0)
    def setUp(self):
        self.cases=copy.deepcopy(self.cases0);self.case=next(c for c in self.cases if c['domain']=='engineering')
        self.gap=copy.deepcopy(next(c for c in self.baseline['cases'] if c['domain']=='engineering')['closure']['runtime_kind_join_gaps'][0])
        original=self.witnesses['engineering'];self.witness={**original,'data':copy.deepcopy(original['data']),
            'expected':copy.deepcopy(original['expected']),'result':copy.deepcopy(original['result']),'metadata':copy.deepcopy(original['metadata']),
            'row':copy.deepcopy(original['row']),'manifest':copy.deepcopy(original['manifest'])}
    def endpoint(self):return self.witness['data']['projection']['subjects'][self.gap['endpoint_ref']]
    def relation(self):return self.witness['data']['projection']['subjects'][self.gap['relation_ref']]
    def close(self):return close_gap(self.case,self.gap,self.witness)
    def reject(self):
        with self.assertRaises(Exception):self.close()
    def test_two_exact_gaps_have_independent_signed_witnesses(self):
        for case in self.cases:
            if case['domain'] in self.witnesses:
                gap=next(c for c in self.baseline['cases'] if c['domain']==case['domain'])['closure']['runtime_kind_join_gaps'][0]
                result=close_gap(case,gap,self.witnesses[case['domain']]);self.assertEqual(result['result'],'PASS')
                self.assertEqual(len(set(result['independent_decision_refs'])),3)
    def test_original_cases_are_not_promoted_by_signed_witness(self):
        result=self.close();self.assertEqual(result['original_case_admission'],'candidate-unadmitted')
        self.assertEqual(result['signed_witness_admission'],'local-admitted-current');self.assertEqual(self.case['status_axes']['admission'],'candidate-unadmitted')
    def test_raw_carrier_and_represented_endpoint_separate(self):
        result=self.close();p=next(v for v in result['endpoint_views'] if v['version_ref']==self.gap['endpoint_ref'])
        self.assertEqual(p['carrier_kind'],'project-identity');self.assertEqual(p['source_projection_kind'],'project-identity')
        self.assertEqual(p['represented_endpoint_kind'],'project');self.assertFalse(p['raw_subject_rewritten'])
    def test_candidate_global_merge_and_authority_absent(self):
        result=self.close();self.assertFalse(result['unqualified_global_merge']);self.assertIsNone(result['actual_owner_outcome'])
        self.assertEqual(result['canonical_effects_applied'],0);self.assertEqual(result['original_domain_effects_reexecuted'],0)
    def test_signed_scope_and_original_record_domains_retained(self):
        result=self.close();self.assertEqual(result['signed_scope_ref'],'project:cyberalchemy-v2-to-lab-migration')
        self.assertEqual(self.endpoint()['record']['project_id'],result['signed_scope_ref'])
        self.assertNotIn('scope_ref',self.endpoint()['record'])
        view=next(v for v in result['endpoint_views'] if v['version_ref']==self.gap['endpoint_ref'])
        self.assertEqual(view['record_scope_basis']['field'],'project_id')
        self.assertEqual(view['record_scope_basis']['coordination_scope'],self.endpoint()['record']['coordination_scope'])
    def test_predecessor_flag_preserved(self):
        self.assertEqual(self.baseline['result'],'FLAG');self.assertEqual(len(self.baseline['runtime_kind_join_gaps']),2)
    def test_four_original_independent_workflow_cases_retained(self):
        self.assertEqual(len(self.cases),4);self.assertEqual({c['domain'] for c in self.cases},EXPECTED_DOMAINS)
        self.assertEqual(len({c['case_id'] for c in self.cases}),4)
    def test_foreign_exact_case_refused(self):self.case['case_id']+='-unreviewed';self.reject()
    def test_other_domain_witness_refused(self):self.witness['row']['domain']='research';self.reject()
    def test_changed_exact_relation_refused(self):self.gap['relation_ref']='unreviewed@1';self.reject()
    def test_changed_signed_relation_body_refused(self):self.relation()['record']['name']='forged';self.reject()
    def test_unadmitted_relation_refused(self):self.relation()['effective_state']='candidate-unadmitted';self.reject()
    def test_withdrawn_relation_refused(self):self.relation()['effective_state']='local-withdrawn';self.reject()
    def test_changed_relation_category_refused(self):self.relation()['category']='artifact-instance';self.reject()
    def test_missing_endpoint_refused(self):self.witness['data']['projection']['subjects'].pop(self.gap['endpoint_ref']);self.reject()
    def test_changed_endpoint_body_refused(self):self.endpoint()['record']['name']='forged';self.reject()
    def test_changed_endpoint_identity_refused(self):self.endpoint()['identity']='project:forged';self.reject()
    def test_changed_raw_carrier_kind_refused(self):self.endpoint()['kind']='project';self.reject()
    def test_changed_endpoint_carrier_refused(self):self.endpoint()['carrier_ref']='cal.artifact-type.work/v1';self.reject()
    def test_unadmitted_endpoint_refused(self):self.endpoint()['effective_state']='candidate-unadmitted';self.reject()
    def test_withdrawn_endpoint_refused(self):self.endpoint()['effective_state']='local-withdrawn';self.reject()
    def test_changed_endpoint_transaction_source_refused(self):self.endpoint()['source']['sha256']='0'*64;self.reject()
    def test_changed_original_endpoint_binding_refused(self):
        r=next(r for r in self.witness['metadata']['selected_records'] if r['version_ref']==self.gap['endpoint_ref']);r['source_binding']['sha256']='0'*64;self.reject()
    def test_rewritten_endpoint_witness_refused(self):
        r=next(r for r in self.witness['metadata']['selected_records'] if r['version_ref']==self.gap['endpoint_ref']);r['record_rewritten']=True;self.reject()
    def test_rewritten_relation_witness_refused(self):
        r=next(r for r in self.witness['metadata']['selected_records'] if r['version_ref']==self.gap['relation_ref']);r['record_rewritten']=True;self.reject()
    def test_missing_signed_endpoint_postimage_refused(self):self.witness['result']['exact_targets'].pop();self.reject()
    def test_collapsed_decision_cores_refused(self):
        cores=self.witness['data']['transactions'][-1]['decision_cores'];cores[0]['decision_ref']=cores[1]['decision_ref'];self.reject()
    def test_changed_decision_subject_refused(self):
        self.witness['data']['transactions'][-1]['decision_cores'][0]['version_ref']='forged@1';self.reject()
    def test_wrong_endpoint_mapping_binding_refused(self):self.witness['manifest']['mapping_binding']['sha256']='0'*64;self.reject()
    def test_wrong_original_carrier_gap_refused(self):self.gap['selected_carrier_semantic_kind']='project';self.reject()
    def test_wrong_declared_endpoint_kind_refused(self):self.gap['declared_endpoint_kind']='work';self.reject()
    def test_withdrawn_carrier_refused(self):
        self.witness['data']['projection']['contracts'][self.endpoint()['carrier_ref']]['lifecycle_state']='local-withdrawn';self.reject()
    def test_changed_descriptor_binding_refused(self):
        self.witness['data']['projection']['contracts'][self.endpoint()['carrier_ref']]['artifact_sha256']='0'*64;self.reject()
    def test_changed_mapping_definition_eligibility_refused(self):
        c=self.witness['data']['projection']['contracts'][self.endpoint()['carrier_ref']]
        self.witness['data']['projection']['subjects'][c['semantic_definition_refs'][0]]['effective_state']='local-withdrawn';self.reject()
    def test_unknown_qualifier_contract_refused(self):
        ref=self.relation()['record']['payload']['relation_kind_ref'];self.witness['data']['projection']['relation_contracts'][ref]['payload']['qualifier_contract']['required_axes'].append('unreviewed');self.reject()
    def test_wrong_ordered_endpoint_pair_refused(self):
        ref=self.relation()['record']['payload']['relation_kind_ref'];self.witness['data']['projection']['relation_contracts'][ref]['payload']['allowed_endpoint_pairs']=[];self.reject()
    def test_selection_pin_drift_refused(self):
        import successor
        with patch.object(successor,'SELECTION_SHA','0'*64):
            with self.assertRaises(Exception):selection()


if __name__=='__main__':unittest.main()
