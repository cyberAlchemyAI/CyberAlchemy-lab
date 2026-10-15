"""Declared host/selection authoring guards; these do not execute domain effects."""
import copy
import json
import subprocess
import unittest
from dataclasses import replace
from unittest.mock import patch
from control import *
sys.path.insert(0,str(PACKAGE/'tools'));sys.path.insert(0,str(PACKAGE/'receipts/action-boundaries'))
from fixtures import Fixture
from evaluator import BoundaryFault

class Guard:
    head='protocol:W09-unit-head'
    def __init__(self):self.invalid=False;self.calls=0
    def __call__(self):
        self.calls+=1
        if self.invalid:raise ValueError('unit head changed')
        return {'head':self.head}

class Controls(unittest.TestCase):
    def setUp(self):self.hosts=[]
    def tearDown(self):
        for f in self.hosts:f.session.close()
    def fixture(self,**kwargs):
        f=Fixture();self.hosts.append(f);return rebind(f,'unit-run','phase',**kwargs)
    def test_exact_selection_closure(self):self.assertEqual(selection()['run_namespace'],'bc3c50170a404b4ba8d8')
    def test_new_ids_for_all_actor_carriers(self):
        f=self.fixture();self.assertEqual(len({r['node_id'] for r in f.by_kind.values()}),9)
        self.assertTrue(all(':lab-W09:unit-run:phase:' in r['node_id'] for r in f.by_kind.values()))
    def test_actual_time(self):
        f=self.fixture();self.assertLess(abs(time.time()-f.now[0]),5);self.assertGreater(f.grant.expires_at,time.time())
    def test_fresh_handles_across_hosts(self):
        a=self.fixture();b=self.fixture();self.assertNotEqual(a.session.instance_ref,b.session.instance_ref)
        self.assertNotEqual(a.ref('agent-profile'),b.ref('agent-profile'))
    def test_actual_handles_are_closed_bindings(self):
        handles=('protocol:ephemeral-agent-instance:unit','protocol:ephemeral-agent-session:unit')
        f=self.fixture(handles=handles);self.assertEqual((f.session.instance_ref,f.session.session_ref),handles)
        self.assertEqual(f.status['runtime_handle_bindings'][f.ref('agent-instance')],handles[0])
        self.assertEqual(f.authority.check(f.raw())['posture'],'permitted')
    def test_all_actor_original_contracts(self):
        f=self.fixture()
        for k in f.by_kind:self.assertEqual(f.records[f.ref(k)].record(k),f.by_kind[k])
    def test_permitted_bounded_action(self):self.assertEqual(self.fixture().authority.check(self.hosts[-1].raw())['posture'],'permitted')
    def test_canonical_action_denied(self):
        f=self.fixture();f.request['action_kind']='admit-canonical';self.assertEqual(f.authority.check(f.raw())['posture'],'denied')
    def test_wrong_project_denied(self):
        f=self.fixture();f.request['scope_ref']='project:other';self.assertEqual(f.authority.check(f.raw())['posture'],'denied')
    def test_wrong_handle_denied(self):
        f=self.fixture();f.request['session_ref']='protocol:other';self.assertEqual(f.authority.check(f.raw())['posture'],'denied')
    def test_revocation_denied(self):
        f=self.fixture();f.status['revoked_refs']=[f.ref('delegation')];self.assertEqual(f.authority.check(f.raw())['posture'],'denied')
    def test_expired_grant_denied(self):
        f=self.fixture();f.grant=replace(f.grant,expires_at=time.time()-1);self.assertEqual(f.authority.check(f.raw())['posture'],'denied')
    def test_current_head_guard(self):
        g=Guard();f=self.fixture(guard=g);self.assertEqual(f.request['expected_head'],g.head)
        self.assertEqual(f.authority.check(f.raw())['posture'],'permitted');self.assertGreater(g.calls,0)
    def test_changed_head_erases_memory(self):
        g=Guard();f=self.fixture(guard=g);f.session.note('declared unit private note');g.invalid=True
        with self.assertRaisesRegex(ValueError,'unit head changed'):f.session.check()
        self.assertTrue(f.session.closed);self.assertEqual(f.session._memory,[])
    def test_source_drift_erases_memory(self):
        f=self.fixture(source_bindings=[bind(HERE/'control.py')]);f.session.note('declared unit private note')
        with patch('control.original',side_effect=ValueError('unit source drift')):
            with self.assertRaisesRegex(ValueError,'unit source drift'):f.session.check()
        self.assertTrue(f.session.closed);self.assertEqual(f.session._memory,[])
    def test_close_erases_memory(self):
        f=self.fixture();f.session.note('declared unit private note');f.session.close();self.assertEqual(f.session._memory,[])
    def test_wrong_source_pin_rejected(self):
        with self.assertRaisesRegex(ValueError,'selected source differs'):original({'path':bind(HERE/'control.py')['path'],'sha256':'0'*64})
    def test_absolute_source_rejected(self):
        with self.assertRaisesRegex(ValueError,'unsafe source'):original({'path':str(HERE/'control.py'),'sha256':sha((HERE/'control.py').read_bytes())})
    def test_parent_escape_rejected(self):
        with self.assertRaisesRegex(ValueError,'unsafe source'):original({'path':'../escape','sha256':'0'*64})
    def test_adapter_original_explicit(self):
        b=bind(SELECTION_PATH.parent/'sources/engineering.py');f=self.fixture(adapter_binding=b)
        self.assertEqual(f.authority.adapter_sha256,b['sha256']);self.assertEqual(f.grant.adapter_sha256,b['sha256'])
        self.assertEqual(load_bytes(f.grant.evidence_original)['selected_adapter_binding'],b)
    def test_permission_does_not_claim_owner(self):
        f=self.fixture();v=load_bytes(f.grant.evidence_original)
        self.assertIsNone(v['actual_owner_outcome']);self.assertTrue(v['fixture_only']);self.assertEqual(v['authority_effect'],'none')
    def test_prototype_lease_closed(self):
        f=Fixture();old=f.session;old.note('unit old memory');self.hosts.append(f);rebind(f,'unit','replacement')
        self.assertTrue(old.closed);self.assertEqual(old._memory,[])
    def test_fresh_input_contracts(self):
        script="from control import *;s=selection();_,e,r=select_sources(s,'research');a=s['inputs']['engineering'];b=s['inputs']['research'];e.resolve_inputs((ROOT/a['selection_binding']['path']).parent,a['selection_binding']['sha256']);r.resolve((ROOT/b['selection_binding']['path']).parent,b['selection_binding']['sha256']);print('fresh-inputs-PASS')"
        completed=subprocess.run([sys.executable,'-c',script],cwd=HERE,text=True,capture_output=True,timeout=60)
        self.assertEqual(completed.returncode,0,completed.stderr);self.assertEqual(completed.stdout.strip(),'fresh-inputs-PASS')

def load_bytes(raw):return json.loads(raw)
if __name__=='__main__':unittest.main(verbosity=2)
