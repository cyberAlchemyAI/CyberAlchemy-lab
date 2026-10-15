"""Explicitly correct the contradictory original wire-budget expectation."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';OLD=BASE/'api-v95';API=BASE/'api-v96'
def bind(p):return {'path':p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def load(p):return json.loads(p.read_bytes())
def emit(p,v):
    with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def methods(p):return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(p.read_text())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
def main():
    spec=importlib.util.spec_from_file_location('_api96_parent_guard',OLD/'guard.py');guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
    parent=guard.verify('a014c72e1f7b8149fe847cc6e6ea94fed45b380b88e2627aa1cdae40c2ab56da')
    assert not API.exists()
    shutil.copytree(OLD,API,ignore=shutil.ignore_patterns('receipts','__pycache__','source-manifest.json','contract-profile.json'))
    p=API/'test_preparation.py';s=p.read_text()
    before="""        c=candidate_call(self.service,self.target);c['message']['budget']['max_output_bytes']=1
        self.assertEqual(self.service.call(compact(c))['message']['code'],'budget-exceeded');self.assertFalse(list((self.root/'workspace/journal').iterdir()))"""
    after="""        # The declared outer wire ceiling is >=4096. Below that bound,
        # refusal is a transport error, before a domain result or durable effect.
        # This matches the independently retained CorrectedPreparation case.
        c=candidate_call(self.service,self.target);c['max_response_bytes']=1
        r=self.service.call(compact(c))
        self.assertEqual(r['schema_version'],'lab-api-transport-error/v1-candidate')
        self.assertEqual(r['code'],'invalid-envelope')
        self.assertFalse(list((self.root/'workspace/journal').iterdir()))"""
    assert s.count(before)==1;p.write_text(s.replace(before,after))
    unchanged=[];revised=[]
    for p in sorted(API.glob('*.py')):
        old=methods(OLD/p.name);new=methods(p);assert old.keys()==new.keys()
        for key in old:(unchanged if old[key]==new[key] else revised).append(p.name+':'+key)
    assert len(unchanged)==322 and revised==['test_preparation.py:test_small_receipt_budget_refused_before_effect']
    context=RUN/'context-R03-wire-budget-fixture-0134.json'
    emit(context,{'schema_version':'lab-bounded-context/v1-candidate','task':'R03 full API qualification',
        'source_bindings':[bind(p) for p in [RUN/'authorization.json',OLD/'source-manifest.json',RUN/'API95-preflight-0134.json',API/'test_preparation_corrected.py',API/'schemas/api-call.schema.json',Path(__file__).resolve()]],
        'obligations':[{'id':'Q1','criterion':'Run all323declared methods using exact independent source/profile fixture pins and actual original guards and clocks.'},
            {'id':'Q2','criterion':'Explicitly correct one wrong domain-budget assertion: wire minimum4096 means invalid-envelope. Retain no-journal-write assertion and independent stdio validation.'}],
        'changed_assertion':{'before':'domain error budget-exceeded','after':'transport error invalid-envelope','reason':'A request violating the closed wire schema never enters the domain handler. No inner budget exists on change.prepare.'},
        'write_scope':[str(API.relative_to(ROOT)),str(RUN.relative_to(ROOT))],'authority_effect':'none','actual_owner_outcome':None})
    profile=load(OLD/'contract-profile.json');rows={r['path']:r for r in profile['files']}
    for row in [*[bind(p) for p in sorted(API.rglob('*')) if p.is_file()],bind(context),bind(Path(__file__).resolve())]:rows[row['path']]=row
    profile.update(files=[rows[k] for k in sorted(rows)],qualification_context_binding=bind(context))
    emit(API/'contract-profile.json',profile)
    full={r['path']:r for r in parent['files']}
    for row in [*rows.values(),bind(API/'contract-profile.json'),bind(OLD/'source-manifest.json')]:full[row['path']]=row
    for row in full.values():assert bind(ROOT/row['path'])==row,row['path']
    emit(API/'source-manifest.json',{**parent,'files':[full[k] for k in sorted(full)],'parent_source_binding':bind(OLD/'source-manifest.json'),
        'unchanged_inherited_method_count':322,'explicit_revised_methods':revised,'original_test_method_count':323,
        'fixture_assertion_correction_binding':bind(context),'original_clocks_or_callbacks_changed':False,
        'whole_API_qualified':False,'runtime_qualification_transferred':False,'task_complete':False,'goal_complete':False})
    print(json.dumps({'result':'FROZEN','source_binding':bind(API/'source-manifest.json'),'profile_binding':bind(API/'contract-profile.json')}))
if __name__=='__main__':main()
