"""W07 joining guards use retained evidence, never claim fresh domain execution."""
import copy
from pathlib import Path
import unittest
from unittest.mock import patch

from integration_support import *
from integration_worker import load_retained_cases
from evaluator import BoundaryFault


class IntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.original=load_retained_cases()
    def setUp(self):self.cases=copy.deepcopy(self.original)
    def bad(self,fn,*a):
        with self.assertRaises(BoundaryFault):fn(*a)
    def case(self,name):return next(c for c in self.cases if c['domain']==name)

    def test_all_four_domains_have_separate_evidence(self):
        r=audit_join(self.cases);self.assertEqual(r['evidence_coverage'],'PASS');self.assertEqual(r['case_count'],4)
    def test_runtime_kind_mismatch_is_not_hidden(self):
        r=audit_join(self.cases);self.assertEqual(r['result'],'FLAG');self.assertEqual(len(r['runtime_kind_join_gaps']),2)
        self.assertTrue(all(x['declared_endpoint_kind']=='project' and x['selected_carrier_semantic_kind']=='project-identity' for x in r['runtime_kind_join_gaps']))
    def test_protocol_and_exact_typed_edges_separate(self):
        r=audit_join(self.cases)
        inline=[v for c in r['cases'] for v in c['closure']['inline_roles']]
        self.assertTrue(any(v['disposition']=='declared-identity-role-multiple-proposed-revisions' for v in inline))
        self.assertTrue(all(v['global_edge_created'] is False and v['exact_revision_selected'] is False for v in inline))
    def test_all_domains_required(self):self.bad(audit_join,self.cases[:3])
    def test_one_case_cannot_establish_all_domains(self):
        self.cases[1]['case_id']=self.cases[0]['case_id'];self.bad(audit_join,self.cases)
    def test_generic_persistence_cannot_prove_workflow(self):
        self.case('engineering')['facts']['actual_execution']=False;self.bad(audit_join,self.cases)
    def test_owner_outcome_cannot_be_invented(self):
        self.case('research')['actual_owner_outcome']='admit';self.bad(audit_join,self.cases)
    def test_canonical_effects_cannot_be_invented(self):
        self.case('learning')['canonical_effects_applied']=1;self.bad(audit_join,self.cases)
    def test_missing_action_permission_axis_rejected(self):
        self.case('failure')['status_axes'].pop('action_permission');self.bad(audit_join,self.cases)
    def test_progress_not_admission(self):
        self.case('engineering')['status_axes']['admission']='admitted-current';self.bad(audit_join,self.cases)
    def test_progress_not_commitment(self):
        self.case('engineering')['status_axes']['commitment']='committed';self.bad(audit_join,self.cases)
    def test_hypothesis_outcome_not_work_satisfaction(self):
        self.case('research')['status_axes']['outcome_satisfaction']='supported';self.bad(audit_join,self.cases)
    def test_status_not_action_permission(self):
        self.case('engineering')['status_axes']['action_permission']='completed';self.bad(audit_join,self.cases)
    def test_unknown_revision_cannot_resolve(self):
        self.case('learning')['records'][0]['version_ref']='artifact:invented@1';self.bad(audit_join,self.cases)
    def test_duplicate_exact_revision_rejected(self):
        c=self.case('engineering');c['records'].append(copy.deepcopy(c['records'][0]));self.bad(audit_join,self.cases)
    def test_original_byte_poison_rejected(self):
        self.case('learning')['records'][0]['sha256']='0'*64;self.bad(audit_join,self.cases)
    def test_path_escape_rejected(self):self.bad(bound,{'path':'../outside','sha256':'0'*64})
    def test_binding_is_closed(self):self.bad(bound,{'path':'README.md','sha256':'0'*64,'caller_confirmation':True})
    def test_exact_generated_code_join_required(self):
        self.case('research')['facts']['host_evaluator_sha256']='0'*64;self.bad(audit_join,self.cases)
    def test_same_failed_source_family_required(self):
        self.case('learning')['facts']['old_builder_sha256']='0'*64;self.bad(audit_join,self.cases)
    def test_exact_lesson_predecessor_required(self):
        self.case('learning')['facts']['lesson_source_W05_receipt_sha256']='0'*64;self.bad(audit_join,self.cases)
    def test_general_research_benefit_rejected(self):
        self.case('research')['facts']['Product_benefit_established']=True;self.bad(audit_join,self.cases)
    def test_cache_claim_rejected(self):
        self.case('research')['facts']['cache_enabled']=True;self.bad(audit_join,self.cases)
    def test_production_incident_claim_rejected(self):
        self.case('failure')['facts']['production_incident_claimed']=True;self.bad(audit_join,self.cases)
    def test_later_application_required(self):
        c=self.case('learning');c['records']=[r for r in c['records'] if r['kind']!='lesson-application'];self.bad(audit_join,self.cases)
    def test_later_outcome_required(self):
        c=self.case('learning');c['records']=[r for r in c['records'] if r['kind']!='lesson-outcome-assessment'];self.bad(audit_join,self.cases)
    def test_selected_proposed_postimages_are_not_globally_merged(self):
        r=audit_join(self.cases);self.assertFalse(r['global_merge_performed'])
        # The retained learning input is byte-identical to its original W05
        # source. Synthetic changed postimage metadata checks the join guard;
        # it supplies no original-byte or real workflow evidence.
        source=self.case('failure')['records'][0]
        later=next(x for x in self.case('learning')['records'] if x['version_ref']==source['version_ref'])
        later['sha256']='0'*64
        collisions=distinguish_proposed_postimages(self.cases)
        self.assertTrue(collisions);self.assertTrue(all(not v['global_merge_allowed'] for v in collisions))
    def test_no_upstream_approval_from_test_receipt(self):
        self.assertTrue(all(parse((PACKAGE/p).read_bytes())['actual_owner_outcome'] is None for p,_ in UPSTREAM.values()))


if __name__=='__main__':unittest.main()
