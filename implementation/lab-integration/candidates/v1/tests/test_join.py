"""Actual cross-component reads, explicit branch provenance and stale-scope rejection."""
import copy,json,os
from dataclasses import replace
from pathlib import Path
import shutil,subprocess,sys
from tempfile import TemporaryDirectory
import unittest

PACKAGE=Path(__file__).resolve().parents[1];ROOT=PACKAGE.parents[3]
sys.path.insert(0,str(PACKAGE))
from joined_inspection import *
from context import GeneratorPins,IMPLEMENTATION_VERSION
from lab_runtime.common import RuntimeFault,encoded
sys.path.insert(0,str(RUNTIME/'tests'));sys.path.insert(0,str(BOOTSTRAP/'tests'));sys.path.insert(0,str(CONTEXT/'tests'))
import test_transition,test_bootstrap,test_context
from lab_runtime.transition import prepare_transition,authorize_transition,apply_transition


class JoinTests(unittest.TestCase):
    observed=None
    @classmethod
    def setUpClass(cls):
        test_transition.TransitionTests.setUpClass()
        cls.addClassCleanup(test_transition.TransitionTests.tearDownClass)
        test_bootstrap.BootstrapTests.setUpClass()
        cls.addClassCleanup(test_bootstrap.BootstrapTests.tearDownClass)
        cls.addClassCleanup(test_bootstrap.BootstrapTests.doClassCleanups)
        test_context.ContextTests.setUpClass()
        cls.addClassCleanup(test_context.ContextTests.tearDownClass)
        cls.shared=TemporaryDirectory(prefix='lab-c09-joined-fixture-',dir=os.environ.get('C09_FIXTURE_ROOT'));cls.addClassCleanup(cls.shared.cleanup)
        cls.root=Path(cls.shared.name)
        transition=test_transition.TransitionTests
        cls.transition_policy=LocalPolicy('role:test-only',transition.public_key,'c09-reconstructed',str(cls.root/'transition'),'scope:c09-isolated','2099-01-01T00:00:00Z')
        prepared=prepare_transition(transition.parent,transition.selection,transition.selections,transition.mapping_path,transition.mapping_sha,cls.transition_policy)
        response=authorize_transition(prepared,cls.transition_policy,transition.private)
        outcome=apply_transition(transition.parent,transition.selection,prepared,response,transition.mapping_path,cls.transition_policy)
        cls.transition_pins=BranchPins(**outcome['pins'])
        instance=test_bootstrap.BootstrapTests(methodName='test_02_bootstrap_and_fresh_process');instance.setUp();cls.addClassCleanup(instance.doCleanups)
        cls.catalog_instance=instance
        _,_,_,cls.catalog_pins=instance.initialized();cls.catalog_policy=instance.policy
        cls.catalog_path=Path(cls.catalog_policy.destination)
        cls.parent_bindings=test_transition.committed_files(transition.parent,transition.parent.verify_full())
        cls.source=test_context.ContextTests.source
        cls.manifest=test_context.ContextTests.manifest;cls.generator_pins=test_context.ContextTests.generator_pins
        cls.native=test_context.ContextTests.native
    def setUp(self):
        self.temp=TemporaryDirectory(prefix='lab-c09-joined-case-',dir=os.environ.get('C09_FIXTURE_ROOT'));self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'project';shutil.copytree(self.source.fixture,self.path)
        self.project=VerifiedLegacyReadStore(self.path,self.source.repository,ROOT,self.source.pins)
        self.pins=JoinPins(self.source.row['profile_sha256'],self.source.snapshot['snapshot_digest'],self.project.verify_full()['head']['transaction_digest'],self.catalog_instance.cat['digest'],self.transition_pins.head_digest)
        self.options={'generator_manifest':self.manifest,'generator_pins':self.generator_pins,'owner_ref':'principal:repository-owner@candidate.1','context_ref':'context:cyberalchemy-v2-to-lab-migration','scope_ref':'project:cyberalchemy-v2-to-lab-migration','capability_ref':'product-capability:cyberalchemy-lab:governed-knowledge-lifecycle','expected_profile_sha256':self.pins.source_profile_sha256,'expected_snapshot_digest':self.pins.source_snapshot_digest,'subject_ref':'product:cyberalchemy-lab'}
    def inspect(self,pins=None):
        return inspect_successor(self.project,self.source.snapshot,self.catalog_path,self.catalog_pins,self.catalog_policy,self.transition_policy.destination,self.transition_pins,self.transition_policy,self.native,pins or self.pins,context_options=self.options)
    def test_joined_realistic_predecision_inspection(self):
        result=self.inspect();JoinTests.observed=copy.deepcopy(result)
        self.assertEqual(result['catalog_summary'],{'contract_versions':144,'source_subjects':485,'candidate_subjects':6,'relation_kinds':41})
        self.assertEqual(len(result['reconstructed_candidates']),1)
        self.assertEqual(result['session_closure']['short_memory_erased'],True)
        self.assertIsNone(result['actual_owner_outcome']);self.assertFalse(result['real_work_satisfaction_claimed'])
        self.assertEqual(result['action_permission'],'none')
        self.assertEqual(self.parent_bindings,test_transition.committed_files(test_transition.TransitionTests.parent,test_transition.TransitionTests.parent.verify_full()))
    def test_wrong_source_profile_or_snapshot_cannot_join(self):
        for key in ['source_profile_sha256','source_snapshot_digest']:
            with self.assertRaisesRegex(RuntimeFault,'joined source'):self.inspect(replace(self.pins,**{key:'0'*64}))
    def test_wrong_catalog_and_transition_pins_cannot_join(self):
        for key in ['catalog_digest','transition_head_digest']:
            with self.assertRaisesRegex(RuntimeFault,'joined .* mismatch'):self.inspect(replace(self.pins,**{key:'0'*64}))
    def test_wrong_project_head_cannot_join(self):
        with self.assertRaisesRegex(RuntimeFault,'Project state source/head mismatch'):self.inspect(replace(self.pins,project_head='0'*64))
    def test_context_source_claim_cannot_override_join(self):
        self.options['expected_snapshot_digest']='0'*64
        with self.assertRaisesRegex(RuntimeFault,'context selected a different joined source'):self.inspect()
    def test_fresh_process_joined_reconstruction(self):
        before=self.inspect()
        body={'project_path':str(self.path),'repository':str(self.source.repository),'project_pins':vars(self.source.pins),'snapshot':self.source.snapshot,'catalog_path':str(self.catalog_path),'catalog_pins':vars(self.catalog_pins),'catalog_policy':vars(self.catalog_policy),'transition_path':self.transition_policy.destination,'transition_pins':vars(self.transition_pins),'transition_policy':vars(self.transition_policy),'native_semantic':str(self.native.semantic_directory),'native_governance':str(self.native.governance_directory),'native_request':self.native.request,'native_executable':str(self.native.executable),'native_pins':vars(self.native.pins),'join_pins':vars(self.pins),'context_options':{**self.options,'generator_manifest':str(self.manifest),'generator_pins':vars(self.generator_pins)}}
        file=Path(self.temp.name)/'cold-join.json';file.write_bytes(encoded(body))
        result=subprocess.run([sys.executable,str(PACKAGE/'cold_join.py'),str(file)],capture_output=True,text=True,timeout=90)
        self.assertEqual(result.returncode,0,result.stderr);cold=json.loads(result.stdout)
        self.assertEqual(cold['catalog_digest'],self.pins.catalog_digest);self.assertEqual(cold['project_state_digest'],digest(before['project_state']))
        self.assertEqual(cold['memory_erased'],True);self.assertEqual(cold['candidate_postures'],['candidate-reconstructed','candidate-unadmitted'])
