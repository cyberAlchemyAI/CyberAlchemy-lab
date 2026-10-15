"""Construct declared API51 lesson read successor; preserve all API50 bytes."""
import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[4]
BASE=ROOT/'product/lab/release-candidates/v1/interface'
OLD,NEW=BASE/'api-v50',BASE/'api-v51'
HOST=BASE/'lesson-host-composition-v1'


def bind(p): return {'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}


def emit(p,v):
    with p.open('x') as f:json.dump(v,f,indent=2,sort_keys=True);f.write('\n')


def replace(p,old,new):
    text=p.read_text();assert text.count(old)==1,(p,old);p.write_text(text.replace(old,new))


def selected_files(base):
    return [p for p in base.rglob('*') if p.is_file() and not {'receipts','__pycache__'} & set(p.parts)
            and p.name not in ('source-manifest.json','contract-profile.json')]


def main():
    spec=importlib.util.spec_from_file_location('_API51_predecessor_guard',OLD/'guard.py')
    guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
    previous=guard.verify('3e46a5bef724a601d3f465841205f8c73a7723637538fd738cdd2ef7a85dcd64')
    report=json.loads((BASE/'lesson-selection-rules-v2/receipts/checks-0001.json').read_bytes())
    assert report['result']=='PASS' and report['pure_cases']==61 and report['original_W06_cases']==53
    NEW.mkdir();(NEW/'receipts').mkdir()
    for p in selected_files(OLD):
        d=NEW/p.relative_to(OLD);d.parent.mkdir(parents=True,exist_ok=True);d.write_bytes(p.read_bytes())
    replace(NEW/'protocol.py',"SUPPORTED=LEGACY_SUPPORTED+('files.materialize','proposal.review','classification.prepare','failure.assess','typed.extension.prepare')",
        "LESSON_SUPPORTED=LEGACY_SUPPORTED+('lesson.select',)\nSUPPORTED=LEGACY_SUPPORTED+('files.materialize','proposal.review','classification.prepare','failure.assess','typed.extension.prepare','lesson.select')")
    replace(NEW/'auth.py',"        metadata=export or review or classification or failure or typed or value['schema_version']=='lab-local-metadata-candidate-policy/v1-candidate'",
        "        lesson=value['schema_version']=='lab-local-lesson-read-policy/v1-candidate'\n        metadata=export or review or classification or failure or typed or value['schema_version']=='lab-local-metadata-candidate-policy/v1-candidate'\n        if lesson:fields+=['lesson_control','development_authorization_binding']")
    replace(NEW/'auth.py',"'lab-local-typed-extension-candidate-policy/v1-candidate')\n            and value['scope_posture']", "'lab-local-typed-extension-candidate-policy/v1-candidate','lab-local-lesson-read-policy/v1-candidate')\n            and value['scope_posture']")
    replace(NEW/'auth.py',"list(EXPORT_SUPPORTED if export else", "list(LESSON_SUPPORTED if lesson else EXPORT_SUPPORTED if export else")
    replace(NEW/'auth.py',"        if classification:\n            from .workspace import read_private",
        "        if lesson:\n            from .workspace import read_private\n            authority=ROOT/'docs/plans/0010-lab-one-shot-execution/runs/0001-candidate-construction/authorization.json'\n            selected=value['lesson_control']['plan_binding']\n            matches=[row for row in selected_manifest['materials'] if row['ref']==selected['ref'] and row['sha256']==selected['sha256']]\n            source.require(value['source_name']=='custody-participation' and value['development_authorization_binding']==binding(str(authority.relative_to(ROOT)),authority.read_bytes()) and len(matches)==1,'lesson policy lacks exact independent development/plan selection')\n            plan_raw=read_private(selected_root/matches[0]['path'])\n            source.require(source.sha(plan_raw)==selected['sha256'] and frame_parse(plan_raw).get('schema_version')=='lab-lesson-host-plan/v1-candidate','independent lesson plan bytes differ')\n        if classification:\n            from .workspace import read_private")
    replace(NEW/'machine_transport.py',"                   'context.get', 'session.inspect', 'operation.inspect')", "                   'context.get', 'session.inspect', 'operation.inspect', 'lesson.select')")
    schema=json.loads((NEW/'authentication.schema.json').read_bytes())
    original=copy.deepcopy(schema['oneOf'])
    variant=copy.deepcopy(original[0])
    variant['properties']['schema_version']={'const':'lab-local-lesson-read-policy/v1-candidate'}
    variant['properties']['allowed_operations']['const'].append('lesson.select')
    variant['properties']['source_name']={'const':'custody-participation'}
    b={'type':'object','additionalProperties':False,'required':['ref','sha256'],'properties':{'ref':{'type':'string','minLength':1},'sha256':{'type':'string','pattern':'^[a-f0-9]{64}$'}}}
    variant['properties']['development_authorization_binding']=b
    variant['properties']['lesson_control']={'type':'object','additionalProperties':False,'required':['plan_binding'],'properties':{'plan_binding':b}}
    variant['required']+=['lesson_control','development_authorization_binding']
    schema['oneOf'].append(variant)
    assert schema['oneOf'][:-1]==original
    (NEW/'authentication.schema.json').write_text(json.dumps(schema,indent=2,sort_keys=True)+'\n')
    replace(NEW/'service.py','from .typed_preparation import TypedPreparation','from .typed_preparation import TypedPreparation\nfrom .lesson_selection import LessonHost')
    replace(NEW/'service.py',"'classification_preparation.py','failure_preparation.py','typed_preparation.py')", "'classification_preparation.py','failure_preparation.py','typed_preparation.py','lesson_selection.py')")
    replace(NEW/'service.py',"'handler_binding':binding(str((HERE/'typed_preparation.py')", "'handler_binding':binding(str((HERE/'lesson_selection.py').relative_to(ROOT)),(HERE/'lesson_selection.py').read_bytes()) if call['operation']=='lesson.select' else binding(str((HERE/'typed_preparation.py')")
    replace(NEW/'service.py',"            elif name=='operation.inspect':domain=self.candidates.inspect(message,request,call['expected_source_cut'])",
        "            elif name=='lesson.select':\n                path=HERE/'source-manifest.json'\n                builder=LessonHost(self,{'path':str(path.relative_to(ROOT)),'sha256':source.sha(path.read_bytes())})\n                domain=builder.select(message,request,call['expected_source_cut'],inner,effective,ceiling)\n            elif name=='operation.inspect':domain=self.candidates.inspect(message,request,call['expected_source_cut'])")
    loader='''"""Select the explicit lesson host composition without changing frozen packages."""
import importlib.util
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
PATH=HERE.parent/'lesson-host-composition-v1'
NAME='_cal_'+HERE.name.replace('-','_')+'_lesson_host_v1'
if NAME not in sys.modules:
    spec=importlib.util.spec_from_file_location(NAME,PATH/'__init__.py',submodule_search_locations=[str(PATH)])
    package=importlib.util.module_from_spec(spec);sys.modules[NAME]=package;spec.loader.exec_module(package)
selected=__import__(NAME+'.host',fromlist=['LessonHost'])
assert Path(selected.__file__).resolve()==PATH/'host.py'
LessonHost=selected.LessonHost
'''
    with (NEW/'lesson_selection.py').open('x') as f:f.write(loader)
    retained=[]
    for p in selected_files(OLD):
        if p.suffix!='.py':continue
        def tests(path):return {n.name:ast.dump(n,include_attributes=False) for n in ast.walk(ast.parse(path.read_bytes())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
        assert tests(p)==tests(NEW/p.relative_to(OLD)),p
        retained.extend(str(p.relative_to(OLD))+':'+name for name in tests(p))
    assert len(retained)==293
    for p in selected_files(NEW):
        if p.suffix=='.py':ast.parse(p.read_bytes())
    emit(RUN/'API51-construction-static-0001.json',{'schema_version':'lab-lesson-host-static/v1-candidate','result':'PASS','retained_methods':293,
        'original_authentication_variants_preserved':True,'new_read_policy':'lab-local-lesson-read-policy/v1-candidate',
        'authored_operations':18,'unimplemented_operations':16,'actual_public_calls':0,'runtime_qualified':False,
        'parent_source_binding':bind(OLD/'source-manifest.json'),'files':[bind(p) for p in selected_files(NEW)]+[bind(p) for p in HOST.iterdir() if p.is_file()],
        'authority_effect':'none','actual_owner_outcome':None,'task_complete':False})
    print(json.dumps({'result':'CONSTRUCTED-UNFROZEN','retained_methods':293,'authored_handlers':18,'actual_public_calls':0}),flush=True)


if __name__=='__main__':main()
