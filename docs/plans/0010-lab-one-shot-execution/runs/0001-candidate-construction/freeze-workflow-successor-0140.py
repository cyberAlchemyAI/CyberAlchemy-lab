"""Finalize only after the same Source11 construction completed successfully."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
RUN=Path(__file__).resolve().parent;ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface';SOURCE=BASE/'current-participation-v11'
ADAPTER=BASE/'current-source-adapter-v9';OLD=BASE/'api-integration-v1';API=BASE/'api-integration-v2'
def bind(p):return {'path':p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def load(p):return json.loads(p.read_bytes())
def emit(p,v):
    with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')
def methods(p):return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(p.read_text())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
def main():
    assert load(SOURCE/'packages/0001/build-result.json')['result']=='PASS'
    package=load(SOURCE/'packages/0001/manifest.json');source=load(SOURCE/'source-manifest.json')
    assert not (API/'source-manifest.json').exists() and not (ADAPTER/'source-manifest.json').exists()
    for row in source['files']+package['files']:assert bind(ROOT/row['path'])==row,row['path']
    parent_adapter=load(BASE/'current-source-adapter-v8/source-manifest.json');arows={r['path']:r for r in parent_adapter['files']}
    for row in source['files']+package['files']:arows[row['path']]=row
    for p in [SOURCE/'source-manifest.json',SOURCE/'packages/0001/manifest.json',*sorted(ADAPTER.glob('*'))]:
        if p.is_file():
            if p.suffix=='.py':ast.parse(p.read_text())
            row=bind(p);arows[row['path']]=row
    emit(ADAPTER/'source-manifest.json',{**parent_adapter,'schema_version':'lab-current-source-adapter/v9-candidate',
        'files':[arows[k] for k in sorted(arows)],'producer_source_binding':bind(SOURCE/'source-manifest.json'),
        'producer_package_binding':bind(SOURCE/'packages/0001/manifest.json'),
        'identity_correction_evidence_binding':bind(RUN/'workflow-integration-diagnosis-0139.json'),'actual_runtime_qualified':False})
    p=API/'source_bridge.py';text=p.read_text();assert 'WORKFLOW_PACKAGE_PIN=None' in text and 'WORKFLOW_ADAPTER_PIN=None' in text
    text=text.replace('WORKFLOW_PACKAGE_PIN=None',"WORKFLOW_PACKAGE_PIN='"+bind(SOURCE/'packages/0001/manifest.json')['sha256']+"'")
    text=text.replace('WORKFLOW_ADAPTER_PIN=None',"WORKFLOW_ADAPTER_PIN='"+bind(ADAPTER/'source-manifest.json')['sha256']+"'");p.write_text(text)
    spec=importlib.util.spec_from_file_location('_workflow_successor_parent',OLD/'guard.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
    parent=g.verify('12cccc986edfd04aede1b1ced57db0777e6d8713b791cd8660796f7cd92d0b15')
    retained=[]
    for p in sorted(API.glob('*.py')):
        ast.parse(p.read_text())
        if (OLD/p.name).exists():assert methods(p)==methods(OLD/p.name),p.name;retained.extend(p.name+':'+n for n in methods(p))
    assert len(retained)==323
    context=RUN/'context-R03-workflow-exact-decision-0140.json'
    emit(context,{'schema_version':'lab-bounded-context/v1-candidate','task':'R03 current workflow exact Decision closure',
        'files':[bind(p) for p in [RUN/'authorization.json',RUN/'workflow-integration-diagnosis-0139.json',OLD/'source-manifest.json',
            SOURCE/'source-manifest.json',SOURCE/'packages/0001/manifest.json',ADAPTER/'source-manifest.json',Path(__file__).resolve()]],
        'correction':'Unique domain interpretation and generated admission Decision identifiers; exact version in Intent Resolution. Original sources and periods retained.',
        'preflight_read_scope':'One synchronous model batch inside the existing pure source/policy guards; full entry/exit guards and original callback checks retained. No permission or body cache across calls.',
        'original_methods_retained':323,'runtime_qualification_transferred':False,'authority_effect':'none','actual_owner_outcome':None})
    profile=load(OLD/'contract-profile.json');rows={r['path']:r for r in profile['files']}
    for folder in [API,ADAPTER,SOURCE]:
        for p in sorted(folder.rglob('*')):
            if p.is_file() and not {'receipts','__pycache__'}&set(p.parts):row=bind(p);rows[row['path']]=row
    for p in [context,Path(__file__).resolve()]:row=bind(p);rows[row['path']]=row
    profile.update(files=[rows[k] for k in sorted(rows)],workflow_context_binding=bind(context),workflow_source_binding=bind(SOURCE/'source-manifest.json'))
    emit(API/'contract-profile.json',profile)
    full={r['path']:r for r in parent['files']}
    for row in [*rows.values(),bind(API/'contract-profile.json'),bind(OLD/'source-manifest.json')]:full[row['path']]=row
    for row in full.values():assert bind(ROOT/row['path'])==row,row['path']
    emit(API/'source-manifest.json',{**parent,'files':[full[k] for k in sorted(full)],'parent_source_binding':bind(OLD/'source-manifest.json'),
        'workflow_context_binding':bind(context),'retained_inherited_methods':retained,'unchanged_inherited_method_count':323,
        'explicit_revised_methods':[],'workflow_public_runtime_qualified':False,'whole_API_qualified':False,'runtime_qualification_transferred':False})
    print(json.dumps({'result':'FROZEN','source_binding':bind(API/'source-manifest.json'),'profile_binding':bind(API/'contract-profile.json'),
        'adapter_binding':bind(ADAPTER/'source-manifest.json'),'package_binding':bind(SOURCE/'packages/0001/manifest.json')}),flush=True)
if __name__=='__main__':main()
