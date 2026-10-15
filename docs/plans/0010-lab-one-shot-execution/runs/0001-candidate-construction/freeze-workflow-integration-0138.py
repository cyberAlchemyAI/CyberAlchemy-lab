"""Freeze the bounded workflow API staging, with no qualification transfer."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';OLD=BASE/'api-v96';API=BASE/'api-integration-v1'
def bind(p):return {'path':p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def load(p):return json.loads(p.read_bytes())
def emit(p,v):
    with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def methods(p):return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(p.read_text())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
def main():
    assert not (API/'source-manifest.json').exists()
    spec=importlib.util.spec_from_file_location('_cal_workflow_parent_guard',OLD/'guard.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
    parent=g.verify('a5c61899e2ec5bd07d098475842848846bdd42d18b82e16d879f835361f44048')
    p=API/'run_session_checks.py';text=p.read_text();before="self.assertEqual(len(self.schemas.operations),34);self.assertEqual(len(SUPPORTED),24)"
    assert text.count(before)==1;p.write_text(text.replace(before,"self.assertEqual(len(self.schemas.operations),34);self.assertEqual(len(SUPPORTED),25)"))
    retained=[];changed=[]
    for p in sorted(API.glob('*.py')):
        ast.parse(p.read_text())
        if (OLD/p.name).exists():
            a=methods(OLD/p.name);b=methods(p);assert a.keys()==b.keys()
            for name in a:(retained if a[name]==b[name] else changed).append(p.name+':'+name)
    assert len(retained)==322 and changed==['run_session_checks.py:test_30_current_handler_profile_retains_all_original_contracts']
    context=RUN/'context-R03-workflow-integration-0138.json'
    emit(context,{'schema_version':'lab-bounded-context/v1-candidate','task':'R03 workflow.transition public integration',
        'source_bindings':[bind(p) for p in [RUN/'authorization.json',OLD/'source-manifest.json',BASE/'workflow-transition-v1/source-manifest.json',
            BASE/'current-participation-v10/source-manifest.json',BASE/'current-participation-v10/packages/0001/manifest.json',BASE/'current-source-adapter-v8/source-manifest.json',Path(__file__).resolve()]],
        'obligations':[{'id':'W1','criterion':'Actual channel/current source, exact named grant and checks, Intent Resolution/Decision/Effect/Goal/Work/Coordination closure before claim.'},
            {'id':'W2','criterion':'Only observed owned coordination transaction may return applied; exact retry/no redispatch, pending recovery and private/source/schema/Actor refusals remain.'},
            {'id':'W3','criterion':'Transition with output carriers requires verified producers; unavailable producer closes no output or Work satisfaction.'}],
        'explicit_fixture_revision':'Original supported-operation count24 becomes25. All other method ASTs retain their API96 bytes; the earlier documented wire-minimum correction remains.',
        'authority_effect':'none','actual_owner_outcome':None,'runtime_qualification_transferred':False,'task_complete':False,'goal_complete':False})
    profile=load(OLD/'contract-profile.json');rows={r['path']:r for r in profile['files']}
    inputs=[bind(context),bind(Path(__file__).resolve())]
    for folder in [API,BASE/'current-source-adapter-v8',BASE/'current-participation-v10',BASE/'workflow-transition-v1']:
        for p in sorted(folder.rglob('*')):
            if p.is_file() and not {'receipts','__pycache__'}&set(p.parts):inputs.append(bind(p))
    for row in inputs:rows[row['path']]=row
    # Select exact literal operation declarations without importing mutable API
    # staging before its independent profile/source freeze exists.
    declarations={}
    for n in ast.parse((API/'protocol.py').read_text()).body:
        if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name):
            key=n.targets[0].id
            if key.endswith('SUPPORTED'):
                def value(x):
                    if isinstance(x,ast.Name):return declarations[x.id]
                    if isinstance(x,ast.BinOp) and isinstance(x.op,ast.Add):return value(x.left)+value(x.right)
                    return ast.literal_eval(x)
                declarations[key]=value(n.value)
    assert len(declarations['SUPPORTED'])==25 and len(set(declarations['SUPPORTED']))==25
    profile.update(implemented_operations=list(declarations['SUPPORTED']),files=[rows[k] for k in sorted(rows)],
        workflow_context_binding=bind(context),workflow_source_binding=bind(BASE/'current-participation-v10/source-manifest.json'),
        claim_ceiling='25authored candidate handlers, including exact owned workflow coordination; actual public/inherited conformance and remaining9operations required.')
    emit(API/'contract-profile.json',profile)
    full={r['path']:r for r in parent['files']}
    for row in [*rows.values(),bind(API/'contract-profile.json'),bind(OLD/'source-manifest.json')]:full[row['path']]=row
    for row in full.values():assert bind(ROOT/row['path'])==row,row['path']
    emit(API/'source-manifest.json',{**parent,'files':[full[k] for k in sorted(full)],'parent_source_binding':bind(OLD/'source-manifest.json'),
        'authored_handler_count':25,'unchanged_inherited_method_count':322,'explicit_revised_methods':changed,
        'workflow_context_binding':bind(context),'workflow_public_runtime_qualified':False,
        'whole_API_qualified':False,'runtime_qualification_transferred':False,'task_complete':False,'goal_complete':False})
    print(json.dumps({'result':'FROZEN','source_binding':bind(API/'source-manifest.json'),'profile_binding':bind(API/'contract-profile.json'),'authored_handlers':25}),flush=True)
if __name__=='__main__':main()
