"""A real isolated publication invalidates a previously verified context."""
import copy,json,os,shutil,sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

PACKAGE=Path(__file__).resolve().parents[1];ROOT=PACKAGE.parents[3];sys.path.insert(0,str(PACKAGE))
from joined_inspection import *
from context import GeneratorPins,IMPLEMENTATION_VERSION
from lab_runtime.common import RuntimeFault
from lab_runtime.profiles import select
from lab_runtime.sources import capture
from lab_runtime.replay import ReplayPins
from lab_runtime.publisher import PublicationPins,owner_response,verify_bundle,repair_publication
sys.path.insert(0,str(RUNTIME/'tests'));sys.path.insert(0,str(CONTEXT/'tests'))
import test_promotion
from test_replay import Store,keygen
from native_fixture import fixture


class PublicationJoinTests(unittest.TestCase):
    observed=None
    @classmethod
    def setUpClass(cls):
        test_promotion.PromotionTests.setUpClass();cls.addClassCleanup(test_promotion.PromotionTests.tearDownClass)
    def test_publication_invalidates_context_and_preserves_committed_bundle(self):
        case=test_promotion.PromotionTests(methodName='test_one_response_complete_carriers_and_cold_replay');case.setUp();self.addCleanup(case.tearDown)
        snapshot=capture(case.selection)
        root=case.root/'context-input';root.mkdir()
        private=root/'context-test.pem';public=root/'context-test.pub';keygen(private,public)
        project_path=root/'project';Store(project_path,case.repo).initialize(load(ROOT/'implementation/lab-runtime/v2/profile.json'),'c09-publication-context','role:test-only',public.read_text().strip())
        binding=RUNTIME/'design/legacy-runtime-bindings.json'
        pins=ReplayPins('v2',binding.relative_to(ROOT).as_posix(),byte_digest(binding.read_bytes()),byte_digest((project_path/'config.json').read_bytes()),load(project_path/'baseline.json')['snapshot_digest'])
        project=VerifiedLegacyReadStore(project_path,case.repo,ROOT,pins)
        native_root=root/'native';native_root.mkdir();native=fixture(native_root,Path(os.environ['LAB_C08_NATIVE_EXECUTABLE']),snapshot)
        manifest=ROOT/os.environ['LAB_C08_GENERATOR_MANIFEST']
        options={'generator_manifest':manifest,'generator_pins':GeneratorPins(byte_digest(manifest.read_bytes()),IMPLEMENTATION_VERSION),'owner_ref':'principal:repository-owner@candidate.1','context_ref':'context:cyberalchemy-v2-to-lab-migration','scope_ref':'project:cyberalchemy-v2-to-lab-migration','capability_ref':'product-capability:cyberalchemy-lab:governed-knowledge-lifecycle','expected_profile_sha256':snapshot['source_profile_sha256'],'expected_snapshot_digest':snapshot['snapshot_digest'],'subject_ref':'product:cyberalchemy-lab'}
        session=ContextSession(project,snapshot,native,**options);self.addCleanup(session.close)
        before=session.context();session.note('private context before fixture publication')
        prepared=case.prepare();response=owner_response(prepared,case.authority,case.owner_private)
        outcome=case.apply(prepared,response);publication=PublicationPins(**outcome['pins'])
        verified=verify_bundle(case.repo/case.authority.bundle_path,publication,case.authority)
        self.assertTrue(verified['cold_verified']);self.assertTrue(outcome['committed'])
        with self.assertRaisesRegex(RuntimeFault,'source changed'):session.context()
        self.assertTrue(session.closed);self.assertEqual(session.core._memory,[])
        repaired=repair_publication(publication,case.authority)
        after=verify_bundle(case.repo/case.authority.bundle_path,publication,case.authority)
        self.assertEqual(after['files'],verified['files'])
        PublicationJoinTests.observed={'fixture_only':True,'actual_owner_outcome':None,'source_context_digest':before['pack_digest'],'publication_pins':vars(publication),'immutable_governance_postimages':len([n for n in verified['files'] if n.startswith('instances/governance/') and n.endswith('.json')]),'previous_session_invalidated':True,'short_memory_erased':True,'committed_bundle_retained':True,'recovery':repaired,'new_owner_response_required':False,'live_repository_admissions':0}
