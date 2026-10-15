from dataclasses import replace, asdict
import json,os,subprocess,sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from fixtures import *
from action import materialize_action


class AuthorityTests(unittest.TestCase):
    def setUp(self):
        self.f=Fixture();self.addCleanup(self.f.session.close)
    def denied(self,reason):
        result=self.f.authority.check(self.f.raw());self.assertNotEqual(result['posture'],'permitted');self.assertIn(reason,str(result['checks']))
    def test_permitted_requires_separate_host_permission(self):
        self.assertEqual(self.f.authority.check(self.f.raw())['posture'],'permitted');self.f.grant=None;self.denied('grant absent')
    def test_unknown_exact_current_reference_denied(self):
        self.f.request['assignment_ref']+='-unknown';self.denied('unresolved')
    def test_historical_authority_denied(self):
        ref=self.f.ref('delegation');self.f.records[ref]=replace(self.f.records[ref],posture='admitted-historical');self.denied('not current')
    def test_original_authority_byte_drift_denied(self):
        ref=self.f.ref('principal');self.f.records[ref]=replace(self.f.records[ref],original=self.f.records[ref].original+b'\n');self.denied('bytes changed')
    def test_expiry_erases_only_Session_memory(self):
        self.f.session.note('private Session scratch');self.f.now[0]+=901;self.denied('expired');self.assertEqual(self.f.session._memory,[]);self.assertTrue(self.f.session.closed)
    def test_expired_grant_denied(self):
        self.f.grant=replace(self.f.grant,expires_at=self.f.now[0]-1);self.denied('expired')
    def test_revocation_after_evaluation_denied(self):
        self.assertEqual(self.f.authority.check(self.f.raw())['posture'],'permitted');self.f.status['revoked_refs']=[self.f.ref('delegation')];self.denied('revoked')
    def test_inactive_role_denied(self):
        self.f.by_kind['role-assignment']['assignment_state']='revoked';self.f.reselect('role-assignment');self.denied('role inactive')
    def test_role_assignee_mismatch_denied(self):
        self.f.by_kind['role-assignment']['assignee_ref']='person-reference:another-person';self.f.reselect('role-assignment');self.denied('assignee differs')
    def test_unknown_or_expired_period_denied(self):
        self.f.status['periods']={};self.denied('unknown authority period');self.f.status['periods']={'protocol:w02-period':[0,self.f.now[0]-1]};self.denied('period expired')
    def test_admitted_old_assignment_rejects_new_ephemeral_Agent(self):
        path=ROOT/'authority/admissions/first-governed-agent-work-episode/v1/instances/artifacts/agent-assignment.json';raw=path.read_bytes();value=parse(raw);ref=value['node_id']+'@candidate.1'
        self.f.records[ref]=SelectedRecord(ref,raw,byte_sha(raw),'admitted-current',str(path.relative_to(ROOT)));self.f.request['assignment_ref']=ref;self.denied('another ephemeral Agent')
    def test_scope_action_and_redelegation_denied(self):
        self.f.request['scope_ref']='project:other';self.denied('scope denied');self.f.request['scope_ref']=self.f.scope;self.f.request['action_kind']='admit';self.denied('action denied');self.f.request['action_kind']='increment-local-counter';self.f.request['redelegating']=True;self.denied('redelegation denied')
    def test_gate_requires_exact_input(self):
        self.f.by_kind['delegation']['payload']['approval_gate_refs']=['gate:w02'];self.f.reselect('delegation');self.denied('gate-required')
        approval={'scope_ref':self.f.scope,'action_kind':self.f.request['action_kind'],'input_sha256':self.f.request['input_sha256'],'expires_at':self.f.now[0]+10};self.f.status['gates']['gate:w02']=approval
        self.assertEqual(self.f.authority.check(self.f.raw())['posture'],'permitted');approval['input_sha256']='0'*64;self.denied('gate-required')
    def test_environment_and_Tool_version_denied(self):
        self.f.grant=replace(self.f.grant,environment_sha256='0'*64);self.denied('environment changed');self.f.grant=replace(self.f.grant,environment_sha256=self.f.environment_sha256);self.f.by_kind['tool']['payload']['interface_version']='shell/v1';self.f.reselect('tool');self.denied('unsupported Tool')
    def test_stop_and_stale_cut_denied(self):
        self.f.status['stopped']=True;self.denied('stop condition');self.f.status['stopped']=False;self.f.status['head']='changed';self.denied('stale')
    def test_client_cannot_supply_trusted_context(self):
        self.f.request['trusted_context']={'grant':'all'};self.denied('closed local')
    def test_duplicate_JSON_key_denied(self):
        raw=self.f.raw().rstrip()[:-1]+b',"principal_ref":"forged"}';self.assertEqual(self.f.authority.check(raw)['posture'],'denied')
    def test_new_Session_has_no_memory_carry(self):
        self.f.session.note('private scratch');old=self.f.session.instance_ref;self.f.session.close();new=SessionLease();self.addCleanup(new.close);self.assertNotEqual(new.instance_ref,old);self.assertEqual(new._memory,[])


class DispatchTests(unittest.TestCase):
    observed=None
    def setUp(self):
        self.temp=TemporaryDirectory(prefix='lab-W02-owned-');self.addCleanup(self.temp.cleanup);self.f=Fixture();self.addCleanup(self.f.session.close);self.root=Path(self.temp.name)/'operations';self.pins=initialize(self.root);self.d=LocalDispatcher(self.root,self.pins,self.f.authority)
    def test_real_Tool_and_candidate_Agent_Action(self):
        result=self.d.dispatch(self.f.raw(),self.f.input);self.assertEqual(result['posture'],'completed');self.assertEqual(self.d.tool.state()['value'],1)
        action=materialize_action(self.f.raw(),result,'protocol:w02-observed-action-receipt');self.assertEqual(action['payload']['session_ref'],self.f.session.session_ref)
        DispatchTests.observed={'fixture_only':True,'actual_owner_outcome':None,'request':self.f.request,'receipt':result,'agent_action':action,'counter':self.d.tool.state(),'pins':asdict(self.d.expected)}
    def test_denied_dispatch_never_changes_Tool(self):
        self.f.status['revoked_refs']=[self.f.ref('delegation')];before=self.d.tool.path.read_bytes();result=self.d.dispatch(self.f.raw(),self.f.input);self.assertEqual(result['posture'],'denied');self.assertEqual(before,self.d.tool.path.read_bytes())
    def test_revocation_between_pending_and_effect(self):
        def revoke(_):self.f.status['revoked_refs']=[self.f.ref('delegation')]
        result=self.d.dispatch(self.f.raw(),self.f.input,pending_observer=revoke);self.assertEqual(result['posture'],'denied');self.assertEqual(self.d.tool.state()['value'],0)
    def test_input_binding_contract_and_output_budget(self):
        with self.assertRaisesRegex(BoundaryFault,'binding changed'):self.d.dispatch(self.f.raw(),b'{}')
        self.f.input=encoded({'increment':True});self.f.request['input_sha256']=byte_sha(self.f.input)
        with self.assertRaisesRegex(BoundaryFault,'input contract'):self.d.dispatch(self.f.raw(),self.f.input)
        self.f.input=encoded({'increment':1});self.f.request['input_sha256']=byte_sha(self.f.input);self.f.grant=replace(self.f.grant,max_output_bytes=1)
        with self.assertRaisesRegex(BoundaryFault,'output budget'):self.d.dispatch(self.f.raw(),self.f.input)
        self.assertEqual(self.d.tool.state()['value'],0)
    def test_Tool_contract_mismatch_rejected(self):
        self.f.by_kind['tool']['payload']['input_contract_ref']='contract:wrong';self.f.reselect('tool')
        with self.assertRaisesRegex(BoundaryFault,'selected Tool input'):self.d.dispatch(self.f.raw(),self.f.input)
    def test_exact_retry_one_effect_and_conflict(self):
        first=self.d.dispatch(self.f.raw(),self.f.input);second=self.d.dispatch(self.f.raw(),self.f.input);self.assertEqual(first,second);self.assertEqual(self.d.tool.state()['value'],1)
        self.f.request['deadline']=datetime.fromtimestamp(self.f.now[0]+500,timezone.utc).isoformat()
        with self.assertRaisesRegex(BoundaryFault,'idempotency-conflict'):self.d.dispatch(self.f.raw(),self.f.input)
    def test_possible_effect_indeterminate_never_redispatched(self):
        first=self.d.dispatch(self.f.raw(),self.f.input,interruption='after-effect');self.assertEqual(first['posture'],'indeterminate');self.assertFalse(first['retry_allowed'])
        self.assertEqual(self.d.dispatch(self.f.raw(),self.f.input)['posture'],'indeterminate');self.assertEqual(self.d.tool.state()['value'],1)
        old=self.f.request['idempotency_key'];self.f.request['idempotency_key']='another'
        with self.assertRaisesRegex(BoundaryFault,'reconciliation-required'):self.d.dispatch(self.f.raw(),self.f.input)
        self.f.request['idempotency_key']=old;self.assertEqual(self.d.reconcile(self.f.raw())['posture'],'completed');self.assertEqual(self.d.tool.state()['value'],1)
    def test_pending_without_effect_observational_recovery(self):
        self.d.dispatch(self.f.raw(),self.f.input,interruption='before-effect');result=self.d.reconcile(self.f.raw());self.assertEqual(result['posture'],'failed');self.assertEqual(self.d.tool.state()['value'],0);self.assertFalse(result['retry_allowed'])
    def test_recovery_requires_separate_current_permission(self):
        self.d.dispatch(self.f.raw(),self.f.input,interruption='after-effect');self.f.grant=replace(self.f.grant,recovery_allowed=False);self.assertEqual(self.d.reconcile(self.f.raw())['posture'],'denied');self.assertEqual(self.d.tool.state()['value'],1)
    def test_missing_ledger_and_counter_drift_reject(self):
        original=(self.root/'journal.json').read_bytes();(self.root/'journal.json').unlink()
        with self.assertRaises(BoundaryFault):self.d.dispatch(self.f.raw(),self.f.input)
        (self.root/'journal.json').write_bytes(original);(self.root/'counter.json').write_bytes(encoded({'value':999,'action_id':'forged','input_sha256':'0'*64}))
        with self.assertRaisesRegex(BoundaryFault,'state drift'):self.d.dispatch(self.f.raw(),self.f.input)
    def test_cold_process_exit_after_real_effect_reconciles_once(self):
        control=Path(self.temp.name)/'child.json';control.write_bytes(encoded({'root':str(self.root),'pins':asdict(self.pins)}))
        code='''import json,os,sys
from fixtures import *
x=parse(Path(sys.argv[1]).read_bytes());f=Fixture();d=LocalDispatcher(x['root'],LedgerPins(**x['pins']),f.authority)
Path(sys.argv[1]).with_name('child-request.json').write_bytes(f.raw())
def observe(p): print(json.dumps(asdict(p)),flush=True)
old=d.tool.execute
def crash(raw,action):
 old(raw,action)
 os._exit(77)
d.tool.execute=crash
d.dispatch(f.raw(),f.input,pending_observer=observe)
'''
        result=subprocess.run([sys.executable,'-c',code,str(control)],cwd=Path(__file__).parent,capture_output=True,text=True,timeout=30);self.assertEqual(result.returncode,77,result.stderr)
        external=LedgerPins(**json.loads(result.stdout));original_request=control.with_name('child-request.json').read_bytes()
        self.assertNotEqual(parse(original_request)['instance_ref'],self.f.session.instance_ref)
        recovered=LocalDispatcher(self.root,external,self.f.authority)
        outcome=recovered.reconcile(original_request,recovery_request=self.f.raw());self.assertEqual(outcome['posture'],'completed');self.assertEqual(recovered.tool.state()['value'],1)


class ActualContextTests(unittest.TestCase):
    observed=None
    def test_actual_committed_context_and_termination_bound_dispatch(self):
        continuity_path=ROOT/'implementation/lab-continuity/candidates/v1'
        sys.path.insert(0,str(continuity_path))
        import continuity as c
        with TemporaryDirectory(prefix='lab-W02-actual-context-') as temp:
            root=Path(temp);archive_sha=c.verify_inputs();data=c.restore_archive(c.ARCHIVE,archive_sha,root/'parent')
            parent=c.VerifiedLegacyReadStore(root/'parent',c.ROOT,c.ROOT,c.ReplayPins(**c.load(c.ARCHIVE)['project_pins']))
            _,_,snapshot=c.selected_source();native_root=root/'native';native_root.mkdir()
            native=c.diagnostic_native_fixture(native_root,Path(os.environ['W02_NATIVE_EXECUTABLE']),snapshot)
            work_ref=data['transactions'][1]['proposal']['targets'][0]['version_ref']
            agent=c.session_for(parent,snapshot,native,work_ref)
            try:
                lease=SessionLease(clock=lambda:1791460800.0,context_reader=agent.context)
                lease.instance_ref=agent.instance_id;lease.session_ref=agent.session_id
                fixture=Fixture(session=lease,head=data['head']['transaction_digest'])
                dispatcher=LocalDispatcher(root/'operations',initialize(root/'operations'),fixture.authority)
                result=dispatcher.dispatch(fixture.raw(),fixture.input)
                self.assertEqual(result['posture'],'completed')
                ActualContextTests.observed={'actual_Work_ref':work_ref,'head':data['head']['transaction_digest'],
                    'context_generator':c.IMPLEMENTATION_VERSION,'fresh_instance_ref':agent.instance_id,
                    'context_cut_is_actual':True,'authority_fixture_is_separate':True,
                    'Tool_output':result['output'],'domain_ontology_claim':False}
                agent.close();fixture.request['idempotency_key']='after-close'
                denied=dispatcher.dispatch(fixture.raw(),fixture.input)
                self.assertEqual(denied['posture'],'denied');self.assertTrue(lease.closed)
                self.assertEqual(lease._memory,[]);self.assertEqual(dispatcher.tool.state()['value'],1)
            finally:agent.close()


if __name__=='__main__':unittest.main()
