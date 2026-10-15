"""Component behavior and actual owned journal tests; no public host qualification."""
import copy
from datetime import timedelta
import tempfile
from pathlib import Path
import unittest
from .kernel import plan,encoded,digest
from .fixtures import build
from .journal import Journal,Indeterminate

class Kernel(unittest.TestCase):
    def setUp(self):self.message,self.facts=build()
    def test_01_exact_named_obligations_and_pending_work(self):
        result=plan(self.message,**self.facts)
        self.assertEqual(result['next_run']['state'],'inspected')
        self.assertFalse(result['actual_apply_completed']);self.assertFalse(result['work_satisfaction_asserted'])
        self.assertFalse(result['event']['canonical_admission_granted'])
        self.assertEqual(len(result['next_run']['event_bindings']),1)
    def test_02_permitted_report_does_not_replace_independent_grant(self):
        self.facts['host_grant']['permitted_transitions']=[]
        with self.assertRaises(ValueError):plan(self.message,**self.facts)
    def test_03_request_cannot_grant_actor_role(self):
        self.facts['host_grant']['actor_role_refs']=[]
        with self.assertRaises(ValueError):plan(self.message,**self.facts)
    def test_04_every_exact_material_and_actor_binding(self):
        for key in ('run_binding','definition_binding','authority_evaluation_binding','satisfaction_report_binding'):
            with self.subTest(key=key):
                changed=copy.deepcopy(self.message);changed[key]['sha256']='0'*64
                with self.assertRaises(ValueError):plan(changed,**self.facts)
        changed=copy.deepcopy(self.message);changed['actor']['principal_ref']='principal:foreign'
        with self.assertRaises(ValueError):plan(changed,**self.facts)
    def test_05_real_clock_period_and_expired_authority(self):
        for instant in [self.facts['now']-timedelta(days=1),self.facts['now']+timedelta(days=1)]:
            facts=copy.deepcopy(self.facts);facts['now']=instant
            with self.assertRaises(ValueError):plan(self.message,**facts)
    def test_06_missing_failed_or_foreign_obligation_refused(self):
        for key in self.facts['selected_obligations']:
            facts=copy.deepcopy(self.facts);del facts['selected_obligations'][key]
            with self.assertRaises(ValueError):plan(self.message,**facts)
        facts=copy.deepcopy(self.facts);facts['selected_obligations'][next(iter(facts['selected_obligations']))]=[]
        with self.assertRaises(ValueError):plan(self.message,**facts)
    def test_07_history_does_not_supply_current_participation(self):
        facts=copy.deepcopy(self.facts);next(iter(facts['selected_headers'].values()))['posture']='local-admitted-historical'
        with self.assertRaises(ValueError):plan(self.message,**facts)
    def test_08_run_cut_state_and_input_closure(self):
        changed=copy.deepcopy(self.message);changed['source_cut']['commit_sha256']='0'*64
        with self.assertRaises(ValueError):plan(changed,**self.facts)
        changed=copy.deepcopy(self.message);changed['expected_state']='done'
        with self.assertRaises(ValueError):plan(changed,**self.facts)
        changed=copy.deepcopy(self.message);changed['input_artifacts']=[]
        with self.assertRaises(ValueError):plan(changed,**self.facts)
    def test_09_closed_schema_and_no_admission_effect(self):
        for key,value in [('unexpected_authority',True),('authority_effect','admit')]:
            changed=copy.deepcopy(self.message);changed[key]=value
            with self.assertRaises(ValueError):plan(changed,**self.facts)

class OwnedJournal(unittest.TestCase):
    def setUp(self):
        self.message,self.facts=build();self.plan=plan(self.message,**self.facts)
        self.temp=tempfile.TemporaryDirectory(prefix='cal-workflow-transition-kernel-');self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)/'workflow'
        self.store=Journal.initialize(self.root,self.facts['run_raw'],self.facts['host_grant']['scope_ref'],self.message['actor']['principal_ref'])
        self.guards=0;self.request={'ref':'request:isolated-workflow','sha256':'a'*64}
    def guard(self):
        self.guards+=1
        # Reevaluate the independently selected original witnesses every time.
        self.assertEqual(plan(self.message,**self.facts),self.plan)
    def snapshot(self):return {p.relative_to(self.root).as_posix():p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
    def test_10_actual_apply_replay_and_exact_retry(self):
        tx=self.store.apply(self.plan,request_binding=self.request,host_guard=self.guard)
        self.assertEqual(tx['event']['to_state'],'inspected');self.assertEqual(tx['canonical_admissions'],0)
        before=self.snapshot();again=self.store.apply(self.plan,request_binding=self.request,host_guard=self.guard)
        self.assertEqual(again,tx);self.assertEqual(self.snapshot(),before);self.assertGreaterEqual(self.guards,6)
    def test_11_conflicting_retry_refused(self):
        self.store.apply(self.plan,request_binding=self.request,host_guard=self.guard)
        with self.assertRaises(ValueError):self.store.apply(self.plan,request_binding={'ref':'request:foreign','sha256':'b'*64},host_guard=self.guard)
    def test_12_claim_interrupt_never_redispatches(self):
        with self.assertRaises(Indeterminate):self.store.apply(self.plan,request_binding=self.request,host_guard=self.guard,crash_at='after-claim')
        before=self.snapshot()
        with self.assertRaises(Indeterminate):self.store.apply(self.plan,request_binding=self.request,host_guard=self.guard)
        self.assertEqual(self.snapshot(),before);self.assertEqual(self.store.replay()[0]['sequence'],0)
    def test_13_actual_observed_transaction_recovery(self):
        with self.assertRaises(Indeterminate):self.store.apply(self.plan,request_binding=self.request,host_guard=self.guard,crash_at='after-transaction')
        fingerprint=digest({'request_binding':self.request,'plan':self.plan})
        tx=self.store.recover(self.message['idempotency_key'],fingerprint,host_guard=self.guard)
        self.assertEqual(self.store.replay()[0]['sequence'],1);self.assertEqual(tx['event']['to_state'],'inspected')
        before=self.snapshot();self.assertEqual(self.store.apply(self.plan,request_binding=self.request,host_guard=self.guard),tx)
        self.assertEqual(self.snapshot(),before)
    def test_14_pending_other_key_cannot_advance(self):
        with self.assertRaises(Indeterminate):self.store.apply(self.plan,request_binding=self.request,host_guard=self.guard,crash_at='after-claim')
        changed=copy.deepcopy(self.plan);changed['event']['idempotency_key']='foreign-key'
        with self.assertRaises(Indeterminate):self.store.apply(changed,request_binding=self.request,host_guard=lambda:None)
        self.assertEqual(self.store.replay()[0]['sequence'],0)
    def test_15_transaction_tamper_refused(self):
        self.store.apply(self.plan,request_binding=self.request,host_guard=self.guard)
        path=self.root/'transactions/00000001.json';path.write_bytes(path.read_bytes()+b' ')
        with self.assertRaises(ValueError):self.store.replay()
