#!/usr/bin/env python3
"""Meaningful model and boundary tests; these never invoke a model."""
import copy, json, tempfile, unittest
from pathlib import Path
from ac_runtime import ROOT, Runtime, SCHEMA, encoded, replay, save
class ModelTests(unittest.TestCase):
    def setUp(self):self.j=json.loads((ROOT/'inputs/cases/J0.json').read_text());self.pool=json.loads((ROOT/'inputs/fixed-pool.json').read_text())['candidates']
    def test_closed_known_options(self):
        self.assertEqual([replay(self.j,c)['status'] for c in self.pool],['feasible']*4+['infeasible','unknown'])
        self.assertEqual([replay(self.j,c)['action_count'] for c in self.pool[:4]],[4,2,5,5])
    def test_completion_boundary(self):
        c=copy.deepcopy(self.pool[2]);c['actions'][2]['tick']=3
        self.assertEqual(replay(self.j,c)['status'],'infeasible')
    def test_resource_and_operator_conflict(self):
        c=copy.deepcopy(self.pool[0]);c['actions'][1]['tick']=0
        self.assertEqual(replay(self.j,c)['status'],'infeasible')
        c=copy.deepcopy(self.pool[1]);c['actions'].insert(1,{'tick':1,'op':'install','arg':'V'})
        self.assertEqual(replay(self.j,c)['status'],'infeasible')
    def test_missing_dependency_refusal_boundary(self):
        hx=json.loads((ROOT/'inputs/cases/HX.json').read_text());self.assertEqual(replay(hx,self.pool[0])['status'],'infeasible')
    def test_hidden_measurement(self):
        q=copy.deepcopy(self.pool[5]);q['actions']=[{'tick':0,'op':'measure','arg':'Q'},{'tick':1,'op':'install','arg':'Q'},{'tick':7,'op':'remove','arg':'Q'}]
        self.assertEqual(replay(self.j,q,4)['status'],'feasible');self.assertEqual(replay(self.j,q,0)['status'],'infeasible')
    def test_original_content_contract(self):
        w=json.loads((ROOT/'inputs/cases/W0.json').read_text());seed=json.loads((ROOT/'inputs/frame-failure.json').read_text())['candidate'];self.assertEqual(replay(w,seed)['status'],'infeasible')
        good=copy.deepcopy(seed);good['claim_fields']=['application','outcome','comparison','ceiling'];self.assertEqual(replay(w,good)['status'],'feasible')
    def test_version_update_far_transfer(self):
        w=json.loads((ROOT/'inputs/cases/HF.json').read_text())
        good={'claim_fields':['application','outcome','comparison','ceiling'],'actions':[{'tick':i,'op':'read','arg':s} for i,s in enumerate(['E1','E2','E3','K','A','U'])]+[{'tick':6+i,'op':'write','arg':str(i+1)} for i in range(3)]+[{'tick':9,'op':'compile','arg':None}]}
        self.assertEqual(replay(w,good)['status'],'feasible');bad=copy.deepcopy(good);bad['actions'][0]['arg']='A';bad['actions'][4]['arg']='E1';self.assertEqual(replay(w,bad)['status'],'infeasible')
class BoundaryTests(unittest.TestCase):
    def test_effective_binary_control_and_exposure(self):
        r=Runtime();j=r.job('AC11-OLD-J0-proposal');c=r.effective_case(j);p=json.loads((ROOT/'inputs/fixed-pool.json').read_text())['candidates']
        self.assertEqual(c['impact_preference'],0);self.assertFalse(replay(c,p[0])['soft_preference_satisfied']);self.assertTrue(replay(c,p[1])['soft_preference_satisfied'])
        self.assertNotIn('EX1',r.payload(r.job('AC09-AFTER-first'))['allowed_source_refs'])
        self.assertIn('EX1',r.payload(r.job('AC09-BEFORE-first'))['allowed_source_refs'])
        r.body=lambda jid:{'handoff':{'summary':'Preserved current J facts.','residue':''},'candidates':[],'operation_trace':[]}
        routed=r.payload(r.job('AC20-DISTINCT-route0'));self.assertIn('AM',routed['allowed_source_refs']);self.assertNotIn('AI',routed['allowed_source_refs'])
    def test_complete_ordinary_review_closure(self):
        r=Runtime();ordinary={j['job_id'] for j in r.plan() if j['strategy_id']=='ORD'}
        for j in r.plan():
            if j['role']=='review':self.assertTrue(ordinary<=set(j['dependencies']))
    def test_failed_call_is_counted_and_gates(self):
        with tempfile.TemporaryDirectory() as d:
            r=Runtime(d);jobs=[{'job_id':'a','role':'proposal','dependencies':[]},{'job_id':'b','role':'builder','dependencies':['a']},{'job_id':'v','role':'review','dependencies':['a','b']}];save(r.p('preparation/PLAN.v1.json'),jobs);save(r.p('receipts/jobs/a.admitted.json'),{'terminal':False,'valid':False})
            r.failed('a',{'observation':'actual_TOOL_ERROR','text':'unscored fake failure fixture'})
            self.assertEqual(len(r.invocations()),1);self.assertIn('b',r.ready()['gateable']);r.gate('b');self.assertIn('v',r.ready()['ready'])
    def test_failed_overhead_count_and_pre_call_reserve(self):
        with tempfile.TemporaryDirectory() as d:
            r=Runtime(d);save(r.p('preparation/PLAN.v1.json'),[])
            with self.assertRaises(ValueError):r.record_overhead('coord-fail',None,'coordinator','unscored fake tool error','error')
            r.reserve_overhead('coord-fail','coordinator');r.record_overhead('coord-fail',None,'coordinator','unscored fake tool error','error')
            self.assertEqual(len(r.invocations()),1);self.assertEqual(r.budget()['coordinator_remaining'],1)
            r.reserve_overhead('audit-fail','completion_audit');r.record_overhead('audit-fail',None,'completion_audit','unscored fake tool error','error')
            self.assertEqual(r.budget()['required_auditors_reserved'],2)
    def test_invalid_terminal_and_missing_output_close(self):
        for malformed in [{'candidates':None},{'candidates':['bad-string']},None]:
            with tempfile.TemporaryDirectory() as d:
                r=Runtime(d);r.integrity=lambda:True;j={'job_id':'x','strategy_id':'AC01','arm':'T','case_id':'J0','role':'proposal','word_cap':1800,'dependencies':[]};save(r.p('preparation/PLAN.v1.json'),[j]);save(r.p('receipts/jobs/x.spawned.json'),{'handle':'agent-x','terminal':False,'valid':False});save(r.p('inputs/cases/J0.json'),json.loads((ROOT/'inputs/cases/J0.json').read_text()))
                if malformed is not None:save(r.p('raw/x.json'),malformed)
                result=r.finish('x',{'observation':'actual_FINAL','handle':'agent-x','text':'Unscored terminal fixture; not a real native observation.'})
                self.assertFalse(result['valid']);self.assertTrue(r.state('x')['terminal'])
    def test_exclusive_save(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'a.json';save(p,{'a':1})
            with self.assertRaises(FileExistsError):save(p,{'a':2})
    def test_fact_grammar_and_revision_delta(self):
        with tempfile.TemporaryDirectory() as d:
            r=Runtime(d);j={'job_id':'x','strategy_id':'AC01','arm':'T','case_id':'J0','role':'proposal','word_cap':1800,'dependencies':[]}
            save(r.p('prompts/x.payload.json'),{'allowed_source_refs':['J01']})
            v=copy.deepcopy(SCHEMA);v.update({k:j[k] for k in ['job_id','strategy_id','arm','case_id']});v['operation_trace']=[{'step':1,'action':'check','source_refs':['J01'],'input_job_refs':[],'result':'supported'}];v['candidates']=[];v['attack']={'failure':'a','invariant':'b','permitted_variable':'c','source_refs':['J01']};v['handoff']={'summary':'Exact source boundary retained.','residue':''};r.validate(j,v)
            v['operation_trace'][0]['source_refs']=['C1/C2']
            with self.assertRaises(ValueError):r.validate(j,v)
    def test_nonfinal_is_not_native_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            r=Runtime(d);r.integrity=lambda:True;j={'job_id':'x','strategy_id':'AC01','arm':'T','case_id':'J0','role':'proposal','word_cap':1800,'dependencies':[]};save(r.p('preparation/PLAN.v1.json'),[j]);save(r.p('receipts/jobs/x.spawned.json'),{'handle':'agent-x','terminal':False,'valid':False})
            with self.assertRaises(ValueError):r.finish('x',{'observation':'file_exists','handle':'agent-x','text':'saved'})
if __name__=='__main__':unittest.main()
