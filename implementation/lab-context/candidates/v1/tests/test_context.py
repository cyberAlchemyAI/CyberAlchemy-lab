"""C08 governed carrier production and native history integration checks."""
import copy,json,os,subprocess
from dataclasses import replace
from pathlib import Path
import shutil,sys
from tempfile import TemporaryDirectory
import unittest
PACKAGE=Path(__file__).resolve().parents[1];ROOT=PACKAGE.parents[3]
sys.path.insert(0,str(PACKAGE));sys.path.insert(0,str(ROOT/'implementation/lab-runtime/candidates/repeatable-operation/tests'));sys.path.insert(0,str(PACKAGE/'tests'))
from context import *
from lab_runtime.common import RuntimeFault
from native_fixture import fixture,seal
from native_reader import closure
from test_session import SessionTests,Clock


class ContextTests(unittest.TestCase):
    observed=[]
    @classmethod
    def setUpClass(cls):
        SessionTests.setUpClass()
        cls.source=SessionTests
        cls.executable=Path(os.environ['LAB_C08_NATIVE_EXECUTABLE'])
        cls.manifest=ROOT/os.environ['LAB_C08_GENERATOR_MANIFEST']
        cls.generator_pins=GeneratorPins(byte_digest(cls.manifest.read_bytes()),IMPLEMENTATION_VERSION)
        cls.native_temp=TemporaryDirectory(prefix='lab-native-master-fixture-')
        cls.native=fixture(Path(cls.native_temp.name),cls.executable,cls.source.snapshot)
    @classmethod
    def tearDownClass(cls):
        cls.native_temp.cleanup();SessionTests.tearDownClass()
    def setUp(self):
        self.temp=TemporaryDirectory(prefix='lab-exact-context-case-');self.root=Path(self.temp.name)
        self.store_path=self.root/'store';shutil.copytree(self.source.fixture,self.store_path)
        self.adapter=__import__('lab_runtime.store',fromlist=['VerifiedLegacyReadStore']).VerifiedLegacyReadStore(self.store_path,self.source.repository,ROOT,self.source.pins)
        self.native_root=self.root/'native';shutil.copytree(Path(self.native_temp.name),self.native_root)
        self.native_store=NativeReadStore(self.native_root/'semantic',self.native_root/'governance',self.native.request,self.executable,self.native.pins)
        self.clock=Clock();self.sessions=[]
    def tearDown(self):
        for session in self.sessions:session.close()
        self.temp.cleanup()
    def session(self,**kwargs):
        args={'generator_manifest':self.manifest,'generator_pins':self.generator_pins,'owner_ref':'principal:repository-owner@candidate.1','context_ref':'context:cyberalchemy-v2-to-lab-migration','scope_ref':'project:cyberalchemy-v2-to-lab-migration','capability_ref':'product-capability:cyberalchemy-lab:governed-knowledge-lifecycle','expected_profile_sha256':self.source.row['profile_sha256'],'expected_snapshot_digest':self.source.snapshot['snapshot_digest'],'subject_ref':'product:cyberalchemy-lab','clock':self.clock,'wall_clock':lambda:1791424453.0,'references':{'assignment_ref':'agent-assignment:first-governed-agent-episode@candidate.1','profile_ref':'agent-profile:governed-repository-candidate-authoring@candidate.1'}}
        args.update(kwargs);session=ContextSession(self.adapter,self.source.snapshot,self.native_store,**args);self.sessions.append(session);return session
    def test_actual_carriers_and_exact_closure(self):
        pack=self.session().context();self.observed.append(copy.deepcopy(pack))
        self.assertEqual(len(pack['candidate_artifacts']),7)
        for kind,record in pack['candidate_artifacts'].items():validate(record,kind,self.source.snapshot)
        for row in pack['resolved_references']:self.assertTrue(row['governed_claim']);self.assertIn(row['version_ref'],self.source.snapshot['subjects'])
        for row in pack['candidate_references']:self.assertFalse(row['governed_claim'])
        self.assertEqual(pack['context_view']['context_version_ref'],'context:cyberalchemy-v2-to-lab-migration@foundation.1')
        self.assertEqual(pack['action_permission'],'none')
    def test_generator_artifacts_are_frozen_package_bytes(self):
        s=self.session();p=s.context();manifest=load(self.manifest)
        self.assertEqual(p['candidate_artifacts']['implementation'],load(ROOT/manifest['implementation_record']['path']))
        self.assertEqual(p['candidate_artifacts']['typed-relation'],load(ROOT/manifest['realization_record']['path']))
        s.close();other=self.session();self.assertEqual(p['generator_provenance'],other.context()['generator_provenance'])
    def test_native_cut_is_independent_of_project_history(self):
        p=self.session().context();self.assertEqual(p['ontology_cut']['payload']['semantic_cursor'],3)
        self.assertTrue(all(v['cursor']!=3 for v in p['project_history_bindings'].values()))
        self.assertEqual(p['native_input_pins']['governance_cursor'],3)
        self.assertEqual(len(p['native_ontology']['governed_nodes']),2)
        self.assertFalse(p['ontology_view']['payload']['replay_source'])
    def test_exact_generator_not_related_implementation_alias(self):
        p=self.session(references={'implementation_ref':'implementation:cyberalchemy-lab:operational-runtime:v1@decision-0075'}).context()
        g=p['generator_provenance'];self.assertEqual(g['implementation_version_ref'],IMPLEMENTATION_VERSION)
        self.assertEqual(g['implementation_posture'],'candidate-unadmitted');self.assertNotEqual(g['package_version'],g['implementation_version_ref'])
    def test_unknown_assignment_reported_without_permission(self):
        p=self.session(references={'assignment_ref':'role:assigned-worker'}).context()
        self.assertTrue(any(x['reference']=='role:assigned-worker' and not x['governed_claim'] for x in p['reference_diagnostics']))
        self.assertEqual(p['action_permission'],'none')
    def test_missing_required_owner_and_context_reject(self):
        for kwargs in [{'owner_ref':'role:repository-owner'},{'context_ref':'context:unknown'},{'scope_ref':'product:cyberalchemy-lab'}]:
            with self.assertRaisesRegex(RuntimeFault,'unresolved'):self.session(**kwargs)
    def test_native_history_change_erases_memory(self):
        s=self.session();s.note('native-private-note');path=next((self.native_root/'semantic').iterdir());path.write_bytes(path.read_bytes()+b'\n')
        with self.assertRaisesRegex(RuntimeFault,'native semantic history changed'):s.context()
        self.assertTrue(s.closed);self.assertEqual(s.core._memory,[]);self.assertIsNone(s._pack)
    def test_governance_history_change_erases_memory(self):
        s=self.session();s.note('governance-private-note');path=next((self.native_root/'governance').iterdir());path.unlink()
        with self.assertRaisesRegex(RuntimeFault,'native governance history changed'):s.context()
        self.assertEqual(s.core._memory,[])
    def test_native_resealed_tamper_rejected_by_actual_runtime(self):
        path=next((self.native_root/'governance').iterdir());event=load(path);event['semantic_ref']['semantic_event_digest']='b'*64;event['complete_resulting_governance_state']['semantic_ref']=event['semantic_ref'];event=seal(self.executable,{'semantic':[],'governance':[event]})['governance'][0];path.write_bytes((json.dumps(event,ensure_ascii=False,separators=(",",":"))+"\n").encode())
        pins=replace(self.native.pins,governance_files_digest=digest({n:byte_digest(v) for n,v in closure(self.native_root/'governance').items()}))
        adapter=NativeReadStore(self.native_root/'semantic',self.native_root/'governance',self.native.request,self.executable,pins)
        with self.assertRaisesRegex(RuntimeFault,'native replay rejected'):adapter.read()
    def test_project_cursor_cannot_replace_native_selector(self):
        request=copy.deepcopy(self.native.request);request['selector']['semantic_cursor']=2
        adapter=NativeReadStore(self.native_root/'semantic',self.native_root/'governance',request,self.executable,self.native.pins)
        with self.assertRaisesRegex(RuntimeFault,'request pin mismatch'):adapter.read()
    def test_governance_prefix_must_be_exact(self):
        request=copy.deepcopy(self.native.request);request['governance_cursor']=2
        pins=replace(self.native.pins,request_sha256=byte_digest(encoded(request)),governance_cursor=2)
        adapter=NativeReadStore(self.native_root/'semantic',self.native_root/'governance',request,self.executable,pins)
        with self.assertRaisesRegex(RuntimeFault,'GOVERNANCE_PREFIX_PIN_MISMATCH'):adapter.read()
    def test_ephemeral_notes_do_not_enter_carriers_or_next_session(self):
        s=self.session();s.note('C08 secret scratch');p=s.context();self.assertNotIn('C08 secret scratch',json.dumps(p));s.close();other=self.session();self.assertEqual(other.core._memory,[]);self.assertNotEqual(s.instance_id,other.instance_id)
    def test_expiry_erases(self):
        s=self.session(ttl=1);s.note('expires');self.clock.value+=2
        with self.assertRaisesRegex(RuntimeFault,'expired'):s.context()
        self.assertEqual(s.core._memory,[]);self.assertIsNone(s._pack)
    def test_candidate_pack_is_detached(self):
        s=self.session();p=s.context();p['context_view']['authority_effect']='admission';self.assertEqual(s.context()['context_view']['authority_effect'],'none')
    def test_budget_rejects(self):
        for kwargs in [{'max_items':1},{'max_bytes':100}]:
            with self.assertRaisesRegex(RuntimeFault,'budget'):self.session(**kwargs)
    def test_false_generator_pin_rejects(self):
        with self.assertRaisesRegex(RuntimeFault,'manifest pin mismatch'):self.session(generator_pins=GeneratorPins('0'*64,IMPLEMENTATION_VERSION))
    def test_schema_changed_bytes_cannot_reuse_compilation(self):
        changed=copy.deepcopy(self.source.snapshot);c=changed['contracts'][CARRIERS['context-view']];raw=base64.b64decode(changed['byte_contents'][c['schema_path']]);schema=loads(raw);schema['properties']['status']={'const':'forged'};raw=encoded(schema);c['schema_sha256']=byte_digest(raw);changed['byte_contents'][c['schema_path']]=base64.b64encode(raw).decode()
        p=self.session().context()
        with self.assertRaisesRegex(RuntimeFault,'carrier invalid'):validate(p['context_view'],'context-view',changed)
    def test_native_executable_and_extra_event_bytes_reject(self):
        adapter=NativeReadStore(self.native_root/'semantic',self.native_root/'governance',self.native.request,self.executable,replace(self.native.pins,executable_sha256='0'*64))
        with self.assertRaisesRegex(RuntimeFault,'native executable changed'):adapter.read()
        (self.native_root/'semantic'/'extra.txt').write_text('unexpected')
        with self.assertRaisesRegex(RuntimeFault,'unexpected material'):self.native_store.read()
    def test_read_consumer_has_no_effect_methods(self):
        s=self.session()
        for name in ['apply','authorize','dispatch','persist','install']:self.assertFalse(hasattr(s,name))
    def test_fresh_process_context_reconstruction(self):
        s=self.session();s.note('memory cannot cross process');p=s.context()
        options={'owner_ref':'principal:repository-owner@candidate.1','context_ref':'context:cyberalchemy-v2-to-lab-migration','scope_ref':'project:cyberalchemy-v2-to-lab-migration','capability_ref':'product-capability:cyberalchemy-lab:governed-knowledge-lifecycle','expected_profile_sha256':self.source.row['profile_sha256'],'expected_snapshot_digest':self.source.snapshot['snapshot_digest'],'subject_ref':'product:cyberalchemy-lab'}
        body={'store_path':str(self.store_path),'repository':str(self.source.repository),'store_pins':vars(self.source.pins),'semantic_directory':str(self.native_store.semantic_directory),'governance_directory':str(self.native_store.governance_directory),'native_request':self.native_store.request,'native_executable':str(self.executable),'native_pins':vars(self.native_store.pins),'generator_manifest':str(self.manifest),'generator_pins':vars(self.generator_pins),'source_snapshot':self.source.snapshot,'options':options}
        file=self.root/'cold-context-input.json';file.write_bytes(encoded(body))
        process=subprocess.run([sys.executable,str(PACKAGE/'cold_probe.py'),str(file)],capture_output=True,text=True,timeout=60)
        self.assertEqual(process.returncode,0,process.stderr);result=json.loads(process.stdout)
        self.assertEqual(result['result'],'PASS');self.assertEqual(result['session_memory_entries'],0)
        self.assertEqual(result['native_projection_digest'],digest(p['native_ontology']))
        self.assertEqual(result['project_state_digest'],digest(p['project_state']));self.assertEqual(result['generator_provenance'],p['generator_provenance'])
    def test_full_context_head_change_erases_memory(self):
        from test_replay import Store,example
        s=self.session();s.note('old committed state');store=Store(self.store_path,self.source.repository);proposal=example(store,'full-context-head-change');store.apply(proposal,store.authorize(proposal,self.source.private))
        with self.assertRaisesRegex(RuntimeFault,'head/configuration/state changed'):s.context()
        self.assertTrue(s.closed);self.assertEqual(s.core._memory,[])
    def test_generator_source_drift_erases_memory(self):
        s=self.session();s.note('bound to code');path=PACKAGE/'native_reader.py';raw=path.read_bytes()
        try:
            path.write_bytes(raw+b'\n')
            with self.assertRaisesRegex(RuntimeFault,'context generator source changed'):s.context()
            self.assertEqual(s.core._memory,[]);self.assertTrue(s.closed)
        finally:path.write_bytes(raw)
    def test_native_missing_subject_rejected_even_with_new_request_pin(self):
        request=copy.deepcopy(self.native.request);request['selector']['required_subject_set'][0]['subject_id']='absent-native-node'
        pins=replace(self.native.pins,request_sha256=byte_digest(encoded(request)))
        adapter=NativeReadStore(self.native_root/'semantic',self.native_root/'governance',request,self.executable,pins)
        with self.assertRaisesRegex(RuntimeFault,'REQUIRED_SUBJECT_MISSING'):adapter.read()


if __name__=='__main__':unittest.main()
