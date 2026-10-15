"""Whole selected-source adapter checks; no Agent or host grant is created."""
import copy
import unittest
from .base import *
from .reader import SelectedReader

class Checks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reader=SelectedReader(cls.adapter_pin)
        cls.context=cls.reader.open_signed(SOURCE_PIN,PACKAGE_PIN)
        cls.selected=cls.context.__enter__()
        cls.view=cls.selected.view
    @classmethod
    def tearDownClass(cls):
        cls.context.__exit__(None,None,None)
    def test_01_selected_new_episode(self):
        s=self.selected
        self.assertEqual(s.view.data['head']['sequence'],2)
        self.assertIn(records.PRINCIPAL+'@'+records.VERSION,s.view.subjects)
        self.assertIn(records.ASSIGNMENT+'@'+records.VERSION,s.view.subjects)
        self.assertEqual(s.selected['candidate_selection_basis']['adapter_source_sha256'],self.adapter_pin)
    def test_02_wrong_independent_pins_refused(self):
        with self.assertRaises(ValueError):SelectedReader('0'*64)
        with self.assertRaises(ValueError):self.reader.package('0'*64,PACKAGE_PIN)
        with self.assertRaises(ValueError):self.reader.package(SOURCE_PIN,'0'*64)
        with self.assertRaises(ValueError):self.reader.selection(SOURCE_PIN,PACKAGE_PIN,'unselected')
    def test_03_all23_original_bodies(self):
        subjects=[s for s in self.view.subjects.values() if s['source'].get('encoding')==self.view.handle.custody.ENCODING]
        self.assertEqual(len(subjects),23)
        from . import model
        for subject in subjects:
            raw,_,_,_=model.record_bytes(self.view,subject)
            self.assertEqual(sha(raw),subject['source']['sha256'])
            self.assertEqual(parse(raw),subject['record'])
            self.assertNotEqual(raw,self.view.handle.common.encoded(subject['record']))
    def test_04_same_cut_exact_current_records(self):
        self.assertEqual(self.selected.sources.source_cut,cut(self.view))
        self.assertTrue(self.selected.records)
        for row in self.selected.records:
            self.assertEqual(self.selected.sources.get(row.artifact).original,row.original)
            self.assertIn(row.posture,self.reader.adapter.CURRENT)
            self.assertEqual(row.artifact['scope_ref'],self.view.data['config']['scope_ref'])
    def test_05_closure_no_inferred_authority(self):
        report=self.selected.closure_report()
        self.assertEqual(report['accounted_subjects'],len(self.view.subjects))
        self.assertEqual(report['included_current_instances'],len(self.selected.records))
        self.assertEqual(report['missing_current_carriers'],[])
        self.assertEqual(report['instance_bound_assignments'],[])
        self.assertEqual(report['authority_effect'],'none')
        self.assertIsNone(report['actual_owner_outcome'])
        self.assertFalse(report['fresh_Session_participation_established'])
        self.assertFalse(report['context_or_ontology_views_generated'])
    def test_06_catalog_not_agent_participation(self):
        refs={row.artifact['version_ref'] for row in self.selected.records}
        for subject in self.view.subjects.values():
            if subject['category'] in self.reader.adapter.EXCLUDED_CATEGORIES:
                self.assertNotIn(subject['version_ref'],refs)
        self.assertFalse(any(row.artifact['carrier_ref'] in ['cal.artifact-type.agent-instance/v1','cal.artifact-type.agent-session/v1'] for row in self.selected.records))
    def test_07_mutated_record_refused(self):
        row=self.selected.records[0];old=copy.deepcopy(row.artifact)
        try:
            row.artifact['byte_sha256']='0'*64
            with self.assertRaises(ValueError):self.selected.guard()
        finally:row.artifact.clear();row.artifact.update(old)
        self.selected.guard()
    def test_08_mutated_selection_refused(self):
        old=self.view.selected['config_sha256']
        try:
            self.view.selected['config_sha256']='0'*64
            with self.assertRaises(ValueError):self.selected.guard()
        finally:self.view.selected['config_sha256']=old
        self.selected.guard()
    def test_09_mutated_source_cut_refused(self):
        old=self.selected.source_cut['commit_sha256']
        try:
            self.selected.source_cut['commit_sha256']='0'*64
            with self.assertRaises(ValueError):self.selected.guard()
        finally:self.selected.source_cut['commit_sha256']=old
        self.selected.guard()
    def test_10_mutated_schema_validator_refused(self):
        validator=next(iter(self.selected.sources.validators.values()));old=copy.deepcopy(validator.schema)
        try:
            validator.schema['title']='altered unselected schema'
            with self.assertRaises(ValueError):self.selected.guard()
        finally:validator.schema.clear();validator.schema.update(old)
        self.selected.guard()
    def test_11_mutated_configuration_refused(self):
        old=self.view.data['config']['store_id']
        try:
            self.view.data['config']['store_id']='store:unselected'
            with self.assertRaises(ValueError):self.selected.guard()
        finally:self.view.data['config']['store_id']=old
        self.selected.guard()
    def test_12_mutated_original_closure_refused(self):
        path=next(iter(self.view.originals));old=self.view.originals[path]
        try:
            self.view.originals[path]=old+b' '
            with self.assertRaises(ValueError):self.selected.guard()
        finally:self.view.originals[path]=old
        self.selected.guard()
    def test_13_private_memory_denied(self):
        from . import eligibility
        with self.assertRaises(eligibility.EligibilityFault):
            eligibility.no_private_memory({'short_memory':['private fixture']})
    def test_14_same_new_principal_assignment_body(self):
        principal=next(r for r in self.selected.records if r.artifact['identity_ref']==records.PRINCIPAL)
        assignment=next(r for r in self.selected.records if r.artifact['identity_ref']==records.ASSIGNMENT)
        self.assertEqual(parse(principal.original)['node_id'],records.PRINCIPAL)
        body=parse(assignment.original)
        self.assertEqual(body['payload']['period'],records.PERIOD)
        self.assertEqual(body['payload']['eligible_agent_ref'],records.PROFILE+'@'+records.VERSION)
    def test_15_closed_adapter_refused(self):
        other=self.reader.adapter.SignedSources(self.view,SOURCE_PIN,
            selection_reader=lambda name:self.reader.selection(SOURCE_PIN,PACKAGE_PIN,name))
        other.close()
        with self.assertRaises(ValueError):other.guard()
        self.selected.guard()

