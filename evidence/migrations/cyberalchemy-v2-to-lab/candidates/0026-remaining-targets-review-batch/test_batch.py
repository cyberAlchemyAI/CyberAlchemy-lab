"""Per-target contract behavior plus cross-family adversarial tests."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from jsonschema import ValidationError
from catalog import TYPES, RELATIONS, POLICIES, LIFECYCLES, EVALUATIONS, DERIVED
from engine import validate_graph, validate_node, validate_relation, profile_eval, project, load_graph, check_revision, read
from support import ROOT, LAB, load, dump, binding
RESULTS={}
class TargetTests(unittest.TestCase):
    def setUp(self): self.graph=load(ROOT/'examples/graph.json')

def artifact_test(name):
    def test(self):
        nodes=validate_graph(self.graph); node=nodes['example:'+name]; self.assertTrue(validate_node(node,nodes))
        bad=copy.deepcopy(self.graph); victim=next(x for x in bad['nodes'] if x['node_id']==node['node_id'])
        if name in ['product','project','team','person-reference']:
            changed=copy.deepcopy(node); changed['identity_scope' if name=='person-reference' else 'identity_boundary']='changed'
            with self.assertRaises(ValueError): check_revision(node,changed)
        elif name=='measurement-method':
            victim['unit']='incompatible-unit'
            with self.assertRaisesRegex(ValueError,'Measurement unit'): validate_graph(bad)
        elif name=='context-profile':
            victim['maximum_anchors']=0
            with self.assertRaises((ValueError,ValidationError)): validate_graph(bad)
        elif name=='ontology':
            victim['relation_ids']=['missing:edge']
            with self.assertRaisesRegex(ValueError,'Ontology'): validate_graph(bad)
        elif name=='role':
            victim['grants_authority']=True
            with self.assertRaises(ValidationError): validate_graph(bad)
        else:
            key=next(k for k,v in TYPES[name].items() if v.startswith(('id:','ids:','ids0:')))
            victim[key]='missing:reference' if TYPES[name][key].startswith('id:') else ['missing:reference']
            with self.assertRaisesRegex(ValueError,'Dangling reference'): validate_graph(bad)
        RESULTS['type.'+name]={'result':'PASS','behavior':'valid target record plus identity, reference or domain constraint rejection'}
    return test
for name in TYPES: setattr(TargetTests,'test_type_'+name.replace('-','_'),artifact_test(name))

def relation_test(name):
    def test(self):
        nodes=validate_graph(self.graph); edge=load(ROOT/'targets'/('relation.'+name)/'fixtures/valid/relation.json'); self.assertTrue(validate_relation(edge,nodes))
        bad=copy.deepcopy(edge); bad['target']='absent'
        with self.assertRaisesRegex(ValueError,'Dangling relation'): validate_relation(bad,nodes)
        bad=copy.deepcopy(edge); bad['direction']='implicit-or-reversed'
        with self.assertRaises(ValidationError): validate_relation(bad,nodes)
        RESULTS['relation.'+name]={'result':'PASS','behavior':'directed valid endpoints; dangling endpoint and wrong direction rejected'}
    return test
for name in RELATIONS: setattr(TargetTests,'test_relation_'+name.replace('-','_'),relation_test(name))

def profile_test(name):
    def test(self):
        folder=ROOT/'targets'/('profile.'+name); p=load(folder/'parameters.json'); good=profile_eval(name,p,load(folder/'fixtures/valid/input.json')); bad=profile_eval(name,p,load(folder/'fixtures/adverse/input.json'))
        self.assertEqual(good['outcome'],'pass-for-review'); self.assertFalse(good['action_authorized']); self.assertFalse(bad['action_authorized'])
        if name=='source-selection-policy': self.assertEqual(bad['selected'],[]); self.assertFalse(bad['selection_complete'])
        elif name=='authority-aware-navigation': self.assertEqual(bad['visible'],[])
        elif name=='retention': self.assertEqual(bad['retention_result'],'retain'); self.assertFalse(bad['deleted'])
        else: self.assertEqual(bad['outcome'],'block')
        wrong=load(folder/'fixtures/valid/input.json'); wrong['scope_ref']='scope:other'; self.assertEqual(profile_eval(name,p,wrong)['outcome'],'not-applicable')
        RESULTS['profile.'+name]={'result':'PASS','behavior':'domain-positive and adverse inputs; exact scope; no authority grant'}
    return test
for name in POLICIES+list(LIFECYCLES)+list(EVALUATIONS): setattr(TargetTests,'test_profile_'+name.replace('-','_'),profile_test(name))

def derived_test(name):
    def test(self):
        first=project(name,self.graph); permuted=copy.deepcopy(self.graph); permuted['nodes'].reverse(); permuted['relations'].reverse()
        self.assertEqual(first,project(name,permuted)); self.assertFalse(first['view_activated']); self.assertFalse(first['completeness_proven'])
        bad=copy.deepcopy(self.graph); bad['relations'][0]['target']='missing'
        with self.assertRaisesRegex(ValueError,'Dangling relation'): project(name,bad)
        RESULTS['derived.'+name]={'result':'PASS','behavior':'order-independent deterministic projection; malformed source graph rejected'}
    return test
for name in DERIVED: setattr(TargetTests,'test_derived_'+name.replace('-','_'),derived_test(name))

class IntegrationTests(unittest.TestCase):
    def setUp(self): self.g=load(ROOT/'examples/graph.json')
    def node(self,name): return next(x for x in self.g['nodes'] if x['node_id']=='example:'+name)
    def test_exact_graph_manifest(self): self.assertEqual(load_graph(ROOT/'examples/graph-manifest.json'),self.g)
    def test_graph_drift(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as d:
            p=Path(d)/'manifest.json'; data=load(ROOT/'examples/graph-manifest.json'); data['nodes'][0]['sha256']='0'*64; dump(p,data)
            with self.assertRaisesRegex(ValueError,'drift'): load_graph(p)
    def test_run_method_mismatch(self):
        method=copy.deepcopy(self.node('method')); method['node_id']='other-method'; self.g['nodes'].append(method); self.node('research-run')['method_ref']='other-method'
        with self.assertRaisesRegex(ValueError,'Run method differs'): validate_graph(self.g)
    def test_run_end_required(self):
        self.node('experiment-run')['period']['end']=None
        with self.assertRaisesRegex(ValueError,'requires end'): validate_graph(self.g)
    def test_negative_uncertainty(self):
        self.node('measurement-result')['uncertainty']=-1
        with self.assertRaises(ValidationError): validate_graph(self.g)
    def test_scope_separation(self):
        n=self.node('model-instance-binding'); n['instance_authority_scope']=n['parent_authority_scope']
        with self.assertRaisesRegex(ValueError,'scopes collapse'): validate_graph(self.g)
    def test_membership_overlap(self):
        n=copy.deepcopy(self.node('team-membership')); n['node_id']='overlap'; self.g['nodes'].append(n)
        with self.assertRaisesRegex(ValueError,'Overlapping'): validate_graph(self.g)
    def test_roster_half_open_period(self):
        n=self.node('team-membership'); n['period']['end']='2026-09-07T00:00:00Z'; n['membership_posture']='ended'
        view=project('team-roster',self.g); row=next(x for x in view['nodes'] if x['node_id']==n['node_id']); self.assertFalse(row['current'])
        before=project('team-roster',self.g,'2026-09-06T23:59:59Z'); self.assertTrue(next(x for x in before['nodes'] if x['node_id']==n['node_id'])['current'])
    def test_context_budget(self):
        self.node('context-request')['budget']=1; self.node('context-view')['selected_refs']=['example:definition','example:evidence-set']
        with self.assertRaisesRegex(ValueError,'exceeds request'): validate_graph(self.g)
    def test_empty_context_records_residue(self):
        self.node('context-view').update(selected_refs=[],residue_refs=[])
        with self.assertRaisesRegex(ValueError,'record residue'): validate_graph(self.g)
    def test_successor_cycle(self):
        e=copy.deepcopy(next(x for x in self.g['relations'] if x['kind']=='successor-of')); e['source'],e['target']=e['target'],e['source']; e['relation_id']='cycle'; self.g['relations'].append(e)
        with self.assertRaisesRegex(ValueError,'Cycle'): validate_graph(self.g)
    def test_immutable_run(self):
        n=self.node('research-run'); changed=copy.deepcopy(n); changed['limitations']=['rewritten']
        with self.assertRaisesRegex(ValueError,'Immutable'): check_revision(n,changed)
    def test_no_lifecycle_shortcut(self):
        f=ROOT/'targets/profile.authority-lifecycle'; p=load(f/'parameters.json'); q=load(f/'fixtures/valid/input.json'); q['to_state']='admitted'; self.assertEqual(profile_eval('authority-lifecycle',p,q)['outcome'],'block')
    def test_missing_evaluation_defers(self):
        f=ROOT/'targets/profile.goal-evaluation'; p=load(f/'parameters.json'); q=load(f/'fixtures/valid/input.json'); q['checks']={}; self.assertEqual(profile_eval('goal-evaluation',p,q)['outcome'],'defer')
    def test_retired_identifier_retained(self):
        f=ROOT/'targets/profile.retention'; p=load(f/'parameters.json'); q=load(f/'fixtures/valid/input.json'); q['permanently_reserved']=True; self.assertEqual(profile_eval('retention',p,q)['retention_result'],'retain')
    def test_publication_no_execution(self):
        f=ROOT/'targets/profile.publication'; result=profile_eval('publication',load(f/'parameters.json'),load(f/'fixtures/valid/input.json')); self.assertFalse(result['publication_performed']); self.assertFalse(result['approval_authenticated'])
    def test_profile_no_boolean_coercion(self):
        f=ROOT/'targets/profile.gate-evaluation'; p=load(f/'parameters.json'); q=load(f/'fixtures/valid/input.json'); q['checks']['criteria_pass']=1
        with self.assertRaises(ValidationError): profile_eval('gate-evaluation',p,q)
    def test_bad_timestamp(self):
        self.node('observation')['observed_at']='yesterday'
        with self.assertRaises(ValidationError): validate_graph(self.g)
    def test_cli(self):
        result=subprocess.run([sys.executable,str(ROOT/'check.py'),'graph',str(ROOT/'examples/graph-manifest.json')],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        f=ROOT/'targets/profile.recursion'; result=subprocess.run([sys.executable,str(ROOT/'check.py'),'profile','recursion',str(f/'fixtures/adverse/input.json')],capture_output=True,text=True); self.assertEqual(result.returncode,1,result.stdout+result.stderr)
    def test_invalid_json(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x.json'; p.write_text('{"a":1,"a":2}')
            with self.assertRaises(ValueError): read(p)

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__]); result=unittest.TextTestRunner(verbosity=2).run(suite)
    dump(ROOT/'receipts/target-validation.json',{'result':'PASS' if result.wasSuccessful() and len(RESULTS)==83 else 'BLOCK','tests_run':result.testsRun,'targets':RESULTS})
    raise SystemExit(0 if result.wasSuccessful() and len(RESULTS)==83 else 1)
