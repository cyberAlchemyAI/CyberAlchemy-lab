import copy,json,os,shutil,subprocess,sys
from dataclasses import asdict,replace
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

PACKAGE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(PACKAGE))
from continuity import *
from lab_runtime.common import RuntimeFault


class ContinuityTests(unittest.TestCase):
    observed=None
    @classmethod
    def setUpClass(cls):
        cls.owned=TemporaryDirectory(prefix='lab-C13-owned-runtime-');cls.addClassCleanup(cls.owned.cleanup);cls.root=Path(cls.owned.name)
        cls.archive_sha=verify_inputs();cls.data=restore_archive(ARCHIVE,cls.archive_sha,cls.root/'parent')
        cls.pins=ReplayPins(**load(ARCHIVE)['project_pins'])
        cls.parent=VerifiedLegacyReadStore(cls.root/'parent',ROOT,ROOT,cls.pins)
        cls.parent_bindings=committed_files(cls.parent,cls.data)
        cls.recovery=recover_committed_parent(cls.parent)
        cls.row,cls.selection,cls.snapshot=selected_source()
        cls.executable=Path(os.environ['C13_NATIVE_EXECUTABLE'])
        native_root=cls.root/'native';native_root.mkdir();cls.native=diagnostic_native_fixture(native_root,cls.executable,cls.snapshot)
        cls.Work_ref=cls.data['transactions'][1]['proposal']['targets'][0]['version_ref']
        cls.master=session_for(cls.parent,cls.snapshot,cls.native,cls.Work_ref);cls.addClassCleanup(cls.master.close)
        cls.pack=cls.master.context();cls.transition=reconstruct_actual_Work(cls.parent,cls.selection,cls.root)
        cls.axis_audit=audit_typed_relations(cls.data)
        cls.observed={'actual_owner_outcome':None,'authority_effect':'none','fixture_only_local_signature':True,
            'actual_C12_Work_version_ref':cls.Work_ref,'current_state_id':cls.pack['project_state']['node_id'],
            'fresh_context':copy.deepcopy(cls.pack),'parent_committed_files':cls.parent_bindings,
            'history_cursors':{k:len(v['payload']['events']) for k,v in cls.data['projection']['histories'].items()},
            'typed_relation_audit':cls.axis_audit,'transition_pins':asdict(cls.transition['pins']),
            'transition_plan':cls.transition['prepared']['plan'],'reconstructed_record_postures':
                {ref:r['effective_state'] for ref,r in cls.transition['verified']['subjects'].items() if ref==cls.Work_ref},
            'recovery':cls.recovery,'deferrals':L1_DEFERRALS,
            'assessment':'proceed with candidate workflow/ontology work; actual admitted L1 closure remains A03',
            'new_review_members':[MANIFEST.relative_to(ROOT).as_posix(),load(MANIFEST)['implementation_record']['path'],load(MANIFEST)['realization_record']['path']],
            'claim_ceiling':'Candidate continuity of actual C12 Work only; no actual repository admission, domain ontology, permanent operator or Product SLA.'}

    def test_actual_fresh_context_includes_committed_Work_and_state(self):
        pack=self.pack
        self.assertEqual(pack['head'],self.pins.expected_head)
        self.assertEqual(pack['project_state'],self.data['projection']['state'])
        self.assertEqual(pack['project_state']['node_id'],'project-state:c12-source-audit-0002:1')
        self.assertTrue(any(r['version_ref']==self.Work_ref and r['effective_state']=='local-admitted-current' for r in pack['resolved_references']))
        self.assertEqual(self.master.core._memory,[])
        self.assertEqual({k:v['cursor'] for k,v in pack['project_history_bindings'].items()},{k:6 for k in self.data['projection']['histories']})

    def test_original_file_hash_and_reconstructed_body_hash_are_distinct(self):
        rows=[r for r in self.pack['source_material_provenance'] if r['reference_class']=='local-committed-original-bytes']
        self.assertEqual(len(rows),4)
        for row in rows:
            raw=(self.parent.path/row['path']).read_bytes();record=pointer(loads(raw),row['selector'])
            self.assertEqual(byte_digest(raw),row['original_file_sha256'])
            self.assertEqual(byte_digest(encoded(record)),row['reconstructed_body_sha256'])
            self.assertNotEqual(row['original_file_sha256'],row['reconstructed_body_sha256'])
            self.assertFalse(row['local_admission_is_repository_admission'])

    def test_wrong_local_selector_rejected(self):
        row=copy.deepcopy(next(r for r in self.pack['resolved_references'] if r['version_ref']==self.Work_ref))
        row['source_binding']['selector']='/consequences/project_state'
        with self.assertRaisesRegex(RuntimeFault,'different governed record'):resolved_material(self.parent,self.snapshot,self.data,row)

    def test_wrong_local_store_rejected(self):
        row=copy.deepcopy(next(r for r in self.pack['resolved_references'] if r['version_ref']==self.Work_ref));row['source_binding']['store_id']='wrong'
        with self.assertRaisesRegex(RuntimeFault,'another store'):resolved_material(self.parent,self.snapshot,self.data,row)

    def test_uncommitted_selector_rejected(self):
        row=copy.deepcopy(next(r for r in self.pack['resolved_references'] if r['version_ref']==self.Work_ref));row['source_binding']['path']='transactions/0000000002.json'
        with self.assertRaisesRegex(RuntimeFault,'not committed'):resolved_material(self.parent,self.snapshot,self.data,row)

    def test_closed_session_erases_notes_and_new_Agent_is_fresh(self):
        first=session_for(self.parent,self.snapshot,self.native,self.Work_ref)
        try:
            first.note('C13 scratch remains Session-only');previous=first.instance_id
            self.assertNotIn('C13 scratch remains Session-only',json.dumps(first.context()))
        finally:first.close()
        self.assertEqual(first.core._memory,[])
        second=session_for(self.parent,self.snapshot,self.native,self.Work_ref)
        try:self.assertEqual(second.core._memory,[]);self.assertNotEqual(previous,second.instance_id)
        finally:second.close()

    def test_native_input_scope_is_explicitly_diagnostic(self):
        self.assertEqual(len(self.pack['native_ontology']['governed_nodes']),2)
        self.assertTrue(all(r['identity']['ontology_id']=='lab-c08-native-fixture' for r in self.pack['native_references']))
        self.assertTrue(any('no domain' in text.lower() for text in self.pack['context_view']['limitations']))
        self.assertEqual(self.pack['action_permission'],'none')

    def test_cold_fresh_process_reconstructs_actual_context(self):
        control=self.root/'cold-context.json'
        control.write_bytes(encoded({'parent':str(self.parent.path),'pins':asdict(self.pins),'snapshot':self.snapshot,
            'native_path':str(self.root/'native'),'native_request':self.native.request,'native_pins':asdict(self.native.pins),'native_executable':str(self.executable),'work_ref':self.Work_ref}))
        code='import sys,json;from continuity import *;x=load(sys.argv[1]);p=VerifiedLegacyReadStore(x["parent"],ROOT,ROOT,ReplayPins(**x["pins"]));n=NativeReadStore(Path(x["native_path"])/"semantic",Path(x["native_path"])/"governance",x["native_request"],x["native_executable"],__import__("native_reader").NativePins(**x["native_pins"]));s=session_for(p,x["snapshot"],n,x["work_ref"]);c=s.context();s.close();print(json.dumps({"head":c["head"],"state":digest(c["project_state"]),"memory":s.core._memory,"material":c["source_material_provenance"]}))'
        result=subprocess.run([sys.executable,'-c',code,str(control)],cwd=PACKAGE,capture_output=True,text=True,timeout=180)
        self.assertEqual(result.returncode,0,result.stderr);cold=json.loads(result.stdout)
        self.assertEqual(cold['head'],self.pack['head']);self.assertEqual(cold['state'],digest(self.pack['project_state']))
        self.assertEqual(cold['memory'],[]);self.assertEqual(cold['material'],self.pack['source_material_provenance'])

    def test_explicit_same_cut_profile_reconstruction(self):
        plan=self.transition['prepared']['plan']
        self.assertTrue(plan['applicable']);self.assertEqual(plan['new_baseline']['profile_sha256'],self.row['profile_sha256'])
        self.assertNotEqual(self.data['baseline']['profile'].get('schema_version'),self.selection.profile['schema_version'])
        self.assertEqual(plan['new_baseline']['source_cut'],'decision:0075')
        self.assertEqual(self.transition['verified']['records'][self.Work_ref],self.data['transactions'][1]['proposal']['targets'][0]['record'])

    def test_parent_committed_bytes_and_histories_preserved(self):
        self.assertEqual(committed_files(self.parent,self.parent.verify_full()),self.parent_bindings)
        self.assertEqual(self.parent.verify_full()['projection']['histories'],self.data['projection']['histories'])

    def test_successor_never_inherits_admission_or_old_signature(self):
        row=self.transition['verified']['subjects'][self.Work_ref]
        self.assertEqual(row['effective_state'],'candidate-reconstructed');self.assertIsNone(row['decision_ref'])
        self.assertFalse(row['provenance']['signatures_copied'])
        self.assertNotEqual(self.transition['response']['signature'],self.data['transactions'][1]['approval']['signature'])

    def test_cold_successor_replay(self):
        control=self.root/'cold-transition.json';control.write_bytes(encoded({'path':self.transition['policy'].destination,'pins':asdict(self.transition['pins']),'policy':asdict(self.transition['policy'])}))
        code='import sys;from continuity import *;x=load(sys.argv[1]);r=replay_successor(x["path"],BranchPins(**x["pins"]),LocalPolicy(**x["policy"]));print(digest(r["records"]))'
        result=subprocess.run([sys.executable,'-c',code,str(control)],cwd=PACKAGE,capture_output=True,text=True,timeout=120)
        self.assertEqual(result.returncode,0,result.stderr);self.assertEqual(result.stdout.strip(),digest(self.transition['verified']['records']))

    def test_actual_six_connections_keep_declared_axes_and_pairs(self):
        audit=audit_typed_relations(self.data);self.assertEqual(len(audit['connections']),6)
        self.assertFalse(audit['semantic_noncollapse_certification'])
        self.assertEqual({r['axis_id'] for r in audit['connections']},{self.data['projection']['relation_contracts'][r['kind_ref']]['payload']['axis_id'] for r in audit['connections']})

    def test_old_exact_revision_is_historical_not_current(self):
        old='project-governance-event-history:cyberalchemy-v2-to-lab-migration@decision-0075'
        reference_row=reference(self.data['projection']['subjects'],old)
        self.assertEqual(reference_row['effective_state'],'local-admitted-historical')
        self.assertNotEqual(reference_row['version_ref'],next(r['version_ref'] for r in self.pack['resolved_references'] if r['kind']=='project-governance-event-history'))

    def test_original_transaction_byte_drift_erases_session_memory(self):
        with TemporaryDirectory(prefix='lab-C13-drift-case-') as temp:
            root=Path(temp);restore_archive(ARCHIVE,self.archive_sha,root/'parent');parent=VerifiedLegacyReadStore(root/'parent',ROOT,ROOT,self.pins)
            session=session_for(parent,self.snapshot,self.native,self.Work_ref)
            try:
                session.note('C13 private drift probe');path=root/'parent/transactions/0000000001.json';path.write_bytes(path.read_bytes()+b'\n')
                with self.assertRaisesRegex(RuntimeFault,'provenance changed'):session.context()
                self.assertTrue(session.closed);self.assertEqual(session.core._memory,[])
            finally:session.close()

    def test_context_budget_refuses_incomplete_projection(self):
        with self.assertRaisesRegex(RuntimeFault,'budget'):session_for(self.parent,self.snapshot,self.native,self.Work_ref,max_items=1)

    def test_generator_independent_pin_required(self):
        with self.assertRaisesRegex(RuntimeFault,'pin mismatch'):verify_generator(MANIFEST,GeneratorPins('0'*64,IMPLEMENTATION_VERSION))

    def test_read_consumer_has_no_effect_methods(self):
        for name in ['apply','authorize','admit','initialize','recover','publish']:
            self.assertFalse(hasattr(self.master,name))

    def test_l1_deferrals_have_explicit_downstream_routes(self):
        self.assertEqual(len(L1_DEFERRALS),9)
        self.assertTrue(all(r['route'] for r in L1_DEFERRALS))
        self.assertIn('R08/A01/A03',{r['route'] for r in L1_DEFERRALS})

    def test_recovery_and_public_export_preserve_current_commit(self):
        self.assertEqual(committed_files(self.parent,self.parent.verify_full()),self.parent_bindings)
        with TemporaryDirectory(prefix='lab-C13-export-case-') as temp:
            exported=Path(temp)/'branch';restore_archive(ARCHIVE,self.archive_sha,exported)
            data=full_replay(exported,ROOT,ROOT,self.pins)
            self.assertEqual(data['head'],self.data['head']);self.assertEqual(data['projection']['state'],self.data['projection']['state'])

    def test_new_generator_artifacts_use_existing_carrier_schemas(self):
        for kind,record in self.pack['candidate_artifacts'].items():validate(record,kind,self.snapshot)
        self.assertEqual(self.pack['generator_provenance']['implementation_version_ref'],IMPLEMENTATION_VERSION)
        self.assertEqual(self.pack['generator_provenance']['implementation_posture'],'candidate-unadmitted')
