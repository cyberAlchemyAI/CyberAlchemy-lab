"""Freeze the complete declared lesson host source before real transport checks."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
from jsonschema import Draft202012Validator

RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface'
OLD,API=BASE/'api-v50',BASE/'api-v51'
HOST=BASE/'lesson-host-composition-v1'
RULES=BASE/'lesson-selection-rules-v2'
CHECKS=BASE/'api51-lesson-checks-v1'


def load(p):return json.loads(p.read_bytes())


def bind(p):return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}


def emit(p,v):
    with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')


def files(root):
    return [p for p in root.rglob('*') if p.is_file() and not {'receipts','__pycache__'} & set(p.parts)
            and p.name not in ('source-manifest.json','contract-profile.json')]


def tests(path):
    return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(path.read_bytes()))
            if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}


def main():
    spec=importlib.util.spec_from_file_location('_API51_freeze_original_guard',OLD/'guard.py')
    guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
    parent=guard.verify('3e46a5bef724a601d3f465841205f8c73a7723637538fd738cdd2ef7a85dcd64')
    proof=load(RULES/'receipts/checks-0001.json')
    assert proof['result']=='PASS' and proof['pure_cases']==61 and proof['pure_failures']==proof['pure_errors']==0
    assert proof['original_W06_full_suite_completed'] and proof['original_W06_actual_exit_code']==0
    retained=[]
    for p in files(OLD):
        if p.suffix=='.py':
            assert tests(p)==tests(API/p.relative_to(OLD)),p
            retained.extend(str(p.relative_to(OLD))+':'+name for name in tests(p))
    assert len(retained)==293
    old=load(OLD/'authentication.schema.json');new=load(API/'authentication.schema.json')
    assert new['oneOf'][:-1]==old['oneOf'] and len(new['oneOf'])==len(old['oneOf'])+1
    Draft202012Validator.check_schema(new)
    Draft202012Validator.check_schema(load(HOST/'plan.schema.json'))
    for p in files(API)+files(HOST)+files(CHECKS):
        if p.suffix=='.py':ast.parse(p.read_bytes())
    context=RUN/'context-R03-lesson-host-API-0051.json'
    emit(context,{'schema_version':'lab-bounded-context/v1-candidate','strict_coverage':'PASS','task':'R03',
        'source_bindings':[bind(OLD/'source-manifest.json'),bind(RULES/'source-manifest.json'),bind(RULES/'receipts/checks-0001.json'),bind(RUN/'authorization.json')],
        'write_scope':[p.relative_to(ROOT).as_posix() for p in (API,HOST,CHECKS)],
        'constraints':['Preserve original34 public contracts and293 inherited test methods.',
            'Preserve every old authentication policy variant and exact operation set; new declared read variant adds only lesson.select.',
            'Actual MachinePeer, parent Service, signed source, live Session, Assignment, independent host plan and original participation checks required.',
            'No source/permission callback replacement, fake Session, action grant, deadline extension, Application or owner outcome.',
            'Nonempty actual signed source and full public suites remain required; zero catalog alone cannot qualify complete lesson behavior.',
            'Single final R08 after full S02; existing candidate development authorization controls effects.'],
        'authority_effect':'none','actual_owner_outcome':None,'task_complete':False})
    static=RUN/'API51-final-static-0001.json'
    changed=[p.relative_to(OLD).as_posix() for p in files(OLD) if p.read_bytes()!=(API/p.relative_to(OLD)).read_bytes()]
    assert sorted(changed)==sorted(['auth.py','authentication.schema.json','machine_transport.py','protocol.py','service.py'])
    emit(static,{'schema_version':'lab-lesson-host-final-static/v1-candidate','result':'PASS','retained_original_methods':293,
        'old_authentication_variants_preserved':True,'authored_handlers':18,'missing_operations':16,
        'changed_inherited_files':changed,'added_handler_loader':'lesson_selection.py','runtime_qualified':False,'actual_public_calls':0,
        'authority_effect':'none','actual_owner_outcome':None,'task_complete':False})
    profile=load(OLD/'contract-profile.json')
    profile['files']=[bind(API/(ROOT/row['path']).relative_to(OLD)) if (ROOT/row['path']).is_relative_to(OLD) else row for row in profile['files']]
    profile['implemented_operations'].append('lesson.select')
    assert len(profile['implemented_operations'])==18
    profile['files']+= [bind(p) for p in files(HOST)+files(CHECKS)+files(RULES)]
    profile['files']+=[bind(API/'lesson_selection.py'),bind(RULES/'source-manifest.json'),bind(RULES/'receipts/checks-0001.json'),bind(context),bind(static)]
    profile['lesson_host_context_binding']=bind(context)
    profile['lesson_host_rule_proof_binding']=bind(RULES/'receipts/checks-0001.json')
    profile['claim_ceiling']='Eighteen authored handlers; original contracts/policies/tests retained. Lesson host transport, nonempty signed inventory, assigned Machine typed permission and full API remain unqualified.'
    emit(API/'contract-profile.json',profile)
    rows={row['path']:row for row in parent['files']}
    dependency=load(RULES/'source-manifest.json')
    for row in dependency['files']+dependency['input_bindings']:rows[row['path']]=row
    added=files(API)+files(HOST)+files(CHECKS)+[OLD/'source-manifest.json',API/'contract-profile.json',RULES/'source-manifest.json',
        RULES/'receipts/checks-0001.json',context,static,Path(__file__).resolve(),RUN/'build-lesson-host-API-0051-0001.py',RUN/'refine-lesson-Machine-subset-0001.py']
    for p in added:
        row=bind(p);rows[row['path']]=row
    for row in rows.values():assert hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],row['path']
    emit(API/'source-manifest.json',{**parent,'files':[rows[k] for k in sorted(rows)],'parent_source_binding':bind(OLD/'source-manifest.json'),
        'context_binding':bind(context),'retained_inherited_methods':retained,'unchanged_inherited_method_count':293,
        'lesson_host_rule_source_binding':bind(RULES/'source-manifest.json'),'whole_API_qualified':False,'current_Agent_qualified':False,
        'lesson_nonempty_signed_source_qualified':False,'task_complete':False,'goal_complete':False})
    print(json.dumps({'result':'FROZEN','source_binding':bind(API/'source-manifest.json'),'profile_binding':bind(API/'contract-profile.json'),
        'original_methods_retained':293,'authored_handlers':18,'missing_operations':16,'actual_public_calls':0}),flush=True)


if __name__=='__main__':main()
