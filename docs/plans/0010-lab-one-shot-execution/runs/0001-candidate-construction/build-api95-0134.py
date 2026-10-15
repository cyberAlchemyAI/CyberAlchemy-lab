"""Retain frozen API94 and correct one contradictory test input in its successor."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil

RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface'
OLD=BASE/'api-v94';API=BASE/'api-v95'
def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def load(p):return json.loads(p.read_bytes())
def emit(p,v):
    with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def methods(p):return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(p.read_text())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
def main():
    spec=importlib.util.spec_from_file_location('_api95_parent_guard',OLD/'guard.py')
    guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
    parent=guard.verify('309aef6ef048a4aab9964a009244a4f789225895a982229f260e02e474723bbf')
    assert not API.exists()
    shutil.copytree(OLD,API,ignore=shutil.ignore_patterns('receipts','__pycache__','source-manifest.json','contract-profile.json'))
    p=API/'test_preparation.py';s=p.read_text()
    before="c=candidate_call(self.service,self.target);c['max_response_bytes']=1"
    after="c=candidate_call(self.service,self.target);c['message']['budget']['max_output_bytes']=1"
    assert s.count(before)==1;s=s.replace(before,after)
    p.write_text(s)
    changed=[];retained=[]
    for p in sorted(API.glob('*.py')):
        old=methods(OLD/p.name);new=methods(p);assert old.keys()==new.keys()
        for name in old:
            (retained if old[name]==new[name] else changed).append(p.name+':'+name)
    assert len(retained)==322 and changed==['test_preparation.py:test_small_receipt_budget_refused_before_effect']
    context=RUN/'context-R03-full-qualification-0134.json'
    emit(context,{'schema_version':'lab-bounded-context/v1-candidate','task':'R03 original API qualification',
        'source_bindings':[bind(p) for p in [RUN/'authorization.json',OLD/'source-manifest.json',RUN/'API94-original323-0001.json',RUN/'API94-current-inspection-0001.json',RUN/'API94-read-boundaries-0001.json',Path(__file__).resolve()]],
        'obligations':[{'id':'Q1','criterion':'Attempt every original323method with actual selected source/profile constants, including absent globals used by inherited fixtures. No callback, clock or source bypass.'},
            {'id':'Q2','criterion':'Preserve invalid wire ceiling refusal in CorrectedPreparation; exercise domain ceiling refusal in Preparation by changing only the valid message budget input. All original assertions retained.'},
            {'id':'Q3','criterion':'Retain failed evidence and frozen ancestors; full acceptance requires zero failures/errors and323actual methods.'}],
        'write_scope':[str(API.relative_to(ROOT)),str(RUN.relative_to(ROOT))],
        'authority_effect':'none','actual_owner_outcome':None,'runtime_qualification_transferred':False})
    local=[bind(p) for p in sorted(API.rglob('*')) if p.is_file()]
    profile=load(OLD/'contract-profile.json');rows={r['path']:r for r in profile['files']}
    for row in [*local,bind(context),bind(Path(__file__).resolve())]:rows[row['path']]=row
    profile.update(files=[rows[k] for k in sorted(rows)],qualification_context_binding=bind(context))
    emit(API/'contract-profile.json',profile)
    full={r['path']:r for r in parent['files']}
    for row in [*rows.values(),bind(API/'contract-profile.json'),bind(OLD/'source-manifest.json')]:full[row['path']]=row
    for row in full.values():assert bind(ROOT/row['path'])==row,row['path']
    emit(API/'source-manifest.json',{**parent,'files':[full[k] for k in sorted(full)],'parent_source_binding':bind(OLD/'source-manifest.json'),
        'unchanged_inherited_method_count':322,'retained_inherited_methods':retained,'explicit_revised_methods':changed,
        'fixture_input_revision':{'before':before,'after':after,'reason':'Outer response minimum4096 is a wire constraint; the domain refusal requires a valid envelope and insufficient inner budget. The separate original corrected test retains invalid-envelope coverage.'},
        'qualification_context_binding':bind(context),'whole_API_qualified':False,'runtime_qualification_transferred':False,'task_complete':False,'goal_complete':False})
    print(json.dumps({'result':'FROZEN','source_binding':bind(API/'source-manifest.json'),'profile_binding':bind(API/'contract-profile.json'),'unchanged_methods':len(retained),'explicit_revised_methods':changed}))
if __name__=='__main__':main()
