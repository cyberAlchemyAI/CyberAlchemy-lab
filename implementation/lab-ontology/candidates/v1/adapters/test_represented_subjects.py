"""Exact prospective mapping guards; no transaction/admission claims."""
import copy
from pathlib import Path
import unittest
from unittest.mock import patch

from represented_subjects import *


class RepresentationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manager = signed_catalog()
        cls.catalog,cls.operations = cls.manager.__enter__()
        cls.adapter = CandidateRepresentationAdapter(cls.catalog,cls.operations)
        cls.cuts = {}
        cls.views = {}
        cls.relations = {}
        for domain in ['engineering','research','failure','learning']:
            path = ROOT/f'implementation/lab-workflows/candidates/v1/receipts/integration/W07/0001/scenarios/{domain}/case.json'
            case = parse(path.read_bytes())
            cut = {'cut_id':case['case_id'],'authority_effect':'none','actual_owner_outcome':None,
                'records':[{k:r[k] for k in ['path','sha256','kind','version_ref']} for r in case['records']]}
            cls.cuts[domain] = cut
            cls.views[domain] = cls.adapter.candidate_cut(cut)
            cls.relations[domain] = cls.adapter.validate_candidate_relations(cls.views[domain])

    @classmethod
    def tearDownClass(cls):
        cls.manager.__exit__(None,None,None)

    def bad(self, fn, *args):
        with self.assertRaises(RepresentationFault):
            fn(*args)

    def row(self, kind, domain='research'):
        return copy.deepcopy(next(r for r in self.cuts[domain]['records'] if r['kind']==kind))

    def test_real_engineering_relations_pass_candidate_view(self):
        self.assertEqual(len(self.relations['engineering']),7)
    def test_real_research_relations_pass_candidate_view(self):
        self.assertEqual(len(self.relations['research']),22)
    def test_real_failure_relations_pass_candidate_view(self):
        self.assertEqual(len(self.relations['failure']),26)
    def test_real_learning_relations_pass_candidate_view(self):
        self.assertEqual(len(self.relations['learning']),15)
    def test_project_keeps_carrier_and_endpoint_axes(self):
        v=self.adapter.represent(self.row('project-identity'))
        self.assertEqual(v['carrier']['kind'],'project-identity')
        self.assertEqual(v['represented_subject']['kind'],'project')
        self.assertEqual(v['source_admission'],'candidate-unadmitted')
        self.assertFalse(v['signed_transaction_mapping_implemented'])
    def test_product_keeps_carrier_and_endpoint_axes(self):
        v=self.adapter.represent(self.row('product-identity'))
        self.assertEqual(v['carrier']['kind'],'product-identity')
        self.assertEqual(v['represented_subject']['kind'],'product')
    def test_method_keeps_candidate_carrier_posture(self):
        v=self.adapter.represent(self.row('method'))
        self.assertEqual(v['carrier']['contract_posture'],'candidate-unadmitted')
        self.assertEqual(v['carrier']['ref'],'cal.artifact-type.method/v1')
        self.assertEqual(v['represented_subject']['kind'],'method')
    def test_signed_input_keeps_original_admission(self):
        v=self.adapter.represent(self.row('product-capability'))
        self.assertEqual(v['source_admission'],'admitted-current')
        self.assertEqual(v['signed_catalog_subject_binding']['sha256'],v['carrier']['source_binding']['sha256'])
    def test_nonmapped_kind_unchanged(self):
        v=self.adapter.represent(self.row('work'))
        self.assertEqual(v['represented_subject']['kind'],'work')
        self.assertIsNone(v['mapping_proposal'])
    def test_deterministic_representation(self):
        row=self.row('project-identity')
        self.assertEqual(self.adapter.represent(row),self.adapter.represent(row))
    def test_raw_catalog_unchanged_after_mapping(self):
        self.assertEqual(object_sha(self.adapter.catalog),self.adapter.catalog_sha256)
        self.assertEqual(object_sha(self.catalog.projection),self.catalog.projection_sha256)
        for c in self.adapter.catalog['contracts'].values():
            if c['semantic_kind']=='project-identity':self.assertEqual(c['semantic_kind'],'project-identity')
    def test_no_current_global_edges_or_owner_effects(self):
        for rows in self.relations.values():
            for r in rows:
                self.assertFalse(r['confirmed_global_edge_eligible']);self.assertEqual(r['transactions_applied'],0)
                self.assertIsNone(r['actual_owner_outcome'])
    def test_caller_catalog_flag_rejected(self):
        self.bad(CandidateRepresentationAdapter,{'verified':True},self.operations)
    def test_mapping_external_pin_required(self):
        self.bad(CandidateRepresentationAdapter,self.catalog,self.operations,{'path':str(MAPPING.relative_to(ROOT)),'sha256':'0'*64})
    def test_closed_row_required(self):
        row=self.row('project-identity');row['admitted']=True
        self.bad(self.adapter.represent,row)
    def test_original_bytes_required(self):
        row=self.row('project-identity');row['sha256']='0'*64
        self.bad(self.adapter.represent,row)
    def test_wrong_carrier_kind_rejected(self):
        row=self.row('project-identity');row['kind']='product-identity'
        self.bad(self.adapter.represent,row)
    def test_undeclared_alias_rejected(self):
        row=self.row('project-identity');row['kind']='project'
        self.bad(self.adapter.represent,row)
    def test_exact_version_required(self):
        row=self.row('project-identity');row['version_ref']='project:other@1'
        self.bad(self.adapter.represent,row)
    def test_literal_version_cannot_change(self):
        row=self.row('project-identity');row['version_ref']=row['version_ref'].split('@')[0]+'@invented'
        self.bad(self.adapter.represent,row)
    def test_cut_owner_outcome_rejected(self):
        cut=copy.deepcopy(self.cuts['engineering']);cut['actual_owner_outcome']='admit'
        self.bad(self.adapter.candidate_cut,cut)
    def test_duplicate_revision_rejected(self):
        cut=copy.deepcopy(self.cuts['engineering']);cut['records'].append(copy.deepcopy(cut['records'][0]))
        self.bad(self.adapter.candidate_cut,cut)
    def test_edited_represented_kind_rejected(self):
        view=copy.deepcopy(self.views['engineering'])
        next(v for v in view['views'].values() if v['carrier']['kind']=='project-identity')['represented_subject']['kind']='product'
        self.bad(self.adapter.validate_candidate_relations,view)
    def test_edited_admission_rejected(self):
        view=copy.deepcopy(self.views['engineering']);next(iter(view['views'].values()))['source_admission']='admitted-current'
        self.bad(self.adapter.validate_candidate_relations,view)
    def test_edited_source_cut_rejected(self):
        view=copy.deepcopy(self.views['engineering']);view['source_archive_binding']['sha256']='0'*64
        self.bad(self.adapter.validate_candidate_relations,view)
    def test_endpoint_outside_exact_cut_rejected(self):
        view=copy.deepcopy(self.views['engineering'])
        ref=next(ref for ref,v in view['views'].items() if v['carrier']['kind']=='project-identity')
        del view['views'][ref]
        self.bad(self.adapter.validate_candidate_relations,view)
    def test_proposed_workflow_cuts_stay_separate(self):
        self.assertEqual(len({v['cut_id'] for v in self.views.values()}),4)
        self.assertTrue(all(v['global_merge_allowed'] is False for v in self.views.values()))
    def test_changed_catalog_rejected(self):
        modified=copy.deepcopy(self.adapter.catalog);modified['contracts'].clear()
        with patch.object(self.adapter,'catalog',modified):self.bad(self.adapter.candidate_cut,self.cuts['engineering'])
    def test_changed_replay_handle_rejected(self):
        with patch.object(self.catalog,'closed',True):self.bad(self.adapter.candidate_cut,self.cuts['engineering'])
    def test_changed_mapping_index_rejected(self):
        proposals=copy.deepcopy(self.adapter.proposals);proposals['cal.artifact-type.project-identity/v1']['endpoint_kind']='product'
        with patch.object(self.adapter,'proposals',proposals):self.bad(self.adapter.candidate_cut,self.cuts['engineering'])
    def test_path_escape_rejected(self):
        self.bad(original,{'path':'../outside','sha256':'0'*64})
    def test_json_duplicate_keys_rejected(self):
        self.bad(parse,b'{"x":1,"x":2}')
    def test_json_nonfinite_rejected(self):
        self.bad(parse,b'{"x":NaN}')


if __name__=='__main__':unittest.main()
